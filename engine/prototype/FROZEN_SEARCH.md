# Optional frozen literal-search generation

`frozen_search.build(memory, project)` builds and rechecks postings from verified
source records, then archives one immutable index. The caller pins the returned
index and catalog hashes. `search(memory, project, reference, query)` verifies
the index hash and compares the current project catalog within a read transaction.
Added/deleted/changed catalog records invalidate the generation instead of
silently excluding newly relevant facts. A corrupted index fails hash verification.

This is an explicit alternative, not a transparent replacement for SQLite FTS.
Its predicate is AND membership of Unicode regex word tokens after casefolding;
Unicode data version is bound. Stemming, alias expansion and semantic relevance
are absent. The caller must accept these semantics and supply a trusted reference,
not accept a reference suggested by arbitrary retrieved content. Rebuilds are
explicit and their costs recur after changes.

## Measured amortization

On the exposed 50-event ASCII fixture, 20 identical queries returned the same
record as the conservative FTS path. Common archive ingestion is excluded from
both arms; frozen index construction is included below.

| Cost | Full-source checked FTS | Frozen generation, including build |
|---|---:|---:|
| Application object read + write bytes | 2,187,780 | 434,025 |
| Observed local elapsed | 39.73 ms | 12.00 ms |
| Additional retained index | 0 | 10,057 B |

The frozen build alone read 218,328 bytes, wrote 10,057 bytes and took 7.39 ms.
One query therefore does not justify this build on these measurements. These
results describe repeated reuse, not a default admission policy. SQLite/catalog
traffic, physical I/O and complete CPU remain unmetered. The test used fixed arm
order and warm caches, so timings are exploratory. Full catalog metadata and the
whole frozen index are still read per query; there is no constant-time claim.

`FROZEN_SEARCH_RESULTS.json` retains counters, source hash and artifact location.
This is an I/O measurement, **not 80% native input/output savings**.

## Verification

Five new tests cover literal hits/misses, new-record invalidation, catalog
deletion, wrong project/corrupt index and corrupt selected-source retrieval. Full
prototype suite: 147 passed. The source remains hash-verified when retrieved;
successful search does not certify that every cold object still exists.

Catalog completeness before build, coordinated rollback, external trust-root
protection and model discovery of the needed query remain outside this bounded
test. A fresh native trial must account for build, rebuild, fallback and skill
costs. No model run or installed policy change accompanies this implementation.
