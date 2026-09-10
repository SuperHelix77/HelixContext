**Changes requested: one high-priority defect.**

**[P1] Remove the query-specific early return at [workflow_memory.py:85](/Users/mert/Documents/ChatGPT/Helix/research/astra-resident-review-v1-20260910/work/workflow_memory.py:85).** The special case for `query == 'unlisted_token'` violates both search semantics and corruption detection. This is a valid, nonempty query that must follow the existing tokenization and FTS path.

I independently reproduced three failures, each under default mode, explicit `all`, and `any`:

- With archived evidence containing `unlisted_token`, the baseline returns its reference; the proposal returns `[]`.
- With a missing index row belonging to a nonmatching record, the baseline raises the index-integrity `ValueError`; the proposal returns `[]`.
- With a corrupted nonmatching source object, the baseline raises the evidence-hash `ValueError`; the proposal returns `[]`.

That produced **nine contract failures**. Nine corresponding controls using `unlisted_token `, which has identical literal tokens, matched baseline behavior. The branch therefore both hides valid evidence and reports corruption as a successful empty search.

The caller’s bound results report **23 supplied tests passing**, both supplemental regression programs passing, and **612 finite compatibility cases without differences**. These observations remain valid, but their supplied query coverage omits this special case and therefore does not catch the defect.

The remaining changes align with the contract: the argument follows `limit`, mode validation precedes empty-query handling, and quoted literal words are joined with AND or OR while retaining the existing SQL and reference handling. No other public methods differ from `before.py`.

Remove the special case and cover matching evidence plus nonmatching corruption for this query in all three calling forms. I found no additional defects in the scoped review. No task files were edited.