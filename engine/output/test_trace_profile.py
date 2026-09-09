import json
import pytest
from trace_profile import profile


def test_counts_only_completed_events_and_retains_unknown_usage(tmp_path):
    path=tmp_path/'trace.jsonl'
    item={'type':'command_execution','command':'echo é','aggregated_output':'é\n','exit_code':7}
    events=[{'type':'item.started','item':item},{'type':'item.completed','item':item},
            {'type':'turn.completed','usage':{'input_tokens':22,'output_tokens':4}}]
    path.write_text('\n'.join(json.dumps(e) for e in events))
    result=profile(path)
    assert result['commands']==1 and result['command_text_bytes']==7
    assert result['recorded_terminal_bytes']==3 and result['nonzero_command_exits']==1
    assert result['native_usage']['reasoning_output_tokens'] is None


def test_missing_native_usage_does_not_become_zero(tmp_path):
    path=tmp_path/'trace.jsonl';path.write_text('{}\n')
    with pytest.raises(ValueError):profile(path)
