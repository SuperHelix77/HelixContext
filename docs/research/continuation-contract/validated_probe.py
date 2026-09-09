"""Research callback: bound evidence validation plus arbitrary caller-authorized probes.
Trusted local execution only; not a sandbox, semantic acceptance or automatic retry.
"""
import os,subprocess,sys,time
from pathlib import Path
from prepared_review import validate,encoded,digest

def execute(evidence,expected_receipt,probe_source,out,*,timeout=30):
    out=Path(out).resolve();out.mkdir(parents=True,exist_ok=False)
    start=time.perf_counter();raw=probe_source.encode();(out/'probe.py').write_bytes(raw)
    row={'schema':'helix.validated-probe.research.v1','status':'STARTED','receipt_hash':expected_receipt,'probe_sha256':digest(raw),'probe_started':False,'semantic_acceptance':None,'unchecked':['semantic adequacy','general capability parity'],'cost':{'snapshot_bytes_written':0,'validation_seconds':0}}
    def publish():
        row['cost']['elapsed_seconds']=time.perf_counter()-start
        row['cost']['limits']='Explicit bytes and wall times only; validator/interpreter/OS I/O, inference and amortization excluded.'
        tmp=out/'result.tmp';tmp.write_bytes(encoded(row));os.replace(tmp,out/'result.json')
    publish()
    try:
        t=time.perf_counter();receipt=validate(evidence,expected_receipt);row['cost']['validation_seconds']+=time.perf_counter()-t
    except (OSError,ValueError,KeyError,TypeError) as e:
        row.update(status='EVIDENCE_INVALID_BEFORE_PROBE',error=type(e).__name__);publish();return row
    stage=out/'task';stage.mkdir();files={n:(Path(receipt['source'])/n).read_bytes() for n in receipt['input_roots']}
    if any(digest(b)!=receipt['input_roots'][n] for n,b in files.items()):
        row['status']='EVIDENCE_CHANGED_DURING_COPY';publish();return row
    files['queue_state.py']=files['proposal.py']
    for n,b in files.items():(stage/n).write_bytes(b)
    row['cost']['snapshot_bytes_written']=sum(map(len,files.values()))
    row['probe_started']=True;publish();t=time.perf_counter()
    try:
        p=subprocess.run([sys.executable,'-B',str(out/'probe.py')],cwd=stage,capture_output=True,timeout=timeout)
        stdout,stderr,code=p.stdout,p.stderr,p.returncode;outcome='PROBE_PASS' if code==0 else 'PROBE_FAIL'
    except subprocess.TimeoutExpired as e:
        stdout,stderr,code=e.stdout or b'',e.stderr or b'',None;outcome='PROBE_TIMEOUT'
    row['cost']['probe_seconds']=time.perf_counter()-t
    for name,data in [('stdout',stdout),('stderr',stderr)]:(out/(name+'.bin')).write_bytes(data);row[name+'_sha256']=digest(data)
    row.update(exit_code=code,status=outcome)
    row['cost']['raw_output_bytes']=len(stdout)+len(stderr)
    try:
        if (out/'probe.py').read_bytes()!=raw or any((stage/n).read_bytes()!=b for n,b in files.items()):raise ValueError('Probe altered bound input')
        t=time.perf_counter();validate(evidence,expected_receipt);row['cost']['validation_seconds']+=time.perf_counter()-t
    except (OSError,ValueError,KeyError,TypeError) as e:row.update(status='EVIDENCE_INVALID_AFTER_PROBE',error=type(e).__name__)
    publish();return row
