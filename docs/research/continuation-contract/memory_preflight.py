"""Exercise existing cold storage with versioned contract evidence. No new memory code."""
import hashlib
import json
from pathlib import Path
import sys
import time

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[2]/'engine/prototype'))
from evidence import Store
from workflow_memory import Memory
import memory_epoch as epoch

def sha(raw):return hashlib.sha256(raw).hexdigest()


def run(directory):
    directory=Path(directory).resolve();directory.mkdir(parents=True,exist_ok=False)
    memory=Memory(Store(directory));started=time.perf_counter();raw= (HERE/'CONTRACT.md').read_bytes()
    ref=memory.record('continuation','early','contract-v1',raw)['record_hash'];refs=[ref]
    for n in range(39):
        refs.append(memory.record('continuation','intervening',str(n),f'completed observation {n:02d}\n'.encode())['record_hash'])
    old=epoch.freeze(memory,'continuation',refs)
    # Introduced after capture; an additional public limit invalidates old semantic conclusions.
    current=raw+b'\nVersion 2 amendment: batches containing more than two new values raise ValueError with call-entry state unchanged.\n'
    newref=memory.record('continuation','later','contract-v2',current)['record_hash']
    new=epoch.freeze(memory,'continuation',refs+[newref])
    with memory.db() as db:
        db.execute('DELETE FROM search');db.execute('DELETE FROM events')
    fresh=Memory(Store(directory));before=dict(fresh.store.metrics)
    old_bytes=epoch.read(fresh.store,old['epoch_sha256'],'continuation',[ref])[0]['raw']
    io={k:fresh.store.metrics[k]-before[k] for k in before}
    rejected=False
    try:epoch.read(fresh.store,old['epoch_sha256'],'continuation',[newref])
    except ValueError:rejected=True
    new_bytes=epoch.read(fresh.store,new['epoch_sha256'],'continuation',[newref])[0]['raw']
    assertions={'old_exact_after_index_loss':old_bytes==raw,'new_exact_after_index_loss':new_bytes==current,
        'old_epoch_excludes_future_record':rejected,'different_authority_roots':sha(old_bytes)!=sha(new_bytes),
        'index_not_silently_rebuilt':fresh.timeline('continuation','early')==[]}
    assert all(assertions.values())
    result={'classification':'OFFLINE_RECOVERY_ONLY','native_calls':0,'assertions':assertions,
        'old_contract_sha256':sha(raw),'new_contract_sha256':sha(current),
        'old_epoch':old['epoch_sha256'],'new_epoch':new['epoch_sha256'],
        'old_read_store_io':io,'useful_old_evidence_bytes':len(raw),
        'old_freeze':old,'new_freeze':new,'seconds':time.perf_counter()-started,
        'source_hashes':{p.name:sha(p.read_bytes()) for p in [HERE/'memory_preflight.py',Path(epoch.__file__),HERE.parents[2]/'engine/prototype/workflow_memory.py',HERE.parents[2]/'engine/prototype/evidence.py']},
        'limits':['No model relevance selection or automatic authority invalidation tested',
                  'No production admission, continuation executor or compaction restoration claim',
                  'Logical Store I/O only; SQLite, physical I/O, storage cost and coordinator inference not fully accounted']}
    (HERE/'MEMORY_RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':run(sys.argv[1])
