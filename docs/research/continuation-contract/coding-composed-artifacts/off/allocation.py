def allocate(total, weights):
    if isinstance(total, bool) or not isinstance(total, int) or total < 0:
        raise ValueError("total must be a nonnegative integer")

    try:
        weights = list(weights)
    except TypeError as exc:
        raise ValueError("weights must be an iterable of nonnegative integers") from exc

    if any(isinstance(weight, bool) or not isinstance(weight, int) or weight < 0
           for weight in weights):
        raise ValueError("weights must contain only nonnegative integers")

    if total == 0:
        return [0] * len(weights)

    weight_sum = sum(weights)
    if not weights or weight_sum == 0:
        raise ValueError("positive total requires positive weights")

    allocations = [(total * weight) // weight_sum for weight in weights]
    remainders = [(total * weight) % weight_sum for weight in weights]
    remaining = total - sum(allocations)

    for index, _ in sorted(enumerate(remainders), key=lambda item: (-item[1], item[0]))[:remaining]:
        allocations[index] += 1

    return allocations
