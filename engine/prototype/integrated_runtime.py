"""Caller-owned integration. No inference, command rewriting or automatic retry.

Independent immutable policy; exact cold recovery survives process restart.
Scope names are logical partitions, not access-control boundaries.
"""
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import time

from evidence import Store
from workflow_memory import Memory, identity
import reducer_runtime
import copy_handles

VERSION='helix.integrated.v1'


def encode(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def sha(raw):return hashlib.sha256(raw).hexdigest()


@dataclass(frozen=True)
class Policy:
    memory:bool=True
    reducers:bool=True
    completion:bool=True
    cold_plans:bool=False
    version:str=VERSION

    def __post_init__(self):
        if any(type(getattr(self,k)) is not bool for k in ('memory','reducers','completion','cold_plans')):raise ValueError('Boolean switches required')
        if self.cold_plans or self.version!=VERSION:raise ValueError('Unsupported policy')


class Runtime:
    def __init__(self,root,project,branch,session,policy=Policy()):
        identity(project,branch,session)
        self.store=Store(root);self.memory=Memory(self.store);self.policy=policy
        self.scope=encode([project,branch]).decode();self.session=session
        self.policy_ref=self.store.put(encode({'policy':asdict(policy),'components':self.components()}))['sha256']

    @staticmethod
    def components():
        base=Path(__file__).parent
        return {name:sha((base/name).read_bytes()) for name in ('integrated_runtime.py','workflow_memory.py','reducer_runtime.py','evidence.py','verification.py','copy_handles.py','renderer.py')}

    def event(self,kind,value):
        # Evidence objects are immutable; append publication is locked and fsynced.
        import fcntl
        raw=encode(value);ref=self.store.put(raw)['sha256']
        event={'schema':'helix.engine.event.v1','timestamp':datetime.now(timezone.utc).isoformat(),
               'type':kind,'policy_ref':self.policy_ref,'evidence_ref':ref,'scope':self.scope,'session':self.session}
        with (self.store.root/'events.jsonl').open('ab') as out:
            fcntl.flock(out,fcntl.LOCK_EX);out.write(encode(event)+b'\n');out.flush();os.fsync(out.fileno())
        return ref

    def record(self,event_id,raw):
        start=time.perf_counter();before=dict(self.store.metrics)
        record=self.memory.record(self.scope,self.session,event_id,raw)
        self.event('memory.record',{'record':record,'seconds':time.perf_counter()-start,'store_io':self.delta(before)})
        return record

    def delta(self,before):return {k:self.store.metrics[k]-before[k] for k in before}

    def search(self,query,limit=10):
        start=time.perf_counter();before=dict(self.store.metrics)
        refs=self.memory.search(self.scope,query,limit)
        self.event('memory.search',{'query':query,'records':refs,'seconds':time.perf_counter()-start,'store_io':self.delta(before),
                                  'memory_metrics':dict(self.memory.metrics),'complete':False})
        return refs

    def retrieve(self,refs,max_bytes=1048576):
        start=time.perf_counter();before=dict(self.store.metrics)
        records=self.memory.retrieve(self.scope,refs,max_bytes)
        self.event('memory.retrieve',{'refs':refs,'useful_bytes':sum(len(r['raw']) for r in records),
                                     'seconds':time.perf_counter()-start,'store_io':self.delta(before)})
        return records

    def working_set(self,query,history_refs,max_bytes=1048576):
        # Explicit caller-pinned history is exhaustive fallback; a lexical miss
        # is never represented as proof that no relevant evidence exists.
        if self.policy.memory:
            selected={r['record_hash'] for r in self.search(query,limit=100)}
            refs=[ref for ref in history_refs if ref in selected]
        else:refs=history_refs
        records=self.retrieve(refs,max_bytes) if refs else []
        return {'records':records,'all_history_refs':history_refs,'coverage':'partial literal selection' if self.policy.memory else 'complete supplied history',
                'recovery_required':self.policy.memory and not refs}

    def checkpoint(self,objective,skills,decisions,refs):
        """Caller supplies authoritative state; references are scoped and verified.

        Skill bodies stay exact and version bound; this is explicit restoration,
        not a claim to intercept Codex's private compaction machinery.
        """
        if not isinstance(objective,str) or not isinstance(decisions,list) or not isinstance(skills,dict):raise ValueError('Invalid state')
        if refs:self.retrieve(refs)
        skill_refs={}
        for name,raw in skills.items():
            identity(name)
            if not isinstance(raw,bytes):raise ValueError('Exact skill bytes required')
            skill_refs[name]=self.store.put(raw)['sha256']
        value={'schema':'helix.checkpoint.v1','scope':self.scope,'policy_ref':self.policy_ref,
               'objective':objective,'decisions':decisions,'skills':skill_refs,'refs':refs}
        return self.event('checkpoint',value)

    def restore(self,ref):
        value=json.loads(self.store.get(ref))
        if value.get('schema')!='helix.checkpoint.v1' or value.get('scope')!=self.scope or value.get('policy_ref')!=self.policy_ref:raise ValueError('Checkpoint scope or policy changed')
        skills={name:self.store.get(key) for name,key in value['skills'].items()}
        records=self.retrieve(value['refs']) if value['refs'] else []
        self.event('checkpoint.restored',{'checkpoint':ref,'skill_hashes':value['skills'],'records':len(records)})
        return {'state':value,'skills':skills,'records':records}

    def command(self,argv,cwd,environment_id,**options):
        result=reducer_runtime.execute(self.store,argv,cwd,environment_id,enabled=self.policy.reducers,**options)
        result['operation_receipt']=self.event('command.completed',result)
        return result

    def complete(self,catalog,response,destination,expected_sha256=None):
        if not self.policy.completion:raise ValueError('Caller completion disabled')
        start=time.perf_counter();before=dict(self.store.metrics)
        result=copy_handles.complete_response(self.store,catalog,response,destination,expected_sha256=expected_sha256)
        result.update(caller_seconds=time.perf_counter()-start,store_io=self.delta(before))
        result['operation_receipt']=self.event('completion',result)
        return result

    def accounting(self):
        paths=[p for p in self.store.root.rglob('*') if p.is_file()]
        return {'store_logical_io':dict(self.store.metrics),'memory':dict(self.memory.metrics),
                'retained_file_bytes':sum(p.stat().st_size for p in paths),'files':len(paths),
                'unmeasured':['physical I/O','SQLite I/O traffic','money','parent research tokens'],
                'note':'Retained bytes are physical file lengths, not allocated disk blocks; model tokens are separate native receipts.'}
