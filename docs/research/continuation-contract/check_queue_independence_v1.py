"""Prospective additional checker; does not amend any frozen benchmark/checker."""
import itertools
from pathlib import Path
import sys

def check(source):
    sequences=0;transitions=0
    for actions in itertools.product(range(10),repeat=3):
        ns={};exec(compile(source,'candidate','exec'),ns);Queue=ns['Queue']
        queues=[Queue(),Queue()];aliases=[q.items for q in queues];expected=[[],[]];cursors=[0,0]
        assert aliases[0] is not aliases[1], 'Distinct live queues must not share their mutable storage'
        for q in queues:assert type(q.items) is list and q.items==[] and q.cursor==0
        for action in actions:
            actor,op=divmod(action,5);q=queues[actor]
            if op==0:
                expected[actor].extend([1,2]);cursors[actor]=len(expected[actor]);assert q.append_batch([1,2])==cursors[actor]
            elif op==1:
                aliases[actor].append(9);expected[actor].append(9)
            elif op==2:
                aliases[actor].clear();expected[actor].clear()
            elif op==3:
                cursors[actor]=len(expected[actor]);assert q.append_batch([])==cursors[actor]
            else:
                try:q.append_batch([3,-1])
                except ValueError:pass
                else:raise AssertionError('Invalid batch accepted')
            for i,obj in enumerate(queues):
                assert obj.items is aliases[i] and obj.items==expected[i] and obj.cursor==cursors[i], 'Cross-instance or per-instance state violation'
            fresh=Queue();assert type(fresh.items) is list and fresh.items==[] and fresh.cursor==0, 'New instance inherits earlier state'
            assert all(fresh.items is not alias for alias in aliases)
            transitions+=1
        sequences+=1
    return {'sequences':sequences,'transitions':transitions}

if __name__=='__main__':print(check(Path(sys.argv[1]).read_text()))
