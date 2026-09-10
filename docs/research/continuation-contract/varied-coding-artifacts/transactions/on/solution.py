def apply_batch(balances, events):
    if not isinstance(balances, dict):
        raise ValueError("balances must be a dict")

    for account, balance in balances.items():
        if not isinstance(account, str) or not account:
            raise ValueError("invalid account")
        if isinstance(balance, bool) or not isinstance(balance, int) or balance < 0:
            raise ValueError("invalid balance")

    try:
        iterator = iter(events)
    except TypeError as exc:
        raise ValueError("events must be iterable") from exc

    result = dict(balances)
    seen = {}

    try:
        for event in iterator:
            if not isinstance(event, dict):
                raise ValueError("invalid event")
            if set(event.keys()) != {"id", "account", "delta"}:
                raise ValueError("invalid event fields")

            event_id = event["id"]
            account = event["account"]
            delta = event["delta"]

            if not isinstance(event_id, str) or not event_id:
                raise ValueError("invalid event id")
            if not isinstance(account, str) or not account:
                raise ValueError("invalid event account")
            if isinstance(delta, bool) or not isinstance(delta, int):
                raise ValueError("invalid event delta")

            signature = (account, delta)
            if event_id in seen:
                if seen[event_id] != signature:
                    raise ValueError("conflicting event id")
                continue

            seen[event_id] = signature
            new_balance = result.get(account, 0) + delta
            if new_balance < 0:
                raise ValueError("negative balance")
            result[account] = new_balance
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError("invalid events iterable") from exc

    return result
