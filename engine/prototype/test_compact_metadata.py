import pytest
from evidence import Store
from decision_packet import metadata,encode
from compact_metadata import table,expand


def test_exact_types_order_unicode_and_all_rows_preserved(tmp_path):
    rows=[{'id':'α','flag':True,'value':'true','payload':'cold'},{'id':'β','flag':'true','value':12345678901234567890,'payload':'exact\r\n'}]
    s=Store(tmp_path);v=metadata(s,b'\n'.join(encode(r) for r in rows),['id','flag','value'],['payload'])
    t=table(s,v);assert expand(t)==v['metadata']
    assert type(expand(t)[0]['flag']) is bool and type(expand(t)[1]['flag']) is str
    v['metadata'][0]['flag']='true'
    with pytest.raises(ValueError):table(s,v)


@pytest.mark.parametrize('v',[{'fields':['a','a'],'rows':[]},{'fields':['a'],'rows':[[1,2]]},{'fields':['a'],'rows':None}])
def test_malformed_table_rejected(v):
    with pytest.raises(ValueError):expand(v)
