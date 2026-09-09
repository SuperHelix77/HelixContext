"""Reproduce published finite code checks offline; write only in temporary staging."""
import ast
import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parent


def main():
    manifest=json.loads((ROOT/'artifact-manifest.json').read_text())
    for rel,digest in {**manifest['sha256'],**manifest['verifier_sources']}.items():
        assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==digest,rel
    pair=json.loads((ROOT/manifest['native_pair_report']).read_text())
    task=json.loads((ROOT/'coding-source.json').read_text())
    tree=ast.parse((ROOT.parent/'luna_capability_pair.py').read_text())
    grade=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='grade')
    scripts=[n.value.value for n in ast.walk(grade) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='script' for t in n.targets) and isinstance(n.value,ast.Constant)]
    assert len(scripts)==1
    with tempfile.TemporaryDirectory(prefix='helix-public-verify-') as tmp:
        tmp=Path(tmp);public=[]
        for arm in ('off','on'):
            assert next(r for r in pair['rows'] if r['arm']==arm)['source_sha256']==manifest['sha256'][arm+'/allocation.py']
            for name in ('settings.json','test_allocation.py'):
                assert (ROOT/arm/name).read_text()==task['files'][name]
            shutil.copytree(ROOT/arm,tmp/arm,ignore=shutil.ignore_patterns('__pycache__'))
            r=subprocess.run([sys.executable,'-c',scripts[0]],cwd=tmp/arm,capture_output=True,text=True,check=True,timeout=30)
            assert r.stdout=='ORACLE_CASES 4433\n' and 'Ran 4 tests' in r.stderr
            public.append({'arm':arm,'public_tests':4,'oracle_cases':4433,'checks':'PASS'})
        # Copy the post-hoc auditor before import so its result files stay temporary.
        helper=tmp/'domain.py';shutil.copyfile(ROOT.parent/'luna_coding_domain_audit.py',helper)
        spec=importlib.util.spec_from_file_location('temporary_domain_audit',helper)
        mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
        with contextlib.redirect_stdout(io.StringIO()):mod.audit(tmp)
        domain=json.loads((tmp/'domain-audit.json').read_text())
    for rel,digest in manifest['sha256'].items():assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==digest
    print(json.dumps({'scope':'Reproduced code checks; provider tokens and general parity are not independently attested',
                      'public_and_original_oracle':public,'posthoc_domain':domain['rows'],'new_model_calls':0},indent=2))


if __name__=='__main__':main()
