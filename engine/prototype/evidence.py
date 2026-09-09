#!/usr/bin/env python3
"""Lossless raw evidence with bounded, explicitly partial model-facing projections."""
import argparse,base64,hashlib,json,os,re,shutil,signal,subprocess,tempfile,time,sys,uuid
from pathlib import Path

def digest(b):return hashlib.sha256(b).hexdigest()
class Store:
 def __init__(self,root):
  self.root=Path(root).resolve();(self.root/'objects').mkdir(parents=True,exist_ok=True)
  self.metrics={'object_bytes_read':0,'object_bytes_written':0,'object_bytes_hashed':0,'object_read_operations':0,'staging_bytes_read':0,'staging_bytes_written':0,'projection_bytes_parsed':0}
 def put(self,data):
  key=digest(data);self.metrics['object_bytes_hashed']+=len(data);p=self.root/'objects'/key
  if p.exists():
   existing=p.read_bytes();self.metrics['object_bytes_read']+=len(existing);self.metrics['object_read_operations']+=1;self.metrics['object_bytes_hashed']+=len(existing)
   if digest(existing)!=key:raise ValueError('Existing evidence object is corrupt')
  else:
   fd,tmp=tempfile.mkstemp(dir=p.parent)
   try:
    with os.fdopen(fd,'wb') as f:f.write(data);f.flush();os.fsync(f.fileno())
    os.replace(tmp,p);self.metrics['object_bytes_written']+=len(data)
   finally:
    if os.path.exists(tmp):os.unlink(tmp)
  return {'sha256':key,'bytes':len(data)}
 def get(self,key):
  if not re.fullmatch('[0-9a-f]{64}',key):raise ValueError('Invalid evidence digest')
  b=(self.root/'objects'/key).read_bytes();self.metrics['object_bytes_read']+=len(b);self.metrics['object_read_operations']+=1;self.metrics['object_bytes_hashed']+=len(b)
  if digest(b)!=key:raise ValueError('Evidence hash mismatch; do not trust the projection')
  return b
 def receipt(self,key):return json.loads(self.get(key))
 def retrieve_many(self,key,ranges,stream='stdout'):
  """Retrieve ordered inclusive spans from one freshly verified source snapshot."""
  if stream not in ('stdout','stderr'):raise ValueError('Invalid evidence stream')
  if not ranges:raise ValueError('At least one range is required')
  for start,end in ranges:
   if type(start) is not int or type(end) is not int or start<1 or end<start:raise ValueError('Invalid 1-based inclusive line range')
  receipt=self.receipt(key);source=receipt[stream];raw=self.get(source['sha256'])
  lines=raw.splitlines(keepends=True)
  # Reject the entire batch if any requested span is outside this source.
  if any(end>len(lines) for start,end in ranges):raise ValueError('Range exceeds evidence lines')
  spans=[]
  for start,end in ranges:
   selected=b''.join(lines[start-1:end])
   try:body={'text':selected.decode('utf-8')}
   except UnicodeDecodeError:body={'base64':base64.b64encode(selected).decode('ascii')}
   spans.append({'range_1based':[start,end],'bytes':len(selected),'sha256':digest(selected),**body})
  return {'schema':'helix.evidence.ranges.v1','receipt':key,'stream':stream,'source':source,'spans':spans,'io':dict(self.metrics),'io_scope':'application object bytes; entire source verified once per call; output hashing, metadata, physical traffic and CPU unmeasured'}
 def retrieve(self,key,stream='stdout',start=None,end=None,index=None):
  receipt=self.receipt(key)
  if index is not None:
   from line_index import retrieve as indexed_retrieve
   raw,_=indexed_retrieve(self,index,receipt[stream]['sha256'],1 if start is None else start,end)
  else:
   raw=self.get(receipt[stream]['sha256'])
  lines=raw.splitlines(keepends=True)
  if start is not None and index is None:
   if start<1 or end is not None and end<start:raise ValueError('Invalid 1-based inclusive line range')
   raw=b''.join(lines[start-1:end])
  try:body={'text':raw.decode('utf-8')}
  except UnicodeDecodeError:body={'base64':base64.b64encode(raw).decode('ascii')}
  return {'receipt':key,'stream':stream,'range_1based':[start,end],'sha256':digest(raw),'bytes':len(raw),'io':dict(self.metrics),'io_scope':'application object/staging byte counts, not physical SSD traffic; OS metadata and cache traffic unmeasured',**body}

ANSI=re.compile(r'\x1b\[[0-?]*[ -/]*[@-~]')
def reduce_stream(raw,kind,limit=8):
 # Lossy decoding is never presented as exact evidence; retrieve supplies exact bytes.
 lines=[line.decode('utf-8',errors='replace') for line in raw.splitlines()];view=[ANSI.sub('',x) for x in lines]
 result={'lines':len(lines),'projection_only':True};diagnostics=[];counts=[];sections=[]
 for i,line in enumerate(view,1):
  if kind=='pytest':
   if re.search(r'\b\d+ (?:passed|failed|error|errors|skipped|xfailed|xpassed)\b',line) and (' in ' in line or line.startswith('=')):
    counts.append({'line':i,'text':line})
   if re.match(r'^(?:FAILED|ERROR)\s',line) or re.match(r'^E\s+',line):diagnostics.append({'line':i,'text':line})
   if re.match(r'^_{3,}.+_{3,}$',line):sections.append({'start':i,'header':line})
  elif kind=='compiler':
   if re.search(r'(?:^|\s)(?:fatal error|error|warning):',line):diagnostics.append({'line':i,'text':line})
  else:
   if re.search(r'(?i)\b(error|failed|failure|warning|exception|panic)\b',line):diagnostics.append({'line':i,'text':line})
 for i,section in enumerate(sections):section['end']=sections[i+1]['start']-1 if i+1<len(sections) else len(lines)
 result.update(summary_candidates=counts[-2:],diagnostics=diagnostics[:limit],diagnostic_lines_omitted=max(0,len(diagnostics)-limit),failure_section_index=sections[:limit],failure_sections_omitted=max(0,len(sections)-limit))
 if not diagnostics and not counts:result['preview']=[{'line':i+1,'text':view[i]} for i in sorted(set(range(min(2,len(view)))) | set(range(max(0,len(view)-2),len(view))))]
 return result

def packet(store,key,kind='generic',max_bytes=6000):
 if max_bytes<1400:raise ValueError('Packet budget too small for provenance and retrieval contract')
 receipt=store.receipt(key)
 p={'schema':'helix.evidence.v1','receipt':key,'store':str(store.root),'command':receipt['argv'],'cwd':receipt['cwd'],'environment_id':receipt['environment_id'],'exit_code':receipt['exit_code'],'timed_out':receipt['timed_out'],'interrupted':receipt.get('interrupted',False),'wall_seconds':receipt['wall_seconds'],'raw':{s:receipt[s] for s in ['stdout','stderr']},'kind':kind,'coverage':'partial typed projection; originals retained losslessly; missing detail must be retrieved','streams':{s:reduce_stream(store.get(receipt[s]['sha256']),kind) for s in ['stdout','stderr']},'changed_watched_files':receipt['changed_watched_files']}
 store.metrics['projection_bytes_parsed']+=sum(receipt[s]['bytes'] for s in ['stdout','stderr']);p['middleware_io']=dict(store.metrics);p['io_scope']='application object/staging bytes; physical disk, metadata and cache traffic unmeasured'
 # Never slice serialized JSON, hashes or exact numeric strings to enforce the budget.
 encode=lambda:json.dumps(p,ensure_ascii=False,separators=(',',':')).encode()
 if len(encode())>max_bytes:
  p['streams']={s:{'lines':p['streams'][s]['lines'],'projection_omitted_due_to_budget':True} for s in p['streams']};p['retrieval_required']=True
 if len(encode())>max_bytes:
  p.pop('command');p.pop('cwd');p.pop('changed_watched_files');p['metadata_in_receipt']=True
 if len(encode())>max_bytes:raise ValueError('Metadata exceeds packet budget; raw receipt remains available')
 return p

def run(store,argv,cwd,environment_id,kind='generic',timeout=None,watch=(),env=None):
 cwd=Path(cwd).resolve();watch=[Path(x) if Path(x).is_absolute() else cwd/x for x in watch]
 snap=lambda:{str(p):digest(p.read_bytes()) if p.is_file() else None for p in watch}
 before=snap();start=time.time();timed_out=False
 staging=store.root/'runs'/uuid.uuid4().hex;staging.mkdir(parents=True)
 out=staging/'stdout';err=staging/'stderr';interrupted=False
 start_json=json.dumps({'argv':argv,'cwd':str(cwd),'started_unix':start});(staging/'started.json').write_text(start_json);store.metrics['staging_bytes_written']+=len(start_json.encode())
 with out.open('wb') as o,err.open('wb') as e:
  child=subprocess.Popen(argv,cwd=cwd,stdout=o,stderr=e,start_new_session=True,env=env)
  try:code=child.wait(timeout=timeout)
  except (subprocess.TimeoutExpired,KeyboardInterrupt) as exc:
   timed_out=isinstance(exc,subprocess.TimeoutExpired);interrupted=not timed_out;os.killpg(child.pid,signal.SIGKILL);code=child.wait()
  finally:
   if child.poll() is None:os.killpg(child.pid,signal.SIGKILL);child.wait()
 out_bytes=out.read_bytes();err_bytes=err.read_bytes();store.metrics['staging_bytes_read']+=len(out_bytes)+len(err_bytes);store.metrics['staging_bytes_written']+=len(out_bytes)+len(err_bytes);stdout=store.put(out_bytes);stderr=store.put(err_bytes)
 end=time.time();after=snap();receipt={'schema':'helix.command.v1','argv':argv,'cwd':str(cwd),'environment_id':environment_id,'started_unix':start,'finished_unix':end,'wall_seconds':round(end-start,6),'exit_code':code,'timed_out':timed_out,'interrupted':interrupted,'stdout':stdout,'stderr':stderr,'changed_watched_files':{p:{'before':before[p],'after':after[p]} for p in before if before[p]!=after[p]},'limits':'stdout/stderr bytes retained separately; cross-stream interleaving not recorded; watched-file changes only; environment label is caller supplied, not a full environment attestation'}
 key=store.put(json.dumps(receipt,ensure_ascii=False,separators=(',',':')).encode())['sha256'];staging_json=json.dumps({'receipt':key,'staging_copies_retained':True});(staging/'receipt.json').write_text(staging_json);store.metrics['staging_bytes_written']+=len(staging_json.encode());return packet(store,key,kind)

def main():
 a=argparse.ArgumentParser();a.add_argument('--store',required=True);sub=a.add_subparsers(dest='op',required=True)
 p=sub.add_parser('run');p.add_argument('--cwd',default='.');p.add_argument('--environment-id',default='unspecified');p.add_argument('--kind',choices=['generic','pytest','compiler'],default='generic');p.add_argument('--timeout',type=float);p.add_argument('--watch',action='append',default=[]);p.add_argument('argv',nargs=argparse.REMAINDER)
 p=sub.add_parser('get');p.add_argument('receipt');p.add_argument('--stream',choices=['stdout','stderr'],default='stdout');p.add_argument('--start',type=int);p.add_argument('--end',type=int);p.add_argument('--index')
 p=sub.add_parser('get-many');p.add_argument('receipt');p.add_argument('--stream',choices=['stdout','stderr'],default='stdout');p.add_argument('--range',dest='ranges',nargs=2,type=int,action='append',required=True,metavar=('START','END'))
 a=a.parse_args();s=Store(a.store)
 if a.op=='run':
  argv=a.argv[1:] if a.argv[:1]==['--'] else a.argv
  if not argv:raise ValueError('A command argv is required')
  result=run(s,argv,a.cwd,a.environment_id,a.kind,a.timeout,a.watch)
 elif a.op=='get-many':result=s.retrieve_many(a.receipt,a.ranges,a.stream)
 else:result=s.retrieve(a.receipt,a.stream,a.start,a.end,a.index)
 print(json.dumps(result,ensure_ascii=False,separators=(',',':')))
 if a.op=='run':
  code=result['exit_code'];sys.exit(124 if result['timed_out'] else 128-code if code<0 else code)
if __name__=='__main__':
 def interrupted(signum,frame):raise KeyboardInterrupt
 signal.signal(signal.SIGTERM,interrupted)
 main()
