"""Offline replay of an already observed answer; never seeds a native prompt."""
import difflib
import json
from pathlib import Path
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
sys.path.insert(0,str(REPO/'engine/prototype'))
import pilot
from indexed_tool import IndexedEditTool,scope_snapshot
from indexed_edits import lines
from indexed_source import render
from source_packet import render as previous_render
from checked_tool import encoded,digest


def replay(root):
    root=Path(root).resolve();root.mkdir(parents=True,exist_ok=False)
    files={n:(pilot.INPUT/'baseline'/n).read_bytes() for n in pilot.FILES[:3]}
    files[pilot.FILES[3]]=(pilot.INPUT/pilot.FILES[3]).read_bytes()
    raw=files[pilot.TARGET]
    expected=(HERE.with_name('native-output-v2')/'artifacts/sol-high/on/workflow_memory.py').read_bytes()
    edits=[]
    for tag,i,j,a,b in difflib.SequenceMatcher(a=lines(raw),b=lines(expected),autojunk=False).get_opcodes():
        if tag!='equal':edits.append({'start_line':i+1,'delete_lines':j-i,'insert':b''.join(lines(expected)[a:b]).decode()})
    # Only this offline replay sees the solved V2 output. Native prepare() imports
    # the unchanged baseline and task and cannot load this request/result.
    req={'threadId':'offline','turnId':'replay','callId':'one','tool':'helix_apply_edits',
         'arguments':{'expected_version':0,'edits':edits}}
    cwd=root/'workspace';cwd.mkdir()
    for n,b in files.items():(cwd/n).write_bytes(b)
    (cwd/(pilot.TARGET+'.helix-lock')).touch()
    bound=pilot.workspace.initialize(cwd)
    initial=scope_snapshot(cwd,pilot.FILES)
    protected={n:digest(b) for n,b in files.items() if n!=pilot.TARGET}
    binding=digest(encoded({'source':digest(raw),'protected':protected,'head':initial['head']}))
    def authority():
        pilot.scope(cwd,bound)
        if any(digest((cwd/n).read_bytes())!=h for n,h in protected.items()):raise ValueError('Protected drift')
        return binding
    def checker(output,directory):
        directory.mkdir();stage=directory/'stage';stage.mkdir()
        for n,b in files.items():(stage/n).write_bytes(output if n==pilot.TARGET else b)
        result=pilot.grade(stage,directory/'checks')
        if result['checks']=='PASS':result['summary']='23 public/regression tests and 94 independent finite cases passed'
        return result
    start=time.perf_counter()
    tool=IndexedEditTool(root/'tool',cwd/pilot.TARGET,raw,authority,checker,expected_binding=binding,
                         scope_observer=lambda:scope_snapshot(cwd,pilot.FILES))
    response=tool(req);elapsed=time.perf_counter()-start
    assert response['success'] and (cwd/pilot.TARGET).read_bytes()==expected
    packet=json.loads(response['contentItems'][0]['text']);diff=packet['review']['exact_diff']
    independent=root/'diff-replay';independent.mkdir();(independent/pilot.TARGET).write_bytes(raw)
    check=subprocess.run(['git','apply','--whitespace=nowarn','-'],input=diff.encode(),cwd=independent,capture_output=True)
    assert check.returncode==0 and (independent/pilot.TARGET).read_bytes()==expected
    source_view,manifest=render(files,[pilot.TARGET],version=0)
    previous_view,_=previous_render(files,version=0)
    native_calls=json.loads((HERE.with_name('native-output-v2')/'artifacts/sol-high/on/internal-calls.json').read_text())
    old=next(x['params']['arguments'] for x in native_calls if x.get('method')=='item/tool/call')
    anatomy=json.loads((HERE.with_name('native-output-v2')/'artifacts/ANATOMY.json').read_text())['sol-high']
    retained=[anatomy[1]['segments'][i]['usage'] for i in (1,3)]
    floor={key:sum(row[key] for row in retained) for key in ('inputTokens','outputTokens')}
    control={key:sum(row['usage'][key] for row in anatomy[0]['segments']) for key in floor}
    result={'classification':'Offline engineering and conditional trace arithmetic; no model evidence',
        'native_calls':0,'solved_edits_used_only_for_offline_replay':True,
        'observed_v2_artifact_reproduced':True,'source_sha256':digest(expected),
        'finite_checks':'23 public/regression tests +94 independent cases PASS',
        'independent_diff_application':'PASS','scope':packet['scope'],
        'prior_edit_argument_bytes':len(encoded(old)),'indexed_argument_bytes':len(encoded(req['arguments'])),
        'prior_hot_view_bytes':len(previous_view.encode()),'indexed_hot_view_bytes':len(source_view.encode()),
        'cold_bytes':sum(len(files[n]) for n in pilot.FILES[1:]),'source_manifest':manifest,
        'receipt_bytes':len(response['contentItems'][0]['text'].encode()),
        'store_io_including_constructor':dict(tool.store.metrics),'elapsed_seconds':elapsed,
        'scope_observation_commands_per_snapshot':3,'whole_physical_io':'UNKNOWN',
        'retained_segments_2_and_4':floor,
        'conditional_saving_if_segments_1_and_3_disappeared':{
            key:100*(1-floor[key]/control[key]) for key in floor},
        'counterfactual_limit':'Deleting entire observed segments is optimistic and unproven, not a model lower bound or measured saving'}
    pilot.save(root/'offline-request.json',req);pilot.save(root/'response.json',response)
    (root/'source-view.txt').write_text(source_view)
    pilot.save(root/'receipt.json',result);pilot.save(HERE/'OFFLINE.json',result)
    print(json.dumps({k:v for k,v in result.items() if k not in ('source_manifest','scope')}))


if __name__=='__main__':replay(sys.argv[1])
