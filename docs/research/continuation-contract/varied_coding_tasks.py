"""Prospective coding tasks and finite independent checks, frozen before inference.

The candidate sees the contracts, buggy modules and public tests only. This is
researcher-authored development coverage, not a secret population holdout.
"""
import copy
import importlib.util
import itertools
import json
from pathlib import Path
import random
import sys
import unittest


def test_file(body):
    return 'import unittest\nimport solution as s\n\nclass Public(unittest.TestCase):\n' + body


TASKS = {
    'intervals': {
        'task': '''Repair solution.py's normalize(intervals). Input is a finite iterable of pairs; each pair must be a list or tuple of length two with integer (not bool) endpoints start <= end. Reject invalid inputs with ValueError. Negative and arbitrarily large integers are valid. Return a new list of tuple pairs representing the sorted, disjoint union of half-open intervals [start,end). Drop empty intervals and merge both overlaps and touching endpoints. Do not mutate input containers. Preserve the function name/signature and protected test_solution.py/settings.json. Use only Python's standard library.''',
        'module': 'def normalize(intervals):\n    return sorted(tuple(pair) for pair in intervals)\n',
        'tests': test_file('''    def test_merge(self):
        self.assertEqual(s.normalize([(5,9),(0,2),(2,5),(3,3)]), [(0,9)])
    def test_empty(self):
        self.assertEqual(s.normalize(iter([])), [])
    def test_no_mutation(self):
        x=[[3,4],[0,1]]; self.assertEqual(s.normalize(x),[(0,1),(3,4)])
        self.assertEqual(x,[[3,4],[0,1]])
    def test_invalid(self):
        for x in [None, [(2,1)], [(False,3)], [(0,1.0)], [[1]]]:
            with self.assertRaises(ValueError): s.normalize(x)
'''),
    },
    'dependencies': {
        'task': '''Repair solution.py's schedule(graph). graph must be a dict mapping nonempty string node IDs to lists or tuples of nonempty string dependency IDs. Return every key and referenced node exactly once in dependency-before-dependent order. Among all valid orders, return the lexicographically smallest full sequence using ordinary Python string ordering. Repeated dependency IDs are ignored; referenced IDs missing as keys have no dependencies. Reject invalid types/IDs or any cycle (including self cycles) with ValueError. Empty graph returns []. Do not mutate input. Preserve the signature and protected test_solution.py/settings.json. Standard library only.''',
        'module': 'def schedule(graph):\n    return sorted(graph)\n',
        'tests': test_file('''    def test_order(self):
        self.assertEqual(s.schedule({'a':['z'],'b':[]}), ['b','z','a'])
    def test_duplicate_dependency(self):
        self.assertEqual(s.schedule({'b':['a','a']}), ['a','b'])
    def test_empty(self):
        self.assertEqual(s.schedule({}), [])
    def test_cycle(self):
        with self.assertRaises(ValueError): s.schedule({'a':['b'],'b':['a']})
    def test_invalid(self):
        for x in [None, {'a':'b'}, {'':[]}, {'a':[False]}]:
            with self.assertRaises(ValueError): s.schedule(x)
'''),
    },
    'transactions': {
        'task': '''Repair solution.py's apply_batch(balances, events). balances is a dict of nonempty string account IDs to nonnegative integer balances (bool is invalid). events is a finite iterable of dicts containing exactly id, account, delta. id/account must be nonempty strings; delta is an integer, not bool. Return a new dict with events applied in delivery order. An absent account starts at zero; a first event with zero delta creates it. Within this batch, a repeated event id with identical account/delta is a no-op; the same id with a different account or delta is a conflict. Reject malformed input, conflicting IDs or an intermediate negative balance with ValueError. A later credit cannot excuse an earlier overdraft. Failure is atomic with respect to caller inputs: neither balances nor event containers may change, on success or failure. Preserve the signature and protected test_solution.py/settings.json. Standard library only.''',
        'module': 'def apply_batch(balances, events):\n    for event in events:\n        balances[event["account"]] = balances.get(event["account"], 0) + event["delta"]\n    return balances\n',
        'tests': test_file('''    def test_replay(self):
        e={'id':'x','account':'a','delta':2}; b={'a':3}
        self.assertEqual(s.apply_batch(b,[e,e]),{'a':5}); self.assertEqual(b,{'a':3})
    def test_order(self):
        e=[{'id':'x','account':'a','delta':-1},{'id':'y','account':'a','delta':2}]
        with self.assertRaises(ValueError): s.apply_batch({},e)
    def test_conflict(self):
        with self.assertRaises(ValueError): s.apply_batch({},[{'id':'x','account':'a','delta':1},{'id':'x','account':'b','delta':1}])
    def test_invalid(self):
        for b,e in [({'a':True},[]),({},[{'id':'x','account':'a','delta':True}]),({},None)]:
            with self.assertRaises(ValueError): s.apply_batch(b,e)
'''),
    },
}


def expect_error(fn, *args):
    before = copy.deepcopy(args)
    try:
        fn(*args)
    except ValueError:
        pass
    else:
        raise AssertionError(('ValueError required', args))
    assert args == before, 'Invalid-input call mutated caller inputs'


def check_intervals(s):
    rng = random.Random(910301); count = 0
    for _ in range(600):
        pairs = [sorted([rng.randrange(-20,21),rng.randrange(-20,21)]) for _ in range(rng.randrange(20))]
        covered = sorted({v for a,b in pairs for v in range(a,b)})
        expected = []
        for v in covered:
            if expected and expected[-1][1] == v: expected[-1] = (expected[-1][0],v+1)
            else: expected.append((v,v+1))
        before = copy.deepcopy(pairs)
        actual = s.normalize(pairs)
        assert actual == expected and type(actual) is list
        assert all(type(p) is tuple for p in actual) and pairs == before
        count += 1
    huge = 10**200
    assert s.normalize(iter([(huge,huge+2),(-huge,0),(0,huge)])) == [(-huge,huge+2)]
    assert s.normalize([(0,0)]) == []
    invalid = [None, 4, [(1,0)], [(True,3)], [(0,2.0)], [(0,None)], ['ab'], [[1]], [[1,2,3]]]
    for value in invalid: expect_error(s.normalize,value)
    return {'valid_cases':count+2,'invalid_cases':len(invalid)}


def check_dependencies(s):
    rng = random.Random(910302); nodes = ['a','b','c','d']; count = 0
    edges = [(a,b) for a in nodes for b in nodes if a!=b]
    # Brute-force complete orders; independent of a queue/indegree implementation.
    for _ in range(350):
        graph={a:[] for a in nodes}
        for a,b in edges:
            if rng.random()<.22: graph[a].append(b)
        feasible=[list(p) for p in itertools.permutations(nodes) if all(p.index(b)<p.index(a) for a,ds in graph.items() for b in ds)]
        before=copy.deepcopy(graph)
        if feasible: assert s.schedule(graph)==min(feasible)
        else: expect_error(s.schedule,graph)
        assert graph==before;count+=1
    extra=[({},[]),({'z':['a','a'],'b':('x',)},['a','x','b','z']),({'α':['🌀']},['🌀','α'])]
    for graph,expected in extra:
        assert s.schedule(graph)==expected;count+=1
    invalid=[None,[],{'a':'b'},{'':[]},{'a':['']},{'a':[False]},{False:[]},{'a':None},{'a':['a']}]
    for graph in invalid: expect_error(s.schedule,graph)
    return {'valid_or_cycle_cases':count,'invalid_cases':len(invalid)}


def check_transactions(s):
    rng=random.Random(910303);count=0
    for _ in range(400):
        initial={'a':rng.randrange(10),'b':rng.randrange(10)};expected=dict(initial);events=[]
        for i in range(rng.randrange(1,25)):
            account=rng.choice(['a','b','new']);prior=expected.get(account,0)
            delta=rng.randrange(-prior,20);event={'id':str(i),'account':account,'delta':delta}
            events.append(event);expected[account]=prior+delta
            if rng.random()<.3:events.append(dict(event))
        before=copy.deepcopy((initial,events));actual=s.apply_batch(initial,events)
        assert actual==expected and actual is not initial and (initial,events)==before
        assert all(type(v)is int for v in actual.values());count+=1
    assert s.apply_batch({},iter([{'id':'x','account':'a','delta':0}]))=={'a':0}
    good={'id':'x','account':'a','delta':2}
    invalid=[(None,[]),({'':1},[]),({'a':True},[]),({'a':-1},[]),({},None),({},[{}]),({},[1]),
             ({},[dict(good,delta=True)]),({},[dict(good,account='')]),({},[dict(good,id=4)]),
             ({},[dict(good,extra=1)]),({},[good,dict(good,delta=3)]),
             ({},[good,dict(good,account='b')]),({},[dict(good,delta=-1),dict(good,id='y')])]
    for balances,events in invalid:expect_error(s.apply_batch,balances,events)
    # A late failure must not leave a prefix mutation in either input.
    expect_error(s.apply_batch,{'a':1},[good,{'id':'y','account':'a','delta':-4}])
    return {'valid_cases':count+1,'invalid_cases':len(invalid)+1}


CHECKS={'intervals':check_intervals,'dependencies':check_dependencies,'transactions':check_transactions}


def grade(case,cwd):
    cwd=Path(cwd);sys.path.insert(0,str(cwd))
    spec=importlib.util.spec_from_file_location('solution',cwd/'solution.py')
    module=importlib.util.module_from_spec(spec);sys.modules['solution']=module;spec.loader.exec_module(module)
    tests=unittest.defaultTestLoader.discover(str(cwd),pattern='test_solution.py')
    result=unittest.TextTestRunner(stream=sys.stderr).run(tests)
    if not result.wasSuccessful():raise AssertionError('Public tests failed')
    extra=CHECKS[case](module)
    return {'public_tests':result.testsRun,'independent_checks':extra,'finite_checks':'PASS'}


if __name__=='__main__':print(json.dumps(grade(sys.argv[1],sys.argv[2])))
