"""Independent bounded rejection-reason checks. Not a full authorization checker.
Inputs must come from caller-validated request and policy bindings. This module
neither establishes their authority nor discovers omitted dependencies.
"""
def check(request,answer,reason):
 if set(request)!={'distinct_approvers','approver_group'}:return 'UNRESOLVED_REQUEST'
 count=request['distinct_approvers'];group=request['approver_group']
 minimum=answer.get('minimum_distinct_approvers');required=answer.get('approver_group')
 if type(count) is not int or count<0 or type(minimum) is not int or minimum<0 or type(group) is not str or type(required) is not str:return 'INVALID_FACTS'
 if answer.get('authorized') is not False:return 'UNRESOLVED_AUTHORIZATION'
 if reason=='INSUFFICIENT_APPROVERS':return 'PASS' if count<minimum else 'FAIL'
 if reason=='WRONG_GROUP':return 'PASS' if group!=required else 'FAIL'
 return 'UNRESOLVED_REASON'
