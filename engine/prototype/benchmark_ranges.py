"""Deterministic I/O microbenchmark, not a model or intelligence benchmark."""
import hashlib,json,random,tempfile,time
from pathlib import Path
from evidence import Store
from line_index import build,retrieve


def run_case(raw, queries, count):
    with tempfile.TemporaryDirectory() as directory:
        root=Path(directory);plain=Store(root/'plain');indexed=Store(root/'indexed')
        source=plain.put(raw)['sha256'];indexed.put(raw)
        plain.metrics={k:0 for k in plain.metrics};indexed.metrics={k:0 for k in indexed.metrics}
        started=time.perf_counter();index=build(indexed,source);setup_seconds=time.perf_counter()-started
        setup=dict(indexed.metrics)
        answers=[];started=time.perf_counter()
        for line in queries[:count]:
            answers.append(plain.get(source).splitlines(keepends=True)[line-1])
        plain_seconds=time.perf_counter()-started
        started=time.perf_counter()
        for line,expected in zip(queries[:count],answers):
            actual,_=retrieve(indexed,index,source,line,line)
            assert actual==expected
        lookup_seconds=time.perf_counter()-started
        baseline=plain.metrics['object_bytes_read']+plain.metrics['object_bytes_written']
        total=indexed.metrics['object_bytes_read']+indexed.metrics['object_bytes_written']
        return {'queries':count,'exact_matches':count,'plain_io':dict(plain.metrics),'indexed_io_including_setup_and_verification':dict(indexed.metrics),'index_setup_io':setup,'application_read_plus_write_saving_fraction':1-total/baseline,'plain_wall_seconds':plain_seconds,'index_setup_wall_seconds':setup_seconds,'indexed_lookup_wall_seconds':lookup_seconds,'indexed_total_wall_seconds':setup_seconds+lookup_seconds,'original_storage_bytes_each_arm':len(raw),'extra_index_object_storage_bytes':sum(p.stat().st_size for p in (indexed.root/'objects').iterdir())-len(raw),'useful_returned_bytes':sum(map(len,answers))}


def main():
    raw=b''.join(f'{i:06d} value={hashlib.sha256(str(i).encode()).hexdigest()} marker={i%97:02d}\n'.encode() for i in range(50000))
    rng=random.Random(884219);queries=[rng.randint(1,50000) for _ in range(40)]
    result={'schema':'helix.range-microbenchmark.v1','source_sha256':hashlib.sha256(raw).hexdigest(),'source_bytes':len(raw),'seed':884219,'queries':queries,'geometry':{'chunk_bytes':16384,'fanout':16},'scope':'synthetic application I/O and observed wall time; no model calls, token savings, capability or physical SSD claim','accounting':'Both arms begin with one identical immutable original; indexed arm includes index construction and full reconstruction verification in every case. Extra index storage disclosed. Application read+write bytes are not monetary costs; hashing, parsing, CPU, memory and cache overlap must not be added as interchangeable units. SQLite, model and coordination costs are absent.','cases':[run_case(raw,queries,n) for n in (1,5,20,40)]}
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
