import stat
import pytest
from config_bound_session import validate,private_write


def test_only_explicitly_overridden_gui_defaults_may_change():
    a=b'model="sol"\nmodel_reasoning_effort="xhigh"\n[tools]\nenabled=true\n'
    b=b'model="luna"\nmodel_reasoning_effort="low"\n[tools]\nenabled=true\n'
    r=validate(a,b)
    assert r['changed_top_level_keys']==['model','model_reasoning_effort']
    assert r['initial_sha256']!=r['final_sha256'] and r['other_parsed_settings_unchanged']


@pytest.mark.parametrize('setting',[b'model_instructions_file="changed"',b'sandbox_mode="changed"',b'approval_policy="changed"',b'[tools]\nenabled=false',b'[mcp_servers.x]\nurl="changed"'])
def test_instruction_tool_permission_and_provider_changes_hold(setting):
    with pytest.raises(ValueError):validate(b'model="luna"\n',b'model="sol"\n'+setting+b'\n')


def test_bool_integer_equality_does_not_weaken_binding():
    with pytest.raises(ValueError):validate(b'x=true\n',b'x=1\n')


def test_comments_and_layout_are_not_executable_configuration():
    assert validate(b'x = 1\n',b'# harmless comment\nx=1\n')['changed_top_level_keys']==[]


def test_snapshots_are_private_and_no_overwrite(tmp_path):
    p=tmp_path/'config';private_write(p,b'local settings')
    assert stat.S_IMODE(p.stat().st_mode)==0o600
    with pytest.raises(FileExistsError):private_write(p,b'changed')
    assert p.read_bytes()==b'local settings'


def test_configuration_failure_still_retains_raw_evidence(tmp_path):
    import io,json
    from types import SimpleNamespace
    from config_bound_session import Session
    s=object.__new__(Session);s.closed=False;s.failed=False;s.rpc=SimpleNamespace(close=lambda:None)
    s.out=tmp_path;s.config_path=tmp_path/'shared.toml';s.config_path.write_bytes(b'sandbox_mode="changed"\n')
    s.initial_config=b'sandbox_mode="original"\n';s.thread='T';s.normalized=io.StringIO()
    s.rollout_path=tmp_path/'rollout';s.rollout_path.write_text(json.dumps({'type':'session_meta','payload':{'id':'T'}})+'\n')
    def record(state,error=None):
        (tmp_path/'status.json').write_text(json.dumps({'state':state,'error':error,'raw_capture':s.capture_status}))
    s.record=record;s.close()
    status=json.loads((tmp_path/'status.json').read_text())
    assert status['state']=='failed' and 'Non-overridden' in status['error']
    assert status['raw_capture']['bytes']>0 and (tmp_path/'raw/raw-rollout.jsonl').exists()
    assert (tmp_path/'config.final.private.toml').read_bytes()==s.config_path.read_bytes()


@pytest.mark.parametrize('turns',[[],[{'index':1}]])
def test_missing_rollout_is_only_acceptable_before_any_model_turn(tmp_path,turns):
    import io,json
    from types import SimpleNamespace
    from config_bound_session import Session
    s=object.__new__(Session);s.closed=False;s.failed=False;s.rpc=SimpleNamespace(close=lambda:None)
    s.out=tmp_path;s.config_path=tmp_path/'config';s.config_path.write_bytes(b'model="other"\n')
    s.initial_config=b'model="other"\n';s.thread='T';s.model='gpt-5.6-luna';s.turns=turns;s.normalized=io.StringIO();s.rollout_path=tmp_path/'missing'
    (tmp_path/'requests.jsonl').write_text(json.dumps({'method':'thread/start','params':{'model':s.model,'config':{'model_reasoning_effort':'high'}}})+'\n')
    (tmp_path/'thread-start.json').write_text(json.dumps({'model':s.model,'reasoningEffort':'high'}))
    def record(state,error=None):(tmp_path/'status.json').write_text(json.dumps({'state':state,'error':error,'raw_capture':s.capture_status}))
    s.record=record;s.close();status=json.loads((tmp_path/'status.json').read_text())
    assert status['state']==('closed' if not turns else 'failed')
    if not turns:assert status['raw_capture']['captured'] is False
