"""Small legacy planner. The benchmark requests changes in successive stages."""
import json
import os
import tempfile


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
    """Build plans while preserving source strings and caller-owned data."""
    if not isinstance(rows, (list, tuple)):
        raise ValueError('rows must be a list or tuple')

    fields = ('inventory_tag', 'label_exact', 'sequence_exact')
    plans = []
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError('each row must be a dict')
        if any(field not in row for field in (*fields, 'windows')):
            raise ValueError('each row must contain all required fields')
        if any(not isinstance(row[field], str) for field in fields):
            raise ValueError('inventory_tag, label_exact and sequence_exact must be strings')
        plan = {field: row[field] for field in fields}
        plan['windows'] = merge_windows(row['windows'])
        plans.append(plan)
    return plans


def write_plan(path, rows):
    """Validate the whole batch, then atomically publish its JSON file."""
    plan = build_plan(rows)
    destination = os.path.abspath(os.fsdecode(path))
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
                mode='w', encoding='utf-8', dir=os.path.dirname(destination),
                prefix='.plan-', suffix='.tmp', delete=False) as stream:
            temporary_path = stream.name
            json.dump(plan, stream, ensure_ascii=False)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_path, destination)
        temporary_path = None
    finally:
        if temporary_path is not None:
            os.unlink(temporary_path)
