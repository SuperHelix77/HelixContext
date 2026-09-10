"""Independent finite graders. Never injected as prepared answers or code."""
import copy
import importlib.util
import json
from pathlib import Path
import random
import subprocess
import sys
import tempfile


def load(path):
    spec=importlib.util.spec_from_file_location('candidate_planner',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def connected_components(intervals,touching):
    # Pairwise overlap graph, independent of the usual sorted sweep implementation.
    groups=[];unseen=set(range(len(intervals)))
    while unseen:
        todo=[unseen.pop()];component=[]
        while todo:
            i=todo.pop();component.append(intervals[i]);a,b=intervals[i]
            for j in list(unseen):
                c,d=intervals[j]
                if (a<=d and c<=b) if touching else (a<d and c<b):
                    unseen.remove(j);todo.append(j)
        groups.append((min(a for a,b in component),max(b for a,b in component)))
    return sorted(groups)


def must_reject(call):
    try:call()
    except ValueError:return
    raise AssertionError('Invalid input was accepted')


def merge_checks(m):
    rng=random.Random(910124);cases=[[],[(1,3),(3,5)],[(1,8),(2,3),(7,9)],
        [(2**60,2**60+1),(2**60+1,2**60+2)]]
    for _ in range(60):
        cases.append([(a,a+rng.randrange(1,8)) for a in [rng.randrange(-15,16) for _ in range(rng.randrange(1,10))]])
    for source in cases:
        for flag in [False,True]:
            before=copy.deepcopy(source);got=m.merge_windows(source,merge_touching=flag)
            assert got==connected_components(source,flag) and source==before
            assert type(got) is list and all(type(x) is tuple and all(type(v) is int for v in x) for x in got)
    for bad in [None,3,'12',[[1,1]],[[2,1]],[[True,3]],[[1,2.0]],[[1]],[[1,2,3]]]:
        must_reject(lambda bad=bad:m.merge_windows(bad))
    must_reject(lambda:m.merge_windows([],merge_touching=1))
    assert m.merge_windows([(1,3),(3,5)])==[(1,3),(3,5)]
    return {'valid_input_variants':len(cases)*2,'invalid_input_variants':10}


def exact_row():
    return {'inventory_tag':'PKG_01_01','label_exact':'cafe\u0301 / Ω / 箱 73109 \t ',
            'sequence_exact':'0000000081700321','windows':[[3,5],[1,3],[2,4],[8,10],[10,12]]}


def expected_plan():
    return [{**{k:v for k,v in exact_row().items() if k!='windows'},
             'windows':[[1,5],[8,10],[10,12]]}]


def build_checks(m):
    source=[exact_row()];before=copy.deepcopy(source);got=m.build_plan(source)
    assert json.loads(json.dumps(got,ensure_ascii=False))==expected_plan() and source==before
    varied=[{**exact_row(),'inventory_tag':'z'},
            {**exact_row(),'inventory_tag':'a','label_exact':'','sequence_exact':''},
            {**exact_row(),'inventory_tag':'z','label_exact':' \t ','sequence_exact':'000'}]
    before=copy.deepcopy(varied);result=m.build_plan(varied)
    assert varied==before and len(result)==3
    for want,got in zip(varied,result):
        assert set(got)=={'inventory_tag','label_exact','sequence_exact','windows'}
        assert all(got[k]==want[k] and type(got[k]) is str for k in ['inventory_tag','label_exact','sequence_exact'])
        assert got['windows']==[(1,5),(8,10),(10,12)]
    for field in ['inventory_tag','label_exact','sequence_exact']:
        for value in [7,None,True]:
            row={**exact_row(),field:value};must_reject(lambda:m.build_plan([row]))
        row=exact_row();del row[field];must_reject(lambda:m.build_plan([row]))
    must_reject(lambda:m.build_plan([{**exact_row(),'windows':[[2,1]]}]))
    for bad in [None,3,'bad',[None],[[]]]:must_reject(lambda bad=bad:m.build_plan(bad))
    return {'exact_label_sequence_and_order':'PASS','invalid_rows_or_containers':18}


def publication_checks(m):
    with tempfile.TemporaryDirectory() as d:
        path=Path(d)/'plan.json';original=b'\x00existing exact state\xff\n'
        for exists in [False,True]:
            if exists:path.write_bytes(original)
            elif path.exists():path.unlink()
            source=[exact_row(),{**exact_row(),'windows':[[4,3]]}];before=copy.deepcopy(source)
            must_reject(lambda:m.write_plan(path,source))
            assert source==before
            assert path.read_bytes()==original if exists else not path.exists()
        m.write_plan(path,[exact_row()]);assert json.loads(path.read_text())==expected_plan()
    return {'invalid_second_row_preserves_existing':'PASS','invalid_second_row_keeps_absent':'PASS','valid_publication':'PASS',
            'atomic_replacement_and_error_propagation':'Requires separate source review/fault injection; these assertions alone do not prove it'}


def replace_fault(source):
    program='''import importlib.util,json,pathlib,sys,tempfile
spec=importlib.util.spec_from_file_location("candidate",sys.argv[1]);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
with tempfile.TemporaryDirectory() as d:
 p=pathlib.Path(d)/"target.json";old=b"existing exact state\\x00\\xff";p.write_bytes(old);attempts=[]
 def hook(event,args):
  if event=="os.rename" and str(args[1])==str(p):
   attempts.append(event);raise OSError("injected replace failure")
 sys.addaudithook(hook)
 failed=False
 try:m.write_plan(p,[{"inventory_tag":"x","label_exact":"x ","sequence_exact":"0001","windows":[[1,2]]}])
 except Exception:failed=True
 assert failed and attempts and p.read_bytes()==old
 print(json.dumps({"replace_failure_observed":True,"existing_bytes_preserved":True}))
'''
    p=subprocess.run([sys.executable,'-B','-c',program,str(Path(source).resolve())],capture_output=True,timeout=10)
    if p.returncode:raise AssertionError('Atomic replace/error propagation gate failed: '+p.stderr.decode())
    return json.loads(p.stdout)


def check(stage,source,artifact=None):
    m=load(source);result={'merge':merge_checks(m)}
    if stage>=38:
        result['build']=build_checks(m)
        if artifact is not None:assert json.loads(Path(artifact).read_text())==expected_plan()
    if stage>=50:
        result['publication']=publication_checks(m)
        result['replace_fault']=replace_fault(source)
    return result
