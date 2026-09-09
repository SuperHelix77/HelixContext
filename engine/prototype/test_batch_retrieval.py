import base64,json,subprocess,sys
from pathlib import Path
import pytest
from evidence import Store


def fixture(tmp_path):
 s=Store(tmp_path/'store');raw=b'first\r\n\xff\x00\nlast\n'
 source=s.put(raw);key=s.put(json.dumps({'stdout':source}).encode())['sha256']
 return s,key,source,raw


def test_batch_preserves_order_duplicates_binary_and_single_read(tmp_path):
 s,key,source,raw=fixture(tmp_path);reader=Store(s.root)
 result=reader.retrieve_many(key,[(3,3),(1,2),(3,3)])
 spans=result['spans']
 assert spans[0]['text']=='last\n' and spans[0]==spans[2]
 assert base64.b64decode(spans[1]['base64'])==b'first\r\n\xff\x00\n'
 assert result['source']==source and result['io']['object_read_operations']==2
 assert result['io']['object_bytes_read']==len(raw)+len((s.root/'objects'/key).read_bytes())


def test_batch_corruption_on_later_call_is_detected(tmp_path):
 s,key,source,raw=fixture(tmp_path)
 s.retrieve_many(key,[(1,1)])
 (s.root/'objects'/source['sha256']).write_bytes(raw.replace(b'last',b'evil'))
 with pytest.raises(ValueError,match='hash mismatch'):s.retrieve_many(key,[(1,1)])


@pytest.mark.parametrize('ranges',[[],[(0,1)],[(2,1)],[(True,1)],[(1,4)],[(1,1),(2,99)]])
def test_bad_batch_fails_without_durable_writes(tmp_path,ranges):
 s,key,source,raw=fixture(tmp_path)
 before={p.name:p.read_bytes() for p in (s.root/'objects').iterdir()}
 with pytest.raises(ValueError):s.retrieve_many(key,ranges)
 assert before=={p.name:p.read_bytes() for p in (s.root/'objects').iterdir()}


def test_cli_batch(tmp_path):
 s,key,source,raw=fixture(tmp_path)
 p=subprocess.run([sys.executable,str(Path(__file__).with_name('evidence.py')),'--store',str(s.root),'get-many',key,'--range','1','1','--range','3','3'],capture_output=True,text=True,check=True)
 assert [r['text'] for r in json.loads(p.stdout)['spans']]==['first\r\n','last\n']
