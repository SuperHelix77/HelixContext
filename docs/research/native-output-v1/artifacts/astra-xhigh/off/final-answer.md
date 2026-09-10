Updated `workflow_memory.py` with `search(project, query, limit=10, match_mode='all')`.

`all` preserves AND matching; `any` uses OR between quoted literal words. Invalid modes raise `ValueError`, including for empty queries. Existing validation, project isolation, ordering, limits, integrity checks, and evidence references remain intact.

All 23 supplied tests passed. Supplemental operator-safety and corruption checks passed; `git diff --check` passed. Only `workflow_memory.py` changed. No outstanding issues.