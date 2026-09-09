import hashlib,json
import pytest
from raw_receipts import capture


def fixture(path):
    rows=[{'type':'session_meta','payload':{'id':'thread1'}},
          {'type':'response_item','payload':{'type':'custom_tool_call','call_id':'c1','name':'exec','input':'synthetic'}},
          {'type':'response_item','payload':{'type':'custom_tool_call_output','call_id':'c1','output':'process creation failed'}},
          {'type':'response_item','payload':{'type':'reasoning','text':'not indexed'}}]
    path.write_bytes(b''.join(json.dumps(r).encode()+b'\n' for r in rows))


def test_failed_attempt_is_preserved_without_command_event(tmp_path):
    source=tmp_path/'source';fixture(source);r=capture(source,tmp_path/'out','thread1')
    assert r['calls']==r['outputs']==1 and r['unmatched_calls']==[]
    assert len(r['records'])==2
    raw=(tmp_path/'out/raw-rollout.jsonl').read_bytes()
    assert raw==source.read_bytes()
    for record in r['records']:
        assert hashlib.sha256(raw[record['start']:record['end']]).hexdigest()==record['line_sha256']
    with pytest.raises(FileExistsError):capture(source,tmp_path/'out','thread1')


def test_foreign_thread_and_truncated_json_publish_nothing(tmp_path):
    source=tmp_path/'source';fixture(source)
    with pytest.raises(ValueError):capture(source,tmp_path/'out','other')
    assert not (tmp_path/'out').exists()
    source.write_bytes(source.read_bytes()+b'{')
    with pytest.raises(ValueError):capture(source,tmp_path/'out','thread1')
    assert not (tmp_path/'out').exists()
