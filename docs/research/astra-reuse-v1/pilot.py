"""Astra ordinary-vs-prepared review, same base/tools/skill. No output rewriting."""
import difflib
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
BASE = HERE.with_name('maintenance-copy-v1')
PRIOR = HERE.with_name('native-output-v1') / 'artifacts/astra-xhigh'
sys.path.insert(0, str(REPO / 'engine/output'))
import effort_session as native
import caller_memory_receipt as memory
import caller_registration

MODEL = 'gpt-6-astra'
EFFORT = 'xhigh'
CONFIG = Path('/Users/mert/.codex/config.toml')
AGENTS = Path('/Users/mert/.codex/AGENTS.md')
SKILL = Path('/Users/mert/.codex/skills/helixcontext/SKILL.md')


def sha(raw): return hashlib.sha256(raw).hexdigest()
def save(path, value): path.write_text(json.dumps(value, indent=2) + '\n')


def protected(cwd):
    return {str(p.relative_to(cwd)): sha(p.read_bytes()) for p in cwd.rglob('*')
            if p.is_file() and ('.helix' not in p.relative_to(cwd).parts)
            and '__pycache__' not in p.parts}


def checks(cwd, out):
    out.mkdir(exist_ok=False)
    before = protected(cwd)
    rows = []
    for label, argv in [('public', [sys.executable, '-B', '-m', 'pytest', '-q', '-p', 'no:cacheprovider']),
                        ('prior_astra_native', [sys.executable, '-B', 'semantic_native.py']),
                        ('prior_astra_helix', [sys.executable, '-B', 'semantic_helix.py'])]:
        begin = time.perf_counter()
        p = subprocess.run(argv, cwd=cwd, capture_output=True, timeout=45)
        (out / (label + '.stdout')).write_bytes(p.stdout)
        (out / (label + '.stderr')).write_bytes(p.stderr)
        rows.append({'check': label, 'argv': argv, 'exit_status': p.returncode,
                     'stdout': p.stdout.decode(), 'stderr': p.stderr.decode(),
                     'seconds': time.perf_counter() - begin,
                     'stdout_sha256': sha(p.stdout), 'stderr_sha256': sha(p.stderr)})
    if protected(cwd) != before: raise ValueError('Checker changed protected task files')
    receipt = {'schema': 'helix.executed-regressions.v1', 'cwd': str(cwd),
               'inputs': before, 'checks': rows,
               'authority': 'Actual execution facts only; semantic adequacy and complete coverage remain unproved'}
    save(out / 'receipt.json', receipt)
    return receipt


def prepare(root):
    root = Path(root).resolve(); root.mkdir(parents=True, exist_ok=False)
    started = time.perf_counter()
    catalog = subprocess.check_output([native.RPC.__init__.__globals__['CLI'], 'debug', 'models'])
    (root / 'catalog.json').write_bytes(catalog)
    row = next(x for x in json.loads(catalog)['models'] if x['slug'] == MODEL)
    source = (PRIOR / 'on/workflow_memory.py').read_bytes()
    baseline = (BASE / 'baseline/workflow_memory.py').read_bytes()
    altered = source.replace(b'def search(self,project,query,limit=10,', b'def search(self,project,query,limit=9,')
    assert source != altered
    cases = [('sample_a', source, ['on', 'off']), ('sample_b', altered, ['off', 'on'])]
    manifest = {'schema': 'helix.astra-probe-reuse.v1', 'model': MODEL, 'effort': EFFORT,
                'comparator': 'Helix ordinary execution, installed shared configuration; not pristine native',
                'base_sha256': sha(row['base_instructions'].encode()), 'cases': [], 'bindings': {}}
    # This evidence freezes code and protocol before any model outcome.
    paths = [Path(__file__), HERE / 'PREREG.md', CONFIG, AGENTS, SKILL,
             Path(native.__file__), Path(memory.__file__), Path(caller_registration.__file__),
             Path(native.RPC.__init__.__globals__['CLI']), native.HELPER,
             REPO / 'engine/output/raw_receipts.py', REPO / 'engine/output/config_bound_session.py',
             REPO / 'engine/output/app_server_native.py', BASE / 'TASK.md', root / 'catalog.json']
    for case, data, order in cases:
        manifest['cases'].append({'case': case, 'order': order, 'source_sha256': sha(data)})
        for arm in order:
            folder = root / (case + '-' + arm); folder.mkdir()
            cwd = folder / 'work'; cwd.mkdir()
            files = {'workflow_memory.py': data, 'before.py': baseline,
                     'TASK.md': (BASE / 'TASK.md').read_bytes(),
                     'test_search_mode_public.py': (BASE / 'test_search_mode_public.py').read_bytes(),
                     'semantic_native.py': (PRIOR / 'off/probe-1.py').read_bytes(),
                     'semantic_helix.py': (PRIOR / 'on/probe-1.py').read_bytes(),
                     'AGENTS.md': memory.LOCAL_RULE.encode(),
                     '.agents/skills/helixcontext/SKILL.md': SKILL.read_bytes()}
            files.update({n: (BASE / 'baseline' / n).read_bytes()
                          for n in ('evidence.py', 'test_workflow_memory.py')})
            for name, raw in files.items():
                p = cwd / name; p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(raw)
            prompt = ('Review the proposed workflow_memory.py implementation against TASK.md and before.py. '
                      'This is a review: do not edit protected task files. Other runs, reference implementations, '
                      'research documents and evaluators are out of scope. Ordinary tools and semantic judgment remain available. '
                      'Verify the supplied tests and the two existing regression programs, semantic_native.py and semantic_helix.py. '
                      'Assess whether the change is correct and preserves the existing API and behavior. '
                      'Return your normal prose review, explaining actual check results, any defects and remaining concerns. '
                      'The caller preserves your final answer exactly; no operation JSON or constrained decision schema is requested.\n'
                      + files['TASK.md'].decode())
            if arm == 'on':
                receipt = checks(cwd, folder / 'preflight')
                if any(x['exit_status'] != 0 for x in receipt['checks']):
                    raise ValueError('Offline fixture gate failed')
                diff = ''.join(difflib.unified_diff(baseline.decode().splitlines(keepends=True),
                              data.decode().splitlines(keepends=True), fromfile='before.py', tofile='workflow_memory.py'))
                prompt += ('\nCaller executed the supplied regressions against the current files before this inference. '
                           'These exact execution facts do not establish semantic correctness or complete coverage. '
                           'Original source and regression programs remain available in this task directory.\n'
                           + json.dumps(receipt) + '\nExact complete change:\n' + diff)
                paths += list((folder / 'preflight').iterdir())
            mem = folder / 'memory'
            memory.prepare(cwd, prompt, 'current scoped code review and regression evidence', mem)
            prompt = memory.attach(cwd, prompt, mem, sha((mem / 'receipt.json').read_bytes()))
            (folder / 'prompt.txt').write_text(prompt)
            paths += [cwd / n for n in files] + list(mem.iterdir()) + [folder / 'prompt.txt']
            save(folder / 'protected.json', protected(cwd)); paths.append(folder / 'protected.json')
    manifest['bindings'] = {str(p.resolve()): sha(p.read_bytes()) for p in paths}
    manifest['preparation_seconds'] = time.perf_counter() - started
    save(root / 'manifest.json', manifest)
    print(json.dumps({'prepared': str(root), 'native_model_calls': 0,
                      'manifest_sha256': sha((root / 'manifest.json').read_bytes())}))


def verify(manifest):
    for name, digest in manifest['bindings'].items():
        if sha(Path(name).read_bytes()) != digest: raise ValueError('Binding changed: ' + name)


def run(root):
    root = Path(root).resolve(); manifest = json.loads((root / 'manifest.json').read_text())
    verify(manifest)
    result_file = root / 'results.json'
    if result_file.exists(): raise ValueError('No restart or hidden retry')
    result = {'state': 'RUNNING', 'manifest_sha256': sha((root / 'manifest.json').read_bytes()), 'rows': []}
    save(result_file, result)
    try:
        for c in manifest['cases']:
            for arm in c['order']:
                verify(manifest)
                folder = root / (c['case'] + '-' + arm); cwd = folder / 'work'
                before = json.loads((folder / 'protected.json').read_text())
                row = {'case': c['case'], 'arm': arm, 'state': 'RUNNING'}
                result['rows'].append(row); save(result_file, result)
                with native.Session(MODEL, cwd, folder / 'native',
                                    cwd / '.agents/skills/helixcontext/SKILL.md', effort=EFFORT) as session:
                    verify(manifest)
                    answer, turn = session.turn(caller_registration.attach(session, (folder / 'prompt.txt').read_text()))
                    row.update(answer=answer, native=turn, usage=dict(session.total))
                    save(result_file, result)
                if session.failed: raise ValueError('Native capture/config audit failed')
                verify(manifest)
                current = protected(cwd)
                if any(current.get(k) != v for k, v in before.items()):
                    raise ValueError('Protected source changed')
                row.update(state='AWAITING_SEMANTIC_AUDIT', extra_files=sorted(set(current) - set(before)),
                           elapsed_seconds=time.perf_counter()-session.started,
                           source_sha256=sha((cwd / 'workflow_memory.py').read_bytes()))
                save(result_file, result)
                print(json.dumps({k: row[k] for k in ('case','arm','state','usage')}), flush=True)
        result['state'] = 'AWAITING_AUDIT'; save(result_file, result)
    except BaseException as exc:
        result.update(state='STOPPED_PENDING_AUDIT', error=repr(exc)); save(result_file, result); raise


if __name__ == '__main__':
    {'prepare': prepare, 'run': run}[sys.argv[1]](sys.argv[2])
