def normalize(intervals):
    try:
        iterator = iter(intervals)
    except TypeError as exc:
        raise ValueError("intervals must be an iterable of pairs") from exc

    valid = []
    for pair in iterator:
        if not isinstance(pair, (list, tuple)) or len(pair) != 2:
            raise ValueError("each interval must be a list or tuple of length two")

        start, end = pair
        if (
            isinstance(start, bool)
            or isinstance(end, bool)
            or not isinstance(start, int)
            or not isinstance(end, int)
            or start > end
        ):
            raise ValueError("interval endpoints must be integers with start <= end")

        if start != end:
            valid.append((start, end))

    valid.sort()

    merged = []
    for start, end in valid:
        if merged and start <= merged[-1][1]:
            if end > merged[-1][1]:
                merged[-1] = (merged[-1][0], end)
        else:
            merged.append((start, end))

    return merged
