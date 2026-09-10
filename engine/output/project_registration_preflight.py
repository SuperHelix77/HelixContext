"""Observe exact caller-owned task registration before freezing configuration.

No semantic inference, no direct config edits. Only a new trusted marker for the
generated Git root is an admitted initialization effect, with no .codex layers.
This is a setup checker; it does not loosen the configuration guard during a run.
"""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import time
import tomllib
from app_server_native import RPC
from config_bound_session import same,private_write,OVERRIDDEN


def registration_delta(initial,current,cwd):
    cwd=Path(cwd).resolve()
    if (cwd/'.codex').exists() or (cwd/'.codex').is_symlink():raise ValueError('Project-local Codex layers require separate review')
    a=tomllib.loads(initial.decode());b=tomllib.loads(current.decode());normalized=copy.deepcopy(b)
    ap=a.get('projects',{});bp=b.get('projects',{})
    if type(ap)is not dict or type(bp)is not dict:raise ValueError('Invalid projects table')
    added=set(bp)-set(ap)
    if added and (added!={str(cwd)} or not same(bp[str(cwd)],{'trust_level':'trusted'})):
        raise ValueError('Unexpected project registration')
    if any(k not in bp or not same(ap[k],bp[k]) for k in ap):raise ValueError('Existing project settings changed')
    if added:
        del normalized['projects'][str(cwd)]
        if 'projects' not in a and not normalized['projects']:del normalized['projects']
    changed=[k for k in a.keys()|normalized.keys() if not same(a.get(k),normalized.get(k))]
    if any(k not in OVERRIDDEN for k in changed):raise ValueError('Other effective settings changed')
    return {'schema':'helix.project-registration.v1','project':str(cwd),'added_trusted_marker':bool(added),
            'no_project_codex_layers':True,'other_effective_settings_unchanged':True,
            'model_defaults_changed':sorted(changed),'before_sha256':hashlib.sha256(initial).hexdigest(),
            'after_sha256':hashlib.sha256(current).hexdigest(),
            'trust_present':bp.get(str(cwd))=={'trust_level':'trusted'}}


def warm(cwd,out,model='gpt-5.6-luna'):
    cwd=Path(cwd).resolve();out=Path(out);out.mkdir(parents=True,exist_ok=False)
    root=Path(subprocess.check_output(['git','rev-parse','--show-toplevel'],cwd=cwd,text=True).strip()).resolve()
    if root!=cwd:raise ValueError('Task must be an isolated Git root')
    shared=Path.home()/'.codex/config.toml';initial=shared.read_bytes();private_write(out/'config.before.private.toml',initial)
    started=time.perf_counter();rpc=RPC(cwd,out,model)
    try:
        rpc.call('initialize',{'clientInfo':{'name':'helix-project-preflight','version':'1'},'capabilities':{'experimentalApi':True}})
        rpc.send({'method':'initialized'})
        resolved=rpc.call('thread/start',{'model':model,'cwd':str(cwd),'ephemeral':False,'approvalPolicy':'never','sandbox':'workspace-write','config':{'model_reasoning_effort':'high','skills.max_context_tokens':512}})
        if resolved.get('model')!=model or resolved.get('reasoningEffort')!='high':raise ValueError('Native settings mismatch')
        (out/'thread-start.json').write_text(json.dumps(resolved,indent=2)+'\n')
    finally:rpc.close()
    current=shared.read_bytes();private_write(out/'config.after.private.toml',current)
    result=registration_delta(initial,current,cwd)
    requests=[json.loads(l) for l in (out/'requests.jsonl').read_text().splitlines()]
    if any(r.get('method')=='turn/start' for r in requests):raise ValueError('Preflight invoked inference')
    result.update(model=model,effort='high',turn_start_requests=0,elapsed_seconds=time.perf_counter()-started,
                  requests_sha256=hashlib.sha256((out/'requests.jsonl').read_bytes()).hexdigest())
    (out/'receipt.json').write_text(json.dumps(result,indent=2)+'\n')
    return result
