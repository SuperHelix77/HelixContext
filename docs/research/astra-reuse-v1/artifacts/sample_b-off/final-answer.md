**[P2] Restore the default limit to 10** at [workflow_memory.py:79](/Users/mert/Documents/ChatGPT/Helix/research/astra-reuse-pilot-v1-20260910/sample_b-off/work/workflow_memory.py:79). The proposed signature changes `limit=10` to `limit=9`, violating the requirement to preserve existing calls and limit behavior. With 12 matching records, I verified that the unchanged call `search('p', 'alpha beta')` returns 10 records under `before.py` but only 9 under the proposal. Explicit `limit=10` works in both. The signature should be `search(self, project, query, limit=10, match_mode='all')`.

Actual check results:

- Supplied pytest tests: **23 passed**.
- `semantic_native.py`: **passed**.
- `semantic_helix.py`: **12 assertions passed**.

Those checks miss the default-limit regression because they do not exercise enough matching records with an omitted limit.

Otherwise, the change preserves literal tokenization and quoted FTS terms, validates the mode before empty-query return, and retains project isolation, ordering, full-project integrity checks, evidence references, and existing error paths. No other methods differ from the baseline. I found no additional defects, but the default-limit regression needs correction before approval.

All reviewed files remained unchanged, verified by before/after SHA-256 comparison.