# Exact recovery after catalog loss — experimental

A pinned immutable epoch now retains the caller-declared record catalog separately
from the mutable SQLite search/event index. The reader verifies the epoch, record
headers and exact raw sources without querying that index. Live-catalog validation
uses one SQLite read snapshot. Recovery never silently rewrites workflow state.

The deterministic probe deleted every indexed event after freezing 50 observations,
then recovered seven records selected after capture. Existing indexed retrieval
failed; epoch retrieval returned the exact original bytes. Tests also cover partial
catalog deletion, later generations, wrong scope, binary pages, limits, tampered
raw evidence, tampered roots and failed freeze. All 225 engineering tests passed:
`python3 -m pytest -q engine/prototype engine/output engine/hud`.

Run `python3 engine/output/memory_epoch_probe.py` to reproduce the structural check.
The [receipt](MEMORY_EPOCH_RESULT.json) binds source hashes and logical store costs.
The temporary probe store is discarded; its root is a reproducible identity, not a
published live retrieval endpoint.

## Hidden cost

On this deliberately small fixture, freeze wrote 11,489 manifest bytes and read
45,369 object bytes. Seven-record recovery returned 742 useful bytes while reading
13,861 bytes: **18.68x logical read amplification**. The reader loads the complete
manifest on each request; pagination currently loads it twice. This is an explicit
recovery mechanism, not an efficiency win. No automatic activation or frozen Sol
profile change is made. Initial recording/index construction, SQLite/physical
traffic and inference/billing costs are outside these phase-specific counters.
JSON parsing is not instrumented by Store's projection parser counter; zero there
must not be interpreted as zero parsing work.

The root and raw store must survive. It detects post-freeze catalog loss, not
history omitted before creation, and cannot repair damaged raw evidence. Coverage
is exactly the supplied references. Fifty deterministic events are not fifty native
model turns. Capability, agentic behavior, native future-relevance recovery and
whole-task net savings remain unproven.
