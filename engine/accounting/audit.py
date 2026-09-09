"""Rate-independent paired native cost audit. Run with Python 3; no dependencies."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCES = ['engine/native-pilots/pilot-v2/results.json', 'engine/render-pilot/results.json']


def categories(usage):
    total, cached = usage['input_tokens'], usage['cached_input_tokens']
    assert isinstance(total, int) and isinstance(cached, int) and 0 <= cached <= total
    assert usage.get('cache_write_input_tokens', 0) == 0, 'Extend accounting for cache-write pricing'
    return dict(uncached_input=total-cached, cached_input=cached, output=usage['output_tokens'])


def audit(root=ROOT):
    comparisons = []
    sources = []
    for name in SOURCES:
        raw = (root/name).read_bytes()
        data = json.loads(raw)
        sources.append(dict(path=name, sha256=hashlib.sha256(raw).hexdigest()))
        for model in sorted({r['model'] for r in data['rows']}):
            pair = [r for r in data['rows'] if r['model'] == model]
            assert len(pair) == 2 and {r['arm'] for r in pair} == {'off', 'on'}
            arms = {r['arm']:r for r in pair}
            off, on = (categories(arms[a]['usage']) for a in ('off','on'))
            delta = {k:off[k]-on[k] for k in off}
            # For nonnegative rates, achievable model-only savings are a weighted
            # average of category savings; the largest is an optimistic bound.
            assert all(off[k] > 0 for k in off), 'Handle zero baseline separately'
            fractions = {k:1-on[k]/off[k] for k in off}
            comparisons.append(dict(
                source=name, model=model, off=off, on=on,
                model_cost_benefit_coefficients=delta,
                category_savings=fractions,
                optimistic_model_only_saving_ceiling=max(fractions.values()),
                eighty_percent_model_cost_possible_at_any_nonnegative_rates=max(fractions.values()) >= .8,
                on_dominated_for_all_positive_token_rates=all(v <= 0 for v in delta.values()) and any(v < 0 for v in delta.values()),
                elapsed_seconds_delta_on_minus_off=arms['on']['elapsed_seconds']-arms['off']['elapsed_seconds'],
                gross_input_saving=1-arms['on']['usage']['input_tokens']/arms['off']['usage']['input_tokens'],
                output_saving=fractions['output'],
            ))
    return dict(schema='helix.rate_independent_cost_audit.v1', sources=sources,
        equation='model benefit = delta_uncached*p_uncached + delta_cached*p_cached + delta_output*p_output; total benefit subtracts incremental non-model overhead',
        rate_scope='Nonnegative per-token rates; same model and rates across each pair; no price assumptions. Cached input and reasoning output are subsets, not additive usage.',
        limits=['Two diagnostic tasks, one paired episode per model per task; no confidence intervals or general capability parity.',
                'The model-only ceiling excludes non-model costs and is not a billing estimate or full-system bound.',
                'Storage, preprocessing CPU, parent coordination, recovery outside native receipts, and development amortization remain incomplete; missing is not zero.',
                'No additional model calls incurred by this arithmetic audit.'], comparisons=comparisons)

if __name__ == '__main__':
    target = Path(__file__).with_name('RATE_INDEPENDENT_AUDIT.json')
    target.write_text(json.dumps(audit(), indent=2)+'\n')
    print(target)
