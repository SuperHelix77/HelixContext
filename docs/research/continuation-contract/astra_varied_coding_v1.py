"""Astra High transfer of the frozen caller/source-only coding boundary.

Uses the already audited task, realization and native-capture machinery. The only
base change is renaming LUNA POLICY to DELEGATION POLICY. No task answer is
prepared for the model. No global settings or original runners are rewritten.
"""
from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
import sys
import time

import luna_varied_coding_v1 as shared
import luna_varied_coding_v2 as workspace
import config_bound_session as config
import project_registration_preflight as registration

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
MODEL = 'gpt-6-astra'
DEFAULT_HASH = '152dfaeeb552876190962be1c12c93d426840ff12691f648261554a7675a6698'
BASE = REPO / 'engine/profiles/astra-coding-transfer-v1/base.md'


@contextmanager
def configured(root):
    root = Path(root).resolve()
    old = shared.BASE, shared.BASE_HASH, shared.verify, shared.observed_session.Session, shared.save, shared.DEFAULT_HASH
    def verify(manifest):
        old[2](manifest)
        config.validate(Path(manifest['config_snapshot']).read_bytes(), Path(manifest['shared_config']).read_bytes())
    def save(path, value):
        if Path(path) == HERE / 'LUNA_VARIED_CODING_V1_RESULT.json':
            path = root / 'astra-audit-raw.json'
        old[4](path, value)
    shared.BASE, shared.BASE_HASH = BASE, shared.sha(BASE)
    shared.DEFAULT_HASH = DEFAULT_HASH
    shared.verify, shared.observed_session.Session, shared.save = verify, config.Session, save
    try:
        yield
    finally:
        shared.BASE, shared.BASE_HASH, shared.verify, shared.observed_session.Session, shared.save, shared.DEFAULT_HASH = old


def prepare(root):
    root = Path(root).resolve()
    start = time.perf_counter()
    luna_base = REPO / 'engine/profiles/luna-coding-v1-75/base.md'
    assert BASE.read_bytes() == luna_base.read_bytes().replace(b'LUNA POLICY', b'DELEGATION POLICY')
    with configured(root):
        shared.prepare(root)  # data/memory only; no native model invocation
    manifest = json.loads((root / 'manifest.json').read_text())
    manifest.update(model=MODEL, base_file=str(BASE), classification=
        'Three fresh Astra High pairs on previously exposed development coding contracts; source-only caller transfer; not a population holdout',
        intervention='Frozen common delegation kernel (model-neutral heading), native skill attachment, exact supplied files, caller realization; no cold plans or generated integration code',
        default_base_sha256=DEFAULT_HASH, original_luna_policy_unchanged=True, git_workspaces={}, registration={})
    for case in manifest['cases']:
        for arm in ('off','on'):
            cwd = root / case / arm
            manifest['git_workspaces'][case+'/'+arm] = workspace.initialize(cwd)
            manifest['sha256'][str(cwd/'.gitignore')] = shared.sha(cwd/'.gitignore')
            warm = root / case / (arm+'-registration')
            manifest['registration'][case+'/'+arm] = registration.warm(cwd,warm,MODEL)
            for path in warm.iterdir():
                if path.is_file():manifest['sha256'][str(path)] = shared.sha(path)
    raw_config = Path('/Users/mert/.codex/config.toml')
    frozen = root / 'config.initial.private.toml'
    config.private_write(frozen,raw_config.read_bytes())
    del manifest['sha256'][str(raw_config)]
    manifest.update(config_snapshot=str(frozen),shared_config=str(raw_config),
        config_rule='Only explicit native-overridden model/effort defaults may change; every other parsed setting remains bound',
        preparation_seconds=time.perf_counter()-start)
    for path in [Path(__file__),HERE/'ASTRA_VARIED_CODING_V1_PREREG.md',Path(workspace.__file__),
                 Path(config.__file__),Path(registration.__file__),frozen,
                 Path('/Applications/ChatGPT.app/Contents/Resources/codex')]:
        manifest['sha256'][str(path.resolve())] = shared.sha(path)
    shared.save(root/'manifest.json',manifest)
    print(json.dumps({'manifest_sha256':shared.sha(root/'manifest.json'),'model':MODEL,
                      'order':manifest['order'],'preparation_seconds':manifest['preparation_seconds'],'model_turns':0}))


def run(root):
    root = Path(root).resolve()
    m = json.loads((root/'manifest.json').read_text())
    assert m['model']==MODEL and m['effort']=='high' and m['base_file']==str(BASE)
    with configured(root):
        shared.verify(m)
        for relative,bound in m['git_workspaces'].items():
            cwd=root/relative
            assert Path(workspace.git(cwd,'rev-parse','--show-toplevel')).resolve()==cwd
            assert workspace.git(cwd,'rev-parse','HEAD')==bound['initial_commit']
            assert workspace.git(cwd,'status','--porcelain=v1','--untracked-files=all')==''
        shared.run(root)


def audit(root):
    root = Path(root).resolve()
    with configured(root):
        shared.audit(root)
    report=json.loads((root/'astra-audit-raw.json').read_text())
    m=json.loads((root/'manifest.json').read_text())
    for row in report['rows']:
        cwd=root/row['case']/row['arm']
        bound=m['git_workspaces'][row['case']+'/'+row['arm']]
        assert Path(workspace.git(cwd,'rev-parse','--show-toplevel')).resolve()==cwd
        assert workspace.git(cwd,'rev-parse',bound['initial_commit']+'^{tree}')==bound['initial_tree']
        folder=root/row['case']/(row['arm']+'-run')
        status=json.loads((folder/'status.json').read_text())
        binding=status['effective_config_binding']
        assert binding['model']==MODEL and binding['effort']=='high'
        assert binding['other_parsed_settings_unchanged'] and binding['native_overrides_verified']
        assert shared.sha(folder/'config.initial.private.toml')==binding['initial_sha256']
        assert shared.sha(folder/'config.final.private.toml')==binding['final_sha256']
        row.update(model=MODEL,effort='high',config_binding=binding)
    report.update(model=MODEL,effort='high',preparation_seconds=m['preparation_seconds'],
        registration=m['registration'],normal_codex_app_integration=False,
        reused_native_controls=False,prior_luna_results_not_overwritten=True,
        boundary='Composite source-only caller/kernel/skill transfer; not isolated effect of a single mechanism')
    shared.save(root/'audit.json',report)
    shared.save(HERE/'ASTRA_VARIED_CODING_V1_RESULT.json',report)
    print(json.dumps({'model':MODEL,'pairs':report['pairs'],'median':report['median_savings_percent']}))


if __name__=='__main__':
    {'prepare':prepare,'run':run,'audit':audit}[sys.argv[1]](sys.argv[2])
