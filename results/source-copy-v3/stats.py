def weighted_mean(values, weights):
    if len(values) != len(weights) or any(w < 0 for w in weights):
        raise ValueError
    total = sum(weights)
    if not total:
        return None
    return sum(v * w for v, w in zip(values, weights)) / total
