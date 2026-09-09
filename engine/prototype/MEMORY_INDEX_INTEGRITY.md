# Index corruption falsifier and explicit recovery cost

Two injected failures reproduced silent false negatives: deleting FTS rows and
replacing indexed text left raw evidence intact but made a decisive literal query
return no results. Exact source hashes on retrieved results did not protect
against evidence that search failed to return.

Search now compares each existing project catalog record and indexed body against
verified archived bytes within the same SQLite read transaction as the query.
Missing/altered bodies raise an explicit error. `rebuild_index(project)` verifies
all source objects before changing rows, then replaces the project's index rows
in one write transaction. Corrupt source evidence prevents rebuilding and leaves
the previous index untouched. Recovery is explicit, with no automatic rerun or
inference call.

## Measured cost, not free safety

The same 50-event fixture's exact lookup still emits 349 payload tokens, but
application object reads increased from 514 to **109,678 bytes**, and operations
from 3 to 103. The current local lookup took about 2.65 ms versus about 0.58 ms in
the earlier run. These are separate single observations, not a controlled latency
estimate. `memory-index-check-results.json` records source hashes and counters.

This conservative check scans full project evidence. It is not sparse retrieval,
and large projects can incur substantially greater costs. A future authenticated
index/generation protocol would need to preserve negative-query correctness
without rereading every source; no such improvement is assumed here.

## Verification boundaries

Four new tests cover missing and altered bodies, successful rebuild and failed
rebuild preserving old state. Full prototype suite: **142 passed**.

This does not certify the event catalog itself against coordinated deletion, nor
all possible corruption of SQLite's internal postings. It detects the tested body
and source mismatches for catalog records that still exist. Recovery of a deleted
catalog needs an externally pinned catalog or journal, which remains open. A
lexical miss still does not prove semantic irrelevance. No native model run or
general intelligence/workflow-parity claim accompanies this change.
