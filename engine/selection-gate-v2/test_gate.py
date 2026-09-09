import pytest
from gate import fixture,expected,reference,grade,mutant,MUTATIONS


def test_reference_matches_independently_frozen_ids():
    source=fixture();assert grade(source,source,reference(source))['accepted']

@pytest.mark.parametrize('mode',MUTATIONS)
def test_semantically_wrong_implementation_is_rejected(mode):
    source=fixture();assert not grade(source,source,mutant(source,mode))['accepted']


def test_exact_output_does_not_excuse_source_mutation():
    source=fixture();assert not grade(source,source+b' ',expected(source))['accepted']


def test_substituting_a_different_original_cannot_change_contract():
    source=fixture().replace(b'000.050',b'000.060')
    result=grade(source,source,expected(source))
    assert not result['source_bound'] and not result['accepted']
