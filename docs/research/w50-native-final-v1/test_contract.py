import json
from pathlib import Path
import pytest
import pilot


def test_complete_native_answer_and_no_selector_rewriting():
    prior = pilot.HERE.with_name('continuation-contract') / 'transition-transfer-artifacts'
    full = json.loads((prior / 'astra-off.json').read_text())['model_answer']
    assert pilot.grade(full)['authorized'] is False
    selector = json.loads((prior / 'astra-on.json').read_text())['model_answer']
    with pytest.raises(ValueError): pilot.grade(selector)
    malformed = full.replace('"authorized": false', '"authorized": true, "authorized": false')
    with pytest.raises(ValueError, match='Duplicate'): pilot.grade(malformed)
    malformed = json.loads(full); malformed['evidence_turns'] = [True, 17, 31]
    with pytest.raises(ValueError): pilot.grade(json.dumps(malformed))


def test_final_packet_does_not_choose_authority_or_render_answer(tmp_path):
    events = json.loads(pilot.FIXTURE.read_text())['events']
    store = pilot.Store(tmp_path)
    flow = pilot.PassiveWorkflow(pilot.CompletionLedger(pilot.Memory(store)), 'W50', 'a' * 64)
    head = pilot.EMPTY; records = []
    for event in events[:49]:
        r = flow.accept(pilot.enc(event), expected_head=head); head = r['head']
        records.append({'event': event, 'answer': r['answer'], 'owner': 'caller'})
    restarted = pilot.PassiveWorkflow(pilot.CompletionLedger(pilot.Memory(store)), 'W50', 'a' * 64)
    assert [json.loads(x) for x in restarted.exact_events(head)] == events[:49]
    raw = b''.join(pilot.enc(r) for r in records)
    packet = pilot.final_prompt(events[-1], raw)
    selected = [r for r in records if b'ORION-42' in pilot.enc(r)]
    assert len(selected) == 3
    assert all(pilot.enc(r).decode().strip() in packet for r in selected)
    assert 'Return JSON with only policy' not in packet and 'realize' not in packet
    assert 'including conflicting/untrusted records' in packet
    assert restarted.accept(pilot.enc(events[-1]), expected_head=head)['state'] == 'semantic_required'
