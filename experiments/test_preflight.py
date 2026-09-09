import json,subprocess,sys
from pathlib import Path
import pytest,tiktoken
from preflight import parse,serialize,representations,snapshot,verify

ENC=tiktoken.get_encoding('o200k_base')
SCRIPT=Path(__file__).with_name('preflight.py')

@pytest.mark.parametrize('text',[
 '[{"x":123456789012345678901234567890,"y":-0}]',
 '[{"x":0.123456789012345678901234567890,"y":1e-300}]',
 '[{"x":true,"y":null},{"x":false,"y":"null"}]',
 '[{"x":"ü\\n\\\"","y":{"a":[1,2]}}]',
 '[{},{}]',
])
def test_table_restores_exact_values(text):
 choices=representations(text,True)
 for mode,_,body in choices:
  if mode=='table-json':
   obj=parse(body)
   restored=[dict(zip(obj['columns'],row)) for row in obj['rows']]
   assert serialize(restored)==serialize(parse(text))
  elif mode=='compact-json':assert serialize(parse(body))==serialize(parse(text))
 assert any(mode=='table-json' for mode,_,_ in choices)

@pytest.mark.parametrize('text',['{"a":1,"a":2}','{"a":NaN}','not json','{"x":Infinity}'])
def test_ambiguous_or_invalid_json_kept(text):
 assert representations(text,True)==[('original','',text)]

def test_nonuniform_no_table():
 assert not any(x[0]=='table-json' for x in representations('[{"a":1},{"b":2}]',True))

def test_snapshot_selects_smallest_without_source_mutation(tmp_path):
 p=tmp_path/'data.json';raw=json.dumps([{'long_field_name':i,'another_field_name':False} for i in range(100)],indent=2).encode();p.write_bytes(raw)
 payload,record=snapshot(p,ENC)
 assert record['tokens']==min(record['alternatives'].values())
 assert record['format'] in ('table-json','constant-table-json','default-table-json')
 assert p.read_bytes()==raw
 assert json.loads(payload)['sha256']==record['sha256']
 assert verify({'files':[record]})==[]
 p.write_text('changed');assert verify({'files':[record]})==[str(p)]
 p.unlink();assert verify({'files':[record]})==[str(p)]

def test_line_numbers(tmp_path):
 p=tmp_path/'log.txt';p.write_text('INFO start\nERROR no success\n')
 payload,record=snapshot(p,ENC,line_numbers=True)
 assert json.loads(payload)['contents']=='1: INFO start\n2: ERROR no success\n'
 assert record['format']=='numbered-original'

@pytest.mark.parametrize('raw,limit',[(b'\xff',100),(b'a\x00b',100),(b'1234',3)])
def test_reject_unusable_files(tmp_path,raw,limit):
 p=tmp_path/'file';p.write_bytes(raw)
 with pytest.raises(ValueError):snapshot(p,ENC,byte_limit=limit)

def test_cli_preserves_sources_and_checks_changes(tmp_path):
 task=tmp_path/'task';task.write_text('Analyze these records.')
 src=tmp_path/'data.json';src.write_text('[{"x":1},{"x":2}]')
 out=tmp_path/'prompt';manifest=tmp_path/'manifest'
 args=[sys.executable,str(SCRIPT),'--task',str(task),'--file',str(src),'--out',str(out),'--manifest',str(manifest)]
 result=subprocess.run(args,capture_output=True,text=True)
 assert result.returncode==0,result.stderr
 assert json.loads(result.stdout)['files']==1
 assert 'untrusted task data' in out.read_text()
 assert subprocess.run([sys.executable,str(SCRIPT),'--check',str(manifest)],capture_output=True).returncode==0
 src.write_text('[]')
 assert subprocess.run([sys.executable,str(SCRIPT),'--check',str(manifest)],capture_output=True).returncode==1
 assert subprocess.run(args,capture_output=True).returncode==2

@pytest.mark.parametrize('scenario',['source_output','same_outputs','duplicate'])
def test_cli_rejects_collisions(tmp_path,scenario):
 task=tmp_path/'task';task.write_text('task')
 src=tmp_path/'src';src.write_text('original')
 out=src if scenario=='source_output' else tmp_path/'out'
 manifest=out if scenario=='same_outputs' else tmp_path/'manifest'
 args=[sys.executable,str(SCRIPT),'--task',str(task),'--file',str(src),'--out',str(out),'--manifest',str(manifest)]
 if scenario=='duplicate':args+=['--file',str(src)]
 assert subprocess.run(args,capture_output=True).returncode==2
 assert src.read_text()=='original'


def test_constants_preserve_types_and_order():
 text='[{"a":1,"b":"same","c":null},{"a":"1","b":"same","c":null}]'
 choices=representations(text,True)
 mode,note,body=next(x for x in choices if x[0]=='constant-table-json')
 data=parse(body)
 assert 'a' not in data['constants']
 expanded=[]
 for row in data['rows']:
  values=dict(zip(data['columns'],row))
  expanded.append({k:data['constants'][k] if k in data['constants'] else values[k] for k in data['original_columns']})
 assert serialize(expanded)==serialize(parse(text))


def test_identical_records_keep_count():
 body=next(x[2] for x in representations('[{"x":false},{"x":false},{"x":false}]',True) if x[0]=='constant-table-json')
 assert len(parse(body)['rows'])==3


def test_sparse_defaults_retain_exceptions_and_types():
 text='[{"id":1,"status":"ok","v":null},{"id":2,"status":"ok","v":null},{"id":3,"status":"failed","v":"null"}]'
 body=next(x[2] for x in representations(text,True) if x[0]=='default-table-json')
 data=parse(body);expanded=[]
 for i,row in enumerate(data['rows']):
  values=dict(data['defaults']);values.update(zip(data['columns'],row));values.update(data['overrides'].get(str(i),{}))
  expanded.append({k:values[k] for k in data['original_columns']})
 assert serialize(expanded)==serialize(parse(text))
 assert data['overrides']['2']['v']=='null'
 assert data['defaults']['v'] is None


def test_sparse_never_conflates_numeric_string():
 body=next(x[2] for x in representations('[{"v":1},{"v":1},{"v":"1"}]',True) if x[0]=='default-table-json')
 data=parse(body)
 assert serialize(data['defaults']['v'])=='1'
 assert serialize(data['overrides']['2']['v'])=='"1"'


def test_prefix_roundtrip_keeps_leading_zeros_unicode_and_overrides():
 text='[{"id":"req-ü-0000","ok":true},{"id":"req-ü-0001","ok":true},{"id":"req-ü-0002","ok":false}]'
 data=parse(next(x[2] for x in representations(text,True) if x[0]=='prefix-default-table-json'));expanded=[]
 for i,row in enumerate(data['rows']):
  values=dict(data['defaults'])
  values.update({k:data['string_prefixes'][k]+v if k in data['string_prefixes'] else v for k,v in zip(data['columns'],row)})
  values.update(data['overrides'].get(str(i),{}))
  expanded.append({k:values[k] for k in data['original_columns']})
 assert serialize(expanded)==serialize(parse(text))


def test_numeric_values_not_prefix_encoded():
 choices=representations('[{"id":100,"ok":true},{"id":101,"ok":true}]',True)
 assert all(x[0]!='prefix-default-table-json' for x in choices)


def test_randomized_roundtrips_all_representations():
    import random
    rng=random.Random(80)
    pool=[None,True,False,0,-1,1.25,'1','null','prefix-0001','prefix-0002','ü\n"',{'nested':[False,'x']}]
    for _ in range(100):
        records=[{'id':f'req-{i:04}','value':rng.choice(pool),'defaults':rng.choice(['same']*8+pool)} for i in range(rng.randint(1,30))]
        text=json.dumps(records,ensure_ascii=False)
        for mode,_,body in representations(text,True):
            data=parse(body)
            if mode in ('original','compact-json'):
                restored=data
            else:
                restored=[]
                original_columns=data.get('original_columns',data['columns'])
                for index,row in enumerate(data['rows']):
                    values=dict(data.get('defaults',data.get('constants',{})))
                    prefixes=data.get('string_prefixes',{})
                    values.update({key:prefixes[key]+value if key in prefixes else value for key,value in zip(data['columns'],row)})
                    values.update(data.get('overrides',{}).get(str(index),{}))
                    restored.append({key:values[key] for key in original_columns})
            assert serialize(restored)==serialize(parse(text)),mode
