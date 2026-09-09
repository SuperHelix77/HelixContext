import pytest
from app_server_native import usage,normalize


def event(i=100,o=20,c=80,r=10):
    return {'params':{'tokenUsage':{'total':{'inputTokens':i,'outputTokens':o,'cachedInputTokens':c,'reasoningOutputTokens':r,'totalTokens':i+o}}}}


def test_usage_is_cumulative_not_delta_and_subsets_are_checked():
    assert usage(event())['input_tokens']==100
    assert usage(event(200))['input_tokens']==200 # never 300
    for e in [event(c=101),event(r=21),event(i=True),event(i=-1)]:
        with pytest.raises(ValueError):usage(e)


def test_normalization_preserves_nonzero_status_and_unicode():
    r=normalize({'method':'item/completed','params':{'item':{'id':'x','type':'commandExecution','command':'cmd','exitCode':7,'aggregatedOutput':'Ω\n'}}})
    assert r['type']=='item.completed' and r['item']['exit_code']==7 and r['item']['aggregated_output']=='Ω\n'
    assert 'text' not in normalize({'method':'item/completed','params':{'item':{'id':'r','type':'reasoning','text':'private reasoning'}}})['item']


def test_v3_preparation_attaches_instead_of_duplicate_skill_body(tmp_path):
    from integrated_v3 import prepare
    root,m,prompts,r,c,e=prepare(tmp_path/'pair')
    assert m['schema'].endswith('.v3') and '$helixcontext' in prompts['on']
    assert '# Helix Context' not in prompts['on']
    assert (root/'tasks/on/.agents/skills/helixcontext/SKILL.md').read_bytes()==(root/'tasks/off/.agents/skills/helixcontext/SKILL.md').read_bytes()
