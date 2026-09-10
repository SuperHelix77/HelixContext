"""Small legacy planner. The benchmark requests changes in successive stages."""
import json


def merge_windows(windows, merge_touching=False):
    """Merge half-open integer intervals without changing caller input."""
    if type(merge_touching) is not bool:
        raise ValueError('merge_touching must be a bool')
    if not isinstance(windows, (list, tuple)):
        raise ValueError('windows must be a list or tuple')

    ordered = []
    for window in windows:
        if not isinstance(window, (list, tuple)) or len(window) != 2:
            raise ValueError('each window must be a two-item list or tuple')
        start, end = window
        if type(start) is not int or type(end) is not int or start >= end:
            raise ValueError('window endpoints must be plain integers with start < end')
        ordered.append((start, end))
    ordered.sort()

    merged = []
    for start, end in ordered:
        if merged and (start < merged[-1][1] or
                       (merge_touching and start == merged[-1][1])):
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged


def build_plan(rows):
    return [{'inventory_tag':row['inventory_tag'],
             'label_exact':row['label_exact'].strip(),
             'sequence_exact':str(int(row['sequence_exact'])),
             'windows':merge_windows(row['windows'])} for row in rows]


def write_plan(path, rows):
    with open(path,'w',encoding='utf-8') as stream:
        json.dump(build_plan(rows),stream,ensure_ascii=False)
