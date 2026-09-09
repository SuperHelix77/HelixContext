import importlib
from decimal import Decimal
import pytest


def cost_api():
    return importlib.import_module('plan_costs')


@pytest.mark.parametrize('creation,ordinary,planned,expected',[
    (10,5,3,6), (0,5,3,1), ('0.3','0.2','0.1',4),
    (10,3,3,None), (10,2,3,None),
    (None,5,3,None), (10,None,3,None), (10,5,None,None),
    ('1000000000000000000000000000000',2,1,1000000000000000000000000000001),
])
def test_strict_break_even(creation,ordinary,planned,expected):
    assert cost_api().break_even(creation,ordinary,planned)==expected


@pytest.mark.parametrize('bad',[-1,True,float('nan'),float('inf'),'NaN','Infinity','-0.01',{},'bad'])
def test_invalid_cost_rejected_even_when_other_cost_unknown(bad):
    with pytest.raises(ValueError):cost_api().break_even(None,bad,1)


def test_each_cost_dimension_is_independent():
    api=cost_api()
    assert api.break_even(Decimal('10'),5,3)==6
    assert api.break_even(None,80,20) is None
    assert api.break_even(1,2,3) is None
