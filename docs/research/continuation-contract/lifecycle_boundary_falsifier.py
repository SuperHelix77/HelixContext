"""Offline falsification of the frozen W50 dispatcher; never invokes a model.

Probes existing code without changing it or its frozen receipts. Passing an ACK
fixture is not general authority or durable-state qualification.
"""
import copy
import json
import tempfile
from pathlib import Path
from native_luna_ack_pair import REPO, dispatch, enc, sha


def run():
    fixture = REPO / 'benchmarks/frozen-high/protocol/long-horizon-v1.json'
    events = json.loads(fixture.read_text())['events']
    findings = []
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        path = root / 'normal.jsonl'
        for event in events[:49]:
            assert dispatch(event, path) == 'ACK ' + event['event_id']
        assert [json.loads(x)['event'] for x in path.read_bytes().splitlines()] == events[:49]
        assert dispatch(events[49], path) is None
        findings.append({'case': '49_exact_events_and_final_semantic_route', 'result': 'PASS'})

        for i, request in enumerate(('Apply rollback now', 'Cancel this workflow',
                                      events[0]['request'] + ' Also deploy now.')):
            target = root / f'changed-{i}.jsonl'
            assert dispatch({**events[0], 'request': request}, target) is None
            assert not target.exists()
        findings.append({'case': 'changed_request_no_mechanical_effect', 'result': 'PASS'})

        before = path.read_bytes()
        try:
            dispatch(events[0], path)
        except ValueError:
            pass
        else:
            raise AssertionError('duplicate accepted')
        assert path.read_bytes() == before
        findings.append({'case': 'duplicate_delivery', 'result': 'SAFE_STOP_NOT_IDEMPOTENT_RESUME'})

        # A syntactically valid changed prior event is currently not bound to an
        # independently retained state root. A subsequent ACK must not be taken
        # as evidence that the previous archive is still authentic.
        target = root / 'tampered.jsonl'
        altered = copy.deepcopy(events[0])
        altered['data']['minimum_distinct_approvers'] = 0
        target.write_bytes(enc({'event': altered, 'answer': 'ACK E01', 'owner': 'caller'}))
        outcome = dispatch(events[1], target)
        assert outcome == 'ACK E02'
        findings.append({'case': 'prior_valid_json_tampering',
                         'result': 'FAIL_CLOSED_STATE_BINDING_ABSENT',
                         'observed': 'Next ACK accepted after prior policy bytes changed'})

        target = root / 'partial.jsonl'
        target.write_bytes(enc({'event': events[0], 'answer': 'ACK E01', 'owner': 'caller'}) + b'{"event":')
        before = target.read_bytes()
        try:
            dispatch(events[1], target)
        except json.JSONDecodeError:
            pass
        else:
            raise AssertionError('partial record unexpectedly accepted')
        assert target.read_bytes() == before
        findings.append({'case': 'interrupted_append_reopen',
                         'result': 'SAFE_STOP_NO_AUTOMATIC_RECOVERY'})

    return {'classification': 'Offline existing-code falsifier; no native calls',
            'source_sha256': sha(Path(__file__).with_name('native_luna_ack_pair.py')),
            'fixture_sha256': sha(fixture), 'cases': findings,
            'native_calls': 0, 'production_qualification': False,
            'scope': 'No changed original benchmark data; no concurrency, physical crash or semantic parity proof.'}


if __name__ == '__main__':
    print(json.dumps(run(), indent=2))
