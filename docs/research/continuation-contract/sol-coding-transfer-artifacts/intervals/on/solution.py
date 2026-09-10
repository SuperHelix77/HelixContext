def normalize(intervals):
    try:
        iterator = iter(intervals)
    except TypeError as exc:
        raise ValueError("intervals must be iterable") from exc

    valid = []
    try:
        for pair in iterator:
            if not isinstance(pair, (list, tuple)) or len(pair) != 2:
                raise ValueError("each interval must be a pair")

            start, end = pair
            if (
                not isinstance(start, int)
                or isinstance(start, bool)
                or not isinstance(end, int)
                or isinstance(end, bool)
                or start > end
            ):
                raise ValueError("invalid interval endpoints")

            if start < end:
                valid.append((start, end))
    except ValueError:
        raise
    except TypeError as exc:
        raise ValueError("invalid intervals iterable") from exc

    valid.sort()
    merged = []

    for start, end in valid:
        if not merged or start > merged[-1][1]:
            merged.append((start, end))
        elif end > merged[-1][1]:
            merged[-1] = (merged[-1][0], end)

    return merged
