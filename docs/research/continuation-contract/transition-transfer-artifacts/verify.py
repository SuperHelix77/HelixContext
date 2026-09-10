"""Offline public derivative verification; no credentials, network or inference."""
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path[:0] = [str(HERE.parent), str(REPO / 'engine/prototype')]
from native_luna_ack_pair import grade
from policy_realization import realize


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    manifest = json.loads((HERE / 'manifest.json').read_text())
    for name, digest in manifest['files'].items():
        assert sha(HERE / name) == digest, name
    for name, digest in manifest['source_bindings'].items():
        assert sha(REPO / name) == digest, name
    report_path = HERE.parent / 'TRANSITION_TRANSFER_V1_RESULT.json'
    assert sha(report_path) == manifest['public_audit_sha256']
    report = json.loads(report_path.read_text())
    history = (HERE / 'history.jsonl').read_bytes()
    fixture = json.loads((HERE / 'fixture.json').read_text())
    assert [json.loads(line)['event'] for line in history.splitlines()] == fixture['events'][:49]
    names = {'input_tokens': 'inputTokens', 'output_tokens': 'outputTokens',
             'cached_input_tokens': 'cachedInputTokens', 'reasoning_output_tokens': 'reasoningOutputTokens',
             'cache_write_input_tokens': 'cacheWriteInputTokens'}
    identities = set()
    totals = {k: 0 for k in names}
    for entry in manifest['rows']:
        data = json.loads((HERE / entry['path']).read_text())
        row = next(r for r in report['rows'] if (r['model_key'], r['arm']) == (entry['model_key'], entry['arm']))
        assert sha(HERE / entry['path']) == entry['sha256']
        assert data['native_sha256'] == row['native_sha256'] not in identities
        identities.add(row['native_sha256'])
        assert data['raw_sha256'] == row['raw_sha256']
        assert data['model'] == row['model'] and data['effort'] == row['effort'] == 'high'
        assert len(data['updates']) == row['segments'] == row['turns'] == (50 if row['arm'] == 'off' else 1)
        accumulated = {k: 0 for k in names}
        for update in data['updates']:
            for key, native in names.items():
                n = update['last'][native]
                assert type(n) is int and n >= 0
                accumulated[key] += n
                assert accumulated[key] == update['total'][native]
            last = update['last']
            assert last['cachedInputTokens'] + last['cacheWriteInputTokens'] <= last['inputTokens']
            assert last['reasoningOutputTokens'] <= last['outputTokens']
        assert accumulated == row['usage']
        for key in totals:
            totals[key] += accumulated[key]
        assert data['acks'] == ['ACK ' + e['event_id'] for e in fixture['events'][:49]]
        assert row['history_sha256'] == hashlib.sha256(history).hexdigest()
        if row['arm'] == 'on':
            selected = json.loads(data['model_answer'])
            assert selected == data['selection']
            actual = realize(selected, history, row['history_sha256'],
                             {'subject': 'ORION-42', 'distinct_approvers': 1, 'approver_group': 'violet'})
            assert actual == data['realized']
            assert actual['answer'] == json.loads(data['answer'])
        else:
            assert data['model_answer'] == data['answer']
        assert data['answer'] == row['answer'] and row['checks'] == 'PASS'
        grade(data['answer'])
    assert totals == report['native_usage_all_attempts']
    for pair in report['pairs']:
        off = next(r['usage'] for r in report['rows'] if r['model_key'] == pair['model_key'] and r['arm'] == 'off')
        on = next(r['usage'] for r in report['rows'] if r['model_key'] == pair['model_key'] and r['arm'] == 'on')
        for key in ('input_tokens', 'output_tokens', 'uncached_input_tokens'):
            a = off[key] if key in off else off['input_tokens'] - off['cached_input_tokens']
            b = on[key] if key in on else on['input_tokens'] - on['cached_input_tokens']
            assert abs((1 - b / a) * 100 - pair['savings_percent'][key]) < 1e-10
    print('PASS: four usage derivatives, 102 segments, 196 ACKs, exact history, caller realization, original finite grader and savings arithmetic; private raw-stream provenance requires the local audit.')


if __name__ == '__main__':
    main()
