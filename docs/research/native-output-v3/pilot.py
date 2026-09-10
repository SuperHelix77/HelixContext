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
sys.path[:0] = [str(HERE.with_name('native-output-v1')), str(REPO / 'engine/output'), str(REPO / 'engine/prototype'), str(HERE.parent / 'continuation-contract')]
import effort_session as observed_session
import effort_session as native
from dynamic_tool_rpc import rpc_type
from indexed_tool import IndexedEditTool as BoundEditTool, SPEC, scope_snapshot
from indexed_source import render
import caller_memory_receipt as memory
import caller_registration
import project_registration_preflight as registration
import luna_varied_coding_v2 as workspace
from evidence import Store
from indexed_edits import compile_edits
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


def prepare(root):
    begin = time.perf_counter(); root = Path(root).resolve(); root.mkdir(parents=True, exist_ok=False)
    inputs = {n: (INPUT / 'baseline' / n).read_bytes() for n in FILES[:3]}
    inputs[FILES[-1]] = (INPUT / FILES[-1]).read_bytes()
    order = ['off', 'on']; secrets.SystemRandom().shuffle(order)
    catalog = json.loads(subprocess.check_output([str(CLI), 'debug', 'models']))['models']
    default = next(r['base_instructions'] for r in catalog if r['slug'] == MODEL)
    m = {'model': MODEL, 'effort': EFFORT, 'order': order, 'max_semantic_turns_per_arm': 2,
         'blind_retries': 0, 'classification': 'V3 fresh known maintenance task; indexed edits + scoped hot source + observed scope. No model/cohort qualification.', 'source_presentation': 'complete_target_indexed_v1', 'review_receipt': 'bound_diff_and_scope_v1', 'edit_interface': 'indexed_lines_v1', 'cold_files': FILES[1:],
         'inputs': {n: hashlib.sha256(raw).hexdigest() for n, raw in inputs.items()}, 'git': {}, 'registration': {},
         'default_base_sha256': hashlib.sha256(default.encode()).hexdigest(), 'base_file': str(BASE)}
    frozen = [Path(__file__), HERE / 'audit_native.py', HERE / 'checked_tool.py', HERE / 'indexed_tool.py', HERE / 'test_indexed_tool.py', REPO / 'engine/prototype/indexed_source.py', REPO / 'engine/prototype/indexed_edits.py', HERE / 'PREREG.md', HERE / 'FROZEN.json', INPUT / 'TASK.md', INPUT / 'oracle.py', INPUT / 'OFFLINE_CALIBRATION.json',
              INPUT / 'BASELINE_MANIFEST.json', BASE, CLI, Path('/Users/mert/.codex/AGENTS.md'), memory.CLIENT]
    frozen += [Path(x.__file__) for x in (observed_session, native, memory, caller_registration, registration, workspace, renderer)]
    frozen += [REPO / 'engine/prototype' / n for n in ('literal_edits.py', 'indexed_edits.py', 'indexed_source.py', 'evidence.py')]
    frozen += [REPO / 'engine/output' / n for n in ('app_server_native.py', 'raw_receipts.py')]
    frozen += [Path(observed_session.HELPER), REPO / 'engine/output/dynamic_tool_rpc.py', REPO / 'engine/output/config_bound_session.py']
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
                  'Ordinary tools and semantic review remain available. Caller independently checks the final artifact. The available test entrypoint is python3 -m pytest. '
                  'Finish with your normal prose/code report of the change, actual check status and outstanding issues; do not substitute operation JSON for the final answer.\n' + (INPUT / 'TASK.md').read_text())
        if arm == 'on':
            common += ('\nCaller attached helix_apply_edits before inference. The current source version is 0. '
                       'Use this internal tool when appropriate for exact edits, staging, required checks and publication. '
                       'You own implementation, semantic review and adequacy. Ordinary tools remain available. '
                       'The tool returns actual execution results; afterward write your normal final prose/code answer. '
                       'Do not return an edit operation or selector as the final answer. '
                       'If evidence or authority is insufficient, explain what is missing.\nComplete current edit target and exact cold-file inventory:\n' +
                       render(inputs, [TARGET], version=0)[0])
            snapshot = scope_snapshot(cwd, FILES)
            save(root / 'on-initial-scope.json', snapshot)
            common += '\nCaller preflight: ' + json.dumps({
                'cwd':snapshot['cwd'], 'head':snapshot['head'], 'status_z':snapshot['status_z'],
                'diff_check_exit':snapshot['diff_check_exit'], 'protected_paths':FILES[1:],
                'source_sha256':m['inputs'][TARGET], 'version':0,
                'required_checks':'23 public/regression tests and 94 independent finite cases',
                'binding':'Caller validates current source, Git HEAD and protected files before applying an edit; results include observed scope. No semantic completeness claim.'})
            frozen.append(root / 'on-initial-scope.json')
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
    root = Path(root).resolve(); m = json.loads((root / 'manifest.json').read_text())
    configure(m['model'], m['effort']); verify(m)
    path = root / 'results.json'
    if path.exists(): raise ValueError('No restart/retry')
    manifest_hash = sha(root / 'manifest.json')
    result = {'state': 'RUNNING', 'manifest_sha256': manifest_hash, 'rows': []}; save(path, result)
    original_rpc = observed_session.RPC
    try:
        for arm in m['order']:
            original(root, m, arm); cwd = root / arm
            assert workspace.git(cwd, 'status', '--porcelain=v1', '--untracked-files=all') == ''
            row = {'arm': arm, 'turns': []}; result['rows'].append(row); save(path, result)
            started = time.perf_counter(); tool = None
            if arm == 'on':
                def authority():
                    verify(m); scope(cwd, m['git'][arm]); return manifest_hash
                def check_output(raw, directory):
                    directory.mkdir(); stage = directory / 'stage'; stage.mkdir()
                    for name in FILES: (stage / name).write_bytes(raw if name == TARGET else (cwd / name).read_bytes())
                    check = grade(stage, directory / 'checks')
                    if check['checks'] == 'PASS': check['summary'] = '23 public/regression tests and 94 independent finite cases passed'
                    return check
                tool = BoundEditTool(root / 'on-tool', cwd / TARGET, (cwd / TARGET).read_bytes(),
                                     authority, check_output, expected_binding=manifest_hash,
                                     scope_observer=lambda: scope_snapshot(cwd, FILES))
                ToolRPC = rpc_type([SPEC], tool)
                class KernelRPC(ToolRPC):
                    def call(self, method, params):
                        if method == 'thread/start': params = {**params, 'config': {**params['config'], 'model_instructions_file': str(BASE)}}
                        return super().call(method, params)
                observed_session.RPC = KernelRPC
            else: observed_session.RPC = original_rpc
            skill = cwd / '.agents/skills/helixcontext/SKILL.md' if arm == 'on' else None
            with native.Session(MODEL, cwd, root / (arm+'-run'), skill, effort=EFFORT) as session:
                prompt = (root / (arm+'-prompt.txt')).read_text()
                if arm == 'on': prompt = caller_registration.attach(session, prompt)
                for index in range(1,3):
                    answer, turn = session.turn(prompt)
                    attempt = {'answer': answer, 'native': turn}; row['turns'].append(attempt)
                    row['usage'] = dict(session.total); save(path, result)
                    verify(m); scope(cwd, m['git'][arm])
                    completion = grade(cwd, root / (arm+'-check-'+str(index)))
                    attempt['completion'] = completion; row['checks'] = completion['checks']; save(path, result)
                    if row['checks'] == 'PASS': break
                    prompt = 'Caller final artifact checks failed. Retain ordinary final-answer structure. Reconsider actual diagnostics; other-run/evaluator files stay out of scope.\n'+json.dumps(completion)
            if session.failed: raise ValueError('Native capture/config failed')
            verify(m); scope(cwd, m['git'][arm])
            row.update(elapsed_seconds=time.perf_counter()-started, source_sha256=sha(cwd/TARGET),
                       store_io=dict(tool.store.metrics) if tool else {},
                       final_answer_contract='Model-native prose/code; exact content requires answer audit')
            save(path,result); print(json.dumps({'model':MODEL,'effort':EFFORT,'arm':arm,'checks':row['checks'],'usage':row['usage']}),flush=True)
        result['state']='AWAITING_AUDIT';save(path,result)
    except BaseException as exc:
        result.update(state='STOPPED_PENDING_AUDIT',error=repr(exc));save(path,result);raise
    finally: observed_session.RPC=original_rpc


if __name__ == '__main__':
    if sys.argv[1] == 'prepare': configure(sys.argv[3],sys.argv[4]);prepare(sys.argv[2])
    elif sys.argv[1] == 'run':run(sys.argv[2])
    else:raise ValueError('Unknown action')
