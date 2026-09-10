def apply_batch(balances, events):
    """Apply a validated, delivery-ordered batch without mutating its inputs."""
    if not isinstance(balances, dict):
        raise ValueError("balances must be a dict")

    for account, balance in balances.items():
        if not isinstance(account, str) or not account:
            raise ValueError("invalid account ID")
        if isinstance(balance, bool) or not isinstance(balance, int) or balance < 0:
            raise ValueError("invalid balance")

    result = dict(balances)
    seen = {}

    try:
        event_iterator = iter(events)
    except TypeError as exc:
        raise ValueError("events must be an iterable") from exc

    for event in event_iterator:
        if not isinstance(event, dict) or set(event.keys()) != {"id", "account", "delta"}:
            raise ValueError("invalid event")

        event_id = event["id"]
        account = event["account"]
        delta = event["delta"]
        if not isinstance(event_id, str) or not event_id:
            raise ValueError("invalid event ID")
        if not isinstance(account, str) or not account:
            raise ValueError("invalid account ID")
        if isinstance(delta, bool) or not isinstance(delta, int):
            raise ValueError("invalid delta")

        signature = (account, delta)
        previous = seen.get(event_id)
        if previous is not None:
            if previous != signature:
                raise ValueError("conflicting event ID")
            continue
        seen[event_id] = signature

        new_balance = result.get(account, 0) + delta
        if new_balance < 0:
            raise ValueError("negative balance")
        result[account] = new_balance

    return result
