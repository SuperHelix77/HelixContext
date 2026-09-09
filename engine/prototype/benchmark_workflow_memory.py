"""Deterministic payload/cost falsifier, not a native model benchmark."""
import argparse
import hashlib
import json
import time
from pathlib import Path
import tiktoken
from evidence import Store
from workflow_memory import Memory


def wire(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'))


def count(value,tokenizer):
    return len(tokenizer.encode(wire(value),disallowed_special=()))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--artifacts',required=True);parser.add_argument('--output',required=True);parser.add_argument('--shared-replay',action='store_true')
    args=parser.parse_args();root=Path(args.artifacts);root.mkdir(parents=True,exist_ok=False)
    tokenizer=tiktoken.get_encoding('o200k_base')
    # The decisive old value is retained before any future query is provided.
    history=[{'event_id':'1','text':'The violet envelope carries code 000.250; preserve its spelling.'}]
    for i in range(2,51):
        history.append({'event_id':str(i),'text':'\n'.join(f'Job {i}, observation {j}: stage completed, remaining checks pending.' for j in range(30))})
    (root/'history.json').write_text(wire(history))
    store=Store(root/'memory');memory=Memory(store)
    start=time.perf_counter()
    for item in history:memory.record('p','s',item['event_id'],item['text'].encode())
    creation=time.perf_counter()-start;creation_io=dict(store.metrics)
    cases=[]
    for name,query,exhaustive in [('exact_old_fact','violet',False),('alias_miss_exhaustive_recovery','purple',True),('all_history_required','',True)]:
        before=dict(store.metrics);start=time.perf_counter();messages=[]
        found=[]
        if query:
            messages.append({'request':'search','project':'p','query':query})
            found=memory.search('p',query)
            messages.append({'response':found})
        if exhaustive and args.shared_replay:
            messages.append({'request':'replay','project':'p','session':'s'})
            replay=memory.replay('p','s');messages.append({'response':replay})
            assert not replay['has_more'] and replay['history']==history
            evidence=[{'event_id':item['event_id'],'raw':item['text'].encode()} for item in replay['history']]
        elif exhaustive:
            messages.append({'request':'timeline','project':'p','session':'s','limit':50})
            found=memory.timeline('p','s',limit=50)
            messages.append({'response':found})
        if not (exhaustive and args.shared_replay):
            ids=[item['record_hash'] for item in found]
            messages.append({'request':'retrieve','project':'p','record_hashes':ids})
            evidence=memory.retrieve('p',ids)
            messages.append({'response':[{**{k:v for k,v in item.items() if k!='raw'},'text':item['raw'].decode()} for item in evidence]})
        elapsed=time.perf_counter()-start
        expected=history if exhaustive else history[:1]
        assert [(item['event_id'],item['raw'].decode()) for item in evidence]==[(item['event_id'],item['text']) for item in expected]
        baseline=count({'history':history},tokenizer)
        payload=sum(count(message,tokenizer) for message in messages)
        (root/(name+'.json')).write_text(wire(messages))
        cases.append({'name':name,'query':query,'returned_records':len(evidence),'exact_sources_match':True,
            'full_history_payload_tokens':baseline,'memory_request_response_payload_tokens':payload,
            'payload_delta_percent':100*(1-payload/baseline),'seconds':elapsed,
            'store_io':{k:store.metrics[k]-before[k] for k in before},
            'routing':'predeclared exact lookup' if not exhaustive else 'predeclared exhaustive fallback; no learned query selection'})
    report={'schema':'helix.memory_payload_falsifier.v1','classification':'synthetic payload and application-cost measurement only',
        'tokenizer':'o200k_base; not asserted to match native model billing','shared_replay':args.shared_replay,'creation_seconds':creation,
        'creation_store_io':creation_io,'cases':cases,
        'logical_retained_bytes':sum(p.stat().st_size for p in store.root.rglob('*') if p.is_file()),
        'history_bytes':len((root/'history.json').read_bytes()),'artifacts':str(root.resolve()),
        'native_input_tokens':None,'native_output_tokens':None,
        'limits':['Full replay is a surface reference, not an optimized ordinary-agent control.',
                  'Queries and fallback choices are predeclared; no model capability evaluation.',
                  'Request and response payloads both counted; platform prompts, future replay, inference and semantic answer excluded.',
                  'Creation, retrieval, logical storage measured separately; SQLite/physical traffic, all CPU and money incomplete.',
                  'No speed comparison with ordinary targeted search and no combined savings claim.'],
        'source_hashes':{name:hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() for name in ['benchmark_workflow_memory.py','workflow_memory.py','evidence.py']},
        'artifact_hashes':{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(root.rglob('*')) if p.is_file()}}
    Path(args.output).write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['creation_seconds','logical_retained_bytes','history_bytes','cases']}))


if __name__=='__main__':main()
