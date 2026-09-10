def normalize(intervals):
    """Return the sorted union of valid half-open integer intervals."""
    try:
        iterator = iter(intervals)
    except TypeError as exc:
        raise ValueError("intervals must be an iterable of pairs") from exc

    ordered = []
    for pair in iterator:
        if not isinstance(pair, (list, tuple)) or len(pair) != 2:
            raise ValueError("each interval must be a list or tuple of length two")
        start, end = pair
        if any(not isinstance(value, int) or isinstance(value, bool)
               for value in (start, end)):
            raise ValueError("interval endpoints must be integers, not bools")
        if start > end:
            raise ValueError("interval start must not exceed its end")
        if start < end:
            ordered.append((start, end))

    ordered.sort()
    merged = []
    for start, end in ordered:
        if merged and start <= merged[-1][1]:
            previous_start, previous_end = merged[-1]
            merged[-1] = (previous_start, max(previous_end, end))
        else:
            merged.append((start, end))
    return merged
