import json
import astra_transfer as transfer


def test_transfer_declares_model_and_budget_before_calls(tmp_path,monkeypatch):
    monkeypatch.setattr(transfer.base,'MODEL',transfer.MODEL)
    root,m,prompts,r,c,e=transfer.prepare(tmp_path/'pair')
    assert m['model']=='gpt-6-astra' and m['effort']=='high'
    assert m['max_calls']==2 and m['post_call_thresholds']['input_tokens']==200000
    assert '$helixcontext' in prompts['on'] and len(e)==6102
    assert json.loads((root/'manifest.json').read_text())['transfer']['target'].startswith('At least 80')
