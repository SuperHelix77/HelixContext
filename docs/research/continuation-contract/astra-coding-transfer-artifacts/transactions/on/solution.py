def apply_batch(balances, events):
    if not isinstance(balances, dict):
        raise ValueError("balances must be a dict")

    result = {}
    for account, balance in balances.items():
        if not isinstance(account, str) or not account:
            raise ValueError("account IDs must be nonempty strings")
        if (
            not isinstance(balance, int)
            or isinstance(balance, bool)
            or balance < 0
        ):
            raise ValueError("balances must be nonnegative integers")
        result[account] = balance

    try:
        iterator = iter(events)
    except TypeError:
        raise ValueError("events must be iterable") from None

    seen = {}
    for event in iterator:
        if not isinstance(event, dict) or set(event) != {"id", "account", "delta"}:
            raise ValueError("events must contain exactly id, account, and delta")

        event_id = event["id"]
        account = event["account"]
        delta = event["delta"]

        if not isinstance(event_id, str) or not event_id:
            raise ValueError("event IDs must be nonempty strings")
        if not isinstance(account, str) or not account:
            raise ValueError("account IDs must be nonempty strings")
        if not isinstance(delta, int) or isinstance(delta, bool):
            raise ValueError("delta must be an integer")

        payload = (account, delta)
        if event_id in seen:
            if seen[event_id] != payload:
                raise ValueError("conflicting event ID")
            continue

        updated = result.get(account, 0) + delta
        if updated < 0:
            raise ValueError("event would create a negative balance")

        result[account] = updated
        seen[event_id] = payload

    return result
