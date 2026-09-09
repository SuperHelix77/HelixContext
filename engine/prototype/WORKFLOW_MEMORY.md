# Workflow memory: first deterministic implementation

Follow-up: [payload measurements and exhaustive-recovery correction](MEMORY_PAYLOAD_RESULTS.md).
`replay` provides exact paged history with one shared provenance reference; it
does not select relevance. The full suite now passes 123 tests.

Later [index-corruption checks and transactional rebuild](MEMORY_INDEX_INTEGRITY.md)
close tested silent-search failures. Full suite: 142 passed. Search now scans all
existing project evidence to verify indexed bodies; earlier sparse-read counters
do not describe this more conservative implementation.

`workflow_memory.Memory(Store(path))` provides:

- `record(project, session, event_id, raw_bytes)`: immutable event identity,
  exact source and metadata objects, transactional lexical-index publication.
- `search(project, query, limit=10)`: compact references, literal keyword AND
  search; no generated summaries or inference calls.
- `timeline(project, session, after=0, limit=50)`: ordered, pageable references
  independent of predicted relevance.
- `retrieve(project, record_hashes, max_bytes=1048576)`: batched exact bytes,
  source-hash verification, all-or-error return and explicit budget rejection.

Sources are historical data, never new instructions. Project filtering is enforced
for search and direct retrieval; it is not an OS access-control boundary. Search
and timeline references are checked against immutable record metadata. An index
search miss is not proof that a fact never occurred. Binary source bytes are
retained exactly, while the text index uses replacement decoding for navigation.

The source archive and FTS index duplicate content; lexical retrieval is not free.
`Memory.metrics` records indexed input bytes and record-operation time;
`Store.metrics` records object traffic. SQLite/physical I/O, search CPU, all failed
attempt costs and model tokens are not fully accounted. No net saving is claimed.

## Verified scope

Eight fixture tests exercise exact late retrieval after 50 events and reopening,
project isolation, idempotency/collisions, binary source and corruption, lexical
miss with timeline fallback, rollback after injected indexing failure, paginated
interleaved projects and tampered index identity. Full prototype suite: 121 tests.

The late-relevance fixture proves persistence and retrieval for a specified query;
it does not test whether a model discovers the correct query or chooses to expand
the timeline. No native compaction, session bootstrap or token benchmark ran.
Search ranking is recency among lexical matches, not semantic relevance.

## Remaining integration gates

Connect caller-owned authorized events through Helix Context; don't ingest
unrelated history automatically. Add decision/supersession/authority semantics,
schema migration/rebuild and index-corruption completeness checks before making
continuity guarantees. Records are immutable through the API, but this prototype
does not prevent direct modification of SQLite by another process.

Freeze request-conditioned bootstrap and fallback behavior before native tests.
Memory must replace eligible caller-supplied history before inference to save
initial input; retrieving additional records after receiving full history does
not recover already-spent tokens. Include capture, indexing, bootstrap, search,
retrieval, misses and recovery in the paired benchmark costs.
