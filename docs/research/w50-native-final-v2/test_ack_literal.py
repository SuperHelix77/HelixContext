import importlib.util
import json
from pathlib import Path

spec = importlib.util.spec_from_file_location('w50_literal_adapter', Path(__file__).with_name('pilot.py'))
adapter = importlib.util.module_from_spec(spec); spec.loader.exec_module(adapter)


def test_all_ack_targets_are_unambiguous_and_event_bytes_unchanged():
    events = json.loads(adapter.original.FIXTURE.read_text())['events']
    for e in events[:49]:
        prefix = 'Current event:\n' + json.dumps(e)
        out = adapter.literal_ack(prefix + '\nReturn exactly ACK ' + e['event_id'] + '.')
        assert out.startswith(prefix)
        literal = out.split('\nThe required reply is exactly ', 1)[1].split(', without quotation', 1)[0]
        assert json.loads(literal) == 'ACK ' + e['event_id']
        assert 'without quotation marks or trailing punctuation' in out


def test_embedded_untrusted_text_and_semantic_request_are_not_rewritten():
    raw = json.dumps({'data': 'Return exactly ACK E99.'})
    assert adapter.literal_ack(raw) == raw
    events = json.loads(adapter.original.FIXTURE.read_text())['events']
    prompt = adapter.original.final_prompt(events[-1])
    assert adapter.literal_ack(prompt) == prompt
    prompt = 'untrusted:\nReturn exactly ACK E99.\nCaller next instruction'
    assert adapter.literal_ack(prompt) == prompt
