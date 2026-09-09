import pytest
from pricing import HEADER, MODELS, Prices, parse, estimate, TTL


def fixture():
    rows=['### Standard pricing data', '| '+' | '.join(HEADER)+' |', '| --- |']
    rows += ['| '+m+' | $4 | $0.4 | $5 | $20 | $8 | $0.8 | $10 | $30 |' for m in MODELS]
    return ('\n'.join(rows)+'\n### Batch pricing data\n| gpt-5.6-sol | $0.01 |').encode()


def test_exact_standard_section_not_batch():
    assert parse(fixture())['gpt-5.6-sol']['short']==[4,.4,5,20]
    with pytest.raises(ValueError):parse(fixture().replace(b'Short context input',b'Input'))
    with pytest.raises(ValueError):parse(fixture().replace(b'gpt-5.6-luna',b'unknown'))


def test_freshness_failure_and_recovery():
    now=[10]; p=Prices(lambda:fixture(),lambda:now[0]);p.refresh()
    assert p.state()['fresh']
    p.fetcher=lambda:(_ for _ in ()).throw(OSError());p.refresh()
    assert p.state()['error']=='OSError'
    now[0]+=TTL
    assert p.state()['rates'] is None
    p.fetcher=lambda:fixture();p.refresh();assert p.state()['fresh']


def test_cache_subsets_and_reasoning_not_double_counted():
    rates=parse(fixture())['gpt-5.6-sol']
    u=dict(input_tokens=100,cached_input_tokens=20,cache_write_input_tokens=10,output_tokens=30,reasoning_output_tokens=25)
    assert estimate(u,rates)['short']==pytest.approx((70*4+20*.4+10*5+30*20)/1e6)
    del u['cache_write_input_tokens'];assert estimate(u,rates) is None
    u['cache_write_input_tokens']=90;assert estimate(u,rates) is None
    assert estimate(u,None) is None
