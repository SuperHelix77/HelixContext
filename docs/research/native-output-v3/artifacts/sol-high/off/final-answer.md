Implemented in [workflow_memory.py](/Users/mert/Documents/ChatGPT/Helix/research/native-output-indexed-v3-sol-high-20260910/off/workflow_memory.py:79):

- Added optional `match_mode='all'` after `limit`.
- Supports literal-word `all`/AND and `any`/OR matching.
- Validates mode before handling empty queries.
- Preserved project isolation, ordering, limits, integrity checks, and evidence references.
- Only `workflow_memory.py` changed.

Checks:

- `python3 -m pytest` — **23 passed**
- `git diff --check` — passed
- `python3 -m py_compile workflow_memory.py` — passed

Outstanding issues: none.