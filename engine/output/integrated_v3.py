"""V3 isolates native skill attachment; both arms use fresh app-server turns."""
from pathlib import Path
import json
import sys
import integrated_pair as v1
import integrated_v2 as v2
import app_server_native
from completion_pair import sha,save


def prepare(root):
    root,m,prompts,runtimes,catalog,expected=v2.prepare(root)
    for arm in ('off','on'):
        cwd=root/'tasks'/arm;skill=(cwd/'helixcontext/SKILL.md').read_bytes()
        native_skill=cwd/'.agents/skills/helixcontext/SKILL.md';native_skill.parent.mkdir(parents=True);native_skill.write_bytes(skill)
        m['preparation'][arm]['source_hashes']['.agents/skills/helixcontext/SKILL.md']=sha(skill)
    old='Apply this supplied Helix Context skill, also available exactly at helixcontext/SKILL.md:\n'+skill.decode()+'\n'
    assert prompts['on'].count(old)==1
    prompts['on']=prompts['on'].replace(old,'$helixcontext is attached using the native skill input, bound to .agents/skills/helixcontext/SKILL.md. The runtime supplies its full instructions.\n')
    for arm in ('off','on'):
        (root/f'{arm}-prompt.txt').write_text(prompts[arm]);m['preparation'][arm]['prompt_bytes']=len(prompts[arm].encode())
    m.update(schema='helix.sol_integrated_pair.v3',classification='Fresh app-server pair on reused development task; never compare CLI control against app-server candidate',
             prompts={k:sha(p.encode()) for k,p in prompts.items()},
             v3={'intervention':'Native skill input instead of inline skill body and model-side loading',
                 'runner':'Both arms app-server; High, workspace-write, never approval, normal tools',
                 'usage':'Final cumulative native thread/tokenUsage/updated; CLI-shaped events are derived, raw wire retained',
                 'registration':'Actual native thread id registered before turn/start; no model-side registration',
                 'scope':'Native attachment plus runner change; one fresh paired task, no holdout or universal parity',
                 'documentation':'https://learn.chatgpt.com/docs/app-server#skills'})
    m['dependencies'].update({str(p):sha(p.read_bytes()) for p in (Path(__file__),Path(app_server_native.__file__))})
    save(root/'manifest.json',m)
    return root,m,prompts,runtimes,catalog,expected


def run(root):
    v1.prepare=prepare;v1.native=app_server_native.native;v1.run(root)


if __name__=='__main__':run(sys.argv[1])
