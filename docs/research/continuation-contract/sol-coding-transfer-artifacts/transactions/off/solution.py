def apply_batch(balances, events):
    """Validate and atomically apply a delivery-ordered batch of events."""
    if not isinstance(balances, dict):
        raise ValueError("balances must be a dict")

    result = {}
    for account, balance in balances.items():
        if not isinstance(account, str) or not account:
            raise ValueError("account IDs must be nonempty strings")
        if isinstance(balance, bool) or not isinstance(balance, int) or balance < 0:
            raise ValueError("balances must be nonnegative integers")
        result[account] = balance

    try:
        iterator = iter(events)
    except (TypeError, ValueError):
        raise ValueError("events must be an iterable") from None

    seen = {}
    try:
        for event in iterator:
            if not isinstance(event, dict) or set(event) != {"id", "account", "delta"}:
                raise ValueError("each event must be a dict with exactly id, account, and delta")

            event_id = event["id"]
            account = event["account"]
            delta = event["delta"]

            if not isinstance(event_id, str) or not event_id:
                raise ValueError("event IDs must be nonempty strings")
            if not isinstance(account, str) or not account:
                raise ValueError("account IDs must be nonempty strings")
            if isinstance(delta, bool) or not isinstance(delta, int):
                raise ValueError("event deltas must be integers")

            payload = (account, delta)
            if event_id in seen:
                if seen[event_id] != payload:
                    raise ValueError("conflicting event ID")
                continue
            seen[event_id] = payload

            new_balance = result.get(account, 0) + delta
            if new_balance < 0:
                raise ValueError("event would create a negative balance")
            result[account] = new_balance
    except (TypeError, KeyError):
        raise ValueError("malformed events iterable") from None

    return result
