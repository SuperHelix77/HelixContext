"""First-release maintenance cells: explicit effort and predeclared publication lock."""
import hashlib
import json
import os
from pathlib import Path
import secrets
import shutil
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
INPUT = HERE.with_name('maintenance-copy-v1')
sys.path[:0] = [str(REPO / 'engine/output'), str(REPO / 'engine/prototype'), str(HERE.parent / 'continuation-contract')]
import effort_session as observed_session
import effort_session as native
import caller_memory_receipt as memory
import caller_registration
import project_registration_preflight as registration
import luna_varied_coding_v2 as workspace
from evidence import Store
from literal_edits import parse, compile_edits, assemble
import renderer
from app_server_native import usage

MODEL = 'gpt-6-astra'
EFFORT = 'xhigh'
CLI = Path('/Applications/ChatGPT.app/Contents/Resources/codex')
BASE = REPO / 'engine/profiles/astra-coding-transfer-v1/base.md'
TARGET = 'workflow_memory.py'
FILES = [TARGET, 'evidence.py', 'test_workflow_memory.py', 'test_search_mode_public.py']


def configure(model, effort):
    global MODEL, EFFORT, BASE
    if (model, effort) not in (('gpt-6-astra', 'xhigh'), ('gpt-5.6-sol', 'high')):
        raise ValueError('Unregistered release cell')
    MODEL, EFFORT = model, effort
    BASE = REPO / ('engine/profiles/' + ('astra' if model == 'gpt-6-astra' else 'sol') + '-coding-transfer-v1/base.md')


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def save(path, value): Path(path).write_text(json.dumps(value, indent=2) + '\n')


def scope(cwd, bound):
    if workspace.git(cwd, 'rev-parse', 'HEAD') != bound['initial_commit']:
        raise RuntimeError('Bound Git history changed')
    raw = subprocess.check_output(['git', 'status', '--porcelain=v1', '-z', '--untracked-files=all'], cwd=cwd)
    if any(item != b' M workflow_memory.py' for item in raw.split(b'\0') if item):
        raise RuntimeError('Unexpected task-file modification')


def proposal(answer, raw, source_key):
    """Only malformed model edits are repairable; binding errors stay fatal."""
    if hashlib.sha256(raw).hexdigest() != source_key:
        raise RuntimeError('Original source changed')
    text = answer.strip()
    if text.startswith('```json\n') and text.endswith('```'): text = text[8:-3]
    try:
        selected = parse(text)
        if isinstance(selected, dict) and 'semantic_obligations' in selected:
            return None, None, {'checks': 'FAIL', 'semantic_attention': selected}
        plan, _ = compile_edits(raw, source_key, selected)
        return text, plan, None
    except (ValueError, UnicodeError) as exc:
        return None, None, {'checks': 'FAIL', 'edit_error': str(exc)}


def prepare(root):
    begin = time.perf_counter(); root = Path(root).resolve(); root.mkdir(parents=True, exist_ok=False)
    inputs = {n: (INPUT / 'baseline' / n).read_bytes() for n in FILES[:3]}
    inputs[FILES[-1]] = (INPUT / FILES[-1]).read_bytes()
    order = ['off', 'on']; secrets.SystemRandom().shuffle(order)
    catalog = json.loads(subprocess.check_output([str(CLI), 'debug', 'models']))['models']
    default = next(r['base_instructions'] for r in catalog if r['slug'] == MODEL)
    m = {'model': MODEL, 'effort': EFFORT, 'order': order, 'max_semantic_turns_per_arm': 2,
         'blind_retries': 0, 'classification': 'Fresh N=1 known maintenance task, model/effort release cell; not earlier coding qualification',
         'inputs': {n: hashlib.sha256(raw).hexdigest() for n, raw in inputs.items()}, 'git': {}, 'registration': {},
         'default_base_sha256': hashlib.sha256(default.encode()).hexdigest(), 'base_file': str(BASE)}
    frozen = [Path(__file__), HERE / 'audit_release.py', HERE / 'test_release_runner.py', HERE / 'PREREG.md', INPUT / 'TASK.md', INPUT / 'oracle.py', INPUT / 'OFFLINE_CALIBRATION.json',
              INPUT / 'BASELINE_MANIFEST.json', BASE, CLI, Path('/Users/mert/.codex/AGENTS.md'), memory.CLIENT]
    frozen += [Path(x.__file__) for x in (observed_session, native, memory, caller_registration, registration, workspace, renderer)]
    frozen += [REPO / 'engine/prototype' / n for n in ('literal_edits.py', 'evidence.py')]
    frozen += [REPO / 'engine/output' / n for n in ('app_server_native.py', 'raw_receipts.py')]
    frozen += [Path(observed_session.HELPER)]
    frozen += [INPUT / 'baseline' / n for n in FILES[:3]] + [INPUT / FILES[-1]]
    for arm in ('off', 'on'):
        cwd = root / arm; cwd.mkdir()
        for name, raw in inputs.items(): (cwd / name).write_bytes(raw)
        (cwd / 'AGENTS.md').write_text(memory.LOCAL_RULE)
        skill = cwd / '.agents/skills/helixcontext/SKILL.md'; skill.parent.mkdir(parents=True)
        skill.write_bytes((REPO / 'skills/helixcontext/SKILL.md').read_bytes())
        (cwd / (TARGET + '.helix-lock')).touch()  # Caller-owned empty metadata, declared before execution.
        m['git'][arm] = workspace.initialize(cwd)
        warm = root / (arm + '-registration'); m['registration'][arm] = registration.warm(cwd, warm, MODEL)
        common = ('Work only in this task directory. Other runs, reference implementations and evaluators are out of scope. '
                  'Ordinary tools and semantic review remain available. Caller independently checks the final artifact.\n' + (INPUT / 'TASK.md').read_text())
        if arm == 'on':
            common += ('\nCaller owns exact editing, required tests and publication. Return JSON only: '
                       '{"edits":[{"old":"exact original text","new":"replacement text"}]}. '
                       'Each old text must occur exactly once in the supplied original workflow_memory.py; spans must not overlap. '
                       'All edits apply simultaneously to that original. You may replace the whole original file if needed. '
                       'Leave caller-owned task files unchanged. You own implementation, semantic review and test adequacy. '
                       'Checks/publication are pending mechanics, not unresolved semantics. Do not claim tests ran before they run. '
                       'If information is insufficient, return {"semantic_obligations":["question"]}. '
                       'Actual failures return for reconsideration.\nExact task files:\n' +
                       json.dumps({n: b.decode() for n, b in inputs.items()}))
        mem = root / (arm + '-memory')
        memory.prepare(cwd, common, 'current memory search maintenance task', mem)
        prompt = memory.attach(cwd, common, mem, sha(mem / 'receipt.json'))
        (root / (arm + '-prompt.txt')).write_text(prompt)
        frozen += [cwd / (TARGET + '.helix-lock')] + [cwd / n for n in FILES if n != TARGET] + [cwd / 'AGENTS.md', skill, cwd / '.gitignore', root / (arm + '-prompt.txt')]
        frozen += [p for p in warm.iterdir() if p.is_file()] + [p for p in mem.iterdir() if p.is_file()]
    cfg = root / 'config.initial.private.toml'; native.private_write(cfg, Path('/Users/mert/.codex/config.toml').read_bytes())
    frozen.append(cfg)
    m.update(config_snapshot=str(cfg), shared_config='/Users/mert/.codex/config.toml',
             preparation_seconds=time.perf_counter()-begin, sha256={str(p.resolve()): sha(p) for p in frozen})
    save(root / 'manifest.json', m)
    print(json.dumps({'manifest_sha256': sha(root / 'manifest.json'), 'order': order, 'model_turns': 0,
                      'preparation_seconds': m['preparation_seconds']}))


def verify(m):
    for name, digest in m['sha256'].items():
        if sha(name) != digest: raise ValueError('Bound source changed: ' + name)
    native.validate(Path(m['config_snapshot']).read_bytes(), Path(m['shared_config']).read_bytes())


def original(root, m, arm):
    verify(m)
    if sha(root / arm / TARGET) != m['inputs'][TARGET]: raise RuntimeError('Original source changed')


def grade(cwd, destination):
    destination.mkdir(parents=True, exist_ok=False); begin = time.perf_counter()
    before = {n: sha(cwd / n) for n in FILES}
    rows = []
    for label, args in [('public', [sys.executable, '-B', '-m', 'pytest', '-q', FILES[2], FILES[3]]),
                        ('oracle', [sys.executable, '-B', str(INPUT / 'oracle.py'), str(cwd)])]:
        try:
            r = subprocess.run(args, cwd=cwd, capture_output=True, timeout=45)
            code, out, err = r.returncode, r.stdout, r.stderr
        except subprocess.TimeoutExpired as exc:
            code, out, err = None, exc.stdout or b'', exc.stderr or b''
        (destination / (label + '.stdout')).write_bytes(out); (destination / (label + '.stderr')).write_bytes(err)
        rows.append(dict(check=label, exit_code=code, stdout=out.decode(errors='replace'), stderr=err.decode(errors='replace'),
                         stdout_sha256=sha(destination / (label + '.stdout')), stderr_sha256=sha(destination / (label + '.stderr'))))
    if any(sha(cwd / n) != h for n, h in before.items()): raise RuntimeError('Checker mutated staged input')
    passed = all(r['exit_code'] == 0 for r in rows)
    if passed:
        assert '23 passed' in rows[0]['stdout'] and json.loads(rows[1]['stdout'])['finite_cases'] == 94
    result = dict(checks='PASS' if passed else 'FAIL', rows=rows, source_sha256=sha(cwd / TARGET), seconds=time.perf_counter()-begin)
    save(destination / 'receipt.json', result); return result


def run(root):
    root = Path(root).resolve(); m = json.loads((root / 'manifest.json').read_text()); configure(m['model'], m['effort']); verify(m)
    path = root / 'results.json'
    if path.exists(): raise ValueError('No restart or retry')
    result = {'state': 'RUNNING', 'manifest_sha256': sha(root / 'manifest.json'), 'rows': []}; save(path, result)
    saved_rpc = observed_session.RPC
    class KernelRPC(saved_rpc):
        def call(self, method, params):
            if method == 'thread/start': params = {**params, 'config': {**params['config'], 'model_instructions_file': str(BASE)}}
            return super().call(method, params)
    try:
        for arm in m['order']:
            original(root, m, arm); cwd = root / arm
            assert workspace.git(cwd, 'rev-parse', 'HEAD') == m['git'][arm]['initial_commit']
            assert workspace.git(cwd, 'status', '--porcelain=v1', '--untracked-files=all') == ''
            observed_session.RPC = KernelRPC if arm == 'on' else saved_rpc
            store = Store(root / (arm + '-store')); source_key = store.put((cwd / TARGET).read_bytes())['sha256']
            row = {'arm': arm, 'turns': []}; result['rows'].append(row); save(path, result)
            started = time.perf_counter()
            skill = cwd / '.agents/skills/helixcontext/SKILL.md' if arm == 'on' else None
            with native.Session(MODEL, cwd, root / (arm + '-run'), skill, effort=EFFORT) as session:
                prompt = (root / (arm + '-prompt.txt')).read_text()
                if arm == 'on': prompt = caller_registration.attach(session, prompt)
                for index in range(1, 3):
                    answer, turn = session.turn(prompt)
                    attempt = {'answer': answer, 'native': turn}; row['turns'].append(attempt)
                    row['usage'] = dict(session.total); save(path, result)
                    verify(m)
                    scope(cwd, m['git'][arm])
                    if arm == 'on':
                        original(root, m, arm)
                        text, plan, completion = proposal(answer, (cwd / TARGET).read_bytes(), source_key)
                        if completion and 'semantic_attention' in completion:
                            attempt['completion'] = completion; row.update(completion); save(path, result); break
                        if completion is None:
                            raw, receipt = assemble(store, source_key, text)
                            stage = root / ('stage-' + str(index)); stage.mkdir()
                            for name in FILES: (stage / name).write_bytes(raw if name == TARGET else (cwd / name).read_bytes())
                            completion = grade(stage, root / ('on-check-' + str(index)))
                            attempt.update(edit_receipt=receipt, completion=completion, stage_source_sha256=sha(stage / TARGET))
                            original(root, m, arm)
                            if completion['checks'] == 'PASS':
                                attempt['publication'] = renderer.publish(store, plan, cwd / TARGET, expected_sha256=source_key)
                                assert (cwd / TARGET).read_bytes() == raw
                        else: attempt['completion'] = completion
                    else:
                        completion = grade(cwd, root / ('off-check-' + str(index))); attempt['completion'] = completion
                    row['checks'] = completion['checks']; save(path, result)
                    if row['checks'] == 'PASS': break
                    prompt = ('Caller checks failed; no successful task claimed. Reconsider the exact diagnostics. '
                              'Candidate edits still refer to the original supplied source. Do not inspect evaluator files.\n' + json.dumps(completion))
            if session.failed: raise ValueError('Native/raw/config capture failed')
            verify(m); scope(cwd, m['git'][arm]); row.update(elapsed_seconds=time.perf_counter()-started, store_io=dict(store.metrics), source_sha256=sha(cwd / TARGET))
            save(path, result); print(json.dumps({'arm': arm, 'checks': row['checks'], 'usage': row['usage']}), flush=True)
        result['state'] = 'AWAITING_AUDIT'; save(path, result)
    except BaseException as exc:
        result.update(state='STOPPED_PENDING_AUDIT', error=repr(exc)); save(path, result); raise
    finally: observed_session.RPC = saved_rpc


if __name__ == '__main__':
    raise SystemExit('Superseded before inference: model-written final output required; see SUPERSEDED.md')
