import pytest
from reason_obligation_check import check
R={'distinct_approvers':1,'approver_group':'violet'}
A={'authorized':False,'minimum_distinct_approvers':2,'approver_group':'violet'}
@pytest.mark.parametrize('task_request,answer,reason,expected',[
 (R,A,'INSUFFICIENT_APPROVERS','PASS'),
 (R,A,'WRONG_GROUP','FAIL'),
 ({**R,'distinct_approvers':2},A,'INSUFFICIENT_APPROVERS','FAIL'),
 ({**R,'approver_group':'amber'},A,'WRONG_GROUP','PASS'),
 ({**R,'new_obligation':True},A,'INSUFFICIENT_APPROVERS','UNRESOLVED_REQUEST'),
 ({**R,'distinct_approvers':True},A,'INSUFFICIENT_APPROVERS','INVALID_FACTS'),
 (R,{**A,'minimum_distinct_approvers':True},'INSUFFICIENT_APPROVERS','INVALID_FACTS'),
 (R,{**A,'authorized':True},'AUTHORIZED','UNRESOLVED_AUTHORIZATION'),
 (R,A,'UNKNOWN','UNRESOLVED_REASON'),
])
def test_adversarial_claims(task_request,answer,reason,expected):
 assert check(task_request,answer,reason)==expected
