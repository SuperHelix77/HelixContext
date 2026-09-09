# Sol uncached input: distinguish overhead from cache accounting

The frozen V3 result is **88.10% total native input savings, 65.10% uncached
input savings**, and 88.98% native output savings. These are different metrics.

| V3 input | Control | Helix |
|---|---:|---:|
| Total native | 167,119 | 19,893 |
| Cached subset | 127,360 | 6,016 |
| Uncached remainder | 39,759 | 13,877 |
| Reported usage segments | 8 | 1 |

The large total saving removes repeated input, much of which control served from
cache. Engine preprocessing time and object I/O are not automatically native
input tokens. Model-visible packets/instructions are input; repeatedly deciding
how to use helpers can cause further input/output. Neither the uncached remainder
nor the percentage gap is a measurement of Engine overhead alone.

Control's sixth segment read 21,894 input with only 6,016 cached, leaving 15,878
uncached tokens in that segment. Neighboring segments had 20,480 and 21,504 cached.
This observed cache-reuse drop accounts for about 40% of control's uncached total.
The trace does not identify its cause. Do not remove it from the baseline or assume
that another control will reproduce it. The candidate's only segment also had
6,016 cached. V3 is one development pair, not a cache-controlled billing study.

## Implemented overhead attack

`prototype/compact_metadata.py` encodes complete verified metadata using full field
names once and ordered JSON row arrays. No abbreviated IDs, field aliases, record
filtering, string/boolean coercion, semantic rule changes or cold-source deletion.
It verifies against exact source and independently roundtrips all projected values
and types. Source bytes and all original instructions/history/preflight remain.

The [transport audit](SOL_UNCACHED_AUDIT.json) measures the complete supplied prompt:
7,022 to 4,986 bytes and **1,879 to 1,416 o200k_base proxy tokens** (463 fewer,
24.64%). This includes the small table-reading instruction. The proxy is not a
native token partition; it cannot be subtracted from native bills as a measurement.
Decoding may add model work. Hence a four-call V3/table/table/V3 comparison is
required, with exact artifact/source checks, unchanged High/tools/caller completion,
all usage retained, and cache counts separately reported. This compares two Helix
candidates; it is not a new native-off/on 80/80 qualification.

## Cache preservation is a separate hypothesis

Official documentation says cache reuse depends on the full rendered prefix,
including relevant settings. It recommends stable instructions first and dynamic
content later. For GPT-5.6+, a shared static prefix with changing suffixes may need
an explicit cache breakpoint; sharing initial text alone is not sufficient.
[OpenAI prompt-caching documentation](https://developers.openai.com/api/docs/guides/prompt-caching).

Those API controls must not be assumed available through our native app-server.
The inspected generated app-server schema did not expose prompt-cache options or
breakpoints. No unsupported flag, instruction removal, reduced reasoning setting,
cache warming hidden from accounting, or artificial baseline padding was added.
Repeated native receipts are needed to distinguish representation savings from
cache reuse. Full platform input attribution and complete billing remain unknown.
