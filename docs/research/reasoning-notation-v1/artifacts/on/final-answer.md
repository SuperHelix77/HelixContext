**Proposal K requires changes. Proposal R is compatible with `before.py` and satisfies the stated contract based on source review and the focused checks.**

Two defects affect K:

1. **Expiry behavior regresses in ordinary `get`.** At [proposal_k.py:33](/Users/mert/Documents/ChatGPT/Helix/research/reasoning-notation-v1-20260910-gated/on/work/proposal_k.py:33), `>` replaces the original `>=`. After storing `"value"` with `now=10, ttl=5`, reading at `now=15` returns `"value"` instead of the default. This also affects `get_many`, which delegates to `get`. Both cases failed the probes. Restore `>=`.

2. **Batch results lose repeated positions.** At [proposal_k.py:43](/Users/mert/Documents/ChatGPT/Helix/research/reasoning-notation-v1-20260910-gated/on/work/proposal_k.py:43), `dict.fromkeys(keys)` removes duplicates. With `"a"` storing `7`, requesting `["a", "missing", "a", "missing"]` with default `-1` returns `[7, -1]` instead of `[7, -1, 7, -1]`. Iterate over `keys` directly.

R retains the original helpers, `put`, and `get` unchanged. Its extension validates the container, timestamp, and every key before lookup, including timestamp validation for an empty list. Iterating over the original list preserves order and duplicates. Delegating to the unchanged `get` preserves expiry handling, stored-value identity, and defaults. Neither read method modifies stored records. I found no additional contract defect in R.

The caller’s verified execution establishes **8 supplied tests passed** against the identical snapshot; I accepted that evidence without rerunning them. Those tests omit exact-deadline reads and repeated keys, explaining why K passes.

I ran [22 additional focused tests](/Users/mert/Documents/ChatGPT/Helix/research/reasoning-notation-v1-20260910-gated/on/work/review_probes/test_cache_contract.py): **R passed all 11; K passed 8 and failed 3**, reproducing the two defects above. Additional coverage checked falsey values and object identity, replacement deadlines, validation before lookup, read immutability, signatures, and baseline error types/messages on empty and populated caches.

These checks provide bounded execution evidence alongside source review, not exhaustive proof. Protected files were unchanged; only the scratch probe file was added.