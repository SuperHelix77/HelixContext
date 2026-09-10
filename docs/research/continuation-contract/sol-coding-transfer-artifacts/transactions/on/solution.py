def apply_batch(balances, events):
    if not isinstance(balances, dict):
        raise ValueError("balances must be a dict")

    result = {}
    for account, balance in balances.items():
        if not isinstance(account, str) or not account:
            raise ValueError("invalid account ID")
        if isinstance(balance, bool) or not isinstance(balance, int) or balance < 0:
            raise ValueError("invalid balance")
        result[account] = balance

    try:
        iterator = iter(events)
    except (TypeError, Exception) as exc:
        raise ValueError("events must be a finite iterable") from exc

    seen = {}
    try:
        for event in iterator:
            if not isinstance(event, dict) or set(event) != {"id", "account", "delta"}:
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

            payload = (account, delta)
            if event_id in seen:
                if seen[event_id] != payload:
                    raise ValueError("conflicting event ID")
                continue

            seen[event_id] = payload
            new_balance = result.get(account, 0) + delta
            if new_balance < 0:
                raise ValueError("negative intermediate balance")
            result[account] = new_balance
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError("invalid events iterable") from exc

    return result
