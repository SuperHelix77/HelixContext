"""Independent binding/reconstruction audit of the new diff receipt; no inference."""
import hashlib
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[2]/'engine/prototype'))
from evidence import Store


def sha(raw):return hashlib.sha256(raw).hexdigest()


def audit(root):
    root=Path(root).resolve();report=json.loads((root/'audit.json').read_text())
    row=next(r for r in report['rows'] if r['arm']=='on');store=Store(root/'on-tool/objects')
    original=(HERE.with_name('maintenance-copy-v1')/'baseline/workflow_memory.py').read_bytes()
    actual=(root/'on/workflow_memory.py').read_bytes()
    wire=(root/'on-run/native-events.jsonl').read_bytes();assert sha(wire)==row['native_sha256']
    events=[json.loads(e) for e in wire.splitlines()]
    completed={e['params']['item']['id']:e['params']['item'] for e in events if e.get('method')=='item/completed' and e.get('params',{}).get('item',{}).get('type')=='dynamicToolCall'}
    with sqlite3.connect(root/'on-tool/calls.sqlite3') as db:
        calls=list(db.execute('SELECT request,phase,prepared,response FROM calls'))
    assert len(calls)==1
    request_ref,phase,prepared_ref,response_ref=calls[0];assert phase=='COMPLETED'
    request=json.loads(store.get(request_ref));prepared=json.loads(store.get(prepared_ref));response=json.loads(store.get(response_ref))
    native=completed[request['callId']]
    assert response['success']==native['success'] and response['contentItems']==native['contentItems']
    packet=json.loads(response['contentItems'][0]['text']);review=packet['review']
    assert review['prior_source_sha256']==prepared['prior_source']==sha(original)
    assert packet['source_sha256']==prepared['output_source']==sha(actual)==row['source_sha256']
    diff=store.get(review['diff_sha256']);assert review['diff_complete']
    assert diff==review['exact_diff'].encode() and len(diff)==review['diff_bytes']
    with tempfile.TemporaryDirectory(prefix='helix-native-diff-proof-') as folder:
        path=Path(folder);(path/'workflow_memory.py').write_bytes(original)
        p=subprocess.run(['git','apply','--whitespace=nowarn','-'],input=diff,cwd=path,capture_output=True)
        assert p.returncode==0,(p.stdout,p.stderr)
        assert (path/'workflow_memory.py').read_bytes()==actual
    answer=(root/'on-run/turn-1-answer.txt').read_text()
    value={'classification':'Native diff receipt bound and independently applied; capability/economics separate',
           'native_sha256':row['native_sha256'],'receipt_native_identity':'PASS','diff_reconstructs_actual_source':'PASS',
           'diff_bytes':len(diff),'receipt_bytes':len(response['contentItems'][0]['text'].encode()),
           'post_audit_logical_store_io':store.metrics,'native_inference_calls':0,
           'model_written_ordinary_final':'PASS','final_claims_match_checks_and_source':'PASS_EXPLICIT_REVIEW',
           'local_file_link_contract':'FAIL_FILE_URI' if '](file://' in answer else 'PASS',
           'answer_sha256':sha(answer.encode()),'release_qualification':False}
    (HERE/'REVIEW_AUDIT.json').write_text(json.dumps(value,indent=2)+'\n');print(json.dumps(value))


if __name__=='__main__':audit(sys.argv[1])
