"""Research-only pre-executed review evidence for trusted local Python fixtures.
Not a sandbox, semantic verifier, production publisher or complete environment closure.
"""
import hashlib,json,os,platform,subprocess,sys,time
from pathlib import Path

class InvalidEvidence(ValueError):pass

def digest(b):return hashlib.sha256(b).hexdigest()
def encoded(x):return (json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode()
def files_at(root):
    names=('proposal.py','CONTRACT.md','check.py','check_independence.py','supplemental.py')
    return {n:(Path(root)/n).read_bytes() for n in names}
def roots(files):return {n:digest(b) for n,b in files.items()}
def runtime():return {'python':sys.version,'platform':platform.platform(),'executable':str(Path(sys.executable).resolve())}

def prepare(source,out):
    start=time.perf_counter();source=Path(source).resolve();out=Path(out).resolve()
    out.mkdir(parents=True,exist_ok=False) # existing attempts are never rerun
    original=files_at(source);bound=roots(original);rt=runtime()
    receipt={'schema':'helix.prepared-review.research.v1','status':'INCOMPLETE','source':str(source),'input_roots':bound,'runtime':rt,'checks':[],'unchecked':['semantic correctness','checker adequacy','undeclared dependencies','general capability parity'],'cost':{'logical_source_bytes_read':sum(map(len,original.values())),'snapshot_bytes_written':0,'raw_output_bytes':0}}
    # Persist incomplete state before execution; never present it as valid PASS.
    (out/'attempt.json').write_bytes(encoded(receipt))
    for name in ('check.py','check_independence.py','supplemental.py'):
        stage=out/name.removesuffix('.py');stage.mkdir()
        stage_files={**original,'queue_state.py':original['proposal.py']}
        for n,b in stage_files.items():(stage/n).write_bytes(b)
        receipt['cost']['snapshot_bytes_written']+=sum(map(len,stage_files.values()))
        argv=[sys.executable,'-B',name,'queue_state.py'];t=time.perf_counter()
        try:
            p=subprocess.run(argv,cwd=stage,capture_output=True,timeout=30)
            stdout,stderr,code=p.stdout,p.stderr,p.returncode;status='PASS' if code==0 else 'FAIL'
        except subprocess.TimeoutExpired as exc:
            stdout,stderr,code=exc.stdout or b'',exc.stderr or b'',None;status='TIMEOUT'
        for stream,data in [('stdout',stdout),('stderr',stderr)]: (stage/(stream+'.bin')).write_bytes(data)
        intact=all((stage/n).read_bytes()==b for n,b in stage_files.items())
        receipt['checks'].append({'name':name,'status':status if intact else 'MUTATED_INPUT','exit_code':code,'argv':argv,'cwd':str(stage),'seconds':time.perf_counter()-t,'stdout_sha256':digest(stdout),'stderr_sha256':digest(stderr)})
        receipt['cost']['raw_output_bytes']+=len(stdout)+len(stderr)
        receipt['cost']['logical_source_bytes_read']+=sum(map(len,stage_files.values()))
        (out/'attempt.json').write_bytes(encoded(receipt))
        if status!='PASS' or not intact:break
    current=files_at(source);receipt['cost']['logical_source_bytes_read']+=sum(map(len,current.values()))
    receipt['status']='READY' if roots(current)==bound and len(receipt['checks'])==3 and all(c['status']=='PASS' for c in receipt['checks']) and runtime()==rt else 'NOT_READY'
    receipt['cost']['prepare_seconds']=time.perf_counter()-start
    receipt['cost']['limits']='Logical explicit reads/writes only; not total OS I/O, process memory, dollar cost or model tokens.'
    data=encoded(receipt);tmp=out/'receipt.tmp';tmp.write_bytes(data);os.replace(tmp,out/'receipt.json')
    return digest(data)

def validate(out,expected_hash):
    out=Path(out);data=(out/'receipt.json').read_bytes()
    if digest(data)!=expected_hash:raise InvalidEvidence('Receipt identity changed')
    r=json.loads(data)
    if r['status']!='READY':raise InvalidEvidence('Checks incomplete, failed or inputs changed')
    if roots(files_at(r['source']))!=r['input_roots'] or runtime()!=r['runtime']:raise InvalidEvidence('Stale source or runtime')
    for c in r['checks']:
        stage=Path(c['cwd'])
        for n,h in r['input_roots'].items():
            if digest((stage/n).read_bytes())!=h:raise InvalidEvidence('Stale snapshot')
        if digest((stage/'queue_state.py').read_bytes())!=r['input_roots']['proposal.py']:raise InvalidEvidence('Stale staged proposal')
        for stream in ('stdout','stderr'):
            if digest((stage/(stream+'.bin')).read_bytes())!=c[stream+'_sha256']:raise InvalidEvidence('Tampered output')
    return r

if __name__=='__main__':print(prepare(*sys.argv[1:]))
