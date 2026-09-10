from pathlib import Path
from luna_varied_coding_v2 import initialize,git


def test_task_has_own_tracked_root_even_inside_parent_repository(tmp_path):
    git(tmp_path,'init','--quiet');(tmp_path/'unrelated-run-secret-name').write_text('not task input')
    cwd=tmp_path/'task';cwd.mkdir();(cwd/'solution.py').write_text('old\n')
    receipt=initialize(cwd)
    assert receipt['tracked']==['.gitignore','solution.py']
    assert Path(git(cwd,'rev-parse','--show-toplevel'))==cwd
    (cwd/'solution.py').write_text('new\n')
    status=git(cwd,'status','--porcelain=v1','--untracked-files=all')
    assert status=='M solution.py'
    diff=git(cwd,'diff','--','solution.py')
    assert '-old' in diff and '+new' in diff and 'unrelated' not in diff


def test_runtime_artifacts_do_not_generate_untracked_noise(tmp_path):
    (tmp_path/'solution.py').write_text('pass\n');initialize(tmp_path)
    for folder in ('.helix','__pycache__','.pytest_cache'):
        p=tmp_path/folder;p.mkdir();(p/'state').write_bytes(b'event')
    assert git(tmp_path,'status','--porcelain=v1','--untracked-files=all')==''
