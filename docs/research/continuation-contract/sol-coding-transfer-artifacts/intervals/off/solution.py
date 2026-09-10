def normalize(intervals):
    """Validate and return the normalized union of half-open intervals."""
    try:
        iterator = iter(intervals)
    except TypeError:
        raise ValueError("intervals must be an iterable") from None

    validated = []
    try:
        for pair in iterator:
            if not isinstance(pair, (list, tuple)) or len(pair) != 2:
                raise ValueError("each interval must be a two-item list or tuple")

            start, end = pair
            if (
                not isinstance(start, int)
                or isinstance(start, bool)
                or not isinstance(end, int)
                or isinstance(end, bool)
                or start > end
            ):
                raise ValueError("interval endpoints must be integers with start <= end")

            if start != end:
                validated.append((start, end))
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError("invalid interval iterable") from exc

    validated.sort()
    merged = []
    for start, end in validated:
        if not merged or start > merged[-1][1]:
            merged.append((start, end))
        elif end > merged[-1][1]:
            merged[-1] = (merged[-1][0], end)

    return merged
