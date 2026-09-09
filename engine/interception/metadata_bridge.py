"""Immutable correlation receipts from app-server events; not an access-control boundary."""
import hashlib,json,os,tempfile,re
from pathlib import Path

def encode(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
def digest(value):return hashlib.sha256(value).hexdigest()
def identity(session,turn,call):
    if not all(isinstance(x,str) and x for x in (session,turn,call)):raise ValueError('Complete event identity required')
    return digest(encode([session,turn,call]))

class Bridge:
    def __init__(self,root):
        self.root=Path(root)
        self.metrics={'receipt_bytes_written':0,'receipt_bytes_read':0,'output_bytes_hashed':0,'source_bytes_written':0,'source_bytes_read':0}
    def publish(self,event):
        if event.get('method')!='item/completed':return None
        params=event['params'];item=params['item']
        if item.get('type')!='commandExecution':return None
        if type(item.get('exitCode')) is not int or item.get('status') not in ('completed','failed'):return None
        if not isinstance(item.get('aggregatedOutput'),str):return None
        key=identity(params['threadId'],params['turnId'],item['id'])
        raw=item['aggregatedOutput'].encode();self.metrics['output_bytes_hashed']+=len(raw)
        self._store_source(raw)
        payload={'schema':'helix.command-metadata.v1','session_id':params['threadId'],'turn_id':params['turnId'],'tool_use_id':item['id'],'output_sha256':digest(raw),'output_bytes':len(raw),'exit_code':item['exitCode'],'native_status':item['status'],'duration_ms':item.get('durationMs'),'command':item.get('command'),'cwd':item.get('cwd')}
        content=encode({'payload':payload,'sha256':digest(encode(payload))});self.root.mkdir(parents=True,exist_ok=True)
        target=self.root/(key+'.json');fd,tmp=tempfile.mkstemp(dir=self.root)
        try:
            with os.fdopen(fd,'wb') as f:f.write(content);f.flush();os.fsync(f.fileno())
            self.metrics['receipt_bytes_written']+=len(content)
            try:os.link(tmp,target)
            except FileExistsError:
                existing=target.read_bytes();self.metrics['receipt_bytes_read']+=len(existing)
                if existing!=content:raise ValueError('Conflicting event for an immutable call identity')
        finally:
            if os.path.exists(tmp):os.unlink(tmp)
        return key
    def _store_source(self,raw):
        folder=self.root/'outputs';folder.mkdir(parents=True,exist_ok=True)
        target=folder/digest(raw);fd,tmp=tempfile.mkstemp(dir=folder)
        try:
            with os.fdopen(fd,'wb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
            self.metrics['source_bytes_written']+=len(raw)
            try:os.link(tmp,target)
            except FileExistsError:
                existing=target.read_bytes();self.metrics['source_bytes_read']+=len(existing)
                if existing!=raw:raise ValueError('Corrupt existing source archive')
        finally:
            if os.path.exists(tmp):os.unlink(tmp)
    def lookup(self,hook):
        key=identity(hook.get('session_id'),hook.get('turn_id'),hook.get('tool_use_id'))
        raw=(self.root/(key+'.json')).read_bytes();self.metrics['receipt_bytes_read']+=len(raw)
        record=json.loads(raw);payload=record['payload']
        if record['sha256']!=digest(encode(payload)):raise ValueError('Metadata receipt corruption')
        expected=(hook['session_id'],hook['turn_id'],hook['tool_use_id'])
        if tuple(payload[k] for k in ('session_id','turn_id','tool_use_id'))!=expected:raise ValueError('Cross-call metadata')
        output=hook.get('tool_response')
        if not isinstance(output,str):raise ValueError('Expected native text envelope')
        source_hash=payload['output_sha256']
        if not re.fullmatch('[a-f0-9]{64}',source_hash):raise ValueError('Invalid source digest')
        source_path=self.root/'outputs'/source_hash;source=source_path.read_bytes()
        self.metrics['source_bytes_read']+=len(source);self.metrics['output_bytes_hashed']+=len(source)
        if digest(source)!=source_hash or len(source)!=payload['output_bytes']:raise ValueError('Native source corruption')
        data=output.encode();self.metrics['output_bytes_hashed']+=len(data)
        shortened=digest(data)!=source_hash
        if shortened and not verified_native_view(source.decode('utf-8'),output):raise ValueError('Unrecognized or changed output view')
        if type(payload.get('exit_code')) is not int:raise ValueError('Invalid status type')
        self.matched_output=source
        return {'exit_code':payload['exit_code'],'native_status':payload['native_status'],'duration_ms':payload['duration_ms'],'metadata_receipt_sha256':record['sha256'],'upstream_truncated':shortened,'received_view_sha256':digest(data),'native_output_ref':{'sha256':source_hash,'bytes':len(source),'path':str(source_path.resolve())},'metadata_bridge_io':dict(self.metrics)}

def verified_native_view(source,view):
    # Match one observed native framing, not arbitrary summaries or rewritten output.
    match=re.fullmatch(r'Warning: truncated output \(original token count: ([0-9]+)\)\nTotal output lines: ([0-9]+)\n\n(.*)…([0-9]+) tokens truncated…(.*)',view,re.S)
    if not match:return False
    total,lines,head,omitted,tail=match.groups()
    return (0<int(omitted)<int(total) and int(lines)==len(source.splitlines()) and bool(head) and bool(tail) and len(head)+len(tail)<len(source) and source.startswith(head) and source.endswith(tail))
