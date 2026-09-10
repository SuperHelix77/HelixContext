"""Predeclared offline query variants, exact source closure and interface accounting."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('query_adapter',HERE/'adapter.py')
a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
VALID=HERE.with_name('native-output-v1')/'artifacts/astra-xhigh/on/workflow_memory.py'
BAD=HERE.with_name('differential-obligations-v1')/'artifacts/uncovered_query-source.py'
QUERIES=['unlisted_token','alpha','café','other evidence','a"b',
    "x'); __import__('pathlib').Path('QUERY_EXECUTED').touch(); #"]


def digest(raw):return hashlib.sha256(raw).hexdigest()


def calibrate(root):
    root=Path(root).resolve();root.mkdir(parents=True,exist_ok=False)
    started=time.perf_counter();cases=[]
    for n,q in enumerate(QUERIES):
        text=BAD.read_text();marker="if query=='unlisted_token':return []"
        assert text.count(marker)==1
        mutated=text.replace(marker,'if query=='+repr(q)+':return []').encode()
        p=root/f'candidate-{n}.py';p.write_bytes(mutated)
        for label,target,query,expected in [('target',p,q,9),('valid',VALID,q,0),('nontarget',p,'control_only',0)]:
            cases.append({'name':f'{n}-{label}','target':str(target),'query':query,'expected_failures':expected,
                          'target_sha256':a.sha(target)})
    files=[Path(__file__),Path(a.__file__),HERE/'DESIGN.md',HERE/'test_adapter.py',a.TEMPLATE,VALID,BAD]
    files += [root/f'candidate-{n}.py' for n in range(len(QUERIES))]
    manifest={'classification':'Constructed exposed offline cases, not model replication',
              'native_calls':0,'cases':cases,'files':{str(p):a.sha(p) for p in files}}
    a.save(root/'manifest.json',manifest);rows=[]
    for c in cases:
        assert a.sha(c['target'])==c['target_sha256']
        bound=a.bind(a.oblig.BASE/'TASK.md',a.oblig.BASE/'baseline/workflow_memory.py',c['target'])
        r=a.run({'query':c['query']},bound,root/c['name'])
        observed=r['observations']
        row={'case':c['name'],'query':c['query'],'source_sha256':c['target_sha256'],
             'contract_failures':observed['contract_failures'],'control_passes':observed['control_passes'],
             'expected_failures':c['expected_failures'],'seconds':r['seconds'],
             'execution_seconds':r['execution_seconds'],'copied_source_bytes':r['copied_source_bytes'],
             'retained_file_bytes_before_receipt':r['retained_file_bytes_before_receipt'],
             'program_sha256':r['program_sha256'],'stdout_sha256':r['stdout_sha256'],
             'query_text_not_executed':not (root/c['name']/'work/QUERY_EXECUTED').exists()}
        rows.append(row);a.save(root/'progress.json',rows)
        assert observed['contract_failures']==c['expected_failures'] and observed['control_passes']==9
        assert row['query_text_not_executed']
    for name,d in manifest['files'].items():assert a.sha(name)==d
    prior=HERE.with_name('astra-obligations-hostile-v1')
    native_root=Path('/Users/mert/Documents/ChatGPT/Helix/research/astra-resident-review-v1-20260910/native')
    native_raw=(native_root/'raw/raw-rollout.jsonl').read_bytes()
    audited=json.loads((prior/'AUDIT.json').read_text())
    assert digest(native_raw)==audited['raw_capture_sha256']
    payload=[]
    for line in native_raw.splitlines():
        e=json.loads(line);p=e.get('payload',{})
        if e.get('type')=='response_item' and p.get('type') in ('custom_tool_call','function_call'):
            v=p.get('input',p.get('arguments',''))
            if isinstance(v,str) and 'targeted_results' in v:payload.append(v)
    assert len(payload)==1
    (root/'native-tool-payload.txt').write_text(payload[0])
    request=json.dumps({'query':'unlisted_token'},separators=(',',':'))
    schema=json.dumps(a.SPEC,separators=(',',':'))
    a.save(root/'prospective-tool-spec.json',a.SPEC)
    import tiktoken
    enc=tiktoken.get_encoding('o200k_base')
    surfaces={'original_tool_payload':payload[0],'original_program':a.TEMPLATE.read_text(),
              'prospective_query_arguments':request,'prospective_tool_schema':schema}
    anatomy={k:{'bytes':len(v.encode()),'o200k_proxy_tokens':len(enc.encode(v))} for k,v in surfaces.items()}
    # Deliberately optimistic deletion arithmetic, not a realizable intervention.
    # The native final and all other segments remain unchanged; no control is used.
    u=audited['usage'];segment=json.loads((prior/'artifacts/usage.json').read_text())[2]
    deleting_segment={k:100*segment[v]/u[k] for k,v in [('input_tokens','inputTokens'),('output_tokens','outputTokens')]}
    result={'state':'OFFLINE_PASS','manifest_sha256':a.sha(root/'manifest.json'),'native_calls':0,
            'rows':rows,'seconds':time.perf_counter()-started,'surface_anatomy':anatomy,
            'proxy_tokenizer':'o200k_base, not the hosted Astra native tokenizer or billing receipt',
            'hypothetical_delete_whole_probe_segment_fraction_of_candidate_percent':deleting_segment,
            'native_saving_percent':None,'full_physical_io_bytes':None,
            'admission':'HOLD_NATIVE: local serialization reduction is not a whole-task 80/80 case; new query-choice/tool overhead and paired behavior unmeasured'}
    a.save(root/'RESULT.json',result)
    print(json.dumps({'state':result['state'],'cases':len(rows),'seconds':result['seconds'],
        'surface_anatomy':anatomy,'delete_whole_segment_only':deleting_segment,'native_calls':0},indent=2))


if __name__=='__main__':calibrate(sys.argv[1])
