def weighted_mean(values, weights):
    if len(values) != len(weights):
        raise ValueError("unequal lengths")
    if any(w < 0 for w in weights):
        raise ValueError("negative weights")
    total_weight = sum(weights)
    if not values or total_weight == 0:
        return None
    return sum(v * w for v, w in zip(values, weights)) / total_weight
