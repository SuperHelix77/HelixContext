Implemented in [workflow_memory.py](/Users/mert/Documents/ChatGPT/Helix/research/native-output-review-v2-sol-high-20260910/off/workflow_memory.py:79).

- Added `match_mode='all'` after `limit`.
- `all` preserves literal-token AND behavior; `any` uses literal-token OR behavior.
- Invalid modes raise `ValueError`, including for empty queries.
- FTS operator injection remains prevented by tokenization and quoting.
- Project isolation, ordering, limits, integrity checks, and evidence references remain unchanged.
- Only `workflow_memory.py` changed.

Checks: `23 passed` via `python3 -m pytest -q`; focused literal-operator and validation checks also passed. No outstanding issues.