"""Pure configuration projection for explicitly scoped benchmark client homes.

Only caller-identified command hashes may be removed. All other parsed settings
are preserved. Hook trust values are never fabricated; relocated identifiers need
native trust revalidation before use. No credentials, files or global env mutated.
"""
import copy
import hashlib
import json
import math
import re
import tomllib


def sha(raw):return hashlib.sha256(raw).hexdigest()


def literal(value):
    if isinstance(value,str):return json.dumps(value,ensure_ascii=False)
    if type(value) is bool:return 'true' if value else 'false'
    if type(value) is int:return str(value)
    if type(value) is float and math.isfinite(value):return repr(value)
    if isinstance(value,list):return '['+','.join(literal(x) for x in value)+']'
    if isinstance(value,dict):
        if any(not isinstance(k,str) for k in value):raise ValueError('TOML keys must be strings')
        return '{'+','.join(literal(k)+'='+literal(v) for k,v in value.items())+'}'
    raise ValueError('Unsupported TOML value; do not silently change its type')


def serialize(config):
    raw=('\n'.join(literal(k)+'='+literal(v) for k,v in config.items())+'\n').encode()
    if tomllib.loads(raw.decode())!=config:raise ValueError('TOML roundtrip mismatch')
    return raw


def project_config(raw,source_file,destination_file,excluded_command_hashes):
    original=tomllib.loads(raw.decode());result=copy.deepcopy(original)
    hashes=set(excluded_command_hashes)
    if any(not isinstance(h,str) or not re.fullmatch('[0-9a-f]{64}',h) for h in hashes):
        raise ValueError('Explicit SHA256 command identities required')
    hooks=original.get('hooks',{})
    if not isinstance(hooks,dict):raise ValueError('Unexpected hook schema')
    source_prefix=str(source_file)+':';target_prefix=str(destination_file)+':'
    projected={};moves={};removed=[];kept=[]
    for event,groups in hooks.items():
        if event=='state':continue
        if not isinstance(groups,list):raise ValueError('Unknown hook event schema')
        new_groups=[];event_id=re.sub(r'(?<!^)(?=[A-Z])','_',event).lower()
        for gi,group in enumerate(groups):
            if not isinstance(group,dict) or not isinstance(group.get('hooks'),list):raise ValueError('Unknown hook group')
            new_hooks=[]
            for hi,hook in enumerate(group['hooks']):
                if not isinstance(hook,dict):raise ValueError('Unknown hook definition')
                old_id=source_prefix+f'{event_id}:{gi}:{hi}'
                command=hook.get('command')
                digest=sha(command.encode()) if hook.get('type')=='command' and isinstance(command,str) else None
                if digest in hashes:
                    removed.append({'id':old_id,'command_sha256':digest});moves[old_id]=None
                else:
                    new_id=target_prefix+f'{event_id}:{len(new_groups)}:{len(new_hooks)}'
                    moves[old_id]=new_id;new_hooks.append(copy.deepcopy(hook))
                    kept.append({'source_id':old_id,'destination_id':new_id,'command_sha256':digest})
            if new_hooks:new_groups.append({**copy.deepcopy(group),'hooks':new_hooks})
        if new_groups:projected[event]=new_groups
    if hashes!={r['command_sha256'] for r in removed}:
        raise ValueError('Excluded command missing; source scope may have drifted')
    state=hooks.get('state',{})
    if not isinstance(state,dict):raise ValueError('Unknown hook trust schema')
    new_state={}
    for old_id,value in state.items():
        if old_id.startswith(source_prefix):
            if old_id not in moves:raise ValueError('Unmatched local hook trust identity')
            new_id=moves[old_id]
        else:new_id=old_id # Foreign trust state is preserved, not promoted to this home.
        if new_id is not None:
            if new_id in new_state:raise ValueError('Hook trust identity collision')
            new_state[new_id]=copy.deepcopy(value)
    if new_state:projected['state']=new_state
    if projected:result['hooks']=projected
    else:result.pop('hooks',None)
    assert {k:v for k,v in original.items() if k!='hooks'}=={k:v for k,v in result.items() if k!='hooks'}
    output=serialize(result)
    receipt={'schema':'helix.client-config-projection.v1','source_sha256':sha(raw),'output_sha256':sha(output),
        'source_bytes':len(raw),'output_bytes':len(output),'removed_hooks':removed,'retained_hooks':kept,
        'all_non_hook_settings_preserved':True,'retained_hook_definitions_preserved':True,
        'trust_values_preserved_without_fabrication':True,'native_trust_revalidated':False,
        'authentication_assets_copied':False,'ordinary_tool_catalog_verified':False}
    return output,receipt
