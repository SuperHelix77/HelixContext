import hashlib
import json
import pytest
from source_packet import render


@pytest.mark.parametrize('raw', [b'', b"words=re.findall(r'\\w+',query)\n", b'```\n````\n',
                               b'first\r\nlast', 'λ\n🌀'.encode(), b'no-final-newline'])
def test_source_body_recovers_exactly_without_decoding_escapes(raw):
    text, manifest = render({'a.py':raw},version=0)
    header, fence, rest = text.split('\n',3)[1:]
    row = json.loads(header)
    assert row == manifest[0] and row['sha256'] == hashlib.sha256(raw).hexdigest()
    assert rest.endswith(fence+'\n')
    body = rest[:-len(fence+'\n')]
    if row['display_padding_newline']: body=body[:-1]
    assert body.encode() == raw


def test_bad_snapshot_fails_instead_of_changing_source():
    for files,version in [({},0),({'a':b'\xff'},0),({'a':b'\x00'},0),({'a':b'x'},True),({'a':'x'},0)]:
        with pytest.raises((ValueError,UnicodeError)):render(files,version=version)
