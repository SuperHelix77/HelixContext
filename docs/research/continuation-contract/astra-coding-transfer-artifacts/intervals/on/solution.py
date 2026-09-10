def normalize(intervals):
    try:
        iterator = iter(intervals)
    except TypeError:
        raise ValueError("intervals must be an iterable of pairs") from None

    validated = []
    for pair in iterator:
        if not isinstance(pair, (list, tuple)) or len(pair) != 2:
            raise ValueError("each interval must be a list or tuple of length two")

        start, end = pair
        if (
            not isinstance(start, int)
            or isinstance(start, bool)
            or not isinstance(end, int)
            or isinstance(end, bool)
        ):
            raise ValueError("endpoints must be integers, not bools")
        if start > end:
            raise ValueError("interval start must not exceed end")
        if start != end:
            validated.append((start, end))

    validated.sort()
    merged = []
    for start, end in validated:
        if merged and start <= merged[-1][1]:
            previous_start, previous_end = merged[-1]
            merged[-1] = (previous_start, max(previous_end, end))
        else:
            merged.append((start, end))

    return merged
