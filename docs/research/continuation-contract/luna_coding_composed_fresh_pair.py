"""Fresh known-fixture qualification of the frozen V7-base plus V3-caller composition."""
import json,secrets,sys
from pathlib import Path
import luna_coding_decision_v3 as v3
import luna_coding_composed_v1 as composition
from observed_session import Session


def prepare(root,prior):
    composition.prepare(root,prior);root=Path(root).resolve();m=json.loads((root/'manifest.json').read_text())
    spec=json.loads((root/'coding-source.json').read_text());off=root/'off';off.mkdir()
    for name,text in spec['files'].items():(off/name).write_text(text)
    # Same skill catalog entry is available; only the candidate attaches it.
    skill=off/'.agents/skills/helixcontext/SKILL.md';skill.parent.mkdir(parents=True)
    skill.write_bytes((root/'on/.agents/skills/helixcontext/SKILL.md').read_bytes())
    prompt='Work only in this task directory. Other runs and evaluators are out of scope. Ordinary tools and semantic review remain available.\n'+spec['task']
    (root/'off-prompt.txt').write_text(prompt)
    order=['off','on'];secrets.SystemRandom().shuffle(order)
    m.update(pair_order=order,pair_classification='Fresh known coding pair; native default base vs frozen V7-base/V3-caller composition; same High/tools; not holdout')
    for p in [Path(__file__),Path(v3.__file__),Path(composition.__file__),Path(__file__).with_name('luna_coding_composed_fresh_audit.py'),skill,root/'off-prompt.txt',off/'settings.json',off/'test_allocation.py']:
        m['sha256'][str(p.resolve())]=v3.v2.cap.kd.sha(p)
    v3.v2.cap.kd.save(root/'manifest.json',m)


def run(root):
    root=Path(root);m=json.loads((root/'manifest.json').read_text());cap=v3.v2.cap
    target=root/'pair-results.json'
    if target.exists():raise ValueError('No retry')
    r={'state':'RUNNING','rows':{}};cap.kd.save(target,r)
    try:
        for arm in m['pair_order']:
            cap.verify(m)
            if arm=='on':
                composition.run(root);candidate=json.loads((root/'results.json').read_text())
                r['rows'][arm]={'usage':candidate['usage'],'checks':candidate['turns'][-1]['completion']['checks']}
            else:
                with Session(m['model'],root/'off',root/'off-run') as s:
                    answer,turn=s.turn((root/'off-prompt.txt').read_text())
                    r['rows'][arm]={'usage':dict(s.total),'answer':answer,'turn':turn}
                    cap.kd.save(target,r)
                if s.failed:raise RuntimeError('Control native/raw capture failed')
                cap.verify(m);r['rows'][arm]['checks']=cap.grade(root,'coding',root/'off',answer)
            cap.kd.save(target,r)
        r['state']='AWAITING_PAIR_AUDIT';cap.kd.save(target,r)
        print(json.dumps(r))
    except BaseException as exc:
        r.update(state='STOPPED_PENDING_AUDIT',error=repr(exc));cap.kd.save(target,r);raise


if __name__=='__main__':globals()[sys.argv[1]](*sys.argv[2:])
