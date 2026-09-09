"""Deterministic, evidence-bound report assembly; never supplies a semantic answer."""
import difflib
import hashlib
import json
import os
from pathlib import Path
import time


def publish(path, *, before, after, assessment, unresolved, grade, stdout, stderr):
    start=time.perf_counter()
    if grade.get('exit_code')!=0 or stdout!=b'PASS 2745 sequences / 8282 transitions\n' or stderr:
        raise ValueError('Complete checker receipt absent')
    if not isinstance(assessment,str) or not assessment.strip() or unresolved!=[]:
        raise ValueError('Semantic assessment or closure absent')
    for key,raw in [('stdout_sha256',stdout),('stderr_sha256',stderr)]:
        if grade.get(key)!=hashlib.sha256(raw).hexdigest():raise ValueError('Checker receipt hash mismatch')
    report={'schema':'helix.research.delivery.v1','assessment':assessment,'unresolved':unresolved,
        'artifact_sha256':hashlib.sha256(after).hexdigest(),
        'diff':''.join(difflib.unified_diff(before.decode().splitlines(keepends=True),after.decode().splitlines(keepends=True),fromfile='before/queue_state.py',tofile='after/queue_state.py')),
        'verification':{'exit_code':0,'stdout':stdout.decode(),'stderr':stderr.decode(),'receipt':grade},
        'scope':'Finite task checks; not universal semantic or workflow parity.'}
    raw=(json.dumps(report,indent=2)+'\n').encode();path=Path(path)
    if path.exists():raise ValueError('Delivery already published')
    temporary=path.with_suffix('.pending');temporary.write_bytes(raw);os.replace(temporary,path)
    return {'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'seconds':time.perf_counter()-start,
            'logical_bytes_written':len(raw),'physical_io':'unmeasured','inference_calls':0}
