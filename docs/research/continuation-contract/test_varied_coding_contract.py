"""Offline grader checks only. These implementations are never candidate inputs."""
import copy
import itertools
import types
import pytest
import varied_coding_tasks as tasks


def intervals(items):
    try:items=list(items)
    except TypeError:raise ValueError()
    for p in items:
        if not isinstance(p,(list,tuple)) or len(p)!=2 or any(not isinstance(v,int) or isinstance(v,bool) for v in p) or p[0]>p[1]:raise ValueError()
    events={}
    for a,b in items:
        events[a]=events.get(a,0)+1;events[b]=events.get(b,0)-1
    active=0;start=None;out=[]
    for x in sorted(events):
        prev=active;active+=events[x]
        if prev==0 and active>0:start=x
        if prev>0 and active==0:out.append((start,x))
    return out


def dependencies(graph):
    if not isinstance(graph,dict):raise ValueError()
    for k,ds in graph.items():
        if not isinstance(k,str) or not k or not isinstance(ds,(list,tuple)) or any(not isinstance(d,str) or not d for d in ds):raise ValueError()
    nodes=sorted(set(graph)|{d for ds in graph.values() for d in ds})
    for p in itertools.permutations(nodes):
        if all(p.index(d)<p.index(k) for k,ds in graph.items() for d in ds):return list(p)
    raise ValueError()


def transactions(balances,events):
    if not isinstance(balances,dict) or any(not isinstance(k,str) or not k or not isinstance(v,int) or isinstance(v,bool) or v<0 for k,v in balances.items()):raise ValueError()
    try:events=list(events)
    except TypeError:raise ValueError()
    out=copy.deepcopy(balances);seen={}
    for e in events:
        if not isinstance(e,dict) or set(e)!={'id','account','delta'} or any(not isinstance(e[k],str) or not e[k] for k in ('id','account')) or not isinstance(e['delta'],int) or isinstance(e['delta'],bool):raise ValueError()
        key=e['id'];payload=(e['account'],e['delta'])
        if key in seen:
            if seen[key]!=payload:raise ValueError()
            continue
        seen[key]=payload;value=out.get(e['account'],0)+e['delta']
        if value<0:raise ValueError()
        out[e['account']]=value
    return out


@pytest.mark.parametrize('case,fn,name',[('intervals',intervals,'normalize'),('dependencies',dependencies,'schedule'),('transactions',transactions,'apply_batch')])
def test_independent_grader_accepts_valid_reference(case,fn,name):
    tasks.CHECKS[case](types.SimpleNamespace(**{name:fn}))


@pytest.mark.parametrize('case',list(tasks.TASKS))
def test_original_defects_are_caught(case):
    module=types.ModuleType('buggy');exec(tasks.TASKS[case]['module'],module.__dict__)
    with pytest.raises((AssertionError,ValueError,TypeError)):
        tasks.CHECKS[case](module)


def test_identity_replay_is_not_account_aliasing():
    balances={'a':0};events=[{'id':'x','account':'a','delta':1},{'id':'x','account':'b','delta':1}]
    tasks.expect_error(transactions,balances,events)


def test_topology_is_lexicographic_order_not_sorted_layers():
    assert dependencies({'b':['a'],'c':[]})==['a','b','c']


def test_interval_empty_bridge_does_not_fill_gap():
    assert intervals([(0,1),(2,2),(3,4)])==[(0,1),(3,4)]
