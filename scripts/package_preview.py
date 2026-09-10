"""Reproducible allowlisted preview archive; excludes credentials and research rollouts."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

ROOT=Path(__file__).resolve().parents[1]
VERSION='0.1.0-preview.1'


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();args.output.parent.mkdir(parents=True,exist_ok=True)
    files={p.relative_to(ROOT).as_posix():p for p in (ROOT/'engine/hud').rglob('*')
           if p.is_file() and p.suffix in ('.py','.js','.css','.html','.json','.md') and not p.name.startswith('test_') and '__pycache__' not in p.parts}
    for p in (ROOT/'engine/prototype').glob('*.py'):
        if not p.name.startswith(('test_','benchmark_')):files[p.relative_to(ROOT).as_posix()]=p
    for name in ('helix_hud.py','engine/README.md','engine/CONTRACT.json','skills/helixcontext/SKILL.md',
                 'docs/release/'+VERSION+'/README.md'):
        files[name]=ROOT/name
    for name in ('PLAN_CLI.md','WORKFLOW_MEMORY.md','INTEGRATION.md'):
        p=ROOT/'engine/prototype'/name
        if p.exists():files[p.relative_to(ROOT).as_posix()]=p
    contents={n:p.read_bytes() for n,p in files.items()}
    contents['README.md']=contents['docs/release/'+VERSION+'/README.md']
    manifest={'version':VERSION,'scope':'Evidence console and explicit-call deterministic Engine primitives; not a qualified universal model policy',
              'files':{n:hashlib.sha256(b).hexdigest() for n,b in sorted(contents.items())}}
    contents['MANIFEST.json']=(json.dumps(manifest,indent=2)+'\n').encode()
    with zipfile.ZipFile(args.output,'w',zipfile.ZIP_DEFLATED) as z:
        for name,raw in sorted(contents.items()):
            info=zipfile.ZipInfo('HelixEngine-'+VERSION+'/'+name,(2026,9,10,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16;z.writestr(info,raw)
    raw=args.output.read_bytes();report={'file':args.output.name,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'files':len(contents)}
    args.output.with_suffix('.sha256').write_text(report['sha256']+'  '+args.output.name+'\n')
    print(json.dumps(report))


if __name__=='__main__':main()
