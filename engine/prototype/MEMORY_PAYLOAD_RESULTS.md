# Memory payload falsifier and fallback correction

Synthetic 50-event history, 100,588 serialized bytes. The first event contains an
exact value needed later. No model selects queries or produces answers. Counts
use `o200k_base` on serialized requests and responses, not native model receipts.
Full-history replay is a surface reference, not an optimized ordinary-agent
control. No whole-task or intelligence-parity claim follows.

| Case | Full history | Initial memory path | Shared-provenance replay |
|---|---:|---:|---:|
| Exact old-fact lookup | 23,890 tokens | 349 | 349 |
| Alias miss, exhaustive recovery | 23,890 | 37,780 | 23,974 |
| All history required | 23,890 | 37,763 | 23,957 |

The selective fixture is 98.54% smaller but assumes the correct literal query.
The initial fallback was 58% larger because references and metadata appeared in
timeline, retrieval request and retrieval response. `Memory.replay` now places
provenance in one cold object, returning exact event text and one evidence hash.
Fallback overhead drops to 0.35% and 0.28%, respectively. No old evidence was
discarded to obtain this change; all queried bytes matched in all cases.

## Hidden costs retained in the report

- Shared-replay run: indexing/recording took 49.1 ms on this local observation;
  queries took 0.58–4.24 ms. These are not comparative speedup measurements.
- The memory store retained 305,620 logical bytes, versus a 100,588-byte history
  file: exact sources, metadata, FTS and replay provenance duplicate storage.
- Exhaustive recovery read 120,553–136,785 application object bytes and performed
  150–151 object reads. SQLite and physical I/O remain outside these counters.
- Search-miss recovery and its request are included. Semantic query discovery,
  bootstrap, model inference and subsequent conversation replay are not measured.

Raw artifacts and source/hash manifests are retained at the paths recorded in
`memory-payload-results.json` and `memory-shared-replay-results.json`. Reproduce
using fresh directories:

```sh
python3 engine/prototype/benchmark_workflow_memory.py \
  --artifacts /tmp/helix-memory-new --output /tmp/memory-results.json --shared-replay
```

Full prototype suite: 123 tests passed. New replay tests cover exact strings,
shared evidence, pagination and budget rejection. General compaction restoration,
model discovery of latent facts and 80% native input/output savings remain open.
