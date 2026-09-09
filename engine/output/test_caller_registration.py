import hashlib
from types import SimpleNamespace
import pytest
from caller_registration import attach


def session(tmp_path):
    skill=tmp_path/'SKILL.md';skill.write_text('fixture skill')
    return SimpleNamespace(turns=[],skill=skill,thread='native-thread',
        registration={'thread_id':'native-thread','skill_sha256':hashlib.sha256(skill.read_bytes()).hexdigest()})


def test_bound_registration_preserves_task_and_scope(tmp_path):
    s=session(tmp_path);text=attach(s,'Do the task exactly.')
    assert text.endswith('Do the task exactly.')
    assert 'task-local' in text and 'not global or future compaction recovery' in text
    assert 'semantic review' in text
    assert not s.turns


def test_no_skill_and_subsequent_turn_are_unchanged(tmp_path):
    s=session(tmp_path);s.turns=[{}];assert attach(s,'Task')=='Task'
    s.turns=[];s.skill=None;assert attach(s,'Task')=='Task'


def test_changed_skill_is_not_attested(tmp_path):
    s=session(tmp_path);s.skill.write_text('changed')
    with pytest.raises(ValueError,match='changed'):attach(s,'Task')


@pytest.mark.parametrize('record',[None,{}, {'thread_id':'other'}])
def test_unbound_registration_is_not_attested(tmp_path,record):
    s=session(tmp_path);s.registration=record
    with pytest.raises(ValueError,match='bound'):attach(s,'Task')
