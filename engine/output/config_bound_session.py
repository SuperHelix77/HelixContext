"""Versioned observed session pinned to effective, explicitly overridden settings.

The native API already fixes model and effort for every benchmark turn. Changes
to those two GUI defaults may be recorded without changing that task. Every other
parsed config value remains bound. Private full snapshots are never public data.
"""
import hashlib
import json
import os
from pathlib import Path
import tomllib
import observed_session
from raw_receipts import capture

OVERRIDDEN=('model','model_reasoning_effort')


def same(a,b):
    if type(a) is not type(b):return False
    if isinstance(a,dict):return a.keys()==b.keys() and all(same(a[k],b[k]) for k in a)
    if isinstance(a,list):return len(a)==len(b) and all(same(x,y) for x,y in zip(a,b))
    return a==b


def validate(initial,current):
    before=tomllib.loads(initial.decode());after=tomllib.loads(current.decode())
    missing=object()
    changes=[k for k in sorted(before.keys()|after.keys()) if not same(before.get(k,missing),after.get(k,missing))]
    if any(k not in OVERRIDDEN for k in changes):raise ValueError('Non-overridden Codex configuration changed')
    return {'schema':'helix.effective-config.v1','initial_sha256':hashlib.sha256(initial).hexdigest(),
            'final_sha256':hashlib.sha256(current).hexdigest(),'changed_top_level_keys':changes,
            'overridden_fields':list(OVERRIDDEN),'other_parsed_settings_unchanged':True}


def private_write(path,raw):
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'wb') as stream:stream.write(raw)


class Session(observed_session.Session):
    def __init__(self,*args,**kwargs):
        path=Path(os.environ.get('CODEX_HOME',str(Path.home()/'.codex')))/'config.toml'
        self.initial_config=path.read_bytes()
        super().__init__(*args,**kwargs)
        if hashlib.sha256(self.initial_config).hexdigest()!=self.config_hash:
            self.failed=True;self.close();raise ValueError('Config changed during session initialization')
        private_write(self.out/'config.initial.private.toml',self.initial_config)

    def close(self):
        if self.closed:return
        self.rpc.close();self.closed=True;audit=None;errors=[]
        try:
            current=self.config_path.read_bytes()
            private_write(self.out/'config.final.private.toml',current)
            audit=validate(self.initial_config,current)
            requests=[json.loads(l) for l in (self.out/'requests.jsonl').read_text().splitlines()]
            starts=[r['params'] for r in requests if r.get('method')=='thread/start']
            if len(starts)!=1 or starts[0].get('model')!=self.model or starts[0].get('config',{}).get('model_reasoning_effort')!='high':
                raise ValueError('Explicit model/effort override missing')
            for r in requests:
                if r.get('method')=='turn/start' and (r['params'].get('model')!=self.model or r['params'].get('effort')!='high'):
                    raise ValueError('A native turn changed model/effort')
            start=json.loads((self.out/'thread-start.json').read_text())
            if start.get('model')!=self.model or start.get('reasoningEffort')!='high':raise ValueError('Native effective settings mismatch')
            audit.update(model=self.model,effort='high',native_overrides_verified=True)
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
