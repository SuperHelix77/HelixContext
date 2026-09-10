**Proposal K needs changes; proposal R satisfies the reviewed contract.**

Two correctness defects exist in K:

1. **Expired values remain readable at the deadline** — [proposal_k.py:33](/Users/mert/Documents/ChatGPT/Helix/research/reasoning-notation-v1-20260910-gated/off/work/proposal_k.py:33). Changing `now >= entry[0]` to `now > entry[0]` breaks the existing `get` API and affects `get_many`. After storing `"value"` with `now=10, ttl=5`, both APIs return it at `now=15`, when they must return the default. The boundary probe passed against `before.py` and R. Restore `>=`.

2. **Repeated input positions disappear** — [proposal_k.py:43](/Users/mert/Documents/ChatGPT/Helix/research/reasoning-notation-v1-20260910-gated/off/work/proposal_k.py:43). `dict.fromkeys(keys)` removes duplicates. With `"a"` storing `7`, requesting `["a", "missing", "a", "missing"]` with default `-1` returns `[7, -1]`, instead of `[7, -1, 7, -1]`. Iterate directly over `keys`.

R preserves the existing functions unchanged, confirmed by AST comparison, including their signatures, validation and error behavior. Its [get_many implementation](/Users/mert/Documents/ChatGPT/Helix/research/reasoning-notation-v1-20260910-gated/off/work/proposal_r.py:37) validates the list, timestamp and every key before lookup, then produces one result per position. I found no contract violation in R.

The caller’s validated execution receipt establishes that **all 8 supplied tests passed** against the reviewed snapshot; I accepted that evidence without repeating execution. Those tests omit exact-deadline reads and repeated keys, explaining why K passes.

I additionally executed nine targeted check groups: **R passed 9/9; K passed 6/9**, with three failures attributable to the two defects above. The remaining checks covered identity preservation for stored values and defaults, falsey values, empty and populated cache validation, validation before any lookup, nonmutation of records during reads, replacement, rejected writes, and signatures.

These results combine source review with targeted execution, not exhaustive proof over every Python input. Permanent regression tests should include exact-deadline reads through both APIs and repeated hits and misses. No files were modified.