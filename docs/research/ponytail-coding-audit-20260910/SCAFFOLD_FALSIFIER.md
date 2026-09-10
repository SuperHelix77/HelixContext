# Test-construction segments are not mostly framework overhead

2026-09-10 follow-up to [the Ponytail audit](RESULT.md). Zero native calls.

**OBSERVED:** the three candidate test programs already parameterize many invalid
inputs, flags, fields and fault cases. Their combined source is 3,337 `o200k_base`
proxy tokens. Selecting every import, test-method declaration, TestCase declaration
and main entrypoint totals only 326 proxy tokens, roughly 9.77% of those source
tokens. This selection even includes imports needed by substantive logic.

`SCAFFOLD_AUDIT.json` records all six native programs, hashes, selected lines and
counts. Counts tokenize selected text separately and are not strictly additive
across original source boundaries. They are neither native billing attribution nor
the result of a safe executable rewrite. No tests were removed or rewritten.

The candidate's 4,521 native output tokens in test-containing segments must not be
treated as removable scaffolding. Those segments include independent overlap
oracles, exact-string preservation, validation matrices, mutation checks, mock
callbacks, atomicity checks and failure recovery. Different numbers of test methods
do not establish better coverage: the shorter control publication program found
the surrogate defect missed by the candidate.

**Verdict:** decline a new native trial justified only by removing unittest wrappers
or forcing one-check tests. The former has a small observed source footprint; the
latter can discard useful semantics. This does not prove every more concise test
representation impossible. A candidate must identify the exact repeated procedure
it replaces and preserve its assertions, independence and failure behavior before
we charge inference for it. New helpers also incur creation/discovery cost.

This finding narrows the earlier hypothesis: minimal coding guidance remains useful,
but the large measured test-segment total does not establish a large simple
boilerplate-saving opportunity. The mixed-W50 candidate remains rejected for its
observed capability failure and output regression.
