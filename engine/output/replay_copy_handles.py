"""Replay existing semantic selections; no inference or new capability score.

Input directory must contain records.jsonl, selected_ids.json and result.jsonl
from a prior run. Raw inputs stay local. The report exposes hashes and costs.
"""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import time

import tiktoken

ENGINE = Path(__file__).resolve().parents[1]/'prototype'
sys.path.insert(0,str(ENGINE))
import copy_handles as handles
from evidence import Store


def replay(source_directory):
    old=Path(source_directory)
    raw=(old/'records.jsonl').read_bytes()
    ids=json.loads((old/'selected_ids.json').read_text())
    expected=(old/'result.jsonl').read_bytes()
    enc=tiktoken.get_encoding('o200k_base')
    def tokens(value):
        return len(enc.encode(json.dumps(value,separators=(',',':')),disallowed_special=()))
    results={}
    for strategy in ['numeric_aliases','original_ids']:
        with tempfile.TemporaryDirectory(prefix='helix-handles-replay-') as td:
            store=Store(Path(td)/'store');key=store.put(raw)['sha256']
            mapping={};by_id={};legend=[];offset=0
            for index,line in enumerate(raw.splitlines(keepends=True)):
                row=json.loads(line)
                if row['id'] in by_id:raise ValueError('Duplicate source ID')
                handle=str(index) if strategy=='numeric_aliases' else row['id']
                by_id[row['id']]=handle
                legend.append([handle,row['id']])
                mapping[handle]={'source_sha256':key,'start_byte':offset,'end_byte':offset+len(line)}
                offset+=len(line)
            ref,creation=handles.freeze(store,mapping)
            selection=[by_id[i] for i in ids]
            response=json.dumps(selection,separators=(',',':'));dest=Path(td)/'result.jsonl'
            started=time.perf_counter()
            receipt=handles.complete_response(store,ref,response,dest)
            elapsed=time.perf_counter()-started
            if dest.read_bytes()!=expected:raise ValueError('Exact replay mismatch')
            explicit={'schema':'helix.copy.v1','operations':[mapping[k] for k in selection]}
            results[strategy]={'creation':creation,'completion':receipt,'completion_seconds':elapsed,
                'available_handles':len(mapping),'selected_handles':len(selection),'exact_bytes_match':True,
                'payload_tokens':{'explicit_range_plan':tokens(explicit),'prior_compact_id_selection':tokens(ids),
                    'selection':tokens(selection),'additional_alias_legend_if_injected':tokens(legend) if strategy=='numeric_aliases' else 0,
                    'catalog_reference_if_injected':tokens(ref)}}
    return {'classification':'Offline replay of exposed historical selections; no new model call',
        'source_sha256':hashlib.sha256(raw).hexdigest(),'selection_sha256':hashlib.sha256((old/'selected_ids.json').read_bytes()).hexdigest(),
        'artifact_sha256':hashlib.sha256(expected).hexdigest(),'artifact_bytes':len(expected),
        'payload_tokenizer':'o200k_base; syntax counts only, not native usage','strategies':results,
        'decision':'Use original IDs for this caller-completion candidate; renaming spends input to save output syntax.',
        'limits':['Source semantic selection is reused, not retested.',
            'Prior helper already accepted IDs; no novelty or new native saving follows from ID selection.',
            'New hypothesis: remove model-side helper invocation, selection-file creation and hash transcription.',
            'Caller preparation, physical I/O and upstream ingestion not fully timed or priced.',
            'Original IDs must already be present in semantic evidence; zero alias overhead is conditional on that.',
            'Native input/output savings, error-recovery costs and capability parity remain unmeasured.'],
        'implementation_hashes':{name:hashlib.sha256((ENGINE/name).read_bytes()).hexdigest()
            for name in ['copy_handles.py','renderer.py','evidence.py']}}


if __name__=='__main__':
    Path(sys.argv[2]).write_text(json.dumps(replay(sys.argv[1]),indent=2)+'\n')
