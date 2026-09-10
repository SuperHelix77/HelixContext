"""Small legacy planner. The benchmark requests changes in successive stages."""
import json
import os
import tempfile


def merge_windows(windows, merge_touching=False):
    """Merge half-open integer windows without modifying caller input."""
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
    """Build ordered plan rows while preserving source strings exactly."""
    if not isinstance(rows, (list, tuple)):
        raise ValueError('rows must be a list or tuple')
    string_fields = ('inventory_tag', 'label_exact', 'sequence_exact')
    plan = []
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError('each row must be a dict')
        if any(field not in row for field in (*string_fields, 'windows')):
            raise ValueError('row is missing a required field')
        if any(not isinstance(row[field], str) for field in string_fields):
            raise ValueError('inventory_tag, label_exact and sequence_exact must be strings')
        planned_row = {field: row[field] for field in string_fields}
        planned_row['windows'] = merge_windows(row['windows'])
        plan.append(planned_row)
    return plan


def write_plan(path, rows):
    """Validate the complete plan, then atomically replace the destination."""
    plan = build_plan(rows)
    destination = os.path.abspath(os.fsdecode(path))
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
                mode='w', encoding='utf-8', dir=os.path.dirname(destination),
                prefix='.planner-', suffix='.tmp', delete=False) as stream:
            temporary_path = stream.name
            json.dump(plan, stream, ensure_ascii=True)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_path, destination)
        temporary_path = None
    finally:
        if temporary_path is not None:
            try:
                os.unlink(temporary_path)
            except FileNotFoundError:
                pass
