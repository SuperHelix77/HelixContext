"""Offline qualified parameterization of an exact, previously model-written probe.

Only query data varies. Never calls a model, changes a final answer or declares
semantic correctness. Trusted research candidates only; not a Python sandbox.
"""
import ast
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import time
import tokenize

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE.with_name('astra-obligations-hostile-v1') / 'artifacts/probe.py'
TEMPLATE_SHA256 = '752282cfa7f354e98a11ceec540965a46f6706411f030990135d02809f7f7693'
spec = importlib.util.spec_from_file_location('query_obligations',
    HERE.with_name('differential-obligations-v1') / 'compare.py')
oblig = importlib.util.module_from_spec(spec); spec.loader.exec_module(oblig)
SPEC = {'type':'function','name':'helix_compare_search',
    'description':('Run the bound finite legacy-search witness for a query you choose. '
    'Compares reference and candidate on matching evidence, missing nonmatching index row, '
    'corrupted nonmatching source, default/all/any, and trailing-whitespace controls. '
    'Returns observed differences, not semantic approval. Other probes and normal tools remain available.'),
    'inputSchema':{'type':'object','properties':{'query':{'type':'string','minLength':1,'maxLength':128}},
                  'required':['query'],'additionalProperties':False}}


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p, obj): Path(p).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')


def compile_query(request):
    if not isinstance(request,dict) or set(request)!={'query'}:
        raise ValueError('One query field required')
    query = request['query']
    if type(query) is not str or not 1 <= len(query) <= 128 or len(query.encode()) > 256:
        raise ValueError('Unsupported query; ordinary tools remain available')
    source = TEMPLATE.read_bytes()
    if hashlib.sha256(source).hexdigest() != TEMPLATE_SHA256:
        raise ValueError('Unqualified probe program')
    text = source.decode(); lines = text.splitlines(keepends=True); edits = []
    replacement = {b'unlisted_token':query.encode(), 'unlisted_token':query, 'unlisted_token ':query+' '}
    for token in tokenize.tokenize(io.BytesIO(source).readline):
        if token.type != tokenize.STRING: continue
        value = ast.literal_eval(token.string)
        if value not in replacement: continue
        start = sum(map(len,lines[:token.start[0]-1]))+token.start[1]
        end = sum(map(len,lines[:token.end[0]-1]))+token.end[1]
        edits.append((start,end,repr(replacement[value])))
    if len(edits) != 5: raise ValueError('Probe literal structure changed')
    for start,end,new in reversed(edits): text = text[:start]+new+text[end:]
    ast.parse(text)  # No execution. Query values were encoded as Python literals.
    return text.encode()


def bind(task, before, candidate):
    if sha(task) != oblig.TASK_SHA256: raise ValueError('Unqualified task')
    b = oblig.binding(before,candidate)
    b['files'].update({str(Path(p).resolve()):sha(p) for p in (task,Path(__file__),TEMPLATE)})
    b['inputs'] = {k:str(Path(v).resolve()) for k,v in
        {'task':task,'before':before,'candidate':candidate,'evidence':oblig.BASE/'baseline/evidence.py'}.items()}
    return b


def observation(value):
    if not isinstance(value,dict) or set(value)!={'targeted_results','contract_failures','control_comparisons','control_passes'}:
        raise ValueError('Missing observation fields')
    rows = value['targeted_results']
    expected = {(s,m) for s in ('matching_evidence','missing_nonmatching_index_row','corrupt_nonmatching_source')
                for m in ('default','all','any')}
    if (not isinstance(rows,list) or len(rows)!=9 or
            {(r.get('scenario'),r.get('mode')) for r in rows} != expected or
            any(type(r.get('contract_holds')) is not bool for r in rows)):
        raise ValueError('Incomplete observations')
    if (type(value['contract_failures']) is not int or value['contract_failures'] != sum(not r['contract_holds'] for r in rows)
            or type(value['control_comparisons']) is not int or value['control_comparisons']!=9
            or type(value['control_passes']) is not int or not 0<=value['control_passes']<=9):
        raise ValueError('Inconsistent observations')
    return value


def run(request, binding, out, runner=subprocess.run):
    begin = time.perf_counter(); oblig.guard(binding)
    i = binding['inputs']
    if binding != bind(i['task'],i['before'],i['candidate']): raise ValueError('Incomplete caller binding')
    program = compile_query(request)
    out = Path(out); out.mkdir(parents=True,exist_ok=False)  # Durable no-retry ownership.
    save(out/'request.json',request); save(out/'binding.json',binding)
    (out/'program.py').write_bytes(program)
    result = {'state':'RUNNING','model_calls':0,'request_sha256':sha(out/'request.json'),
              'program_sha256':sha(out/'program.py'),'binding_sha256':sha(out/'binding.json')}
    save(out/'receipt.json',result)
    try:
        work = out/'work'; work.mkdir()
        for dest,key in [('before.py','before'),('workflow_memory.py','candidate'),('evidence.py','evidence')]:
            (work/dest).write_bytes(Path(i[key]).read_bytes())
            if sha(work/dest)!=binding['files'][i[key]]: raise ValueError('Copy binding changed')
        result['copied_source_bytes'] = sum(p.stat().st_size for p in work.iterdir())
        started = time.perf_counter()
        p = runner([sys.executable,'-B','-'],input=program,cwd=work,capture_output=True,timeout=30)
        result['execution_seconds'] = time.perf_counter()-started
        (out/'stdout').write_bytes(p.stdout); (out/'stderr').write_bytes(p.stderr)
        result.update(exit_status=p.returncode,stdout_sha256=sha(out/'stdout'),stderr_sha256=sha(out/'stderr'),
                      stdout_bytes=len(p.stdout),stderr_bytes=len(p.stderr))
        oblig.guard(binding)
        for dest,key in [('before.py','before'),('workflow_memory.py','candidate'),('evidence.py','evidence')]:
            if sha(work/dest)!=binding['files'][i[key]]: raise ValueError('Executed input copy changed')
        if p.returncode: raise ValueError('Procedure failed; no automatic rerun')
        value = observation(json.loads(p.stdout))
        result.update(state='OBSERVATIONS_RECORDED',observations=value,
                      semantic_adequacy='UNESTABLISHED; finite scope only')
    except BaseException as exc:
        if isinstance(exc,subprocess.TimeoutExpired):
            (out/'stdout').write_bytes(exc.stdout or b''); (out/'stderr').write_bytes(exc.stderr or b'')
            result.update(stdout_sha256=sha(out/'stdout'),stderr_sha256=sha(out/'stderr'),
                          stdout_bytes=(out/'stdout').stat().st_size,stderr_bytes=(out/'stderr').stat().st_size)
        result.update(state='FAILED_NO_VALID_OBSERVATIONS',error=repr(exc))
        raise
    finally:
        result['seconds'] = time.perf_counter()-begin
        result['retained_file_bytes_before_receipt'] = sum(p.stat().st_size for p in out.rglob('*') if p.is_file())
        result['full_physical_io'] = 'UNMEASURED'
        save(out/'receipt.json',result)
    return result
