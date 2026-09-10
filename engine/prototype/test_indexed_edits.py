import hashlib
import random
import pytest
from evidence import Store
from indexed_edits import compile_edits
import renderer


def apply(tmp_path,raw,edits):
    store=Store(tmp_path);source=store.put(raw)['sha256']
    plan,receipt=compile_edits(raw,source,{'edits':edits})
    output,_=renderer.assemble(store,plan)
    assert store.get(source)==raw
    return output,receipt


def e(at,count,text):return {'start_line':at,'delete_lines':count,'insert':text}


@pytest.mark.parametrize('raw,edits,want',[
    (b'a\nb\n',[e(2,1,'x\n')],b'a\nx\n'),
    (b'a\r\nb\r\n',[e(2,1,'x\r\n')],b'a\r\nx\r\n'),
    ('λ\n🌀'.encode(),[e(2,1,'é')],'λ\né'.encode()),
    (b'a\nb',[e(3,0,'\nc')],b'a\nb\nc'),
    (b'',[e(1,0,'x')],b'x'),
    (b'a\nb\n',[e(1,2,'')],b''),
    (b'a\nb\n',[e(3,0,'c\n'),e(1,0,'first\n')],b'first\na\nb\nc\n'),
])
def test_exact_boundaries_and_copy(tmp_path,raw,edits,want):
    got,receipt=apply(tmp_path,raw,edits)
    assert got==want and receipt['copied_bytes']+receipt['literal_bytes']==len(want)


@pytest.mark.parametrize('edits',[
    [e(0,1,'x')],[e(True,1,'x')],[e(1,True,'x')],[e(1,-1,'x')],
    [e(3,1,'x')],[e(4,0,'x')],[e(1,2,'x'),e(2,0,'z')],
    [e(1,0,'x'),e(1,0,'y')],[e(1,1,'x'),e(1,0,'y')],
])
def test_invalid_or_ambiguous_edits_fail_before_realization(tmp_path,edits):
    with pytest.raises(ValueError):apply(tmp_path,b'a\nb\n',edits)


def test_stale_source_and_invalid_text_rejected():
    raw=b'new';old=hashlib.sha256(b'old').hexdigest()
    with pytest.raises(ValueError):compile_edits(raw,old,{'edits':[e(1,1,'x')]})
    bad=b'\xff'
    with pytest.raises(UnicodeError):compile_edits(bad,hashlib.sha256(bad).hexdigest(),{'edits':[]})


def test_generated_nonoverlapping_edits_match_reverse_list_oracle(tmp_path):
    rng=random.Random(910650)
    for case in range(200):
        source=[f'line {i} λ\r\n'.encode() for i in range(rng.randrange(1,25))]
        positions=rng.sample(range(len(source)),rng.randrange(len(source)+1));edits=[];expected=list(source)
        for i in sorted(positions,reverse=True):
            insertion=rng.choice(['','X\n','A\r\nB\n','🌀'])
            edits.append(e(i+1,1,insertion));expected[i:i+1]=[insertion.encode()]
        got,_=apply(tmp_path/str(case),b''.join(source),edits)
        assert got==b''.join(expected)
