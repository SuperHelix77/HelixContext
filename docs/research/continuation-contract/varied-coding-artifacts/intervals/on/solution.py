def normalize(intervals):
    try:
        iterator = iter(intervals)
    except TypeError as exc:
        raise ValueError("intervals must be iterable") from exc

    normalized = []
    for pair in iterator:
        if not isinstance(pair, (list, tuple)) or len(pair) != 2:
            raise ValueError("each interval must be a pair")

        start, end = pair
        if (
            isinstance(start, bool)
            or isinstance(end, bool)
            or not isinstance(start, int)
            or not isinstance(end, int)
            or start > end
        ):
            raise ValueError("invalid interval endpoints")

        if start < end:
            normalized.append((start, end))

    normalized.sort()

    merged = []
    for start, end in normalized:
        if merged and start <= merged[-1][1]:
            if end > merged[-1][1]:
                merged[-1] = (merged[-1][0], end)
        else:
            merged.append((start, end))

    return merged
