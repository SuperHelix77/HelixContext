import pytest
from cohorts import summarize, unique_usage, tariff_medians


def run(identity, amount, state='CLOSED'):
    return {'id': identity, 'native_thread_id': identity, 'model': 'luna', 'effort': 'high', 'state': state,
            'usage_source': 'Native app-server cumulative update',
            'usage': {'input_tokens': amount, 'output_tokens': amount, 'cached_input_tokens': amount // 2}}


def test_median_differs_from_pooled_and_regressions_stay_visible():
    runs = [run('a', 100), run('b', 20), run('c', 1000), run('d', 2000), run('e', 100), run('f', 10)]
    pairs = [{'id': str(i), 'off': a, 'on': b, 'artifact_check': check} for i, (a, b, check) in enumerate([('a','b',True),('c','d',False),('e','f',None)])]
    spec = {'id': 'L', 'model': 'luna', 'effort': 'high', 'pairs': ['0','1','2']}
    row = summarize([spec], pairs, runs)[0]
    assert row['n_pairs'] == 3 and row['median_savings_percent']['input_tokens'] == 80
    assert row['ratio_of_totals_savings_percent']['input_tokens'] < 0
    assert row['finite_check_failures'] == 1 and row['finite_check_unknown'] == 1
    assert row['release_qualification'] == 'NOT_ESTABLISHED'


def test_duplicate_control_missing_data_and_model_mismatch_are_explicit():
    runs = [run('a',100),run('b',20),run('c',15),run('d',10)]
    runs[-1]['effort'] = 'xhigh'
    pairs = [{'id':'1','off':'a','on':'b'}, {'id':'2','off':'a','on':'c'}, {'id':'3','off':'c','on':'d'}]
    row = summarize([{'model':'luna','effort':'high','pairs':['1','2','3','missing']}],pairs,runs)[0]
    assert row['n_pairs'] == 1 and len(row['excluded']) == 3


def test_unique_totals_include_failure_and_remove_aliases():
    a=run('a',100);alias={**a,'id':'a-alias'};failed=run('b',20,'FAILED')
    total=unique_usage([a,alias,failed])
    assert total['usage']['input_tokens'] == 120 and total['unique_threads'] == 2
    assert total['aliases_removed'] == 1
    newer={**a,'usage':{**a['usage'],'input_tokens':120,'cached_input_tokens':60,'output_tokens':110}}
    assert unique_usage([a,newer])['usage']['input_tokens'] == 120
    conflict={**a,'usage':{**a['usage'],'input_tokens':120,'output_tokens':80}}
    assert unique_usage([a,conflict])['usage'] is None


def test_tariff_medians_withhold_partial_or_stale_cohort():
    cohort={'samples':[{'id':'p'},{'id':'q'}],'n_pairs':2}
    pairs=[{'id':'p','off':'a','on':'b'},{'id':'q','off':'c','on':'d'}]
    costs={'a':{'short':1,'long':2},'b':{'short':0.2,'long':0.4},'c':{'short':10,'long':20},'d':{'short':20,'long':40}}
    assert tariff_medians(cohort,pairs,costs)=={'short':-10,'long':-10}
    costs['b']=None
    assert tariff_medians(cohort,pairs,costs)=={'short':None,'long':None}
