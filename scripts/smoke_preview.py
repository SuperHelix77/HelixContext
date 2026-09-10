"""Verify extracted distribution hashes, primitive entrypoints and real HTTP projection."""
import hashlib,json,subprocess,sys,tempfile,time,urllib.request,zipfile
from pathlib import Path
archive=Path(sys.argv[1]);report_path=Path(sys.argv[2])
with tempfile.TemporaryDirectory(prefix='helix-package-smoke-') as tmp:
 with zipfile.ZipFile(archive) as z:
  assert z.testzip() is None;z.extractall(tmp)
 root=next(Path(tmp).iterdir());m=json.loads((root/'MANIFEST.json').read_text())
 for name,sha in m['files'].items():assert hashlib.sha256((root/name).read_bytes()).hexdigest()==sha
 for tool in ['engine/prototype/evidence.py','engine/prototype/plan_cli.py']:
  p=subprocess.run([sys.executable,str(root/tool),'--help'],capture_output=True);assert p.returncode==0,p.stderr
 proc=subprocess.Popen([sys.executable,str(root/'helix_hud.py'),'--port','8772','--data-dir',str(root/'local-state')],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 try:
  for i in range(40):
   try:
    with urllib.request.urlopen('http://127.0.0.1:8772/api/release-state',timeout=2) as f:d=json.load(f)
    break
   except OSError:time.sleep(.1)
  else:raise RuntimeError('Packaged server not reachable')
  assert not d['release']['problems'];assert len(d['release']['lanes'])==5;assert d['runs']==[]
  assert next(l for l in d['release']['lanes'] if 'luna' in l['model'])['comparison_gate']=='FAIL'
  result={'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'archive_crc':'PASS','manifest_files':len(m['files']),
          'primitive_help':'PASS','clean_extraction_http':'PASS','negative_luna_gate_retained':'PASS','model_calls':0}
 finally:proc.terminate();proc.wait(timeout=5)
report_path.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
