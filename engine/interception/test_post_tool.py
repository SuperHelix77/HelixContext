import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from post_tool import transform,safe_transform


def event(**changes):
    payload={'hook_event_name':'PostToolUse','tool_name':'Bash','tool_input':{'command':'synthetic-command'},'tool_response':{'output':'info noise\n'*3000+'ERROR exact=000.050\n','exit_code':7,'timed_out':False}}
    payload.update(changes)
    return json.dumps(payload,ensure_ascii=False,indent=3).encode()


def test_archive_precedes_projection_and_exit_is_preserved(tmp_path):
    raw=event();result=transform(raw,tmp_path);packet=json.loads(result['stopReason'])
    assert result['continue'] is False and 'decision' not in result and 'hookSpecificOutput' not in result
    assert Path(packet['archive_path']).read_bytes()==raw
    assert packet['original_result_metadata']['exit_code']==7
    assert packet['projection']['diagnostics'][0]['text']=='ERROR exact=000.050'
    assert len(result['stopReason'].encode())<3500


def test_unknown_response_and_small_results_pass_through(tmp_path):
    for response in ('unknown format',{'output':'x'*20000},{'output':'small','exit_code':0},{'output':'x'*20000,'exit_code':False}):
        assert transform(event(tool_response=response),tmp_path)=={}
    assert not list(tmp_path.iterdir())


def test_explicit_retrieval_is_not_recursively_compressed(tmp_path):
    assert transform(event(tool_input={'command':'HELIX_FULL_OUTPUT=1 cat archive'}),tmp_path)=={}


def test_failed_archive_does_not_suppress_native_result(tmp_path):
    invalid=tmp_path/'file';invalid.write_text('not a directory')
    assert safe_transform(event(),invalid)=={}
    assert safe_transform(b'not JSON',tmp_path)=={}


def test_large_diagnostic_falls_back_to_exact_archive(tmp_path):
    raw=event(tool_response={'output':'ERROR '+('large '*6000),'exit_code':1})
    result=transform(raw,tmp_path);packet=json.loads(result['stopReason'])
    assert packet['expansion_required'] and packet['projection']['omitted']
    assert Path(packet['archive_path']).read_bytes()==raw


def test_other_tool_types_are_unmodified(tmp_path):
    assert transform(event(tool_name='apply_patch'),tmp_path)=={}
    assert transform(event(hook_event_name='PreToolUse'),tmp_path)=={}
