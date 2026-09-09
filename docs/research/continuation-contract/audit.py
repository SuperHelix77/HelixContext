"""Independent state-transition oracle plus implementation mutation audit.
Finite offline evaluator evidence only: no model calls or production execution.
"""
import hashlib
import itertools
import json
from pathlib import Path
import platform
import sys
import time

HERE=Path(__file__).resolve().parent
GOOD='''class Queue:
    def __init__(self): self.items=[]; self.cursor=0
    def append_batch(self, values):
        pending=[]
        for value in values:
            if type(value) is not int or value<0: raise ValueError('invalid')
            pending.append(value)
        self.items.extend(pending)
        self.cursor=len(self.items)
        return self.cursor
'''
class IntChild(int):pass
class IterFailure(Exception):pass


def exercise(source, operations):
    ns={};exec(source,ns);q=ns['Queue']();alias=q.items;expected=[];cursor=0
    for operation in operations:
        if operation=='alias_add':alias.extend([10,20]);expected.extend([10,20])
        elif operation=='alias_clear':alias.clear();expected.clear()
        elif operation=='alias_replace':alias[:]=[9];expected[:]=[9]
        elif operation=='alias_remove':
            if expected:alias.pop();expected.pop()
        else:
            old_items=list(expected);old_cursor=cursor
            invalid={'bool':True,'subclass':IntChild(2),'negative':-1,'float':1.2,'string':'2','none':None}
            failure=None
            if operation in invalid:
                values=iter([3,invalid[operation],4]);failure=ValueError
            elif operation in ('failure_enter','failure_midway'):
                error=IterFailure(operation);failure=error
                class Broken:
                    yielded=False
                    def __iter__(self):
                        if operation=='failure_enter':raise error
                        return self
                    def __next__(self):
                        assert q.items==old_items and q.cursor==old_cursor and q.items is alias
                        if not self.yielded:
                            self.yielded=True
                            return 7
                        raise error
                values=Broken()
            else:
                payload=[] if operation=='empty' else [0,2,7]
                class Once:
                    calls=0
                    def __iter__(self):
                        self.calls+=1
                        assert self.calls==1
                        for v in payload:
                            assert q.items==old_items and q.cursor==old_cursor and q.items is alias
                            yield v
                values=Once()
            try:result=q.append_batch(values)
            except Exception as exc:
                if failure is ValueError:assert type(exc) is ValueError
                elif isinstance(failure,Exception):assert exc is failure
                else:raise
                assert q.items==old_items and q.cursor==old_cursor and q.items is alias
            else:
                assert failure is None,'invalid input accepted'
                expected.extend(payload);cursor=len(expected)
                assert result==len(expected)
        assert q.items is alias and q.items==expected and q.cursor==cursor
    return True


def audit():
    started=time.perf_counter()
    actions=('append','empty','alias_add','alias_clear','alias_replace','alias_remove','bool','subclass','negative','float','string','none','failure_enter','failure_midway')
    # Exhaustive length-three sequences, plus delayed alias mutation and subsequent recovery.
    sequences=list(itertools.product(actions,repeat=3))
    delayed=tuple(['append']*39+['alias_add','negative','empty','failure_midway','append','alias_clear','bool','empty','alias_replace','failure_enter','append'])
    assert len(delayed)==50;sequences.append(delayed)
    for seq in sequences:exercise(GOOD,seq)
    variants={
        'stale_cursor':GOOD.replace('self.cursor=len(self.items)','self.cursor+=len(pending)'),
        'accept_bool_subclass':GOOD.replace('type(value) is not int','not isinstance(value,int)'),
        'reverse_order':GOOD.replace('extend(pending)','extend(reversed(pending))'),
        'replace_list':GOOD.replace('self.items.extend(pending)','self.items=self.items+pending'),
        'double_consumption':GOOD.replace('pending=[]','list(values)\n        pending=[]'),
        'empty_no_sync':GOOD.replace('self.items.extend(pending)','if not pending: return self.cursor\n        self.items.extend(pending)'),
        'eager_mutation':GOOD.replace('pending.append(value)','pending.append(value)\n            self.items.append(value)').replace('self.items.extend(pending)','pass'),
        'wrap_iteration_exception':GOOD.replace('for value in values:',"try: values=list(values)\n        except Exception: raise RuntimeError('wrapped')\n        for value in values:")}
    failures={}
    for name,code in variants.items():
        for seq in sequences:
            try:exercise(code,seq)
            except Exception as e:
                failures[name]={'witness':list(seq),'exception':type(e).__name__};break
        else:raise AssertionError('Mutation escaped: '+name)
    roots={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (HERE/'CONTRACT.md',Path(__file__))}
    return {'classification':'OFFLINE_FINITE_TRANSITION_AND_MUTATION_AUDIT','native_calls':0,
            'contract_sha256':roots['CONTRACT.md'],'audit_sha256':roots['audit.py'],'reference_sha256':hashlib.sha256(GOOD.encode()).hexdigest(),
            'python':platform.python_version(),'sequences':len(sequences),'transitions':sum(map(len,sequences)),
            'mutation_rejections':failures,'delayed_trajectory_length':50,'reference_pass':True,
            'seconds':time.perf_counter()-started,'parity':'UNTESTED','token_savings':None,
            'limitations':['Finite evaluator coverage, not proof for arbitrary Python programs',
                          'Delayed sequence is an offline state test, not a 50-turn model memory test',
                          'No Engine stale-state gate or persistence implementation tested']}

if __name__=='__main__':
    result=audit();Path(sys.argv[1]).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
