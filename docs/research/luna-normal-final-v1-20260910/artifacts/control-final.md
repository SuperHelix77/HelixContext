Implemented `Memory.search(..., match_mode='all')` in [workflow_memory.py](/private/tmp/luna-normal-final-v1-run-20260910/off/workflow_memory.py).

- Preserves default literal-word `AND` behavior.
- Adds literal-word `OR` behavior for `any`.
- Validates mode before empty-query handling.
- Preserves isolation, ordering, limits, integrity checks, and error behavior.
- Only `workflow_memory.py` changed.

Checks: `23 passed`; `git diff --check` passed.