"""Real frozen-suite smoke check. No native inference or semantic acceptance."""
import json,shlex,sys,hashlib
from pathlib import Path
from prepared_review import prepare,validate

def run(original,out):
    original=Path(original);out=Path(out);out.mkdir(parents=True,exist_ok=False)
    raw=(original/'receipts/run/events.jsonl').read_bytes();status=json.loads((original/'receipts/run/status.json').read_text())
    assert hashlib.sha256(raw).hexdigest()==status['events_sha256']
    commands=[e['item']['command'] for e in map(json.loads,raw.splitlines()) if e.get('type')=='item.completed' and e.get('item',{}).get('type')=='command_execution']
    command=next(c for c in commands if 'class HostileInt' in c)
    supplemental=shlex.split(command)[-1].split("<<'PY'\n",1)[1].rsplit('\nPY',1)[0]
    results={}
    for label in ('valid','known_uncovered_defect'):
        source=out/label/'source';source.mkdir(parents=True)
        for n in ('proposal.py','CONTRACT.md','check.py','check_independence.py'):(source/n).write_bytes((original/n).read_bytes())
        (source/'supplemental.py').write_text(supplemental)
        if label!='valid':
            p=source/'proposal.py';p.write_text(p.read_text().replace('            pending.append(value)','            if value != 4093: pending.append(value)'))
        evidence=out/label/'evidence';h=prepare(source,evidence);r=validate(evidence,h)
        assert r['status']=='READY'
        ns={};exec((source/'proposal.py').read_text(),ns);q=ns['Queue']();ret=q.append_batch([4093])
        expected=label=='valid';assert (ret==1 and q.items==[4093])==expected
        results[label]={'receipt_hash':h,'mechanical_status':r['status'],'checks':{c['name']:c['status'] for c in r['checks']},'independent_contract_witness_pass':expected,'cost':r['cost']}
    result={'classification':'Offline research preflight; no native decisions or savings','native_calls':0,'results':results,'source_events_sha256':hashlib.sha256(raw).hexdigest()}
    (out/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':run(*sys.argv[1:])
