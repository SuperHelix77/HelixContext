def apply_batch(balances, events):
    """Apply an ordered batch atomically, ignoring identical event replays."""
    if not isinstance(balances, dict):
        raise ValueError("balances must be a dict")

    result = {}
    for account, balance in balances.items():
        if not isinstance(account, str) or not account:
            raise ValueError("account IDs must be nonempty strings")
        if (not isinstance(balance, int) or isinstance(balance, bool)
                or balance < 0):
            raise ValueError("balances must be nonnegative integers")
        result[account] = balance

    try:
        iterator = iter(events)
    except TypeError as exc:
        raise ValueError("events must be iterable") from exc

    seen = {}
    for event in iterator:
        if not isinstance(event, dict) or event.keys() != {"id", "account", "delta"}:
            raise ValueError("events must contain exactly id, account, delta")
        event_id, account, delta = event["id"], event["account"], event["delta"]
        if not isinstance(event_id, str) or not event_id:
            raise ValueError("event IDs must be nonempty strings")
        if not isinstance(account, str) or not account:
            raise ValueError("account IDs must be nonempty strings")
        if not isinstance(delta, int) or isinstance(delta, bool):
            raise ValueError("deltas must be integers")

        payload = (account, delta)
        if event_id in seen:
            if seen[event_id] != payload:
                raise ValueError("conflicting event ID")
            continue

        balance = result.get(account, 0) + delta
        if balance < 0:
            raise ValueError("event would overdraw account")
        result[account] = balance
        seen[event_id] = payload

    return result
