"""One fresh Astra High pair; existing executor, complete native final, no retry."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import secrets
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


old = module('cold_review_helpers', HERE.with_name('astra-reuse-v1') / 'pilot.py')
sys.path.insert(0, str(HERE.with_name('continuation-contract')))
fixture = module('cold_fixture', HERE.with_name('continuation-contract') / 'luna_resolved_retrieval_pair.py')
MODEL = 'gpt-6-astra'
EFFORT = 'high'


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p, v): Path(p).write_text(json.dumps(v, ensure_ascii=False, indent=2) + '\n')
def read(p): return json.loads(Path(p).read_text())


def unique(pairs):
    d = {}
    for k, v in pairs:
        if k in d: raise ValueError('Duplicate final field')
        d[k] = v
    return d


def grade(answer, expected):
    # Parsing is for grading only. Original native final bytes remain untouched.
    text = answer.strip()
    if text.startswith('```'):
        m = re.fullmatch(r'```(?:json)?\s*\n(.*?)\n```', text, re.DOTALL)
        if not m: raise ValueError('Malformed JSON fence')
        text = m[1]
    value = json.loads(text, object_pairs_hook=unique)
    if not fixture.equal(value, expected): raise ValueError('Final answer fidelity failure')
    return value


def recover(root, task, source, constraints=()):
    """Fresh archive + reopened store. Unsupported requests never yield packets."""
    start = time.perf_counter()
    store = fixture.Store(root / 'store')
    ref = store.put(source)
    ingest = dict(store.metrics)
    state = {'schema': fixture.gate.VERSION, 'adapter_version': fixture.resolve.VERSION,
             'task_sha256': hashlib.sha256(task.encode()).hexdigest(),
             'source_ref': ref, 'active_constraints': list(constraints)}
    save(root / 'task-state.json', state)
    pinned = fixture.gate.state_root(state)
    reopened = fixture.Store(root / 'store')
    outcome = fixture.gate.dispatch(task, reopened, ref, expected_state_root=pinned,
                current_state=lambda: read(root / 'task-state.json'),
                semantic=lambda *_: {'semantic_work_remains': True})
    if outcome['state'] != 'RESOLVED':
        raise ValueError('Prepared packet not admitted: ' + outcome['state'])
    answer = outcome['answer']
    notes = [n for event in json.loads(source) if event['turn'] == answer['evidence_turn']
             for n in event['data']['notes'] if n['inventory_tag'] == answer['inventory_tag']]
    if len(notes) != 1: raise ValueError('Exact original note not uniquely located')
    packet = {'schema': 'helix.cold-native-final.v1', 'source_file': 'history.json',
              'source_ref': ref, 'task_state_root': pinned,
              'executor': fixture.resolve.VERSION, 'gate': fixture.gate.VERSION,
              'recovered_fields': answer, 'original_note': notes[0],
              'checked_predicates': outcome['checked_predicates'],
              'unchecked_obligations': outcome['unchecked_obligations']}
    save(root / 'packet.json', packet)
    receipt = {'outcome': outcome, 'ingest_io': ingest, 'reopened_recovery_io': dict(reopened.metrics),
               'seconds': time.perf_counter() - start,
               'scope': 'Logical Store object I/O; full physical I/O unmeasured. JSON parsing and binding reads additional.'}
    save(root / 'recovery.json', receipt)
    return packet


def prepare(root):
    start = time.perf_counter(); root = Path(root).resolve(); root.mkdir(parents=True, exist_ok=False)
    spec = fixture.fixtures()['cold']; expected = fixture.expected('cold', spec)
    save(root / 'fixture.json', spec); save(root / 'expected.private.json', expected)
    source = (json.dumps(spec['source'], ensure_ascii=False, indent=2) + '\n').encode()
    packet = recover(root, spec['task'], source)
    if not fixture.equal(packet['recovered_fields'], expected): raise ValueError('Independent oracle disagrees')
    catalog = subprocess.check_output([old.native.RPC.__init__.__globals__['CLI'], 'debug', 'models'])
    (root / 'catalog.json').write_bytes(catalog)
    base = next(x['base_instructions'] for x in json.loads(catalog)['models'] if x['slug'] == MODEL)
    order = ['off', 'on']; secrets.SystemRandom().shuffle(order)
    m = {'schema': 'helix.cold-native-final.v1', 'model': MODEL, 'effort': EFFORT, 'order': order,
         'base_sha256': hashlib.sha256(base.encode()).hexdigest(), 'native_turns_authorized': 2,
         'classification': 'Exposed development snapshot; Engine-managed ordinary control; same installed configuration and original base',
         'source_sha256': hashlib.sha256(source).hexdigest(), 'source_bytes': len(source), 'protected': {}, 'prompt_bytes': {}}
    for arm in ('off', 'on'):
        cwd = root / arm; cwd.mkdir()
        (cwd / 'history.json').write_bytes(source)
        (cwd / 'AGENTS.md').write_text(old.memory.LOCAL_RULE)
        skill = cwd / '.agents/skills/helixcontext/SKILL.md'; skill.parent.mkdir(parents=True); skill.write_bytes(old.SKILL.read_bytes())
        task = (fixture.COMMON + spec['task'] + '\nComplete exact prior events are in history.json; retrieve whatever evidence you need. '
                'Return the complete requested JSON in your normal final answer. The caller preserves your final answer unchanged.\n')
        if arm == 'on':
            task += ('Caller archived and reopened the exact source, then executed the bound exact lookup before this inference. '
                     'These completed extraction facts do not establish semantic adequacy or complete authority. '
                     'The complete original history and ordinary tools remain available. Global operational instructions remain model responsibilities.\n'
                     + json.dumps(packet, ensure_ascii=False, separators=(',', ':')) + '\n')
        mem = root / (arm + '-memory')
        old.memory.prepare(cwd, task, 'current task exact packing note', mem)
        prompt = old.memory.attach(cwd, task, mem, sha(mem / 'receipt.json'))
        (root / (arm + '-prompt.txt')).write_text(prompt)
        m['protected'][arm] = old.protected(cwd); m['prompt_bytes'][arm] = len(prompt.encode())
    # Bind actual imported repository modules plus the protocol, installation and runtime.
    paths = {Path(__file__), HERE / 'PREREG.md', HERE / 'test_pilot.py', old.CONFIG, old.AGENTS,
             old.SKILL, old.memory.CLIENT, old.native.HELPER, Path(old.native.RPC.__init__.__globals__['CLI']),
             Path(sys.executable).resolve(), Path(old.__file__), Path(fixture.__file__)}
    for mod in list(sys.modules.values()):
        p = getattr(mod, '__file__', None)
        if p and Path(p).resolve().is_relative_to(REPO): paths.add(Path(p).resolve())
    paths.update((REPO / 'benchmarks/frozen-high/protocol' / n) for n in ['reasoning-v2.json', 'latent-v1/delay-40.json'])
    paths.update(p for p in root.rglob('*') if p.is_file())
    m['bindings'] = {str(p.resolve()): sha(p) for p in sorted(paths)}
    m['preparation_seconds'] = time.perf_counter() - start
    save(root / 'manifest.json', m)
    print(json.dumps({k: m[k] for k in ['order', 'source_bytes', 'prompt_bytes', 'preparation_seconds']}))


def preflight(root):
    root = Path(root).resolve(); m = read(root / 'manifest.json'); old.verify(m)
    started = time.perf_counter()
    for arm in m['order']:
        cwd = root / arm
        with old.native.Session(MODEL, cwd, root / (arm + '-preflight'), cwd / '.agents/skills/helixcontext/SKILL.md', effort=EFFORT) as s:
            assert not s.turns
        if s.failed: raise ValueError('Native preflight failed')
        old.verify(m)
    save(root / 'PREFLIGHT.json', {'state': 'PASS', 'model_turns': 0, 'manifest_sha256': sha(root / 'manifest.json'),
                                 'seconds': time.perf_counter() - started})


def admitted(root):
    m = read(root / 'manifest.json'); old.verify(m); p = read(root / 'PREFLIGHT.json')
    if p.get('state') != 'PASS' or p.get('model_turns') != 0 or p.get('manifest_sha256') != sha(root / 'manifest.json'):
        raise ValueError('Preflight does not bind current manifest')
    if (m.get('model'), m.get('effort'), m.get('native_turns_authorized')) != (MODEL, EFFORT, 2):
        raise ValueError('Model, effort or call count changed')
    if sorted(m['order']) != ['off', 'on']: raise ValueError('Invalid pair')
    return m


def run(root):
    root = Path(root).resolve(); m = admitted(root)
    result = {'state': 'RUNNING', 'manifest_sha256': sha(root / 'manifest.json'), 'rows': []}
    with (root / 'results.json').open('x') as f: json.dump(result, f)
    try:
        for arm in m['order']:
            old.verify(m); cwd = root / arm
            row = {'arm': arm, 'state': 'RUNNING'}; result['rows'].append(row); save(root / 'results.json', result)
            with old.native.Session(MODEL, cwd, root / (arm + '-run'), cwd / '.agents/skills/helixcontext/SKILL.md', effort=EFFORT) as s:
                old.verify(m)
                answer, turn = s.turn(old.caller_registration.attach(s, (root / (arm + '-prompt.txt')).read_text()))
                row.update(answer=answer, usage=dict(s.total), turn=turn); save(root / 'results.json', result)
            if s.failed: raise ValueError('Native/config/raw closure failed')
            old.verify(m)
            now = old.protected(cwd)
            if any(now.get(k) != v for k, v in m['protected'][arm].items()): raise ValueError('Protected task changed')
            grade(answer, read(root / 'expected.private.json'))
            row.update(state='AWAITING_AUDIT', mechanical_final_grade='PASS', elapsed_seconds=time.perf_counter()-s.started,
                       extra_files=sorted(set(now) - set(m['protected'][arm])))
            save(root / 'results.json', result)
            print(json.dumps({k: row[k] for k in ['arm','state','usage']}), flush=True)
        result['state'] = 'AWAITING_AUDIT'
    except BaseException as exc:
        result.update(state='STOPPED_PENDING_AUDIT', error=repr(exc)); raise
    finally:
        save(root / 'results.json', result)


if __name__ == '__main__':
    {'prepare': prepare, 'preflight': preflight, 'run': run}[sys.argv[1]](sys.argv[2])
