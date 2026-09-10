Implemented in `workflow_memory.py` only.

- Added `match_mode='all'` after `limit`, preserving existing calls.
- Supports fixed `all`/`any` modes using quoted literal tokens with `AND`/`OR`.
- Validates mode before empty-query return.
- Preserved project isolation, ordering, limits, integrity checks, and error behavior.

Validation: **23 public/regression tests and 94 independent finite cases passed**.  
Published source SHA-256: `233d42aedb117556ff4943d0751eeb9fb9c3ec55c3e83471c50596a32b31e66a`.

Scope inspection confirmed only `workflow_memory.py` changed. No outstanding issues.