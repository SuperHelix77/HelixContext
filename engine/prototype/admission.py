"""Caller-owned admission before optimization preparation. No inference.

Qualification is trusted caller configuration, never a model-supplied document.
This gate does not infer task similarity or turn finite checks into general parity.
It selects a callback once; failures after execution begins propagate, not rerun.
"""
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import time


@dataclass(frozen=True)
class Request:
    model: str
    effort: str
    contract_hash: str
    mode: str = 'production'


def encode(value):return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def sha(raw):return hashlib.sha256(raw).hexdigest()


def decide(request,*,qualification=None,repo=None):
    start=time.perf_counter();read_bytes=0;read_ops=0
    def receipt(route,reason):
        return {'schema':'helix.admission.v1','route':route,'reason':reason,
                'request':dict(vars(request)),'logical_bytes_read':read_bytes,'read_operations':read_ops,
                'seconds':time.perf_counter()-start,'savings_claim':None,
                'scope':'Admission only; not native token, billing, physical I/O or parity measurement.'}
    # No file reads or optimization setup for unsupported/production requests.
    if request.mode!='qualified_fixture_research':return receipt('native','No production qualification established')
    if not isinstance(qualification,dict):return receipt('native','No exact research qualification')
    if any(qualification.get(k)!=getattr(request,k) for k in ('model','effort','contract_hash')):
        return receipt('native','Model, effort or exact task contract mismatch')
    if qualification.get('scope')!='finite_fixture_only':return receipt('native','Unsupported qualification scope')
    try:
        root=Path(repo).resolve()
        def verified(relative,expected):
            nonlocal read_bytes,read_ops
            path=(root/relative).resolve()
            if not path.is_relative_to(root):raise ValueError('Binding escapes repository')
            raw=path.read_bytes();read_bytes+=len(raw);read_ops+=1
            if sha(raw)!=expected:raise ValueError('Binding changed')
            return raw
        # The small qualification maps exact task contract to a pinned profile.
        profile=json.loads(verified(qualification['profile'],qualification['profile_sha256']))
        if not isinstance(profile,dict):raise ValueError('Invalid profile object')
        if profile.get('model')!=request.model or profile.get('effort')!=request.effort or profile.get('frozen') is not True:
            raise ValueError('Profile identity or freeze mismatch')
        evidence_path=str(Path(qualification['profile']).parent/profile['evidence'])
        evidence=json.loads(verified(evidence_path,profile['evidence_sha256']))
        rows=evidence['rows']
        if len(rows)!=2 or {r['arm'] for r in rows}!={'off','on'}:raise ValueError('Invalid paired evidence')
        arms={r['arm']:r for r in rows}
        for row in rows:
            if row.get('artifact_exact') is not True or row.get('source_unchanged') is not True or row.get('passed') is not True:
                raise ValueError('Finite checks not established')
        for key in ('input_tokens','output_tokens'):
            off=arms['off']['usage'][key];on=arms['on']['usage'][key]
            if type(off) is not int or type(on) is not int or off<=0 or on<0 or on*5>off:
                raise ValueError('Separate native 80 percent gate not met')
        bindings=profile['source_hashes']
        if not isinstance(bindings,dict) or not bindings:raise ValueError('Missing implementation closure')
        for path,digest in bindings.items():verified(path,digest)
    except (OSError,ValueError,KeyError,TypeError) as exc:
        return receipt('native','Qualification invalid: '+type(exc).__name__)
    return receipt('optimized','Exact frozen research qualification only; general parity remains open')


def dispatch(request,payload,*,native,optimized,qualification=None,repo=None):
    decision=decide(request,qualification=qualification,repo=repo)
    # Payload, model/effort and required workflow are not rewritten by admission.
    # Deliberately no catch-and-retry: optimized may already have side effects.
    result=(optimized if decision['route']=='optimized' else native)(request,payload)
    return result,decision
