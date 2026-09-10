"""Offline grader calibration only. Never copy into either native task directory."""
import json
import os
import tempfile
from pathlib import Path


def merge_windows(windows, merge_touching=False):
    if not isinstance(windows,(list,tuple)) or type(merge_touching) is not bool:raise ValueError('input')
    ordered=[]
    for pair in windows:
        if not isinstance(pair,(list,tuple)) or len(pair)!=2 or any(type(x) is not int for x in pair) or pair[0]>=pair[1]:raise ValueError('window')
        ordered.append(tuple(pair))
    result=[]
    for a,b in sorted(ordered):
        if result and (a<result[-1][1] or merge_touching and a==result[-1][1]):result[-1]=(result[-1][0],max(b,result[-1][1]))
        else:result.append((a,b))
    return result


def build_plan(rows):
    if not isinstance(rows,(list,tuple)):raise ValueError('rows')
    result=[]
    for row in rows:
        if not isinstance(row,dict) or any(k not in row for k in ['inventory_tag','label_exact','sequence_exact','windows']):raise ValueError('row')
        if any(type(row[k]) is not str for k in ['inventory_tag','label_exact','sequence_exact']):raise ValueError('field')
        result.append({**{k:row[k] for k in ['inventory_tag','label_exact','sequence_exact']},'windows':merge_windows(row['windows'])})
    return result


def write_plan(path,rows):
    content=json.dumps(build_plan(rows),ensure_ascii=False).encode('utf-8');path=Path(path)
    fd,name=tempfile.mkstemp(dir=path.parent)
    try:
        with os.fdopen(fd,'wb') as stream:stream.write(content);stream.flush();os.fsync(stream.fileno())
        os.replace(name,path)
    finally:
        if os.path.exists(name):os.unlink(name)
