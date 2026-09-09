import pytest
from native_usage import aggregate,validate_resume


def test_unknown_optional_usage_is_not_zero():
    assert aggregate([{'input_tokens':20,'output_tokens':3},{'input_tokens':10,'output_tokens':2,'reasoning_output_tokens':1}])=={
        'input_tokens':30,'output_tokens':5,'cached_input_tokens':None,'cache_write_input_tokens':None,'reasoning_output_tokens':None}


@pytest.mark.parametrize('bad',[{}, {'input_tokens':True,'output_tokens':2},{'input_tokens':-1,'output_tokens':2}])
def test_invalid_core_measurement_rejected(bad):
    with pytest.raises(ValueError):aggregate([bad])


def test_resume_requires_same_model_effort_and_prompt():
    status={'state':'completed','exit_code':0,'model':'luna','effort':'high','usage':{'input_tokens':10,'output_tokens':2}}
    assert validate_resume(status,'luna','p','p')['input_tokens']==10
    for model,prompt,stored in [('sol','p','p'),('luna','new','p')]:
        with pytest.raises(ValueError):validate_resume(status,model,prompt,stored)
