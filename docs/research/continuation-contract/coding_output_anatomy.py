"""Reconcile the nine coding pairs without inference or counterfactual billing."""
import ast
import hashlib
import json
from pathlib import Path
import statistics

HERE = Path(__file__).resolve().parent
SOURCES = {
    'luna': ('LUNA_VARIED_CODING_CONTINUATION_RESULT.json', 'varied-coding-artifacts'),
    'sol': ('SOL_VARIED_CODING_V1_RESULT.json', 'sol-coding-transfer-artifacts'),
    'astra': ('ASTRA_VARIED_CODING_V1_RESULT.json', 'astra-coding-transfer-artifacts'),
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    rows, cohorts, sources, seen = [], [], {}, set()
    for model, (filename, artifact_dir) in SOURCES.items():
        report = json.loads((HERE / filename).read_text())
        manifest = json.loads((HERE / artifact_dir / 'manifest.json').read_text())
        assert manifest['paired_audit_sha256'] == sha(HERE / filename)
        sources[filename] = sha(HERE / filename)
        paired = []
        for case in ('intervals', 'dependencies', 'transactions'):
            arms = {a: next(r for r in report['rows'] if (r['case'], r['arm']) == (case, a))
                    for a in ('off', 'on')}
            for arm, row in arms.items():
                assert row['finite_checks'] == row['checks']['finite_checks'] == 'PASS'
                assert row['native_sha256'] not in seen, 'Duplicated native denominator'
                seen.add(row['native_sha256'])
                source = HERE / artifact_dir / case / arm / 'solution.py'
                assert sha(source) == row['source_sha256']
                ast.parse(source.read_text())
                u = row['usage']
                assert 0 <= u['cached_input_tokens'] <= u['input_tokens']
                assert 0 <= u['reasoning_output_tokens'] <= u['output_tokens']
            control, candidate = arms['off'], arms['on']
            cu, hu = control['usage'], candidate['usage']
            assert candidate['segments'] == 1 and candidate['raw_tool_calls'] == 0
            savings = {key: 100 * (1 - hu[key] / cu[key])
                       for key in ('input_tokens', 'output_tokens')}
            uncached = {arm: r['usage']['input_tokens'] - r['usage']['cached_input_tokens']
                        for arm, r in arms.items()}
            savings['uncached_input_tokens'] = 100 * (1 - uncached['on'] / uncached['off'])
            expected = next(p for p in report['pairs'] if p['case'] == case)
            assert all(abs(savings[k] - expected['savings_percent'][k]) < 1e-9 for k in savings)
            budget = .25 * cu['output_tokens']
            non_reasoning = hu['output_tokens'] - hu['reasoning_output_tokens']
            remaining = budget - hu['reasoning_output_tokens']
            source = HERE / artifact_dir / case / 'on' / 'solution.py'
            row = {
                'model': model, 'effort': 'high', 'case': case,
                'control_usage': cu, 'candidate_usage': hu,
                'control_native_sha256': control['native_sha256'],
                'candidate_native_sha256': candidate['native_sha256'],
                'savings_percent': savings, 'finite_checks': 'PASS',
                'candidate_segments': candidate['segments'],
                'candidate_raw_tool_calls': candidate['raw_tool_calls'],
                'candidate_source_bytes': source.stat().st_size,
                'candidate_ast_nodes': sum(1 for _ in ast.walk(ast.parse(source.read_text()))),
                'candidate_non_reasoning_output_tokens': non_reasoning,
                'target75_output_budget': budget,
                'non_reasoning_allowance_if_reasoning_fixed': remaining,
                'formatting_only_cannot_reach75_if_reasoning_fixed': remaining < 0,
                'ceiling_if_all_non_reasoning_output_deleted_percent':
                    100 * (1 - hu['reasoning_output_tokens'] / cu['output_tokens']),
                'meets_75_75': expected['meets_75_75'],
                'meets_80_80': expected['meets_80_80'],
            }
            rows.append(row)
            paired.append(row)
        median = {k: statistics.median(r['savings_percent'][k] for r in paired)
                  for k in paired[0]['savings_percent']}
        assert all(abs(median[k] - report['median_savings_percent'][k]) < 1e-9 for k in median)
        cohorts.append({'model': model, 'N': 3, 'median_savings_percent': median,
                        'pairs_meeting75': sum(r['meets_75_75'] for r in paired),
                        'pairs_meeting80': sum(r['meets_80_80'] for r in paired)})
    artifact = {
        'schema': 'helix.coding-output-anatomy.v1', 'source_audits': sources,
        'cohorts': cohorts, 'rows': rows, 'unique_native_streams': len(seen),
        'new_model_calls': 0, 'general_capability_parity_established': False,
        'interpretation': 'Observed counters and conditional arithmetic only. Reasoning is a subset of output; its contents and causes are unknown.',
        'limits': ['Same exposed contracts, not independent task populations',
                   'Luna config-audit amendment and prior failed attempts remain in its original reports',
                   'No cross-model economic ranking or pooling with W50/retrieval/assembly',
                   'Fixed-reasoning ceilings are not irreducible limits or measured interventions',
                   'Source bytes and AST nodes are not native token allocations'],
    }
    out = HERE / 'CODING_OUTPUT_ANATOMY_20260910.json'
    out.write_text(json.dumps(artifact, indent=2) + '\n')
    print(json.dumps({'cohorts': cohorts, 'streams': len(seen),
                      'audit_sha256': sha(out), 'new_model_calls': 0}))


if __name__ == '__main__':
    main()
