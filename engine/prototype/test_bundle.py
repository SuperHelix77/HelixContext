import copy,sys
from concurrent.futures import ThreadPoolExecutor
import pytest
from evidence import Store,run
from bundle import commit,load


def fixture(tmp_path):
 s=Store(tmp_path/'store')
 raw=b'incidental=000.250\r\nERROR cursor=0\n'
 p=run(s,[sys.executable,'-c',f'import sys;sys.stdout.buffer.write({raw!r})'],tmp_path,'fixture')
 key=p['raw']['stdout']['sha256']
 plan={'schema':'helix.copy.v1','operations':[{'source_sha256':key,'start_byte':0,'end_byte':len(raw)}]}
 return s,p,plan,raw


def test_capture_recover_render_and_restart(tmp_path):
 s,p,plan,raw=fixture(tmp_path)
 spans=s.retrieve_many(p['receipt'],[(1,1),(2,2)])
 assert ''.join(r['text'] for r in spans['spans']).encode()==raw
 r=commit(s,'workflow',p,plan,0)
 recovered=load(Store(s.root),'workflow')
 assert recovered['artifact']==raw and recovered['revision']==r['revision']==1
 assert recovered['packet']['receipt']==p['receipt']


@pytest.mark.parametrize('failure',['late_copy','unbound_source','stale_revision','packet_type','corrupt_source'])
def test_composed_failure_keeps_canonical_bundle(tmp_path,failure):
 s,p,plan,raw=fixture(tmp_path);first=commit(s,'workflow',p,plan,0)
 expected=1
 if failure=='late_copy':plan['operations'].append({'source_sha256':p['raw']['stdout']['sha256'],'start_byte':0,'end_byte':len(raw)+1})
 if failure=='unbound_source':plan['operations'][0]={'source_sha256':s.put(b'other')['sha256'],'start_byte':0,'end_byte':5}
 if failure=='stale_revision':expected=0
 if failure=='packet_type':p['exit_code']=False
 if failure=='corrupt_source':(s.root/'objects'/p['raw']['stdout']['sha256']).write_bytes(b'corrupt')
 with pytest.raises(ValueError):commit(s,'workflow',p,plan,expected)
 # Read pointer directly: corrupted cold evidence must still fail load.
 import sqlite3
 with sqlite3.connect(s.root/'bundles.sqlite3') as db:
  assert db.execute('SELECT revision,object FROM bundles WHERE name=?',('workflow',)).fetchone()==(1,first['bundle_sha256'])
 if failure=='corrupt_source':
  with pytest.raises(ValueError):load(s,'workflow')
 else:assert load(s,'workflow')['artifact']==raw


def test_two_writers_only_one_advances(tmp_path):
 s,p,plan,raw=fixture(tmp_path);commit(s,'workflow',p,plan,0)
 def writer(_):
  try:return commit(Store(s.root),'workflow',p,copy.deepcopy(plan),1)['revision']
  except ValueError:return 'stale'
 with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(writer,range(2)))
 assert sorted(map(str,results))==['2','stale']
 assert load(s,'workflow')['revision']==2
