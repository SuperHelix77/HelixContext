"""Versioned coding trial: caller memory receipt + local instruction recognition."""
import json,sys
from pathlib import Path
import luna_coding_decision_v2 as v2
import caller_memory_receipt as memory


def prepare(root,prior):
    v2.prepare(root,prior);root=Path(root).resolve();cwd=root/'on'
    manifest_path=root/'manifest.json';m=json.loads(manifest_path.read_text())
    task=(root/'prompt.txt').read_text().replace('Caller completed memory consultation; no recalled task facts. ','',1)
    receipt_dir=root/'memory-preflight'
    memory.prepare(cwd,task,'allocation.py allocate largest remainder unittest',receipt_dir)
    pin=memory.digest((receipt_dir/'receipt.json').read_bytes())
    (root/'prompt.txt').write_text(memory.attach(cwd,task,receipt_dir,pin))
    local=cwd/'AGENTS.md';local.write_text(memory.LOCAL_RULE)
    m['input_roots']['AGENTS.md']=v2.cap.kd.sha(local)
    m['classification']='Adaptive known coding V3; source-only caller completion plus task-bound memory preflight; retained control'
    m['intervention']='Local AGENTS recognizes actual caller memory receipt; no production/global instruction change'
    m['memory_preflight']=str(receipt_dir/'receipt.json')
    m['sha256'][str(root/'prompt.txt')]=v2.cap.kd.sha(root/'prompt.txt')
    for p in [Path(__file__),Path(memory.__file__),memory.CLIENT,local,*receipt_dir.iterdir()]:
        m['sha256'][str(p.resolve())]=v2.cap.kd.sha(p)
    v2.cap.kd.save(manifest_path,m)
    print(json.dumps({'manifest_sha256':v2.cap.kd.sha(manifest_path),'memory_state':json.loads((receipt_dir/'receipt.json').read_text())['state']}))


if __name__=='__main__':{'prepare':prepare,'run':v2.run}[sys.argv[1]](*sys.argv[2:])
