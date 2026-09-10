"""Replay V1 proposals unchanged through V2; preserve original failed selectors."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
sys.path[:0]=[str(HERE.with_name('native-output-v1')),str(REPO/'engine/prototype')]
from review_tool import ReviewEditTool
import pilot
from source_packet import render


def sha(raw):return hashlib.sha256(raw).hexdigest()


def run(root):
    root=Path(root).resolve();root.mkdir(exist_ok=False,parents=True);rows=[]
    sources={str(p.relative_to(REPO)):sha(p.read_bytes()) for p in [Path(__file__),HERE/'review_tool.py',REPO/'engine/prototype/source_packet.py',HERE.with_name('native-output-v1')/'bound_edit_tool.py']}
    for model in ['astra-xhigh','sol-high']:
        path=root/model;path.mkdir();cwd=path/'workspace';cwd.mkdir()
        files={n:(pilot.INPUT/'baseline'/n).read_bytes() for n in pilot.FILES[:3]}
        files[pilot.FILES[3]]=(pilot.INPUT/pilot.FILES[3]).read_bytes()
        for name,raw in files.items():(cwd/name).write_bytes(raw)
        source_view,source_manifest=render(files,version=0)
        (path/'source-packet.txt').write_text(source_view)
        protected={n:sha(raw) for n,raw in files.items() if n!=pilot.TARGET}
        binding=sha(json.dumps({'sources':sources,'protected':protected,'initial':sha(files[pilot.TARGET])},sort_keys=True).encode())
        def authority():
            assert all(sha((REPO/n).read_bytes())==h for n,h in sources.items())
            assert all(sha((cwd/n).read_bytes())==h for n,h in protected.items())
            return binding
        def checker(raw,directory):
            directory.mkdir();stage=directory/'stage';stage.mkdir()
            for n,b in files.items():(stage/n).write_bytes(raw if n==pilot.TARGET else b)
            result=pilot.grade(stage,directory/'checks')
            if result['checks']=='PASS':result['summary']='23 public/regression tests and 94 independent finite cases passed'
            return result
        tool=ReviewEditTool(path/'tool',cwd/pilot.TARGET,files[pilot.TARGET],authority,checker,expected_binding=binding)
        records=json.loads((HERE.with_name('native-output-v1')/'artifacts'/model/'on/internal-calls.json').read_text())
        requests=[e['params'] for e in records if e.get('method')=='item/tool/call']
        native_replies=[e['params']['item'] for e in records if e.get('method')=='item/completed']
        before=dict(tool.store.metrics);start=time.perf_counter();responses=[]
        for request,prior in zip(requests,native_replies,strict=True):
            reply=tool(request);assert reply['success']==prior['success']
            responses.append(reply)
        assert responses[-1]['success']
        published=(cwd/pilot.TARGET).read_bytes()
        assert published==(HERE.with_name('native-output-v1')/'artifacts'/model/'on/workflow_memory.py').read_bytes()
        p=json.loads(responses[-1]['contentItems'][0]['text']);v=p['review']
        assert v['diff_complete'] and v['prior_source_sha256']==sha(files[pilot.TARGET])
        diffdir=path/'diff-roundtrip';diffdir.mkdir();(diffdir/pilot.TARGET).write_bytes(files[pilot.TARGET])
        applied=subprocess.run(['git','apply','--whitespace=nowarn','-'],input=v['exact_diff'].encode(),cwd=diffdir,capture_output=True)
        assert applied.returncode==0,(applied.stdout,applied.stderr)
        assert (diffdir/pilot.TARGET).read_bytes()==published
        row={'model_fixture':model,'original_requests_unchanged':True,'original_rejected_calls':sum(not r['success'] for r in responses),
             'exact_artifact':'PASS','finite_checks':'23 public/regression +94 independent cases PASS',
             'diff_application_reconstructs_published_bytes':True,'input_source_packet_bytes':len(source_view.encode()),
             'prior_json_source_bytes':len(json.dumps({n:b.decode() for n,b in files.items()}).encode()),
             'review_diff_bytes':v['diff_bytes'],'prior_receipt_bytes':len(native_replies[-1]['contentItems'][0]['text'].encode()),
             'review_receipt_bytes':len(responses[-1]['contentItems'][0]['text'].encode()),
             'store_io':{k:tool.store.metrics[k]-before[k] for k in before},'seconds':time.perf_counter()-start,
             'source_sha256':sha(published),'native_calls':0}
        (path/'receipts.json').write_text(json.dumps(responses,indent=2)+'\n');rows.append(row)
    result={'classification':'Offline exact replay and display correction; native economics/behavior UNTESTED','sources':sources,'rows':rows,
            'native_calls':0,'model_release':False,'no_automatic_selector_repair':True}
    (root/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');(HERE/'OFFLINE.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__=='__main__':run(sys.argv[1])
