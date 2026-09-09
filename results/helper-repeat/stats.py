def weighted_mean(values, weights):
    if len(values) != len(weights):
        raise ValueError("values and weights must have equal lengths")
    if any(w < 0 for w in weights):
        raise ValueError("weights must be nonnegative")
    total = sum(weights)
    if not values or total == 0:
        return None
    return sum(v * w for v, w in zip(values, weights)) / total
