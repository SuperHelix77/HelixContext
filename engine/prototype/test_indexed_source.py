import hashlib
import pytest
from indexed_source import render


def test_exact_lines_and_cold_inventory():
    raw='λ\r\n```\nlast'.encode(); files={'hot.py':raw,'cold.py':b'future decisive evidence\n'}
    view,manifest=render(files,['hot.py'],version=4)
    assert '1|λ\r\n2|```\n3|last\n````' in view
    assert 'No terminal LF' in view and 'future decisive evidence' not in view
    assert manifest[0]['sha256']==hashlib.sha256(files['cold.py']).hexdigest()
    assert not manifest[0]['hot'] and manifest[1]['hot']
    assert 'Cold files remain readable' in view


@pytest.mark.parametrize('raw',[b'',b'one',b'one\n',b'\n',b'a\r\nb\n'])
def test_numbered_view_can_be_recovered_exactly(raw):
    view,manifest=render({'a':raw},['a'],version=0)
    numbered=view.split('a\n```\n',1)[1].split('```\n',1)[0]
    recovered=b''.join(line.split(b'|',1)[1] for line in numbered.encode().splitlines(keepends=True) if b'|' in line)
    if raw and not raw.endswith(b'\n'):recovered=recovered[:-1]
    assert recovered==raw and manifest[0]['bytes']==len(raw)


@pytest.mark.parametrize('files,hot,version',[
    ({'a':b'valid'},['absent'],0),({'a':b'valid'},['a','a'],0),
    ({'a':b'\0'},['a'],0),({'a':b'\xff'},['a'],0),({'a':b'x'},['a'],True),
])
def test_invalid_view_rejected(files,hot,version):
    with pytest.raises((ValueError,UnicodeError)):render(files,hot,version=version)
