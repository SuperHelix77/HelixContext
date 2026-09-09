import hashlib,json
from pathlib import Path
import pytest
from policy_realization import realize


def fixture():
    events=json.loads((Path(__file__).resolve().parents[2]/'benchmarks/frozen-high/protocol/long-horizon-v1.json').read_text())['events'][:49]
    return events


def execute(events,selection=None,count=1,group='violet'):
    raw=b'\n'.join(json.dumps({'event':e}).encode() for e in events)
    return realize(selection or {'policy':'E01','amendments':['E17']},raw,hashlib.sha256(raw).hexdigest(),
                   {'subject':'ORION-42','distinct_approvers':count,'approver_group':group})


@pytest.mark.parametrize('count',range(5))
@pytest.mark.parametrize('group',['violet','amber','other'])
def test_structured_request_truth_table(count,group):
    r=execute(fixture(),count=count,group=group)
    assert r['answer']['authorized']==(count>=2 and group=='violet')
    assert r['reason']==('INSUFFICIENT_APPROVERS' if count<2 else 'WRONG_GROUP' if group!='violet' else 'AUTHORIZED')
    assert r['answer']['accounting_sequence']=='9007199254740993'
    assert r['answer']['latency_threshold_ms']=='0.125'


@pytest.mark.parametrize('change',['extra_constraint','unknown_scope','vendor','stale','duplicate'])
def test_unknown_and_conflicting_contracts_reenter(change):
    events=fixture();selection={'policy':'E01','amendments':['E17']}
    if change=='extra_constraint':events[0]['data']['requires_weekday']=True
    if change=='unknown_scope':events[16]['data']['scope']='All requirements change.'
    if change=='vendor':selection['amendments']=['E31']
    if change=='duplicate':events.append(events[0])
    if change=='stale':
        with pytest.raises(ValueError):realize(selection,b'[]','0'*64,{})
    else:
        with pytest.raises(ValueError):execute(events,selection)


def test_semantically_wrong_omission_is_not_certified():
    r=execute(fixture(),{'policy':'E01','amendments':[]},count=2)
    assert r['answer']['authorized'] is False  # wrong for actual governing amended policy
    assert 'does not validate semantic selection' in r['authority']
    # A functional grader must catch the omitted amendment; hashes cannot.
    assert r['answer']['approver_group']!='violet'
