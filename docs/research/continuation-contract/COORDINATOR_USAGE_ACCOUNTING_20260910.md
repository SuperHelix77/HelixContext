# Coordinator research overhead — 2026-09-10

**OBSERVED counters; INFERRED epoch reconstruction.** The coordinator's own native
ledger is now visible in the HUD, separate from candidate/control savings.
Reading only its last cumulative counter would discard two earlier counter epochs.
The frozen observation ends at **2026-09-10T02:44:27.567Z**; the live HUD continues
updating and will therefore show larger values as work proceeds.

| Native measure | Reconstructed thread total | Latest native counter | Earlier closed epochs |
|---|---:|---:|---:|
| Input | 263,166,053 | 245,355,304 | 17,810,749 |
| Cached input, subset | 258,009,088 | 240,687,488 | 17,321,600 |
| Output | 1,583,779 | 1,493,074 | 90,705 |
| Reported reasoning, subset of output | 617,973 | 589,850 | 28,123 |

Reconstructed uncached input: **5,156,965**. There are
3 observed counter epochs, 1962 changed usage updates,
and 23 duplicate updates ignored. Updates are **not**
assumed to be a count of model calls. Native totals include cached input; reasoning
is already included in output.

## Boundary and inference

The source is the full available Helix coordinator thread from
2026-09-08T17:13:04.699Z, including work before the current active goal. Child
benchmark streams are excluded from this table and remain in the experiment
ledger. Other agents, external researchers, storage, physical I/O, historical
pricing and included-plan quota are not completely accounted here. Do not add
these counters to a particular benchmark arm or call them a deployment overhead.

The two decreases have the fresh-counter shape: all cumulative dimensions drop,
and the new total equals the last-usage record. The reader treats those as new
epochs, preserving prior counters. This is an explicit reconstruction assumption,
not independent provider billing evidence. Ambiguous decreases withhold totals.
The latest reported counter is exposed alongside the reconstruction so the
interpretation remains auditable.

The [frozen metadata](COORDINATOR_USAGE_EPOCHS_20260910.json) binds a
76,177,634-byte source prefix at SHA-256
`e75b2f028afb8ddfb4be5f1a510d371dd52cf762a2e78687badc9449e4916937`. Raw prompt/tool/history contents stay local. This
hash identifies an observed prefix; it is not proof that an already-read file
cannot be edited later. Historical rewrites followed by appends require rescan.

## Monitoring cost and validation

The frozen offline scan read 76,177,634 logical bytes in
5 bounded batches, taking 0.226 seconds on
this machine. This is one local observation, not a latency guarantee or physical
SSD measure. The live reader ingests up to16MB per scan and then only appended
bytes. Reads are included in the observer's own overhead. No model is invoked
for parsing, rendering, reset detection or routine refresh.

The combined affected execution/copy/HUD suite passes **77 tests**, including
six incremental-reader tests and an integration test proving coordinator usage
does not change benchmark denominators or savings. Partial appends, duplicate
updates, epoch resets, ambiguous corrections, replacement/truncation, invalid
subsets and private-content exclusion are covered. Indexing/invalid/missing
usage remains unknown rather than zero. The browser displays the coordinator
section alongside unchanged coding medians; prices remain separately refreshed.

## Economic consequence

Helix's development cost is substantial and must not disappear behind attractive
per-task percentages. This ledger makes a previously unmetered cost term visible;
it does **not** establish that the research has paid for itself. An amortization
claim still needs total research cost in comparable units, deployment setup and
failure costs, a qualified task distribution, and observed savings at actual reuse
frequency. The three coding suites still fail their75/75 output qualification.

The next paid experiment must remove measured work, survive the offline
capability/state gates, and count every attempt. Repeating already exhausted
formatting or command-compression trials would add research cost without testing
a supported mechanism.
