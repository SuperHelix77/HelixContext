import json
import pytest
from project_registration_preflight import registration_delta


def project(path,body='trust_level="trusted"'):
    return ('\n[projects.'+json.dumps(str(path))+']\n'+body+'\n').encode()


def test_exact_new_marker_is_setup_with_no_local_layers(tmp_path):
    r=registration_delta(b'model="a"\n',b'model="b"\n'+project(tmp_path),tmp_path)
    assert r['added_trusted_marker'] and r['trust_present'] and r['model_defaults_changed']==['model']


@pytest.mark.parametrize('body',['trust_level="untrusted"','trust_level="trusted"\nextra=true'])
def test_no_new_policy_can_hide_inside_registration(tmp_path,body):
    with pytest.raises(ValueError):registration_delta(b'',project(tmp_path,body),tmp_path)


def test_changed_existing_trust_or_other_project_is_not_initialization(tmp_path):
    with pytest.raises(ValueError):registration_delta(project(tmp_path,'trust_level="untrusted"'),project(tmp_path),tmp_path)
    with pytest.raises(ValueError):registration_delta(b'',project(tmp_path/'other'),tmp_path)


def test_local_config_hooks_or_broken_symlink_require_review(tmp_path):
    (tmp_path/'.codex').symlink_to(tmp_path/'missing')
    with pytest.raises(ValueError):registration_delta(b'',project(tmp_path),tmp_path)


def test_other_settings_do_not_pass_as_registration(tmp_path):
    with pytest.raises(ValueError):registration_delta(b'x=true\n',b'x=1\n'+project(tmp_path),tmp_path)
