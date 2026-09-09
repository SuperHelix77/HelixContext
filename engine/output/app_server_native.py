"""Fresh native app-server turn with exact raw events and derived HUD events.

Usage is the final cumulative native total, never the sum of cumulative updates.
Full RPC wire remains cold. No inference retries or auto-approval are implemented.
"""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import selectors
import signal
import subprocess
import time

CLI='/Applications/ChatGPT.app/Contents/Resources/codex'
HELPER=Path('/Users/mert/.codex/helix-context/bin/runtime-b09051d7f65fa98b.py')


def sha(raw):return hashlib.sha256(raw).hexdigest()
def save(path,value):path.write_text(json.dumps(value,indent=2)+'\n')


def usage(event):
    total=event['params']['tokenUsage']['total']
    mapping={'input_tokens':'inputTokens','output_tokens':'outputTokens','cached_input_tokens':'cachedInputTokens','reasoning_output_tokens':'reasoningOutputTokens','cache_write_input_tokens':'cacheWriteInputTokens'}
    result={k:total.get(v,0) if k=='cache_write_input_tokens' else total[v] for k,v in mapping.items()}
    if any(type(n) is not int or n<0 for n in result.values()):raise ValueError('Invalid native usage')
    if result['cached_input_tokens']>result['input_tokens'] or result['reasoning_output_tokens']>result['output_tokens']:raise ValueError('Invalid usage subsets')
    if total['totalTokens']!=result['input_tokens']+result['output_tokens']:raise ValueError('Native total mismatch')
    return result


def normalize(event):
    method=event.get('method');params=event.get('params',{})
    if method=='turn/started':return {'type':'turn.started'}
    if method in ('item/started','item/completed'):
        item=params['item'];kind=item.get('type');value={'id':item.get('id'),'type':{'commandExecution':'command_execution','agentMessage':'agent_message','fileChange':'file_change'}.get(kind,kind)}
        if kind=='commandExecution':value.update(command=item.get('command'),exit_code=item.get('exitCode'),aggregated_output=item.get('aggregatedOutput') or '')
        elif kind=='agentMessage':value['text']=item.get('text','')
        elif kind=='fileChange':value['changes']=item.get('changes',[])
        # Reasoning content and other full payloads stay only in cold raw RPC.
        return {'type':method.replace('/','.'),'item':value}
    return None


class RPC:
    def __init__(self,cwd,out,model):
        self.out=out;self.raw=(out/'native-events.jsonl').open('wb');self.requests=(out/'requests.jsonl').open('wb');self.stderr=(out/'stderr.txt').open('wb')
        self.p=subprocess.Popen([CLI,'app-server','--stdio','-c','model='+json.dumps(model),'-c','model_reasoning_effort="high"','-c','skills.max_context_tokens=512'],cwd=cwd,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=self.stderr,bufsize=0,start_new_session=True)
        self.selector=selectors.DefaultSelector();self.selector.register(self.p.stdout,selectors.EVENT_READ)
        self.buffer=b'';self.next_id=0;self.events=[];self.deadline=time.monotonic()+600

    def send(self,value):
        raw=(json.dumps(value,separators=(',',':'))+'\n').encode();self.requests.write(raw);self.requests.flush();self.p.stdin.write(raw);self.p.stdin.flush()

    def read(self):
        while b'\n' not in self.buffer:
            remaining=self.deadline-time.monotonic()
            if remaining<=0:raise TimeoutError('Native deadline')
            if not self.selector.select(min(remaining,10)):continue
            raw=os.read(self.p.stdout.fileno(),65536)
            if not raw:raise RuntimeError('Native server closed')
            self.buffer+=raw
        line,self.buffer=self.buffer.split(b'\n',1);self.raw.write(line+b'\n');self.raw.flush()
        event=json.loads(line);self.events.append(event)
        if 'method' in event and 'id' in event:
            self.send({'id':event['id'],'error':{'code':-32000,'message':'Unattended benchmark cannot fulfill interactive request'}})
            raise RuntimeError('Unexpected server request; preserved and stopped')
        return event

    def call(self,method,params):
        self.next_id+=1;rid=self.next_id;self.send({'id':rid,'method':method,'params':params})
        while True:
            e=self.read()
            if e.get('id')==rid:
                if 'error' in e:raise RuntimeError(str(e['error']))
                return e['result']

    def close(self):
        if self.p.poll() is None:
            os.killpg(self.p.pid,signal.SIGTERM)
            try:self.p.wait(timeout=5)
            except subprocess.TimeoutExpired:os.killpg(self.p.pid,signal.SIGKILL);self.p.wait()
        self.selector.close();self.raw.close();self.requests.close();self.stderr.close()


def native(model,cwd,prompt,out):
    out.mkdir(parents=True,exist_ok=False);(out/'prompt.txt').write_text(prompt)
    start=time.perf_counter();rpc=RPC(cwd,out,model);status={'state':'starting','model':model,'effort':'high','runner':'app-server','pid':rpc.p.pid,'started_unix':time.time()}
    save(out/'status.json',status);registration=None;native_usage=None;thread=None;turn=None
    normalized=(out/'events.jsonl').open('w');cursor=0
    def drain():
        nonlocal cursor,native_usage
        for e in rpc.events[cursor:]:
            if e.get('method')=='thread/tokenUsage/updated' and e['params']['threadId']==thread:
                new=usage(e)
                if native_usage and any(new[k]<native_usage[k] for k in new):raise ValueError('Nonmonotonic cumulative native usage')
                native_usage=new
            value=normalize(e)
            if value:normalized.write(json.dumps(value)+'\n')
        cursor=len(rpc.events);normalized.flush()
    try:
        rpc.call('initialize',{'clientInfo':{'name':'helix-paired-native','version':'3'},'capabilities':{'experimentalApi':True}});rpc.send({'method':'initialized'})
        response=rpc.call('thread/start',{'model':model,'cwd':str(cwd),'ephemeral':True,'approvalPolicy':'never','sandbox':'workspace-write','config':{'model_reasoning_effort':'high','skills.max_context_tokens':512}})
        save(out/'thread-start.json',response)
        if response['model']!=model or response.get('reasoningEffort')!='high' or response['approvalPolicy']!='never':raise ValueError('Native model/effort/approval mismatch')
        thread=response['thread']['id'];status['thread_id']=thread
        normalized.write(json.dumps({'type':'thread.started','thread_id':thread})+'\n')
        inputs=[{'type':'text','text':prompt}]
        if cwd.name=='on':
            skill=cwd/'.agents/skills/helixcontext/SKILL.md'
            listed=rpc.call('skills/list',{'cwds':[str(cwd)],'forceReload':True,'perCwdExtraUserRoots':[{'cwd':str(cwd),'extraUserRoots':[str(skill.parent.parent)]}]})
            save(out/'skills-list.json',listed)
            found=[s for row in listed['data'] for s in row['skills'] if s['path']==str(skill) and s['name']=='helixcontext' and s['enabled']]
            if len(found)!=1:raise ValueError('Exact native skill unavailable')
            before=time.perf_counter();spec=importlib.util.spec_from_file_location('helix_v3_registry',HELPER);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
            helper=module.Runtime(cwd/'.helix/continuity.sqlite3')
            try:
                helper.activate(thread,skill,'benchmark');restored=helper.skills(thread)
                if len(restored)!=1 or restored[0]['digest']!=sha(skill.read_bytes()):raise ValueError('Skill registry mismatch')
            finally:helper.db.close()
            registration={'state':'registered_before_inference','native_thread_id':thread,'skill_sha256':sha(skill.read_bytes()),'seconds':time.perf_counter()-before,'skill_path':str(skill)}
            save(out.parent.parent/'registration.json',registration)
            inputs.append({'type':'skill','name':'helixcontext','path':str(skill)})
        status['state']='running';save(out/'status.json',status)
        response=rpc.call('turn/start',{'threadId':thread,'model':model,'effort':'high','input':inputs})
        turn=response['turn']['id'];drain()
        while True:
            done=next((e for e in rpc.events if e.get('method')=='turn/completed' and e['params']['threadId']==thread and e['params']['turn']['id']==turn),None)
            if done:break
            rpc.read();drain()
        if done['params']['turn']['status']!='completed':raise RuntimeError('Native turn failed')
        if native_usage is None:raise ValueError('Missing native token receipt')
        answers=[e['params']['item'] for e in rpc.events if e.get('method')=='item/completed' and e['params']['item'].get('type')=='agentMessage']
        final=[i for i in answers if i.get('phase')=='final_answer']
        answer=(final or answers)[-1]['text'] if answers else ''
        (out/'answer.txt').write_text(answer)
        normalized.write(json.dumps({'type':'turn.completed','usage':native_usage,'provenance':'final cumulative thread/tokenUsage/updated in native-events.jsonl'})+'\n');normalized.flush()
        status.update(state='completed',exit_code=0,usage=native_usage,elapsed_seconds=time.perf_counter()-start,
                      events_sha256=sha((out/'events.jsonl').read_bytes()),native_events_sha256=sha((out/'native-events.jsonl').read_bytes()),
                      normalization='Derived CLI-shaped projection; native-events.jsonl remains authoritative',registration=registration)
        save(out/'status.json',status)
        return answer,status
    except Exception as exc:
        try:drain()
        except Exception as accounting_error:status['accounting_error']=str(accounting_error)
        status.update(state='failed',usage=native_usage,error=type(exc).__name__+': '+str(exc),elapsed_seconds=time.perf_counter()-start,
            events_sha256=sha((out/'events.jsonl').read_bytes()),native_events_sha256=sha((out/'native-events.jsonl').read_bytes()))
        save(out/'status.json',status);raise
    finally:normalized.close();rpc.close()
