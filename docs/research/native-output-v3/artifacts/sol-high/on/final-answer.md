Implemented in [`workflow_memory.py`](file:///Users/mert/Documents/ChatGPT/Helix/research/native-output-indexed-v3-sol-high-20260910/on/workflow_memory.py#L79):

- Added `match_mode='all'` after `limit`, preserving existing calls.
- `all` uses literal-token `AND`; `any` uses literal-token `OR`.
- Validates `match_mode` before empty-query return.
- Raw query text cannot inject FTS syntax.
- No other files changed.

Validation: **23 public/regression tests and 94 independent finite cases passed**.  
Final SHA-256: `52422bad02c86da6c889085ee1e4d284fabe3a72aa3801e8d286d41f4eb52bb2`

An initial staged check failed due to a missing edit-boundary newline; it was not published, then corrected and fully rechecked. No outstanding issues.