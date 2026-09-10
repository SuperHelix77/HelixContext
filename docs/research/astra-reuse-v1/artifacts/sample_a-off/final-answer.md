I found no actionable defects. The change matches `TASK.md` and preserves the existing API and behavior from `before.py`: `match_mode` follows `limit`, defaults to `all`, and is validated before empty-query handling. Both modes quote the existing literal tokens, preventing query text from becoming FTS operators. Project filtering, ordering, limits, full-project integrity checks, evidence references, and other methods remain unchanged.

Verification succeeded:

- Supplied pytest tests: **23 passed**.
- `semantic_native.py`: passed all checks.
- `semantic_helix.py`: **12 semantic assertions passed**.

These checks cover literal operators, Unicode and underscore/FTS phrase behavior, argument validation, exact evidence, and corruption in nonmatching records beyond the result limit.

No change-specific concerns remain from this review. File hashes confirmed that no task files changed during verification.