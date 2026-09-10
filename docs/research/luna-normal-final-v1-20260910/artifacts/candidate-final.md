Implemented in [workflow_memory.py](file:///private/tmp/luna-normal-final-v1-run-20260910/on/workflow_memory.py):

- Added `match_mode='all'` after `limit`.
- Added validated `all`/`any` modes using quoted literal FTS tokens.
- Preserved validation, ordering, limits, isolation, integrity checks, and errors.

Validation passed:

- 23 public/regression tests
- 94 independent finite cases
- Focused semantic probes
- `git diff --check`
- Only `workflow_memory.py` changed.