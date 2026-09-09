"""Deterministic recovery/cost falsifier, not a native model benchmark."""
import hashlib
import json
from pathlib import Path
import random
import sys
import tempfile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'prototype'))
from evidence import Store
from workflow_memory import Memory
import memory_epoch as epoch


def probe():
    with tempfile.TemporaryDirectory() as directory:
        store=Store(Path(directory));memory=Memory(store);refs=[];raws=[]
        for i in range(50):
            raw=f'observation {i:02d}; opaque receipt {hashlib.sha256(str(i).encode()).hexdigest()}; 000.{i:03d}\r\n'.encode()
            raws.append(raw);refs.append(memory.record('P','capture',str(i),raw)['record_hash'])
        frozen=epoch.freeze(memory,'P',refs)
        # Selection is supplied after freeze and cannot affect epoch contents.
        selected=random.Random(908).sample(range(50),7)
        with memory.db() as db:
            db.execute('DELETE FROM search');db.execute('DELETE FROM events')
        fresh=Memory(store)
        try:fresh.retrieve('P',[refs[selected[0]]]);old_failed=False
        except ValueError:old_failed=True
        before=dict(store.metrics)
        recovered=epoch.read(store,frozen['epoch_sha256'],'P',[refs[i] for i in selected])
        io={k:store.metrics[k]-before[k] for k in before}
        useful=sum(len(r['raw']) for r in recovered)
        exact=[r['raw'] for r in recovered]==[raws[i] for i in selected]
        assert old_failed and exact
        return {'classification':'deterministic engineering falsifier; no native model parity or savings claim',
                'events':50,'selected_after_freeze':selected,'old_indexed_retrieval_failed':old_failed,
                'epoch_exact_recovery_passed':exact,'freeze':frozen,'recovery_store_io':io,
                'useful_recovered_bytes':useful,'logical_read_amplification':io['object_bytes_read']/useful,
                'limits':['50 events are not 50 native turns','Caller must retain trusted epoch root and raw store',
                          'Coverage is caller-declared; omitted pre-freeze history is not detected',
                          'SQLite traffic, physical I/O, inference and billing unmeasured',
                          'Experimental caller API; not enabled by default'],
                'sources':{name:hashlib.sha256((Path(__file__).resolve().parents[1]/'prototype'/name).read_bytes()).hexdigest()
                           for name in ['memory_epoch.py','workflow_memory.py','evidence.py']}}

if __name__=='__main__':print(json.dumps(probe(),indent=2))
