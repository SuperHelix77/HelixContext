"""Same frozen profile/contracts; isolated tracked Git workspaces.

V1 retained as scope-confounded development. V2 changes repository preparation,
not model instructions, task semantics, checks, tools, effort or candidate policy.
"""
import json
from pathlib import Path
import subprocess
import sys
import luna_varied_coding_v1 as v1


def git(cwd,*args):
    return subprocess.check_output(['git',*args],cwd=cwd,text=True,stderr=subprocess.STDOUT).strip()


def initialize(cwd):
    git(cwd,'-c','init.defaultBranch=main','init','--quiet')
    git(cwd,'config','user.name','Helix Benchmark')
    git(cwd,'config','user.email','benchmark@example.invalid')
    (cwd/'.gitignore').write_text('__pycache__/\n.pytest_cache/\n.helix/\n')
    git(cwd,'add','.');git(cwd,'-c','commit.gpgsign=false','commit','--quiet','-m','Frozen input fixture')
    assert Path(git(cwd,'rev-parse','--show-toplevel')).resolve()==cwd.resolve()
    assert git(cwd,'status','--porcelain=v1','--untracked-files=all')==''
    return {'root':str(cwd.resolve()),'initial_commit':git(cwd,'rev-parse','HEAD'),
            'initial_tree':git(cwd,'rev-parse','HEAD^{tree}'),'tracked':git(cwd,'ls-files').splitlines()}


def prepare(root):
    v1.prepare(root);root=Path(root).resolve();m=json.loads((root/'manifest.json').read_text());m['git_workspaces']={}
    for case in m['cases']:
        for arm in ('off','on'):
            cwd=root/case/arm;m['git_workspaces'][case+'/'+arm]=initialize(cwd)
            m['sha256'][str(cwd/'.gitignore')]=v1.sha(cwd/'.gitignore')
    # Exact prompts and task files retain V1 bytes. Memory receipts are refreshed
    # and bound to each new directory; their model-visible scoped packets match.
    prior=root.parent/'luna-varied-coding-v1-20260910'
    for case in m['cases']:
        assert (root/case/'source.json').read_bytes()==(prior/case/'source.json').read_bytes()
        for arm in ('off','on'):
            assert (root/case/(arm+'-prompt.txt')).read_bytes()==(prior/case/(arm+'-prompt.txt')).read_bytes()
    m['classification']='Three fresh pairs on same development contracts with isolated tracked Git roots; frozen profile, matched memory preflight; not population holdout'
    m['intervention_since_v1']='Tracked isolated Git workspace plus ignored runtime artifacts only; task/prompt/base/skill/checks unchanged'
    m['prior_classification']='V1 finite checks passed but control Git status exposed sibling run metadata; not clean qualification'
    for p in [Path(__file__),Path(__file__).with_name('test_varied_coding_workspace.py')]:m['sha256'][str(p.resolve())]=v1.sha(p)
    v1.save(root/'manifest.json',m)
    print(json.dumps({'final_manifest_sha256':v1.sha(root/'manifest.json'),'isolated_workspaces':len(m['git_workspaces'])}))


def run(root):
    root=Path(root).resolve();m=json.loads((root/'manifest.json').read_text());v1.verify(m)
    for rel,expected in m['git_workspaces'].items():
        cwd=root/rel
        assert Path(git(cwd,'rev-parse','--show-toplevel')).resolve()==cwd
        assert git(cwd,'rev-parse','HEAD')==expected['initial_commit']
        assert git(cwd,'status','--porcelain=v1','--untracked-files=all')==''
    v1.run(root)


def audit(root):
    # Redirect only the shared auditor's report destination. Never overwrite V1,
    # even transiently; an interrupted audit must leave old evidence intact.
    root=Path(root).resolve();target=v1.HERE/'LUNA_VARIED_CODING_V1_RESULT.json'
    original_save=v1.save
    def save_variant(path,value):
        return original_save(root/'v2-audit-raw.json' if Path(path)==target else path,value)
    v1.save=save_variant
    try:
        v1.audit(root);report=json.loads((root/'v2-audit-raw.json').read_text())
    finally:v1.save=original_save
    m=json.loads((root/'manifest.json').read_text())
    for rel,expected in m['git_workspaces'].items():
        cwd=root/rel
        assert Path(git(cwd,'rev-parse','--show-toplevel')).resolve()==cwd
        assert git(cwd,'rev-parse',expected['initial_commit']+'^{tree}')==expected['initial_tree']
        assert 'solution.py' in expected['tracked']
    report['workspace_boundary']={'isolated_git_roots':6,'source_tracked_at_start':True,'prompt_bytes_unchanged_from_v1':True,
        'note':'Known tasks after V1; no profile tuning. Unrelated parent-repository status avoided.'}
    v1.save(root/'audit.json',report);v1.save(v1.HERE/'LUNA_VARIED_CODING_V2_RESULT.json',report)


if __name__=='__main__':{'prepare':prepare,'run':run,'audit':audit}[sys.argv[1]](sys.argv[2])
