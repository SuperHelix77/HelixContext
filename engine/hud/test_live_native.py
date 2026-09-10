import hashlib
import json
from types import SimpleNamespace
import pytest
import server


def event(count):
    return (json.dumps({'method':'thread/tokenUsage/updated','params':{'threadId':'T','tokenUsage':{'total':{
        'inputTokens':count,'outputTokens':10,'cachedInputTokens':0,'reasoningOutputTokens':5,'cacheWriteInputTokens':0}}}})+'\n').encode()


def fixture(tmp_path,monkeypatch):
    monkeypatch.setattr(server,'live_process',lambda *args:True)
    prefix=event(100);wire=tmp_path/'wire.jsonl';wire.write_bytes(prefix+event(200))
    status={'state':'running','model':'gpt-5.6-luna','effort':'high','pid':123,'thread_id':'T',
            'native_events_sha256':hashlib.sha256(prefix).hexdigest(),'usage':server.native_totals(prefix,'T')}
    (tmp_path/'status.json').write_text(json.dumps(status))
    cfg={'experiments':[{'id':'live','name':'Live test','classification':'Offline test','root':str(tmp_path),
                        'runs':[{'arm':'on','status':'status.json','native_events':'wire.jsonl','cwd':'.'}]}]}
    return cfg,status,wire


def test_live_append_reports_new_counters_without_final_pass(tmp_path,monkeypatch):
    cfg,status,wire=fixture(tmp_path,monkeypatch)
    result,_=server.snapshot(cfg);r=result['runs'][0]
    assert r['state']=='RUNNING' and r['usage']['input_tokens']==200
    assert r['usage_live'] is True and r['usage_receipt_state']=='LIVE_PREFIX_VALIDATED_UNSEALED'
    assert r['artifact_check'] is None
    assert result['problems']==[]


@pytest.mark.parametrize('change',['prefix','closed','dead','sealed_counters'])
def test_bad_binding_or_dead_writer_does_not_get_live_exception(tmp_path,monkeypatch,change):
    cfg,status,wire=fixture(tmp_path,monkeypatch)
    if change=='prefix':wire.write_bytes(event(99)+event(200))
    elif change=='closed':status['state']='closed'
    elif change=='dead':monkeypatch.setattr(server,'live_process',lambda *args:False)
    else:status['usage']['input_tokens']=99
    (tmp_path/'status.json').write_text(json.dumps(status))
    result,_=server.snapshot(cfg);assert result['runs'][0]['usage'] is None
    assert result['runs'][0]['artifact_check'] is None


def test_final_seal_reconciles_after_live_update(tmp_path,monkeypatch):
    cfg,status,wire=fixture(tmp_path,monkeypatch)
    status.update(state='closed',native_events_sha256=hashlib.sha256(wire.read_bytes()).hexdigest(),usage=server.native_totals(wire.read_bytes(),'T'))
    (tmp_path/'status.json').write_text(json.dumps(status));result,_=server.snapshot(cfg)
    assert result['runs'][0]['usage_receipt_state']=='SEALED'
    assert result['runs'][0]['usage']['input_tokens']==200
    assert result['runs'][0]['usage_live'] is False


def test_app_server_liveness_uses_actual_cwd_without_runner_hint(tmp_path,monkeypatch):
    def run(argv,**kwargs):
        output='/Applications/ChatGPT.app/Contents/Resources/codex app-server --stdio -c model="gpt-5.6-luna"' if argv[0]=='ps' else 'p123\nn'+str(tmp_path)+'\n'
        return SimpleNamespace(returncode=0,stdout=output)
    monkeypatch.setattr(server.subprocess,'run',run)
    assert server.live_process({'pid':123,'model':'gpt-5.6-luna'},tmp_path) is True
    assert server.live_process({'pid':123,'model':'gpt-5.6-sol'},tmp_path) is False
