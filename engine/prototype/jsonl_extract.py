"""Exact decoded text-line selection from declared JSONL event records.

Raw bytes are archived before parsing. This is an explicit reader, not a shell
rewrite, semantic summary or assertion that unselected evidence is irrelevant.
"""
import argparse
import json
from pathlib import Path
from evidence import Store


def encode(value):return json.dumps(value,separators=(',',':'),ensure_ascii=True,allow_nan=False).encode()


def unique(pairs):
    result={}
    for key,value in pairs:
        if key in result:raise ValueError('Duplicate JSON key')
        result[key]=value
    return result


def reject_constant(value):raise ValueError('Nonstandard JSON constant')


def extract(store,raw,query,max_bytes=6000,max_matches=8):
    if not isinstance(raw,bytes) or not isinstance(query,str) or not query:
        raise ValueError('Exact bytes and nonempty literal query required')
    if type(max_bytes) is not int or max_bytes<800 or type(max_matches) is not int or max_matches<1:
        raise ValueError('Invalid projection budget')
    source=store.put(raw)
    base={'schema':'helix.jsonl_lines.v1','source':source,
          'coverage':'partial literal matches in decoded text; other fields/lines remain in exact raw source'}
    # Parse the entire source before publishing any supported projection. A bad
    # late record must not leave an apparently complete early answer.
    records=[]
    try:
        for number,line in enumerate(raw.split(b'\n'),1):
            if not line.strip():continue
            record=json.loads(line.decode('utf-8'),object_pairs_hook=unique,parse_constant=reject_constant)
            if not isinstance(record,dict) or not isinstance(record.get('event_id'),str) or not isinstance(record.get('text'),str):
                raise ValueError('Unsupported event schema')
            record['text'].encode('utf-8');record['event_id'].encode('utf-8')
            records.append((number,record))
    except (ValueError,UnicodeError):
        return {**base,'status':'UNSUPPORTED','action':'Use exact raw source; no partial parse is accepted'}
    total=sum(query in line for _,record in records for line in record['text'].splitlines(keepends=True))
    result={**base,'status':'PROJECTED','records':len(records),'query':query,
            'matching_lines':total,'omitted_matching_lines':total,'matches':[]}
    if len(encode(result))>max_bytes:raise ValueError('Metadata exceeds budget; raw source remains archived')
    for number,record in records:
        for text_line,line in enumerate(record['text'].splitlines(keepends=True),1):
            if query not in line or len(result['matches'])>=max_matches:continue
            candidate={'record_line':number,'event_id':record['event_id'],'text_line':text_line,'text':line}
            result['matches'].append(candidate);result['omitted_matching_lines']-=1
            if len(encode(result))>max_bytes:
                result['matches'].pop();result['omitted_matching_lines']+=1
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--store',required=True);p.add_argument('--max-bytes',type=int,default=6000)
    p.add_argument('source');p.add_argument('query');args=p.parse_args()
    store=Store(args.store)
    result=extract(store,Path(args.source).read_bytes(),args.query,max_bytes=args.max_bytes)
    if result['status']=='PROJECTED':verify(store,result,result['source']['sha256'],args.query)
    print(encode(result).decode());return 0 if result['status']=='PROJECTED' else 2


def verify(store,packet,source_hash,query):
    """Check selected positions and all match counts without calling extract.

    Caller binds the intended source/query. This validates structural extraction,
    not whether the literal query captures all task-relevant information.
    """
    if packet.get('schema')!='helix.jsonl_lines.v1' or packet.get('status')!='PROJECTED':
        raise ValueError('Supported projection required')
    if packet.get('query')!=query or packet.get('source',{}).get('sha256')!=source_hash:
        raise ValueError('Source/query binding mismatch')
    raw=store.get(source_hash)
    if packet['source'].get('bytes')!=len(raw):raise ValueError('Source length mismatch')
    expected={};records=0
    for n,line in enumerate(raw.split(b'\n'),1):
        if not line.strip():continue
        obj=json.loads(line.decode('utf-8'),object_pairs_hook=unique,parse_constant=reject_constant)
        if not isinstance(obj,dict) or not isinstance(obj.get('event_id'),str) or not isinstance(obj.get('text'),str):
            raise ValueError('Unsupported source schema')
        records+=1
        for k,text in enumerate(obj['text'].splitlines(keepends=True),1):
            if query in text:expected[(n,k)]={'record_line':n,'event_id':obj['event_id'],'text_line':k,'text':text}
    matches=packet.get('matches')
    if not isinstance(matches,list):raise ValueError('Missing matches')
    previous=(0,0)
    for match in matches:
        if not isinstance(match,dict) or type(match.get('record_line')) is not int or type(match.get('text_line')) is not int:
            raise ValueError('Invalid match location')
        location=(match['record_line'],match['text_line'])
        if location<=previous or expected.get(location)!=match:raise ValueError('Altered, duplicate or unordered source evidence')
        previous=location
    for key,value in [('records',records),('matching_lines',len(expected)),('omitted_matching_lines',len(expected)-len(matches))]:
        if type(packet.get(key)) is not int or packet[key]!=value:raise ValueError('Incorrect count')
    return True


if __name__=='__main__':raise SystemExit(main())
