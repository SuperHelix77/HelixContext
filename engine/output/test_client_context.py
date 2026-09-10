import copy
import datetime
import tomllib
import pytest
from client_context import project_config,serialize,sha


def configuration():
    return {'model':'ordinary','features':{'multi_agent':True},'service_tier':'default',
        'plugins':{'ordinary@plugin':{'enabled':True}},'mcp_servers':{'ordinary':{'env':{'LITERAL':'a\\b\n$()'}}},
        'projects':{'/path/λ':{'trust_level':'trusted'}},
        'hooks':{'PreToolUse':[{'matcher':'.*','hooks':[
            {'type':'command','command':'known helix','timeout':2},
            {'type':'command','command':'ordinary tool','timeout':7}]}],
            'Interrupt':[{'hooks':[{'type':'command','command':'ordinary stop','timeout':3}]}],
            'state':{'/original:pre_tool_use:0:0':{'trusted_hash':'original-helix-trust'},
                     '/original:pre_tool_use:0:1':{'trusted_hash':'original-other-trust'},
                     '/original:interrupt:0:0':{'trusted_hash':'original-stop-trust'}}}}


def test_only_declared_hook_removed_and_every_other_setting_retained():
    c=configuration();before=copy.deepcopy(c)
    raw,receipt=project_config(serialize(c),'/original','/isolated',{sha(b'known helix')})
    out=tomllib.loads(raw.decode())
    assert c==before
    assert {k:v for k,v in out.items() if k!='hooks'}=={k:v for k,v in c.items() if k!='hooks'}
    assert out['hooks']['PreToolUse'][0]['hooks']==[c['hooks']['PreToolUse'][0]['hooks'][1]]
    assert out['hooks']['Interrupt']==c['hooks']['Interrupt']
    assert out['hooks']['state']['/isolated:pre_tool_use:0:0']['trusted_hash']=='original-other-trust'
    assert len(receipt['removed_hooks'])==1 and len(receipt['retained_hooks'])==2
    assert not receipt['native_trust_revalidated'] and not receipt['ordinary_tool_catalog_verified']


def test_group_reindex_and_foreign_trust_preserve_identity_without_new_grants():
    c=configuration();c['hooks']['PreToolUse']=[
        {'hooks':[{'type':'command','command':'known helix'}]},
        {'hooks':[{'type':'command','command':'ordinary tool'}]}]
    c['hooks']['state']={'/original:pre_tool_use:0:0':{'trusted_hash':'H'},
                        '/original:pre_tool_use:1:0':{'trusted_hash':'O'},
                        '/foreign:interrupt:0:0':{'trusted_hash':'F'}}
    raw,_=project_config(serialize(c),'/original','/isolated',{sha(b'known helix')})
    state=tomllib.loads(raw.decode())['hooks']['state']
    assert state=={'/isolated:pre_tool_use:0:0':{'trusted_hash':'O'},'/foreign:interrupt:0:0':{'trusted_hash':'F'}}


def test_hash_drift_unknown_state_and_missing_command_fail():
    c=configuration()
    with pytest.raises(ValueError,match='missing'):project_config(serialize(c),'/original','/isolated',{sha(b'changed')})
    c['hooks']['state']['/original:unknown:9:2']={'trusted_hash':'unknown'}
    with pytest.raises(ValueError,match='Unmatched'):project_config(serialize(c),'/original','/isolated',{sha(b'known helix')})


def test_projection_without_exclusions_cannot_drop_hooks():
    c=configuration();raw,receipt=project_config(serialize(c),'/original','/isolated',set())
    out=tomllib.loads(raw.decode())
    assert out['hooks']['PreToolUse']==c['hooks']['PreToolUse'] and not receipt['removed_hooks']


@pytest.mark.parametrize('value',[datetime.date(2026,9,10),float('nan'),None,{1:'invalid key'}])
def test_unknown_serialization_types_fail_without_silent_conversion(value):
    with pytest.raises(ValueError):serialize({'unsupported':value})


def test_strings_and_types_roundtrip_without_shell_interpretation():
    c={'quoted"key':{'str':'quotes "λ"\\\n$(not executed)','bool':False,'int':4,'float':1.25,'array':[1,'2',True]}}
    assert tomllib.loads(serialize(c).decode())==c
