import hashlib,json,os,sys
from pathlib import Path
import pytest
from guarded_edit import run

def setup(tmp_path,test=None):
 p=tmp_path/'target.py';p.write_text('old\n');p.chmod(0o640)
 s={'file':'target.py','sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'test':test or [sys.executable,'-c','assert open("target.py").read()=="new\\n"']}
 m=tmp_path/'manifest.json';m.write_text(json.dumps(s));return p,m

def test_edit_and_real_test(tmp_path):
 p,m=setup(tmp_path);assert run(m,b'new\n')==0;assert p.stat().st_mode&0o777==0o640

def test_stale_preserved(tmp_path):
 p,m=setup(tmp_path);p.write_text('user change\n')
 with pytest.raises(ValueError,match='stale'):run(m,b'new\n')
 assert p.read_text()=='user change\n'

def test_failing_test_propagates(tmp_path):
 p,m=setup(tmp_path,[sys.executable,'-c','print("diagnostic");raise SystemExit(7)'])
 assert run(m,b'new\n')==7;assert p.read_text()=='new\n'

def test_symlink_rejected(tmp_path):
 p,m=setup(tmp_path);p.rename(tmp_path/'original');p.symlink_to(tmp_path/'original')
 with pytest.raises(ValueError,match='regular'):run(m,b'new\n')
 assert (tmp_path/'original').read_text()=='old\n'

def test_invalid_encoding_no_edit(tmp_path):
 p,m=setup(tmp_path)
 with pytest.raises(ValueError):run(m,b'\xff')
 assert p.read_text()=='old\n'

def test_bad_command_no_edit(tmp_path):
 p,m=setup(tmp_path);s=json.loads(m.read_text());s['test']='true';m.write_text(json.dumps(s))
 with pytest.raises(ValueError,match='argv'):run(m,b'new\n')
 assert p.read_text()=='old\n'

def test_escape_rejected(tmp_path):
 p,m=setup(tmp_path);s=json.loads(m.read_text());s['file']='../external';m.write_text(json.dumps(s))
 with pytest.raises(ValueError):run(m,b'new\n')

def test_insert_keeps_original_lines(tmp_path):
 p,m=setup(tmp_path,[sys.executable,'-c','assert open("target.py").read()=="new\\nold\\n"'])
 assert run(m,b'new\n',1)==0
 assert p.read_text()=='new\nold\n'

@pytest.mark.parametrize('line',[0,3,-1])
def test_invalid_insert_no_write(tmp_path,line):
 p,m=setup(tmp_path)
 with pytest.raises(ValueError,match='line'):run(m,b'new\n',line)
 assert p.read_text()=='old\n'

def test_insert_requires_newline(tmp_path):
 p,m=setup(tmp_path)
 with pytest.raises(ValueError,match='newline'):run(m,b'new',1)
 assert p.read_text()=='old\n'
