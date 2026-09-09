"""Loopback-only read-only projection of registered native benchmark receipts.

The observer writes only its own append-only journal. It never invokes an LLM,
executes benchmark commands or queries agents. Paths come from caller config.
"""
import argparse
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import re
from pathlib import Path
import subprocess
import threading
import time
import uuid
from pricing import Prices, estimate
from urllib.parse import urlsplit, parse_qs

HERE=Path(__file__).resolve().parent
FILE_CACHE={}
READ_BYTES=0


def cached_bytes(path,limit):
    global READ_BYTES
    stat=path.stat();signature=(stat.st_ino,stat.st_size,stat.st_mtime_ns,stat.st_ctime_ns)
    prior=FILE_CACHE.get(str(path))
    if prior and prior[0]==signature:return prior[1]
    if stat.st_size>limit:raise ValueError('Receipt exceeds reader limit')
    raw=path.read_bytes();READ_BYTES+=len(raw)
    after=path.stat()
    if signature!=(after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns):raise ValueError('Receipt changed during read')
    FILE_CACHE[str(path)]=(signature,raw)
    return raw


def read_json(path):
    raw=cached_bytes(path,4_000_000)
    return json.loads(raw),hashlib.sha256(raw).hexdigest()


TRACE_CACHE={}
def trace_view(path):
    raw=cached_bytes(path,16_000_000)
    digest=hashlib.sha256(raw).hexdigest()
    prior=TRACE_CACHE.get(str(path))
    if prior and prior[0]==digest:return prior[1]
    events=[]
    for line in raw.splitlines():
        try:events.append(json.loads(line))
        except (ValueError,UnicodeError):continue
    commands=[e['item'] for e in events if e.get('type')=='item.completed' and e.get('item',{}).get('type')=='command_execution']
    suspects=[i for i in commands if re.search(r'engine/|renderer\.py|named_plans\.py|copy_handles\.py',i.get('command',''))
              and re.search(r'\b(cat|sed|head|tail|rg)\b|read_text\(',i.get('command',''))]
    timeline=[]
    for index,event in enumerate(events):
        item=event.get('item',{});kind=event.get('type','unknown')
        detail=item.get('type') or ''
        entry={'sequence':index+1,'type':kind,'detail':detail,
            'execution_timestamp':event.get('timestamp'),
            'exit_code':item.get('exit_code')}
        if kind=='item.completed' and detail=='command_execution':entry['recorded_output_bytes']=len(item.get('aggregated_output','').encode())
        if kind in ('turn.started','turn.completed','turn.failed','item.started','item.completed'):timeline.append(entry)
    result={'commands':len(commands),'recorded_tool_bytes':sum(len(i.get('aggregated_output','').encode()) for i in commands),
        'generated_command_bytes':sum(len(i.get('command','').encode()) for i in commands),
        'suspected_engine_read_output_bytes':sum(len(i.get('aggregated_output','').encode()) for i in suspects),
        'timeline':timeline[-20:], 'trace_sha256':digest}
    turns=[usage(e.get('usage')) for e in events if e.get('type')=='turn.completed']
    result['trace_usage']=({key:sum(t[key] for t in turns) if all(t.get(key) is not None for t in turns) else None
                            for key in turns[0]} if turns and all(t is not None for t in turns) else None)
    if timeline:
        last=timeline[-1];result['last_event']=last['type']+(' · '+last['detail'] if last['detail'] else '')
        result['phase']='Completed' if last['type']=='turn.completed' else 'Tool' if last['type']=='item.started' and last['detail']=='command_execution' else 'Model / unclassified'
    TRACE_CACHE[str(path)]=(digest,result)
    return result


def engine_view(path):
    raw=cached_bytes(path,4_000_000)
    events=[];types={};policy=None
    for line in raw.splitlines():
        try:event=json.loads(line)
        except (ValueError,UnicodeError):continue # Incomplete append is retried next scan.
        if event.get('schema')!='helix.engine.event.v1':raise ValueError('Unknown Engine event')
        for field in ('evidence_ref','policy_ref'):
            key=event.get(field,'')
            if not re.fullmatch('[0-9a-f]{64}',key):raise ValueError('Invalid Engine ref')
            source=cached_bytes(path.parent/'objects'/key,4_000_000)
            if hashlib.sha256(source).hexdigest()!=key:raise ValueError('Engine evidence tampered')
            if field=='policy_ref':policy=json.loads(source)['policy']
        kind=event['type'];types[kind]=types.get(kind,0)+1
        events.append({'sequence':len(events)+1,'type':'engine.'+kind,'detail':event['evidence_ref'][:12],
                       'execution_timestamp':event['timestamp'],'exit_code':None})
    return {'engine_timeline':events[-20:],'engine_event_counts':types,'engine_policy':policy,
            'engine_event_source_hash':hashlib.sha256(raw).hexdigest()}


def native_cumulative(path,thread_id):
    raw=cached_bytes(path,16_000_000);latest=None
    for line in raw.splitlines():
        try:event=json.loads(line)
        except (ValueError,UnicodeError):continue
        if event.get('method')!='thread/tokenUsage/updated':continue
        params=event.get('params',{})
        if params.get('threadId')!=thread_id:continue
        total=params['tokenUsage']['total']
        value={key:total[field] for key,field in [('input_tokens','inputTokens'),('output_tokens','outputTokens'),('cached_input_tokens','cachedInputTokens'),('reasoning_output_tokens','reasoningOutputTokens')]}
        if usage(value) is None or any(v is None for v in value.values()):raise ValueError('Invalid native cumulative counter')
        if value['cached_input_tokens']>value['input_tokens'] or value['reasoning_output_tokens']>value['output_tokens']:raise ValueError('Invalid native subsets')
        if latest and any(value[k]<latest[k] for k in value):raise ValueError('Cumulative native counters decreased')
        value['cache_write_input_tokens']=total.get('cacheWriteInputTokens')
        latest=value
    return latest,hashlib.sha256(raw).hexdigest()


def usage(value):
    if not isinstance(value,dict):return None
    result={}
    for key in ['input_tokens','output_tokens','cached_input_tokens','reasoning_output_tokens','cache_write_input_tokens']:
        n=value.get(key)
        if n is not None and (type(n) is not int or n<0):return None
        result[key]=n
    return result


def safe_path(root,relative):
    path=(root/relative).resolve()
    if not path.is_relative_to(root.resolve()):raise ValueError('Configured path escapes root')
    return path


def live_process(status,cwd):
    pid=status.get('pid')
    if type(pid) is not int or pid<1 or not cwd:return None
    try:
        result=subprocess.run(['ps','-p',str(pid),'-o','command='],capture_output=True,text=True,timeout=1)
        command=result.stdout
        if status.get('runner')=='app-server':
            if result.returncode!=0 or 'app-server' not in command or status.get('model','<unknown>') not in command:return False
            location=subprocess.run(['lsof','-a','-p',str(pid),'-d','cwd','-Fn'],capture_output=True,text=True,timeout=2)
            paths=[line[1:] for line in location.stdout.splitlines() if line.startswith('n')]
            return any(Path(p).resolve()==Path(cwd).resolve() for p in paths)
        return result.returncode==0 and 'codex' in command and str(cwd) in command and status.get('model','<unknown>') in command
    except (OSError,subprocess.TimeoutExpired):return None


def report_rows(report):
    rows=report.get('rows',[]) if isinstance(report,dict) else []
    return [r for r in rows if isinstance(r,dict)] if isinstance(rows,list) else []


def measured_check(report,arm):
    row=next((r for r in report_rows(report) if r.get('arm')==arm),{})
    # Finite artifact/source checks only; never intelligence or workflow parity.
    grade=row.get('grade',{})
    exact=row.get('artifact_exact',grade.get('exact_artifact'))
    source=row.get('source_unchanged',grade.get('source_unchanged'))
    if exact is False or source is False or row.get('passed') is False:return False
    if exact is True and source is True:return True
    return None


def snapshot(config):
    runs=[];pairs=[];problems=[];receipts={}
    for experiment in config['experiments']:
        root=Path(experiment['root']).resolve()
        report={}
        manifest={}
        if experiment.get('manifest'):
            try:manifest,_=read_json(safe_path(root,experiment['manifest']))
            except (OSError,ValueError):pass
        if experiment.get('result'):
            try:report,_=read_json(safe_path(root,experiment['result']))
            except (OSError,ValueError):pass
        current=[]
        for spec in experiment['runs']:
            rid=experiment['id']+'-'+spec['arm']
            path=safe_path(root,spec['status'])
            row={'id':rid,'experiment_id':experiment['id'],'experiment':experiment['name'],
                'classification':experiment['classification'],'arm':spec['arm'],
                'state':'UNAVAILABLE','model':manifest.get('model'),'usage':None,'elapsed_seconds':None,
                'source':str(path),'source_hash':None,'updated_at':None,
                'artifact_check':measured_check(report,spec['arm']),'last_event':None}
            report_row=next((r for r in report_rows(report) if r.get('arm')==spec['arm']),{})
            completion=report_row.get('completion')
            row.update(raw_source_bytes=manifest.get('source_bytes'),model_visible_bytes=None,
                engine_calls=1 if isinstance(completion,dict) else None,
                engine_operations=completion.get('operations') if isinstance(completion,dict) else None,
                engine_output_bytes=completion.get('bytes') if isinstance(completion,dict) else None,
                engine_seconds=completion.get('caller_seconds') if isinstance(completion,dict) else None,
                delegated_work='Exact copy + byte validation' if isinstance(completion,dict) else 'Not instrumented',
                mechanisms={'exact_copy':'observed' if isinstance(completion,dict) else 'not observed',
                    'memory':'unmeasured','retrieval':'unmeasured','plans':'unmeasured','reducers':'unmeasured'})
            try:
                status,digest=read_json(path)
                if not isinstance(status,dict):raise ValueError('Invalid status')
                row.update(model=status.get('model'),state=str(status.get('state','UNKNOWN')).upper(),
                    usage=usage(status.get('usage')),elapsed_seconds=status.get('elapsed_seconds'),
                    source_hash=digest,updated_at=path.stat().st_mtime,
                    trace_hash=status.get('events_sha256'),effort=status.get('effort'))
                if row['state'] in ('RUNNING','STARTING'):
                    present=live_process(status,safe_path(root,spec['cwd']) if spec.get('cwd') else None)
                    row['state']='RUNNING' if present is True else 'STALE' if present is False else 'RUNNING_UNVERIFIED'
                    row['process_checked_at']=int(time.time())//5*5
                receipts[rid]=path
                if spec.get('events'):
                    events=safe_path(root,spec['events'])
                    if events.exists():
                        size=events.stat().st_size;row['trace_bytes']=size
                        row.update(trace_view(events))
                        if row.get('trace_usage'):
                            if row['usage'] and any(row['usage'].get(k)!=row['trace_usage'].get(k) for k in ['input_tokens','output_tokens']):
                                row['usage']=None;row['artifact_check']=None
                                problems.append({'run':rid,'message':'Native usage disagrees with trace; tokens withheld.'})
                            elif row['usage'] is None and status.get('usage') is None and status.get('events_sha256')==row['trace_sha256']:
                                row['usage']=row['trace_usage']
                        if status.get('events_sha256') and row['trace_sha256']!=status['events_sha256']:
                            row['artifact_check']=None
                            problems.append({'run':rid,'message':'Trace hash differs from status receipt; checks unverified.'})
                if spec.get('native_events') and status.get('thread_id'):
                    native_tokens,native_hash=native_cumulative(safe_path(root,spec['native_events']),status['thread_id'])
                    if status.get('native_events_sha256') and native_hash!=status['native_events_sha256']:raise ValueError('Raw native wire hash mismatch')
                    if native_tokens:
                        if row['usage'] and any(row['usage'].get(k)!=native_tokens[k] for k in native_tokens):raise ValueError('Raw native usage mismatch')
                        row['usage']=native_tokens;row['usage_source']='Native app-server cumulative update'
                        row['usage_live']=row['state']=='RUNNING'
                bound=bool(status.get('events_sha256')) and report_row.get('events_sha256')==status.get('events_sha256')
                if not bound:
                    row['artifact_check']=None
                    row.update(engine_calls=None,engine_operations=None,engine_output_bytes=None,engine_seconds=None,
                               delegated_work='Not instrumented')
                    row['mechanisms']['exact_copy']='not observed'
            except (OSError,ValueError,TypeError) as exc:
                row.update(state='UNAVAILABLE',usage=None,error=type(exc).__name__)
                problems.append({'run':rid,'message':'Receipt unavailable or invalid; measurements are unknown.'})
            if spec.get('engine_events'):
                try:
                    row.update(engine_view(safe_path(root,spec['engine_events'])))
                    policy=row.get('engine_policy') or {}
                    for key in ('memory','reducers','cold_plans','completion'):
                        row['mechanisms'][key]='enabled (policy)' if policy.get(key) is True else 'disabled (policy)' if policy.get(key) is False else 'unknown'
                    counts=row['engine_event_counts']
                    row['delegated_work']='; '.join(k+': '+str(v) for k,v in counts.items()) or row['delegated_work']
                except (OSError,ValueError,KeyError,TypeError):
                    problems.append({'run':rid,'message':'Engine events unavailable or integrity check failed.'})
            current.append(row);runs.append(row)
        off=next((r for r in current if r['arm']=='off'),None)
        on=next((r for r in current if r['arm']=='on'),None)
        savings={}
        for key in ['input_tokens','output_tokens']:
            b=(off or {}).get('usage') or {};h=(on or {}).get('usage') or {}
            savings[key]=(1-h[key]/b[key])*100 if b.get(key) is not None and b[key]>0 and h.get(key) is not None else None
        pairs.append({'id':experiment['id'],'name':experiment['name'],
            'classification':experiment['classification'],'model':(on or off or {}).get('model'),
            'off':off['id'] if off else None,'on':on['id'] if on else None,'savings':savings,
            'artifact_check':True if off and on and off['artifact_check'] is True and on['artifact_check'] is True else
                False if any(r['artifact_check'] is False for r in current) else None})
    return {'schema':'helix.hud.v1','runs':runs,'pairs':pairs,'problems':problems,
        'scope':'Registered native benchmark runs only. Parent chat and unregistered agents are not instrumented.',
        'capability_parity':'Not established','inference_calls_by_hud':0},receipts


class Observer:
    def __init__(self,config,journal):
        self.config=config;self.journal=journal;self.condition=threading.Condition()
        self.current=None;self.revision=0;self.receipts={};self.last_scan=None
        self.error=None;self.digest=None;self.read_cycles=0
        self.observer_id=uuid.uuid4().hex
        self.prices=Prices()

    def scan(self):
        data,receipts=snapshot(self.config)
        digest=hashlib.sha256(json.dumps(data,sort_keys=True).encode()).hexdigest()
        with self.condition:
            self.last_scan=time.time();self.read_cycles+=1;self.receipts=receipts;self.error=None
            if digest!=self.digest:
                self.revision+=1;data['revision']=self.revision;data['observed_at']=self.last_scan;data['observer_id']=self.observer_id
                self.journal.parent.mkdir(parents=True,exist_ok=True)
                with self.journal.open('a') as out:out.write(json.dumps({'type':'snapshot','event_id':self.observer_id+':'+str(self.revision),'revision':self.revision,'at':self.last_scan,'timestamp_kind':'observation','state':data})+'\n')
                self.current=data;self.digest=digest;self.condition.notify_all()

    def state(self):
        with self.condition:
            data=dict(self.current or {})
            price=self.prices.state()
            data['pricing']=price
            data['costs']={r['id']:estimate(r.get('usage'),(price.get('rates') or {}).get(r.get('model'))) for r in data.get('runs',[]) if r.get('state')=='COMPLETED' and r.get('usage_source')=='Native app-server cumulative update'}
            return {**data,'observer':{'last_scan':self.last_scan,'read_cycles':self.read_cycles,
                'error':self.error,'journal':str(self.journal),'poll_seconds':2,'logical_file_bytes_read':READ_BYTES,
                'cost_scope':'File reads and local CPU; no inference. Exact physical I/O unmetered.'}}

    def loop(self):
        while True:
            try:self.scan()
            except Exception as exc:
                with self.condition:self.error=type(exc).__name__;self.condition.notify_all()
            time.sleep(2)


def make_handler(observer):
    class Handler(BaseHTTPRequestHandler):
        protocol_version='HTTP/1.1'
        def log_message(self,*args):pass
        def send_data(self,data,ctype,code=200):
            self.send_response(code);self.send_header('Content-Type',ctype)
            self.send_header('Content-Length',str(len(data)));self.send_header('Cache-Control','no-store')
            self.send_header('X-Content-Type-Options','nosniff')
            self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; frame-ancestors 'none'")
            self.end_headers();self.wfile.write(data)
        def do_GET(self):
            host=self.headers.get('Host','').split(':')[0]
            if host not in ('127.0.0.1','localhost'):return self.send_data(b'Loopback host required','text/plain',403)
            parsed=urlsplit(self.path)
            if parsed.path=='/api/state':return self.send_data(json.dumps(observer.state()).encode(),'application/json')
            if parsed.path=='/api/receipt':
                key=parse_qs(parsed.query).get('id',[''])[0]
                with observer.condition:path=observer.receipts.get(key)
                if path is None:return self.send_data(b'Unknown receipt','text/plain',404)
                try:data,_=read_json(path)
                except (ValueError,OSError):return self.send_data(b'Receipt unavailable','text/plain',503)
                return self.send_data(json.dumps(data,indent=2).encode(),'application/json')
            if parsed.path=='/api/events':
                self.send_response(200);self.send_header('Content-Type','text/event-stream')
                self.send_header('Cache-Control','no-store');self.send_header('Connection','close');self.end_headers()
                revision=-1
                try:
                    while True:
                        with observer.condition:
                            if observer.revision==revision:observer.condition.wait(timeout=5)
                            revision=observer.revision
                        # Heartbeats include observer liveness; no model calls or agent polling.
                        self.wfile.write(('data: '+json.dumps(observer.state())+'\n\n').encode());self.wfile.flush()
                except (BrokenPipeError,ConnectionResetError):return
            assets={'/':'index.html','/app.js':'app.js','/style.css':'style.css'}
            if parsed.path not in assets:return self.send_data(b'Not found','text/plain',404)
            name=assets[parsed.path];ctype={'html':'text/html','js':'text/javascript','css':'text/css'}[name.rsplit('.',1)[1]]
            return self.send_data((HERE/name).read_bytes(),ctype+'; charset=utf-8')
    return Handler


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--config',required=True)
    parser.add_argument('--port',type=int,default=8769);parser.add_argument('--journal',required=True)
    args=parser.parse_args();config,_=read_json(Path(args.config))
    observer=Observer(config,Path(args.journal));observer.scan()
    server=ThreadingHTTPServer(('127.0.0.1',args.port),make_handler(observer));server.daemon_threads=True
    threading.Thread(target=observer.loop,daemon=True).start()
    threading.Thread(target=observer.prices.loop,daemon=True).start()
    print(f'Helix HUD http://127.0.0.1:{args.port} · read-only · no inference',flush=True)
    server.serve_forever()


if __name__=='__main__':main()
