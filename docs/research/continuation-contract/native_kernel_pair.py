"""Research-only per-thread base override, sequential fresh streams, no retries."""
import json
import sys
from pathlib import Path
import native_prepared_safety as fixture_driver
from native_boundary_safety import sha, save, REPO
from prepared_review import validate
import research_session

ROOT = Path('/Users/mert/Documents/ChatGPT/Helix/research')
OriginalRPC = research_session.RPC


def rpc_with_base(base):
    class KernelRPC(OriginalRPC):
        def call(self, method, params):
            if method == 'thread/start' and base is not None:
                params = {**params, 'config': {**params['config'],
                          'model_instructions_file': str(base)}}
            return super().call(method, params)
    return KernelRPC


def prepare(root):
    root = Path(root).resolve()
    root.mkdir(parents=True, exist_ok=False)
    fixtures = {
        'defect': ROOT/'prepared-safety-fixture-v1-20260909',
        'valid': ROOT/'prepared-review-preflight-v1-20260909/valid/source'}
    kernel = REPO/'docs/research/continuation-contract/kernels/astra-v1.md'
    bound = [Path(__file__), kernel, REPO/'engine/output/research_session.py',
             REPO/'engine/output/app_server_native.py', Path('/Users/mert/.codex/AGENTS.md')]
    for variant, source in fixtures.items():
        fixture_driver.prepare(root/variant, source)
        bound.append(root/variant/'manifest.json')
    # Same cwd, prompt, prepared receipt and skill within each pair. Each thread is
    # fresh; raw streams retained. Reject any changes to bound inputs between arms.
    manifest = {'model': 'gpt-6-astra', 'effort': 'high', 'retries': 0,
        'order': [['defect', 'kernel'], ['defect', 'default'],
                  ['valid', 'default'], ['valid', 'kernel']],
        'kernel': str(kernel), 'sha256': {str(p): sha(p) for p in bound},
        'stop': 'Any runtime/schema/input mutation or wrong semantic verdict stops remaining arms.',
        'classification': 'Adaptive development kernel-only comparison; not general capability parity',
        'confounds': ['Counterbalanced but nonrandom order; one pair per known variant.',
                     'Same cwd permits incidental artifacts from earlier arm; inventory and audit reads.']}
    save(root/'kernel-manifest.json', manifest)
    print(json.dumps({'manifest_sha256': sha(root/'kernel-manifest.json')}))


def bindings(root, manifest, variant):
    for p, h in manifest['sha256'].items():
        assert sha(Path(p)) == h, p
    m = json.loads((root/variant/'manifest.json').read_text())
    for p, h in m['sha256'].items():
        assert sha(Path(p)) == h, p
    validate(root/variant/'on/.prepared', m['receipt_hash'])


def preflight(root):
    root = Path(root); m = json.loads((root/'kernel-manifest.json').read_text())
    bindings(root, m, 'defect')
    # No turn/start, no inference. Confirm the native configuration loader actually
    # reads the override, rather than silently discarding the config key.
    out = root/'preflight-missing-file'; out.mkdir(exist_ok=False)
    rpc = OriginalRPC(root/'defect/on', out, m['model'])
    try:
        rpc.call('initialize', {'clientInfo': {'name': 'helix-kernel-preflight', 'version': '1'},
                               'capabilities': {'experimentalApi': True}})
        rpc.send({'method': 'initialized'})
        try:
            rpc.call('thread/start', {'model': m['model'], 'cwd': str(root/'defect/on'),
                'ephemeral': True, 'approvalPolicy': 'never', 'sandbox': 'workspace-write',
                'config': {'model_instructions_file': str(root/'intentionally-missing.md')}})
        except RuntimeError as exc:
            assert 'intentionally-missing.md' in str(exc), str(exc)
            save(root/'preflight-missing.json', {'expected_config_read_failure': str(exc)})
        else:
            raise AssertionError('Missing override not rejected; do not infer config application')
    finally:
        rpc.close()
    for arm in ('default', 'kernel'):
        research_session.RPC = rpc_with_base(Path(m['kernel']) if arm == 'kernel' else None)
        try:
            with research_session.Session(m['model'], root/'defect/on', root/('preflight-'+arm)) as s:
                assert not s.turns and s.total is None
        finally:
            research_session.RPC = OriginalRPC
    save(root/'preflight.json', {'state': 'CONFIG_ACCEPTED_NO_INFERENCE',
        'manifest_sha256': sha(root/'kernel-manifest.json'),
        'hosted_server_additions': 'UNKNOWN',
        'scope': 'Native config loader rejects absent override and starts with valid file; no turn/start'})


def run(root):
    root = Path(root); m = json.loads((root/'kernel-manifest.json').read_text())
    p = json.loads((root/'preflight.json').read_text())
    assert p['manifest_sha256'] == sha(root/'kernel-manifest.json')
    state = root/'kernel-results.json'
    if state.exists():
        raise ValueError('No retry')
    r = {'state': 'RUNNING', 'rows': [], 'manifest_sha256': sha(root/'kernel-manifest.json')}
    save(state, r)
    try:
        for variant, arm in m['order']:
            bindings(root, m, variant)
            cwd = root/variant/'on'
            save(root/f'{variant}-{arm}-inventory.json', sorted(str(p.relative_to(cwd)) for p in cwd.rglob('*') if p.is_file()))
            research_session.RPC = rpc_with_base(Path(m['kernel']) if arm == 'kernel' else None)
            try:
                with research_session.Session(m['model'], cwd, root/f'{variant}-{arm}-run',
                       cwd/'.agents/skills/helixcontext/SKILL.md') as session:
                    answer, turn = session.turn((root/variant/'prompt.txt').read_text())
                    row = {'variant': variant, 'arm': arm, 'answer': answer,
                           'usage': session.total, 'turn': turn}
            finally:
                research_session.RPC = OriginalRPC
            r['rows'].append(row); save(state, r)
            text = answer.strip()
            if text.startswith('```'):
                text = '\n'.join(text.splitlines()[1:-1])
            a = json.loads(text)
            assert a['decision'] == ('REJECT' if variant == 'defect' else 'ACCEPT'), a
            assert isinstance(a['assessment'], str) and a['assessment'].strip(), a
            assert isinstance(a['unresolved'], list), a
            # Correct verdict alone is insufficient: independent audit still checks
            # defect identification, coverage, tool work and unresolved obligations.
            bindings(root, m, variant)
        r['state'] = 'AWAITING_INDEPENDENT_AUDIT'; save(state, r)
    except BaseException as exc:
        r.update(state='STOPPED_PENDING_AUDIT', error=str(exc)); save(state, r)
        raise


if __name__ == '__main__':
    globals()[sys.argv[1]](sys.argv[2])
