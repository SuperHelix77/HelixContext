# Astra High coding transfer V1 — 2026-09-10

**OBSERVED: finite behavior passes; 75/75 coding qualification fails.** Three fresh
pairs give median **83.07% input / 60.02% output / 27.60% uncached-input savings**.
All six artifacts pass the same 13 public tests and 1,389 independent cases per
arm. No pair reaches 75/75 or 80/80. General capability/workflow parity remains
unproven. Engine stayed active on every candidate.

| Task | Control input / output | Helix input / output | Input saved | Output saved | Uncached saved |
|---|---:|---:|---:|---:|---:|
| Intervals | 79,368 / 1,113 | 16,962 / 445 | 78.63% | 60.02% | 27.60% |
| Dependencies | 100,195 / 1,375 | 16,963 / 479 | 83.07% | 65.16% | 62.87% |
| Transactions | 101,585 / 1,440 | 17,134 / 699 | 83.13% | 51.46% | −9.15% |

Controls total 281,148 input / 3,928 output; candidates total 51,059 / 1,623.
Ratio-of-totals savings are 81.84% input / 58.68% output, distinct from the
medians above. No retrieval, W50 or assembly result is pooled into this cohort.

## Frozen comparison and provenance

The [preregistration](ASTRA_VARIED_CODING_V1_PREREG.md), runner and base were
committed as `4250676` before inference. Manifest SHA-256:
`f434a16b481fb728c597fe3b525ccb4a9ca26af74cdb38afd0476867473b7b8d`.

Both arms used native `gpt-6-astra`, **High**, ordinary tools, the same contracts,
public tests and actual scoped memory preflight. Coordinator Extra High is not
the benchmark effort. All six workspaces were isolated, tracked Git roots.
Project registration preceded config freeze. No retry, reused native control,
guard amendment or policy change occurred within this suite.

Control used Astra's current default client base (21,269 bytes, SHA-256
`152dfaeeb552876190962be1c12c93d426840ff12691f648261554a7675a6698`).
Candidate used the already frozen common delegation kernel, native skill
attachment, resident exact source and caller staging/checks/publication. Its
base is byte-identical to the Sol transfer kernel. This is a composite policy
comparison, not causal isolation of a kernel clause or Engine mechanism.

No solution or algorithm hint was supplied. These three contracts were exposed
in earlier Luna/Sol development; they are not a population holdout. Frozen order
was intervals off/on, dependencies on/off, transactions off/on. Cache state was
observed, not controlled. Config hashes, actual native model/effort, raw streams,
usage sums, protected files and published-source bindings passed the audit.

## Execution and residual

| Task | Control segments / tools | Helix segments / tools | Control reasoning | Helix reasoning | Control / Helix elapsed |
|---|---:|---:|---:|---:|---:|
| Intervals | 4 / 3 | 1 / 0 | 61 | 199 | 42.71 / 21.98 s |
| Dependencies | 5 / 4 | 1 / 0 | 45 | 148 | 56.02 / 18.01 s |
| Transactions | 5 / 4 | 1 / 0 | 64 | 316 | 56.43 / 24.78 s |

All candidate answers contain replacement source only. No setup code, Engine
source inspection, skill-discovery command or reporting continuation appears in
these candidate paths. This removes the visible integration behavior observed in
the earlier Astra regression; it does not retrospectively invalidate that result
or prove which clause changed behavior. The tasks and full intervention differ.

Reasoning counters are a subset of output, not a separate surcharge. Candidate
reasoning totals 663 versus control 170. **UNKNOWN:** why this difference occurred;
counts do not identify hidden reasoning or causally measure semantic work.

**CONDITIONAL arithmetic:** if the observed candidate reasoning counts stayed
fixed, a 75%-saving output budget leaves only 79.25 / 195.75 / 44 tokens for all
other output, compared with the observed 246 / 331 / 383. Deleting every
non-reasoning output token would give ceilings of 82.12% / 89.24% / 78.06%.
These are not irreducible lower bounds or feasible implementations. The code is
part of the required result; deleting it without exact realization loses the task.

**INFERRED:** more output reducers or log compression have no demonstrated
material surface on these zero-command candidate paths. Smaller acknowledgements
cannot eliminate another segment: there is only one. A further attack must
remove work inside that semantic/code-generation call, with its own fresh
capability evidence, or exploit independently available reusable work on a
different task distribution. Do not insert these solved fixture algorithms into
the caller and report the result as fresh coding intelligence.

## Costs and limitations

All six native workflows cost **332,207 input / 5,551 output**, including
239,104 cached and 93,103 uncached input. The 833 reported reasoning tokens are
already included in output. There were no failed launches or retries in this
suite; earlier project failures and coordinator costs remain outside this total.

The transaction candidate used 17,134 uncached input versus control 15,697.
Its 83.13% total-input saving therefore accompanied **9.15% more uncached input**.
Do not call total-input percentages monetary or included-plan quota savings.

Preparation took 2.877 seconds including six memory preflights, isolated Git
setup, registration and binding. Candidate memory calls took 0.133 / 0.131 /
0.133 seconds, retaining 37,845 / 37,854 / 37,854 raw bytes. Caller checks and
publication took 0.266 / 0.272 / 0.270 seconds. These partial elapsed/logical
measures exclude complete physical I/O, storage, energy and research accounting;
unmeasured costs are not zero. Model elapsed excludes some setup and closeout.

The [audit](ASTRA_VARIED_CODING_V1_RESULT.json), SHA-256
`7e0dd5fcb4e1ab0266cae07d8d7ef976ba366311b89c529a562f0c900fc10d6c`,
binds counters and exact artifacts. The public [artifact verifier](astra-coding-transfer-artifacts/README.md)
reexecutes all six implementations and preserves their protected inputs without
inference. Raw rollouts and private config/memory remain local. Extracted counters
are not independent provider attestations.

Semantic review and ordinary tools remained available. Finite function checks
do not establish long-horizon workflow parity or coverage of arbitrary coding
tasks. The research caller lacks OS-enforced isolation from an uncooperative
concurrent writer; automatic normal-Codex-app delivery remains unverified.

**Verdict:** preserve the measured coding input/latency improvement; do not mark
Astra coding released at 75/75. Keep the Engine active while preserving ordinary
semantic execution when needed. The HUD exposes these exact pairs and their
own failed qualification, independently refreshed tariff scenarios, and limits.
