"""Explicit harness amendment: continue unexecuted arms, never retry a model."""
import json
import sys
from pathlib import Path
import native_kernel_pair as driver


def run(root):
    root = Path(root)
    original = root/'kernel-results.json'
    result = root/'amended-results.json'
    if result.exists():
        raise ValueError('No retry')
    old = json.loads(original.read_text())
    m = json.loads((root/'kernel-manifest.json').read_text())
    assert old['state'] == 'STOPPED_PENDING_AUDIT' and len(old['rows']) == 1
    first = old['rows'][0]
    assert [first['variant'], first['arm']] == m['order'][0] == ['defect', 'kernel']
    a = json.loads(first['answer'])
    assert a['decision'] == 'REJECT' and isinstance(a['assessment'], dict)
    assert a['assessment']['finding'] and a['assessment']['evidence']
    assert isinstance(a['unresolved'], list)
    driver.bindings(root, m, 'defect')
    assert not any((root/f'{v}-{arm}-run').exists() for v, arm in m['order'][1:])
    amendment = {'classification': 'Post-outcome harness schema amendment, no repeated inference',
        'reason': 'Prompt did not require assessment to be a string; substantive JSON object is admissible.',
        'original_result_sha256': driver.sha(original),
        'driver_sha256': driver.sha(Path(__file__)),
        'original_manifest_sha256': driver.sha(root/'kernel-manifest.json'),
        'remaining_order': m['order'][1:], 'retries': 0}
    driver.save(root/'amendment.json', amendment)
    r = {'state': 'RUNNING', 'rows': old['rows'], 'amendment': amendment}
    driver.save(result, r)
    try:
        for variant, arm in m['order'][1:]:
            driver.bindings(root, m, variant)
            cwd = root/variant/'on'
            driver.save(root/f'{variant}-{arm}-inventory.json', sorted(str(p.relative_to(cwd)) for p in cwd.rglob('*') if p.is_file()))
            driver.research_session.RPC = driver.rpc_with_base(Path(m['kernel']) if arm == 'kernel' else None)
            try:
                with driver.research_session.Session(m['model'], cwd, root/f'{variant}-{arm}-run',
                        cwd/'.agents/skills/helixcontext/SKILL.md') as s:
                    answer, turn = s.turn((root/variant/'prompt.txt').read_text())
                    row = {'variant': variant, 'arm': arm, 'answer': answer, 'usage': s.total, 'turn': turn}
            finally:
                driver.research_session.RPC = driver.OriginalRPC
            r['rows'].append(row); driver.save(result, r)
            text = answer.strip()
            if text.startswith('```'):
                text = '\n'.join(text.splitlines()[1:-1])
            a = json.loads(text)
            assert a['decision'] == ('REJECT' if variant == 'defect' else 'ACCEPT'), a
            assert isinstance(a['assessment'], (str, dict)) and a['assessment'], a
            assert isinstance(a['unresolved'], list), a
            driver.bindings(root, m, variant)
        r['state'] = 'AWAITING_INDEPENDENT_AUDIT'; driver.save(result, r)
    except BaseException as exc:
        r.update(state='STOPPED_PENDING_AUDIT', error=str(exc)); driver.save(result, r)
        raise


if __name__ == '__main__':
    run(sys.argv[1])
