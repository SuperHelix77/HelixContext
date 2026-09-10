"""Observed/config-bound session with explicit High or Extra High per thread/turn.

Versioned derivative; original High-only runners remain frozen. Process default
is High; explicit thread and turn settings are verified against native replies.
No global configuration override, no inferred effort and no inference retry.
"""
import importlib.util
import json
from pathlib import Path
import time
import os
from app_server_native import RPC, HELPER, usage, normalize, save, sha
from raw_receipts import capture
from config_bound_session import private_write, validate

class Session:
    def __init__(self,model,cwd,out,skill=None,effort='high'):
        if effort not in ('high','xhigh'):raise ValueError('Unqualified research effort')
        self.effort=effort
        self.model=model;self.cwd=Path(cwd);self.out=Path(out)
        self.out.mkdir(parents=True,exist_ok=False)
        self.rpc=RPC(self.cwd,self.out,model);self.thread=None;self.total=None
        self.turns=[];self.failed=False;self.closed=False;self.skill=Path(skill) if skill else None
        self.started=time.perf_counter();self.normalized=(self.out/'events.jsonl').open('w')
        self.cursor=0;self.registration=None;self.capture_status=None;self.rollout_path=None
        config=Path(os.environ.get("CODEX_HOME",str(Path.home()/".codex")))/"config.toml"
        self.config_path=config
        self.initial_config=config.read_bytes()
        self.config_hash=sha(self.initial_config)
        private_write(self.out/'config.initial.private.toml',self.initial_config)
        try:
            self.rpc.call('initialize',{'clientInfo':{'name':'helix-research-continuation','version':'1'},'capabilities':{'experimentalApi':True}})
            self.rpc.send({'method':'initialized'})
            r=self.rpc.call('thread/start',{'model':model,'cwd':str(self.cwd),'ephemeral':False,'approvalPolicy':'never','sandbox':'workspace-write','config':{'model_reasoning_effort':self.effort,'skills.max_context_tokens':512}})
            save(self.out/'thread-start.json',r)
            if r['model']!=model or r.get('reasoningEffort')!=self.effort or r['approvalPolicy']!='never':raise ValueError('Native configuration mismatch')
            self.thread=r['thread']['id'];self.rollout_path=r['thread'].get('path')
            if self.skill:
                listing=self.rpc.call('skills/list',{'cwds':[str(self.cwd)],'forceReload':True,'perCwdExtraUserRoots':[{'cwd':str(self.cwd),'extraUserRoots':[str(self.skill.parent.parent)]}]})
                save(self.out/'skills-list.json',listing)
                found=[s for row in listing['data'] for s in row['skills'] if s['path']==str(self.skill) and s['name']=='helixcontext' and s['enabled']]
                if len(found)!=1:raise ValueError('Exact skill unavailable')
                spec=importlib.util.spec_from_file_location('helix_session_registry',HELPER);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
                rt=module.Runtime(self.cwd/'.helix/continuity.sqlite3')
                try:
                    rt.activate(self.thread,self.skill,'research-continuation');restored=rt.skills(self.thread)
                    if len(restored)!=1 or restored[0]['digest']!=sha(self.skill.read_bytes()):raise ValueError('Skill registry mismatch')
                finally:rt.db.close()
                self.registration={'skill_sha256':sha(self.skill.read_bytes()),'thread_id':self.thread,'scope':'registered before first inference; subsequent skill availability not yet behaviorally qualified'}
            self.record('ready')
        except BaseException as e:
            self.failed=True;self.record('failed',str(e));self.close();raise

    def record(self,state,error=None):
        self.normalized.flush()
        save(self.out/'status.json',{'state':state,'model':self.model,'effort':self.effort,'thread_id':self.thread,'pid':self.rpc.p.pid,'usage':self.total,'turns':self.turns,'registration':self.registration,'elapsed_seconds':time.perf_counter()-self.started,'error':error,'config_sha256':self.config_hash,'raw_capture':self.capture_status,'native_events_sha256':sha((self.out/'native-events.jsonl').read_bytes()),'events_sha256':sha((self.out/'events.jsonl').read_bytes())})

    def turn(self,text=None,tool_output=None):
        if self.failed or self.closed:raise ValueError('Session terminal; no implicit retry')
        if (text is None)==(tool_output is None):raise ValueError('Exactly one input kind required')
        if text is not None and (not isinstance(text,str) or not text):raise ValueError('Nonempty text required')
        if tool_output is not None and (not isinstance(tool_output,dict) or not tool_output.get('name') or 'output' not in tool_output):raise ValueError('Named tool output required')
        if tool_output is not None and not self.turns:raise ValueError('Initial semantic task required')
        baseline=dict(self.total) if self.total else None;offset=len(self.rpc.events)
        row={'state':'STARTED','index':len(self.turns)+1,'baseline':baseline};self.turns.append(row)
        params={'threadId':self.thread,'model':self.model,'effort':self.effort,'input':[]}
        if text is not None:params['input']=[{'type':'text','text':text}]
        else:params['toolOutput']=tool_output
        if row['index']==1 and self.skill:params['input'].append({'type':'skill','name':'helixcontext','path':str(self.skill)})
        save(self.out/('turn-'+str(row['index'])+'-input.json'),params);self.record('running')
        self.rpc.deadline=time.monotonic()+600
        try:
            reply=self.rpc.call('turn/start',params);tid=reply['turn']['id'];row['turn_id']=tid
            observed=False;done=None;answers=[]
            while done is None:
                pending=self.rpc.events[offset:];offset=len(self.rpc.events)
                for e in pending:
                    p=e.get('params',{})
                    if p.get('threadId')!=self.thread:continue
                    if e.get('method')=='thread/tokenUsage/updated':
                        if p.get('turnId')!=tid:raise ValueError('Unattributed or stale-turn usage')
                        new=usage(e)
                        if self.total and any(new[k]<self.total[k] for k in new):raise ValueError('Nonmonotonic thread usage')
                        self.total=new;observed=True
                    if p.get('turnId',p.get('turn',{}).get('id'))!=tid:continue
                    value=normalize(e)
                    if value:self.normalized.write(json.dumps({**value,'thread_id':self.thread,'turn_id':tid})+'\n')
                    if e.get('method')=='item/completed' and p['item'].get('type')=='agentMessage':answers.append(p['item'])
                    if e.get('method')=='turn/completed':done=p['turn']
                if done is None:self.rpc.read()
            if not observed:raise ValueError('Missing usage for this turn')
            delta={k:v-(baseline[k] if baseline else 0) for k,v in self.total.items()}
            if delta['cached_input_tokens']>delta['input_tokens'] or delta['reasoning_output_tokens']>delta['output_tokens']:raise ValueError('Invalid per-turn subsets')
            row.update(state=done['status'],usage_delta=delta,usage_cumulative=dict(self.total))
            if done['status']!='completed':raise RuntimeError('Native turn did not complete')
            finals=[a for a in answers if a.get('phase')=='final_answer'];answer=(finals or answers)[-1]['text'] if answers else ''
            (self.out/('turn-'+str(row['index'])+'-answer.txt')).write_text(answer)
            self.record('ready');return answer,dict(row)
        except BaseException as e:
            self.failed=True;row.update(state='FAILED',error=str(e),partial_cumulative=self.total);self.record('failed',str(e));raise

    def close(self):
        if self.closed:return
        self.rpc.close();self.closed=True;audit=None;errors=[]
        try:
            current=self.config_path.read_bytes()
            private_write(self.out/'config.final.private.toml',current)
            audit=validate(self.initial_config,current)
            requests=[json.loads(l) for l in (self.out/'requests.jsonl').read_text().splitlines()]
            starts=[r['params'] for r in requests if r.get('method')=='thread/start']
            if len(starts)!=1 or starts[0].get('model')!=self.model or starts[0].get('config',{}).get('model_reasoning_effort')!=self.effort:
                raise ValueError('Explicit model/effort override missing')
            for r in requests:
                if r.get('method')=='turn/start' and (r['params'].get('model')!=self.model or r['params'].get('effort')!=self.effort):
                    raise ValueError('A native turn changed model/effort')
            start=json.loads((self.out/'thread-start.json').read_text())
            if start.get('model')!=self.model or start.get('reasoningEffort')!=self.effort:raise ValueError('Native effective settings mismatch')
            audit.update(model=self.model,effort=self.effort,native_overrides_verified=True)
        except Exception as exc:
            errors.append(repr(exc))
        # Preserve native evidence even when configuration qualification fails.
        # Capturing evidence does not make that run an admissible denominator.
        try:
            if getattr(self,'turns',None)==[] and (not self.rollout_path or not Path(self.rollout_path).exists()):
                self.capture_status={'state':'NO_MODEL_TURN_NO_ROLLOUT','captured':False,'scope':'Thread setup only; no turn/start or completed task claimed'}
            else:
                if not self.rollout_path:raise ValueError('Missing durable raw rollout')
                self.capture_status=capture(self.rollout_path,self.out/'raw',self.thread)
        except Exception as exc:
            self.capture_status={'error':repr(exc)};errors.append(repr(exc))
        if errors:self.failed=True
        self.record('failed' if self.failed else 'closed','; '.join(errors) or None);self.normalized.close()
        # Preserve the initial raw hash in the existing status field; add the
        # versioned equivalence evidence without rewriting original run protocols.
        path=self.out/'status.json';status=json.loads(path.read_text())
        status['effective_config_binding']=audit
        path.write_text(json.dumps(status,indent=2)+'\n')

    def __enter__(self):return self
    def __exit__(self,*exc):self.close()
