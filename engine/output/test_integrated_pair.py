import json
from integrated_pair import prepare


def test_prepare_freezes_real_preflight_and_all_recovery_sources(tmp_path):
    root,manifest,prompts,runtimes,catalog,expected=prepare(tmp_path/'pair')
    assert manifest['max_calls']==2 and manifest['policy']['cold_plans'] is False
    assert len(expected)==6102
    assert all(manifest['preparation'][a]['source_hashes']['records.jsonl']==manifest['source_sha256'] for a in ('off','on'))
    result=manifest['preparation']['on']['costs']['command']
    assert result['visible']['exit_code']==0 and result['execution']['underlying_executions']==1
    assert '36 passed' in (root/'tasks/on/preflight.log').read_text()
    assert 'September' in prompts['on'] and '000.250' not in prompts['on']
    assert manifest['preparation']['on']['costs']['ingestion']['memory']['index_input_bytes']>0
    assert len(runtimes['on'].restore(manifest['preparation']['on']['costs']['checkpoint'])['records'])==4
