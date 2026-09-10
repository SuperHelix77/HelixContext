"""Receipt-derived descriptive statistics. No model ranking or release inference."""
from statistics import median

COUNTERS = ('input_tokens', 'output_tokens', 'uncached_input_tokens')


def counts(run):
    u = run.get('usage') or {}
    if run.get('usage_source') != 'Native app-server cumulative update': return None
    if any(type(u.get(k)) is not int or u[k] < 0 for k in ('input_tokens', 'output_tokens', 'cached_input_tokens')): return None
    if u['cached_input_tokens'] > u['input_tokens']: return None
    return {**{k: u[k] for k in ('input_tokens', 'output_tokens')},
            'uncached_input_tokens': u['input_tokens'] - u['cached_input_tokens']}


def unique_usage(runs):
    """Count a registered native thread once, including measured failed attempts.

    Distinct cumulative snapshots of one thread must be ordered componentwise.
    Conflicting counters remain unknown; never add repeated-control aliases.
    """
    groups = {}
    for run in runs:
        if counts(run) is None or not run.get('native_thread_id'): continue
        key = (run['model'], run['native_thread_id'])
        groups.setdefault(key, []).append(run)
    totals = {k: 0 for k in COUNTERS}
    accepted = 0; aliases = 0; conflicts = 0
    for items in groups.values():
        values = [counts(r) for r in items]
        greatest = next((v for v in values if all(all(v[k] >= w[k] for k in COUNTERS) for w in values)), None)
        if greatest is None: conflicts += 1; continue
        accepted += 1; aliases += len(items) - 1
        for k in COUNTERS: totals[k] += greatest[k]
    return {'unique_threads': accepted, 'aliases_removed': aliases, 'conflicting_threads': conflicts,
            'usage': totals if accepted else None,
            'scope': 'Registered, verified native threads counted once; parent chat and absent receipts excluded'}


def summarize(specs, pairs, runs):
    lookup = {r['id']: r for r in runs}; pair_map = {p['id']: p for p in pairs}; output = []
    for spec in specs:
        samples = []; excluded = []; used = set()
        for identity in spec['pairs']:
            pair = pair_map.get(identity, {})
            a = lookup.get(pair.get('off'), {}); b = lookup.get(pair.get('on'), {})
            av = counts(a); bv = counts(b)
            if av is None or bv is None or any(r.get('state') not in ('CLOSED', 'COMPLETED') for r in (a, b)):
                excluded.append({'id': identity, 'reason': 'Missing completed native counters'}); continue
            if any(r.get('model') != spec['model'] or r.get('effort') != spec['effort'] for r in (a, b)):
                excluded.append({'id': identity, 'reason': 'Model or effort not matched'}); continue
            identities = {(r.get('model'), r.get('native_thread_id')) for r in (a, b)}
            if None in (a.get('native_thread_id'), b.get('native_thread_id')) or len(identities) != 2 or used & identities:
                excluded.append({'id': identity, 'reason': 'Repeated or unidentified native thread within cohort'}); continue
            used |= identities
            savings = {k: (1 - bv[k] / av[k]) * 100 if av[k] > 0 else None for k in COUNTERS}
            samples.append({'id': identity, 'control': av, 'candidate': bv, 'savings_percent': savings,
                            'finite_checks': pair.get('artifact_check')})
        medians = {}; pooled = {}
        for k in COUNTERS:
            values = [s['savings_percent'][k] for s in samples if s['savings_percent'][k] is not None]
            medians[k] = median(values) if len(values) == len(samples) and values else None
            control = sum(s['control'][k] for s in samples)
            pooled[k] = (1 - sum(s['candidate'][k] for s in samples) / control) * 100 if control else None
        complete = bool(spec['pairs']) and len(samples) == len(spec['pairs'])
        target = spec.get('release_target_percent')
        requested = type(target) in (int, float) and 0 <= target <= 100
        economic = ('PENDING_COHORT' if not complete else
                    'UNKNOWN_COUNTER' if any(medians[k] is None for k in ('input_tokens','output_tokens')) else
                    'PASS' if min(medians['input_tokens'],medians['output_tokens']) >= target else 'FAIL') if requested else 'NOT_REQUESTED'
        output.append({**spec, 'n_pairs': len(samples), 'registered_pairs': len(spec['pairs']),
                       'median_savings_percent': medians, 'ratio_of_totals_savings_percent': pooled,
                       'cohort_complete': complete,
                       'release_median_savings_percent': medians if complete else {k: None for k in COUNTERS},
                       'economic_gate': economic,
                       'finite_check_passes': sum(s['finite_checks'] is True for s in samples),
                       'finite_check_failures': sum(s['finite_checks'] is False for s in samples),
                       'finite_check_unknown': sum(s['finite_checks'] is None for s in samples),
                       'samples': samples, 'excluded': excluded,
                       'release_qualification': 'NOT_ESTABLISHED', 'uncertainty': 'Descriptive cohort; no confidence interval or universal parity claim'})
    return output


def tariff_medians(cohort, pairs, costs):
    """Current short/long tariff scenarios, never an included-plan quota ratio."""
    pair_map={p['id']:p for p in pairs}
    result={}
    for tier in ('short','long'):
        values=[]
        for sample in cohort['samples']:
            pair=pair_map[sample['id']]
            a=costs.get(pair['off']);b=costs.get(pair['on'])
            if a and b and a.get(tier,0)>0 and b.get(tier) is not None:
                values.append((1-b[tier]/a[tier])*100)
        result[tier]=median(values) if values and len(values)==cohort['n_pairs'] else None
    return result
