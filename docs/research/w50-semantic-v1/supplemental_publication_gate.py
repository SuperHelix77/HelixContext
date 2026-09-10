"""Post-run falsifier from native control's extra probe, not a retroactive gate.

The declared row API accepts Python strings. A lone surrogate is a Python string
and can be represented by JSON escaping. Test valid-value publication separately
from mechanical rollback on injected I/O failure. No artifact is repaired here.
"""
import importlib.util
import json
from pathlib import Path
import tempfile


def check(source):
    spec=importlib.util.spec_from_file_location('publication_candidate',source)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    cases=['\ud800','\udfff','x\ud800y','\x00','cafe\u0301 / Ω / 箱 \t ','🙂']
    failures=[]
    with tempfile.TemporaryDirectory() as d:
        path=Path(d)/'plan.json'
        for value in cases:
            for exists in [False,True]:
                if path.exists():path.unlink()
                if exists:path.write_bytes(b'prior exact state')
                rows=[{'inventory_tag':'x','label_exact':value,'sequence_exact':'0001','windows':[(1,2)]}]
                try:
                    m.write_plan(path,rows)
                    assert json.loads(path.read_text())[0]['label_exact']==value
                except Exception as e:
                    failures.append({'value_repr':repr(value),'existing_destination':exists,'exception':type(e).__name__})
    return {'cases':12,'failures':failures,'verdict':'FAIL' if failures else 'PASS'}
