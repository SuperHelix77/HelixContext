# Maintain an existing memory search API

Extend `Memory.search` in `workflow_memory.py` with an optional
`match_mode='all'` argument after `limit`, preserving existing calls.

`all` retains existing literal-word AND search. `any` returns records containing
at least one of the query's literal words, using the same existing tokenization
and SQLite FTS behavior. Query text must never become raw FTS operator syntax.
Validate the mode even for an empty query: non-strings or values other than
`all` and `any` raise `ValueError`. Keep existing project/query/limit validation.

Both modes retain project isolation, most-recent-first ordering, limit behavior,
complete index-integrity checks, exact evidence references and error behavior.
An empty tokenized query still returns an empty list after argument validation.
Do not weaken corruption detection or change other public methods.

Only `workflow_memory.py` may change. `evidence.py` and the supplied tests are
protected. Standard library implementation only; pytest is available for tests.
Use ordinary semantic judgment and tools as needed. This is a real maintenance
change to existing code, not permission to substitute a fixture-specific answer.
