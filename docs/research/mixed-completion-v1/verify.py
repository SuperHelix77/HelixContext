"""Check frozen offline artifacts and code identity; no model requests."""
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]


def main():
    closure=json.loads((HERE/'CLOSURE.json').read_text())
    for name,digest in closure['files'].items():
        assert hashlib.sha256((REPO/name).read_bytes()).hexdigest()==digest,name
    r=json.loads((HERE/'RESULT.json').read_text())
    for name,digest in r['source_bindings'].items():
        assert hashlib.sha256((REPO/name).read_bytes()).hexdigest()==digest,name
    assert r['new_native_calls']==0 and r['scripted_events']==50
    assert r['scripted_semantic_checkpoints']==4 and r['caller_owned_acks']==46
    assert r['exact_order_answer_state_recovery']=='PASS'
    assert r['late_replay_does_not_roll_back_state']=='PASS'
    initial_bytes=len(json.dumps({'established_facts':[],'open_questions':[]},sort_keys=True,separators=(',',':')).encode())
    assert initial_bytes+sum(x['store_delta']['object_bytes_read'] for x in r['per_append'])==r['append_io']['object_bytes_read']
    prior=json.loads((REPO/'docs/research/cold-native-final-v1/AUDIT.json').read_text())
    for x in r['native_format_replays']:
        original=next(p for p in prior['rows'] if p['arm']==x['arm'])
        assert x['native_sha256']==original['native_sha256'] and x['final_sha256']==original['final_sha256']
        assert x['unchanged_native_final']=='PASS'
    print(json.dumps({'integrity':'PASS','bound_files':len(closure['files']),'new_native_calls':0,
                      'status':'OFFLINE_INTEGRATION_CANDIDATE_NOT_MODEL_RELEASE'}))


if __name__=='__main__':main()
