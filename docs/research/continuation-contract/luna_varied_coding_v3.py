"""Isolated Git pairs with effective configuration binding and full raw retention."""
import json
from pathlib import Path
import sys
import luna_varied_coding_v1 as v1
import luna_varied_coding_v2 as v2
import config_bound_session as config


def prepare(root):
    v2.prepare(root);root=Path(root).resolve();m=json.loads((root/'manifest.json').read_text())
    shared=Path('/Users/mert/.codex/config.toml');raw=shared.read_bytes()
    assert v1.sha(shared)==m['sha256'][str(shared)]
    frozen=root/'config.initial.private.toml';config.private_write(frozen,raw)
    del m['sha256'][str(shared)]
    m.update(config_snapshot=str(frozen),shared_config=str(shared),
             classification='Three fresh known coding pairs; isolated tracked Git roots; effective settings bound; frozen profile, High effort, matched memory preflight',
             config_rule='Only model/model_reasoning_effort GUI defaults may change: explicitly overridden and native-verified each thread/turn. All other parsed settings bound; raw config snapshots private.',
             prior_interruption='V2 stopped after one completed control because the raw shared config changed. It remains charged and is not reused.')
    for p in [Path(__file__),Path(config.__file__),frozen]:m['sha256'][str(p.resolve())]=v1.sha(p)
    v1.save(root/'manifest.json',m)
    print(json.dumps({'final_manifest_sha256':v1.sha(root/'manifest.json'),'config_rule':m['config_rule']}))


def run(root):
    root=Path(root).resolve();original_verify=v1.verify;original_session=v1.observed_session.Session
    def verify(m):
        original_verify(m)
        config.validate(Path(m['config_snapshot']).read_bytes(),Path(m['shared_config']).read_bytes())
    v1.verify=verify;v1.observed_session.Session=config.Session
    try:v2.run(root)
    finally:v1.verify=original_verify;v1.observed_session.Session=original_session


def audit(root):
    root=Path(root).resolve();original_save=v1.save
    def save_variant(path,value):
        return original_save(root/'v3-audit-raw.json' if Path(path)==v1.HERE/'LUNA_VARIED_CODING_V2_RESULT.json' else path,value)
    v1.save=save_variant
    try:v2.audit(root)
    finally:v1.save=original_save
    report=json.loads((root/'v3-audit-raw.json').read_text())
    for row in report['rows']:
        path=root/row['case']/(row['arm']+'-run');status=json.loads((path/'status.json').read_text())
        binding=status['effective_config_binding']
        assert binding['other_parsed_settings_unchanged'] and binding['native_overrides_verified']
        assert binding['model']=='gpt-5.6-luna' and binding['effort']=='high'
        assert v1.sha(path/'config.initial.private.toml')==binding['initial_sha256']
        assert v1.sha(path/'config.final.private.toml')==binding['final_sha256']
        row['config_binding']=binding
    report['prior_interruption_reused']=False
    v1.save(root/'audit.json',report);v1.save(v1.HERE/'LUNA_VARIED_CODING_V3_RESULT.json',report)


if __name__=='__main__':{'prepare':prepare,'run':run,'audit':audit}[sys.argv[1]](sys.argv[2])
