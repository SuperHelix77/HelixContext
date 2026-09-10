"""Single preregistered hostile review. Original base, full model final, no retry."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec); spec.loader.exec_module(value)
    return value


old = module('qualified_prior_review', HERE.with_name('astra-reuse-v1') / 'pilot.py')
compare = module('qualified_observations', HERE.with_name('differential-obligations-v1') / 'compare.py')
MODEL = 'gpt-6-astra'; EFFORT = 'xhigh'


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p, x): Path(p).write_text(json.dumps(x, indent=2) + '\n')


def prepare(root):
    started = time.perf_counter(); root = Path(root).resolve(); root.mkdir(parents=True, exist_ok=False)
    cwd = root / 'work'; cwd.mkdir()
    files = {
        'workflow_memory.py': HERE.with_name('differential-obligations-v1') / 'artifacts/uncovered_query-source.py',
        'before.py': old.BASE / 'baseline/workflow_memory.py', 'TASK.md': old.BASE / 'TASK.md',
        'evidence.py': old.BASE / 'baseline/evidence.py',
        'test_workflow_memory.py': old.BASE / 'baseline/test_workflow_memory.py',
        'test_search_mode_public.py': old.BASE / 'test_search_mode_public.py',
        'semantic_native.py': old.PRIOR / 'off/probe-1.py',
        'semantic_helix.py': old.PRIOR / 'on/probe-1.py',
        '.agents/skills/helixcontext/SKILL.md': old.SKILL,
    }
    for name, source in files.items():
        p = cwd / name; p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(source.read_bytes())
    (cwd / 'AGENTS.md').write_text(old.memory.LOCAL_RULE)
    before = old.protected(cwd)
    regressions = old.checks(cwd, root / 'regressions')
    assert all(c['exit_status'] == 0 for c in regressions['checks'])
    differential = compare.compare(cwd / 'before.py', cwd / 'workflow_memory.py', root / 'comparisons',
                                   compare.binding(cwd / 'before.py', cwd / 'workflow_memory.py'))
    assert differential['state'] == 'NO_DIFFERENCE_IN_ENUMERATED_CASES'
    assert differential['case_count'] == 612 and old.protected(cwd) == before
    # Neutral resident evidence, not a selected answer or a defective-case hint.
    prompt = ('Review the proposed workflow_memory.py against the recorded requirements in TASK.md and before.py. '
              'This is a review; do not edit protected task files. Other runs/research/evaluators are out of scope except the exact executor and evidence paths supplied here. '
              'Ordinary tools, exact evidence and independent semantic judgment remain available. '
              'Return your normal complete prose review with actual check results, defects and remaining concerns. '
              'Caller delivers your model-written final unchanged.\n'
              'Caller ran the supplied tests and both existing regression programs against these exact files. '
              'Caller also ran the qualified finite compatibility relations. These observations do not establish '
              'semantic correctness or complete coverage. Full raw outcomes are retained at the supplied paths.\n')
    prompt += json.dumps({'regressions': regressions, 'comparisons': {
        k: differential[k] for k in ['state', 'case_count', 'families', 'outcomes', 'semantic_adequacy']}})
    for name in files:
        if name.startswith('.agents/'): continue
        prompt += '\nEXACT FILE ' + name + '\n' + (cwd / name).read_text()
    # The actual executor source is literal evidence; its original path remains executable.
    executor = Path(compare.__file__)
    prompt += '\nEXACT COMPARISON EXECUTOR ' + str(executor) + '\n' + executor.read_text()
    mem = root / 'memory'; old.memory.prepare(cwd, prompt, 'current scoped code review evidence', mem)
    prompt = old.memory.attach(cwd, prompt, mem, sha(mem / 'receipt.json'))
    (root / 'prompt.txt').write_text(prompt)
    catalog = subprocess.check_output([old.native.RPC.__init__.__globals__['CLI'], 'debug', 'models'])
    (root / 'catalog.json').write_bytes(catalog)
    base = next(r['base_instructions'] for r in json.loads(catalog)['models'] if r['slug'] == MODEL)
    paths = [Path(__file__), HERE / 'PREREG.md', executor, Path(old.__file__), old.CONFIG, old.AGENTS,
             old.SKILL, old.memory.CLIENT, Path(old.native.__file__), Path(old.memory.__file__), Path(old.caller_registration.__file__),
             old.native.HELPER, Path(old.native.RPC.__init__.__globals__['CLI'])]
    paths += [Path(p) for p in differential['binding']['files']]
    paths += [REPO / 'engine/output' / n for n in ('app_server_native.py', 'raw_receipts.py', 'config_bound_session.py')]
    paths += [p for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    # Disposable comparison DB state is not frozen; exact observations/receipts are.
    paths = [p for p in paths if not (p.is_relative_to(root) and
             any(x.startswith(('old-', 'new-')) for x in p.relative_to(root).parts))]
    manifest = {'model': MODEL, 'effort': EFFORT, 'base_sha256': hashlib.sha256(base.encode()).hexdigest(),
                'bindings': {str(p.resolve()): sha(p) for p in paths}, 'protected': before,
                'classification': 'One exposed hostile candidate, no control or saving claim',
                'prompt_bytes': len(prompt.encode()), 'preparation_seconds': time.perf_counter() - started,
                'native_turns_authorized': 1}
    manifest['comparison_binding'] = differential['binding']
    save(root / 'manifest.json', manifest)
    print(json.dumps({k: manifest[k] for k in ['prompt_bytes', 'preparation_seconds']}))


def preflight(root):
    root = Path(root).resolve(); m = json.loads((root / 'manifest.json').read_text()); old.verify(m)
    compare.guard(m['comparison_binding'])
    with old.native.Session(MODEL, root / 'work', root / 'no-call-preflight',
                            root / 'work/.agents/skills/helixcontext/SKILL.md', effort=EFFORT) as s:
        assert not s.turns
    assert not s.failed; old.verify(m); compare.guard(m['comparison_binding'])
    save(root / 'PREFLIGHT.json', {'state': 'PASS', 'model_turns': 0, 'manifest_sha256': sha(root / 'manifest.json')})


def admitted(root):
    root = Path(root).resolve(); m = json.loads((root / 'manifest.json').read_text())
    old.verify(m); compare.guard(m['comparison_binding'])
    p = json.loads((root / 'PREFLIGHT.json').read_text())
    if (p.get('state') != 'PASS' or p.get('model_turns') != 0 or
            p.get('manifest_sha256') != sha(root / 'manifest.json')):
        raise ValueError('Preflight does not authorize current manifest')
    if m.get('model') != MODEL or m.get('effort') != EFFORT or m.get('native_turns_authorized') != 1:
        raise ValueError('Unqualified model/effort/call count')
    return m


def run(root):
    root = Path(root).resolve(); m = admitted(root)
    cwd = root / 'work'; result = {'state': 'RUNNING', 'manifest_sha256': sha(root / 'manifest.json')}
    # Atomic ownership claim: crashes and concurrent starts cannot buy a retry.
    with (root / 'result.json').open('x') as f: json.dump(result, f)
    try:
        with old.native.Session(MODEL, cwd, root / 'native', cwd / '.agents/skills/helixcontext/SKILL.md', effort=EFFORT) as s:
            answer, turn = s.turn(old.caller_registration.attach(s, (root / 'prompt.txt').read_text()))
            result.update(answer=answer, usage=s.total, turn=turn); save(root / 'result.json', result)
        assert not s.failed; old.verify(m); compare.guard(m['comparison_binding'])
        now = old.protected(cwd)
        assert all(now.get(k) == v for k, v in m['protected'].items())
        result.update(state='AWAITING_SEMANTIC_AUDIT', extra_files=sorted(set(now) - set(m['protected'])))
    except BaseException as exc:
        result.update(state='STOPPED_PENDING_AUDIT', error=repr(exc)); raise
    finally:
        save(root / 'result.json', result)


if __name__ == '__main__':
    {'prepare': prepare, 'preflight': preflight, 'run': run}[sys.argv[1]](sys.argv[2])
