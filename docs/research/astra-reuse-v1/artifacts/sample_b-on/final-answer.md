**[P2] Restore the default limit to 10** at [workflow_memory.py:79](/Users/mert/Documents/ChatGPT/Helix/research/astra-reuse-pilot-v1-20260910/sample_b-on/work/workflow_memory.py:79). The signature changes `limit=10` to `limit=9`, violating the requirement to preserve existing calls and limit behavior. Existing `search(project, query)` calls silently lose their tenth matching result.

I confirmed this with a temporary store containing 12 matching records: `before.py` returned 10 records, while the proposed implementation returned 9. The compatibility assertion failed. Explicit `limit=10` returned exactly the original results in both modes.

The caller-validated execution results report **23 pytest tests passed**, `semantic_native.py` passed, and `semantic_helix.py` passed its **12 assertions**, all with exit status 0. I reused those results and inspected the programs. Their coverage includes literal operators, Unicode/FTS behavior, validation, provenance and corruption detection, but none exercises the default limit with ten or more matching records—so their passes miss this regression.

I found no additional defect in the change: mode validation precedes the empty-query return, quoted tokens preserve literal FTS handling, and project filtering, ordering, full index validation, references and other methods remain unchanged.

The implementation needs `limit=10` restored before acceptance. A default-limit boundary regression should cover this gap. No task files were edited.