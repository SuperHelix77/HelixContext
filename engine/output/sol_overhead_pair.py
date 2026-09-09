"""Four fresh Sol High calls: unchanged V3, table, table, unchanged V3.

Within-Helix overhead experiment, not a fresh native-off/on qualification.
Cache is observed, never assumed controlled or manually warmed for free.
"""
import json
from pathlib import Path
import shutil
import sys
import time
import app_server_native
from completion_pair import sha,save
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'prototype'))
from evidence import Store
from decision_packet import metadata
from compact_metadata import table
import copy_handles

BASE=Path('/Users/mert/Documents/ChatGPT/Helix/research/sol-integrated-v3-20260909')
MODEL='gpt-5.6-sol'


def prepare(root):
    root=Path(root).resolve();root.mkdir(parents=True,exist_ok=False)
    original=json.loads((BASE/'manifest.json').read_text());hashes=original['preparation']['on']['source_hashes']
    source=(BASE/'tasks/on/records.jsonl').read_bytes();assert sha(source)==hashes['records.jsonl']
    prompt=(BASE/'on-prompt.txt').read_text();assert sha(prompt.encode())==original['prompts']['on']
    rows=[json.loads(l) for l in source.splitlines()];selected=[]
    for group in sorted({r['group'] for r in rows}):
        candidates=[r for r in rows if r['group']==group and r['published'] is True]
        if candidates:
            winner=max(candidates,key=lambda r:r['revision'])
            if winner['approved'] is True and winner['expires_day']>=30:selected.append(winner['id'])
    raw_by_id={json.loads(line)['id']:line for line in source.splitlines(keepends=True)}
    expected=b''.join(raw_by_id[i] for i in selected)
    runs=[]
    for number,variant in enumerate(['v3','table','table','v3']):
        run=root/str(number);cwd=run/'on';cwd.mkdir(parents=True);start=time.perf_counter()
        for name,digest in hashes.items():
            raw=(BASE/'tasks/on'/name).read_bytes();assert sha(raw)==digest
            dest=cwd/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
        store=Store(run/'store');key=store.put(source)['sha256'];mapping={};offset=0
        for line in source.splitlines(keepends=True):
            row=json.loads(line);mapping[row['id']]={'source_sha256':key,'start_byte':offset,'end_byte':offset+len(line)};offset+=len(line)
        catalog,creation=copy_handles.freeze(store,mapping)
        actual=prompt
        if variant=='table':
            view=metadata(store,source,['id','group','revision','published','approved','expires_day'],['payload'])
            old=json.dumps(view['metadata'],ensure_ascii=False,separators=(',',':'));assert actual.count(old)==1
            new='JSON table: each row follows the named fields; JSON value types are unchanged.\n'+json.dumps(table(store,view),ensure_ascii=False,separators=(',',':'))
            actual=actual.replace(old,new)
        (run/'prompt.txt').write_text(actual)
        runs.append({'number':number,'variant':variant,'cwd':str(cwd),'prompt_sha256':sha(actual.encode()),'catalog':catalog,
                     'preparation_seconds':time.perf_counter()-start,'preparation_store_io':dict(store.metrics),'catalog_creation':creation})
    manifest={'schema':'helix.sol.overhead.v1','model':MODEL,'effort':'high','order':['v3','table','table','v3'],'max_native_calls':4,
        'per_call_post_limits':{'input_tokens':80000,'output_tokens':6000},'source_hashes':hashes,'runs':runs,
        'expected_ids':selected,'expected_artifact_sha256':sha(expected),'original_manifest_sha256':sha((BASE/'manifest.json').read_bytes()),
        'driver_sha256':sha(Path(__file__).read_bytes()),'classification':'Counterbalanced development comparison of two Helix candidates; cache state uncontrolled and explicitly reported'}
    save(root/'manifest.json',manifest);return root,manifest


def run(root):
    root,m=prepare(root);rows=[]
    for spec in m['runs']:
        directory=root/str(spec['number']);cwd=Path(spec['cwd']);prompt=(directory/'prompt.txt').read_text()
        assert sha(prompt.encode())==spec['prompt_sha256']
        try:
            response,status=app_server_native.native(MODEL,cwd,prompt,directory/'receipts/on')
            store=Store(directory/'store');start=time.perf_counter()
            completion=copy_handles.complete_response(store,spec['catalog'],response,cwd/'result.jsonl')
            exact=json.loads(response)==m['expected_ids'] and sha((cwd/'result.jsonl').read_bytes())==m['expected_artifact_sha256']
            unchanged=all(sha((cwd/name).read_bytes())==h for name,h in m['source_hashes'].items())
            rows.append({'number':spec['number'],'variant':spec['variant'],'usage':status['usage'],'uncached_input':status['usage']['input_tokens']-status['usage']['cached_input_tokens'],
                'native_elapsed_seconds':status['elapsed_seconds'],'exact_artifact':exact,'source_unchanged':unchanged,
                'completion_seconds':time.perf_counter()-start,'completion_store_io':dict(store.metrics),'completion':completion,
                'native_events_sha256':status['native_events_sha256']})
            if not exact or not unchanged or any(status['usage'][k]>v for k,v in m['per_call_post_limits'].items()):
                save(root/'results.json',{'state':'STOPPED_CHECK_OR_BUDGET','rows':rows});return
            save(root/'results.json',{'state':'RUNNING','rows':rows})
        except Exception as e:
            save(root/'results.json',{'state':'STOPPED_ERROR','error':str(e),'rows':rows});raise
    sums={v:{k:sum(r['usage'][k] for r in rows if r['variant']==v) for k in ['input_tokens','output_tokens','cached_input_tokens']} for v in ('v3','table')}
    for v in sums:sums[v]['uncached_input']=sums[v]['input_tokens']-sums[v]['cached_input_tokens']
    savings={k:100*(1-sums['table'][k]/sums['v3'][k]) for k in ('input_tokens','output_tokens','uncached_input')}
    result={'state':'COMPLETED','classification':m['classification'],'rows':rows,'sums':sums,'savings_vs_v3_percent':savings,
            'limits':'Two repetitions each; not native-off/on, no general parity or guaranteed cache/billing effect.'}
    save(root/'results.json',result);print(json.dumps({k:v for k,v in result.items() if k!='rows'}),flush=True)

if __name__=='__main__':run(sys.argv[1])
