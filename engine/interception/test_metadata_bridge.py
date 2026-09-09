import copy,json
import pytest
from metadata_bridge import Bridge
from post_tool import safe_transform

def pair(exit_code=7,call='call-a'):
    output='noise\n'*3000+'ERROR expected=000.050\n'
    event={'method':'item/completed','params':{'threadId':'s','turnId':'t','item':{'type':'commandExecution','id':call,'exitCode':exit_code,'status':'failed' if exit_code else 'completed','aggregatedOutput':output,'command':'fixture','cwd':'fixture','durationMs':1}}}
    hook={'hook_event_name':'PostToolUse','tool_name':'Bash','session_id':'s','turn_id':'t','tool_use_id':call,'tool_input':{'command':'fixture'},'tool_response':output}
    return event,hook

def test_identical_text_preserves_distinct_exit_status(tmp_path):
    bridge=Bridge(tmp_path/'bridge')
    for code,call in ((0,'first'),(7,'second')):
        event,hook=pair(code,call);bridge.publish(event)
        raw=json.dumps(hook).encode();result=safe_transform(raw,tmp_path/'archive',bridge_root=bridge.root)
        packet=json.loads(result['stopReason'])
        assert packet['original_result_metadata']['exit_code']==code
        from pathlib import Path
        assert Path(packet['archive_path']).read_bytes()==raw

def test_missing_or_cross_turn_metadata_keeps_native_output(tmp_path):
    bridge=Bridge(tmp_path/'bridge');event,hook=pair();bridge.publish(event)
    for field in ('session_id','turn_id','tool_use_id'):
        changed={**hook,field:'other'}
        assert safe_transform(json.dumps(changed).encode(),tmp_path/'archive',bridge_root=bridge.root)=={}

def test_changed_or_truncated_output_keeps_native_output(tmp_path):
    bridge=Bridge(tmp_path/'bridge');event,hook=pair();bridge.publish(event);hook['tool_response']=hook['tool_response'][:-5]
    assert safe_transform(json.dumps(hook).encode(),tmp_path/'archive',bridge_root=bridge.root)=={}

def test_conflicting_republication_cannot_change_status(tmp_path):
    bridge=Bridge(tmp_path);event,hook=pair();key=bridge.publish(event);bridge.publish(event)
    changed=copy.deepcopy(event);changed['params']['item']['exitCode']=0
    with pytest.raises(ValueError):bridge.publish(changed)
    assert bridge.lookup(hook)['exit_code']==7

def test_corruption_falls_back_without_suppressing(tmp_path):
    bridge=Bridge(tmp_path/'bridge');event,hook=pair();key=bridge.publish(event)
    p=bridge.root/(key+'.json');value=json.loads(p.read_bytes());value['payload']['exit_code']=0;p.write_text(json.dumps(value))
    assert safe_transform(json.dumps(hook).encode(),tmp_path/'archive',bridge_root=bridge.root)=={}

def test_running_or_unknown_exit_is_not_published(tmp_path):
    bridge=Bridge(tmp_path);event,hook=pair();event['params']['item']['exitCode']=None
    assert bridge.publish(event) is None
    assert not list(tmp_path.iterdir())
