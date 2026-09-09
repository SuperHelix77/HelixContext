"""Deterministic I/O comparison, not a model or physical disk benchmark."""
import json,tempfile
from evidence import Store
from pathlib import Path


def measure():
 with tempfile.TemporaryDirectory() as root:
  s=Store(root);raw=b''.join(f'line {i:06d} exact 000.250 payload\n'.encode() for i in range(100000))
  source=s.put(raw);key=s.put(json.dumps({'stdout':source}).encode())['sha256']
  rows=[]
  for count in (1,5,20):
   spans=[(i*4000+1,i*4000+2) for i in range(count)]
   separate=Store(root);expected=[separate.retrieve(key,start=a,end=b) for a,b in spans]
   batch=Store(root);got=batch.retrieve_many(key,spans)
   assert [(r['text'],r['sha256']) for r in expected]==[(r['text'],r['sha256']) for r in got['spans']]
   rows.append(dict(ranges=count,exact=True,separate_io=separate.metrics,batch_io=batch.metrics,application_read_saving=1-batch.metrics['object_bytes_read']/separate.metrics['object_bytes_read']))
  return dict(scope='Synthetic range retrieval only. No native token savings, reasoning parity, physical disk or CPU claim. Full source is still read and verified per batch. Setup excluded symmetrically; no persistent cache or index added.',source_bytes=len(raw),rows=rows)

if __name__=='__main__':
 Path(__file__).with_name('batch-results.json').write_text(json.dumps(measure(),indent=2)+'\n')
