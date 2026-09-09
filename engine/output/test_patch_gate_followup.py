from patch_gate_followup import preserved_tests
from astra_patch_pair import TESTS


def test_addition_allowed_but_original_assertion_changes_rejected():
    assert preserved_tests(TESTS,TESTS+'\nclass Extra: pass\n')
    assert not preserved_tests(TESTS,TESTS.replace('self.assertEqual(q.cursor,1)','self.assertEqual(q.cursor,99)'))
    assert not preserved_tests(TESTS,'')
    assert not preserved_tests(TESTS,TESTS+TESTS)
