"""Zero-inference Astra trace and existing semantic-probe reuse falsifier.

Known development artifacts only. Preserves exact prior probe source; no generated
test oracle is fed to a model. An exit status certifies execution, not adequacy.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
PRIOR = HERE.with_name('native-output-v1')
BASE = HERE.with_name('maintenance-copy-v1')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def run(root):
    root = Path(root).resolve()
    root.mkdir(parents=True, exist_ok=False)
    prior = json.loads((PRIOR / 'artifacts/MANIFEST.json').read_text())
    for name, digest in prior['files'].items():
        if sha((PRIOR / 'artifacts' / name).read_bytes()) != digest:
            raise ValueError('Prior evidence drift: ' + name)
    anatomy_raw = (PRIOR / 'artifacts/ANATOMY.json').read_bytes()
    anatomy = json.loads(anatomy_raw)['astra-xhigh']
    rows = []
    for arm in anatomy:
        rows.append({'arm': arm['arm'], 'segments': [
            {'segment': i + 1, 'usage': s['usage'], 'operations': [
                {'kind': op['kind'], 'event': op['event'],
                 'command_sha256': sha(op['command'].encode()) if 'command' in op else None,
                 'command_bytes': len(op.get('command', '').encode()),
                 'returned_bytes': op.get('output_bytes')}
                for op in s['observable_operations']]}
            for i, s in enumerate(arm['segments'])]})
    candidate = next(a for a in rows if a['arm'] == 'on')
    control = next(a for a in rows if a['arm'] == 'off')
    # This is deliberately NOT a causal attribution or realizable prediction.
    # The mixed semantic-probe segment is retained in this trace-only ceiling.
    retained = [candidate['segments'][i]['usage'] for i in (1, 2, 3)]
    arithmetic = {}
    for key in ('inputTokens', 'outputTokens'):
        denominator = sum(s['usage'][key] for s in control['segments'])
        numerator = sum(s[key] for s in retained)
        arithmetic[key] = {'control': denominator, 'retained': numerator,
                           'conditional_saving_percent': 100 * (1 - numerator / denominator)}

    files = {n: (BASE / 'baseline' / n).read_bytes()
             for n in ('evidence.py', 'test_workflow_memory.py')}
    files['test_search_mode_public.py'] = (BASE / 'test_search_mode_public.py').read_bytes()
    valid = (PRIOR / 'artifacts/astra-xhigh/on/workflow_memory.py').read_bytes()
    original = (BASE / 'baseline/workflow_memory.py').read_bytes()
    probes = {arm: (PRIOR / 'artifacts/astra-xhigh' / arm / 'probe-1.py').read_bytes()
              for arm in ('off', 'on')}
    text = valid.decode()
    marker = "match=(' AND ' if match_mode=='all' else ' OR ').join('\"'+word+'\"' for word in words)"
    if text.count(marker) != 1:
        raise ValueError('Frozen mutation site changed')
    mutants = {
        'valid': valid,
        'original_missing_feature': original,
        'raw_fts_all': text.replace(marker, "match=query if match_mode=='all' else ' OR '.join('\"'+word+'\"' for word in words)").encode(),
        'ascii_tokenization': text.replace("flags=re.UNICODE", "flags=re.ASCII").encode(),
    }
    assert mutants['ascii_tokenization'] != valid
    manifest = {'classification': 'Known-source offline falsifier; no hosted inference',
                'audit_source_sha256': sha(Path(__file__).read_bytes()),
                'prior_manifest_sha256': sha((PRIOR / 'artifacts/MANIFEST.json').read_bytes()),
                'anatomy_sha256': sha(anatomy_raw),
                'target_sources': {n: sha(b) for n, b in mutants.items()},
                'protected_files': {n: sha(b) for n, b in files.items()},
                'exact_probe_sources': {n: sha(b) for n, b in probes.items()},
                'authority': 'Original maintenance task unchanged; test reuse does not establish semantic completeness',
                'task_sha256': sha((BASE / 'TASK.md').read_bytes()),
                'python_sha256': sha(Path(sys.executable).resolve().read_bytes())}
    save(root / 'manifest.json', manifest)
    cases = []
    start = time.perf_counter()
    for case, source in mutants.items():
        folder = root / case
        folder.mkdir()
        work = folder / 'work'
        work.mkdir()
        (work / 'workflow_memory.py').write_bytes(source)
        for name, raw in files.items():
            (work / name).write_bytes(raw)
        commands = [('public', [sys.executable, '-B', '-m', 'pytest', '-q',
                                '-p', 'no:cacheprovider'], None)]
        commands += [('prior_astra_' + arm, [sys.executable, '-B', '-'], raw)
                     for arm, raw in probes.items()]
        outcomes = []
        for name, argv, input_bytes in commands:
            begin = time.perf_counter()
            result = subprocess.run(argv, input=input_bytes, cwd=work,
                                    capture_output=True, timeout=45)
            elapsed = time.perf_counter() - begin
            (folder / (name + '.stdout')).write_bytes(result.stdout)
            (folder / (name + '.stderr')).write_bytes(result.stderr)
            outcomes.append({'name': name, 'exit_status': result.returncode,
                             'seconds': elapsed, 'stdout_bytes': len(result.stdout),
                             'stderr_bytes': len(result.stderr),
                             'stdout_sha256': sha(result.stdout), 'stderr_sha256': sha(result.stderr),
                             'exact_program_sha256': sha(input_bytes) if input_bytes else None})
            # Execution cannot silently rewrite its declared source/authority.
            assert (work / 'workflow_memory.py').read_bytes() == source
            assert all((work / n).read_bytes() == b for n, b in files.items())
        cases.append({'case': case, 'source_sha256': sha(source), 'executions': outcomes})
        save(root / 'progress.json', cases)
    by_name = {c['case']: c for c in cases}
    assert all(x['exit_status'] == 0 for x in by_name['valid']['executions'])
    assert all(x['exit_status'] != 0 for x in by_name['original_missing_feature']['executions'])
    # Do not assert that a chosen mutant escapes public tests: observe honestly.
    result = {'classification': 'Offline probe-reuse and trace audit; not native-token savings or capability parity',
              'native_model_calls': 0, 'prior_model': 'gpt-6-astra', 'prior_effort': 'xhigh',
              'trace': rows, 'delete_initial_reread_only': arithmetic,
              'mixed_probe_segment': {'input_tokens': 26032, 'output_tokens': 1187,
                                     'reported_reasoning_output_tokens': 516,
                                     'causal_token_attribution': 'UNKNOWN; code, interpretation and review mixed'},
              'probe_bytes_available_for_exact_reuse': sum(map(len, probes.values())),
              'cases': cases, 'elapsed_seconds': time.perf_counter() - start,
              'exact_sources_unchanged_after_execution': True,
              'storage_payload_bytes': sum(p.stat().st_size for p in root.rglob('*') if p.is_file()),
              'total_io_bytes': None, 'model_cost_saving': None,
              'limits': ['Historical probes already exposed; not new independent model replication.',
                         'Both future arms must have equal access to reusable regression tests.',
                         'Passing old probes cannot establish adequate current coverage or exclude unseen defects.',
                         'No hidden reasoning classification, no whole-segment deletion of semantic probes.',
                         'Mutation checks cover only the explicit defects and do not certify arbitrary code.']}
    save(root / 'result.json', result)
    save(HERE / 'OFFLINE.json', result)
    print(json.dumps({'native_model_calls': 0, 'cases': [
        {'case': c['case'], 'exits': [r['exit_status'] for r in c['executions']]}
        for c in cases], 'seconds': result['elapsed_seconds']}))


if __name__ == '__main__':
    run(sys.argv[1])
