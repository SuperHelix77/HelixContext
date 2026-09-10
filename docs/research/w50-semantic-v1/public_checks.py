"""Caller selects only the currently introduced checks for a native workdir."""
MERGE='''from planner import merge_windows,build_plan,write_plan
assert merge_windows([(3,5),(1,3),(2,4),(8,10),(10,12)])==[(1,5),(8,10),(10,12)]
assert merge_windows([(1,3),(3,5)],merge_touching=True)==[(1,5)]
assert merge_windows([])==[]
'''
BUILD='''row={'inventory_tag':'sample','label_exact':'cafe\\u0301 / Ω / 箱 \\t ','sequence_exact':'0000000000123','windows':[(1,3),(3,5)]}
result=build_plan([row])[0]
assert result['label_exact']==row['label_exact'] and result['sequence_exact']==row['sequence_exact']
assert result['windows']==[(1,3),(3,5)]
'''
WRITE='''import tempfile
from pathlib import Path
with tempfile.TemporaryDirectory() as d:
 p=Path(d)/'plan.json';p.write_bytes(b'previous exact bytes')
 try:write_plan(p,[row,{**row,'windows':[(3,2)]}])
 except ValueError:pass
 else:raise AssertionError('invalid batch accepted')
 assert p.read_bytes()==b'previous exact bytes'
'''


def source(stage):
    if stage not in [25,38,50]:raise ValueError('No code checks at this checkpoint')
    return MERGE+(BUILD if stage>=38 else '')+(WRITE if stage>=50 else '')+"print('Supplied checks passed')\n"
