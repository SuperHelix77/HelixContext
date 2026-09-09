"""Offline checks of intervention placement; these do not test model behavior."""
import native_kernel_pair as kernel


def test_thread_local_override_preserves_other_controls(monkeypatch, tmp_path):
    received=[]
    class FakeRPC:
        def call(self, method, params):
            received.append((method, params));return params
    monkeypatch.setattr(kernel,'OriginalRPC',FakeRPC)
    cls=kernel.rpc_with_base(tmp_path/'kernel.md');rpc=cls()
    original={'model':'gpt-5.6-luna','cwd':'/task','approvalPolicy':'never','sandbox':'workspace-write',
              'config':{'model_reasoning_effort':'high','skills.max_context_tokens':512}}
    result=rpc.call('thread/start',original)
    assert result['config']=={**original['config'],'model_instructions_file':str(tmp_path/'kernel.md')}
    assert result['sandbox']=='workspace-write' and result['model']=='gpt-5.6-luna'
    assert 'model_instructions_file' not in original['config']
    turn={'effort':'high','input':[{'type':'text','text':'unmodified task'}]}
    assert rpc.call('turn/start',turn)==turn
