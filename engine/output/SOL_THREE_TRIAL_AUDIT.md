# Three Sol trials → Integrated V2

These are three different development comparisons, not three replicates. Their
savings cannot be multiplied, and the combined trial cannot identify each
component's causal contribution.

| Trial | Control input/output | Candidate input/output | Savings input/output | Command calls off/on |
|---|---:|---:|---:|---:|
| Exact-evidence Query V2 | 56,598 / 820 | 28,543 / 410 | 49.57% / 50.00% | 3 / 1 |
| Caller completion | 45,393 / 1,427 | 14,824 / 401 | 67.34% / 71.90% | 2 / 0 |
| Integrated V1 | 136,608 / 2,673 | 116,717 / 1,588 | 14.56% / 40.59% | 5 / 5 |

Query moved useful evidence into the first prompt. Sol still hashed the source
and read nearby spans in one command. Caller completion supplied an explicit
source hash, all decision fields, direct selection rules and a clear mechanical
verification handoff. Sol returned original IDs without a tool call. V1 supplied
more machinery but dropped that explicit source-hash handoff, described history
as partial, and asked the model to find rules in the archive. It then showed an
Engine receipt containing bookkeeping counters and paths. Sol reread the skill,
discovered files, searched policy, sampled payload, and generated a jq selector.

These are observations, not proof that the words alone caused behavior. V1 also
changed the task, used a new model sample and suffered runtime anomalies. Its
initial candidate prompt was 8,540 bytes, versus caller-completion's 7,199 and
Query's 2,902. Its 86.4% recorded-tool-byte reduction did not remove the five
model-side command calls.

A concrete environment issue was found during the audit: current global
`AGENTS.md` directs active skills to register in a global Helix SQLite database.
The benchmark runs in a workspace-write sandbox. V1's candidate narrated a
registration failure, and stderr independently records a filesystem denial, but
the denied path and registration call are not identified in the native command
trace. The conflict is real in current instructions; attribution of that
particular denial remains a hypothesis. Historical environment snapshots were
not captured in the earlier two trials, so retrospective equivalence is unknown.

## Audited hypotheses

1. **Complete task evidence plus an explicit responsibility boundary may avoid
   reconstruction.** Caller completion supports the hypothesis; one sample and a
   different task do not establish causality. V2 restores the bound field census
   and retains normal verification/recovery when needed.
2. **A small history should remain complete.** Filtering four short records saves
   little and introduces a completeness question. V2 includes all four, including
   superseded and rejected decisions. Large history remains recoverable in Memory;
   V2 does not declare lexical search semantically exhaustive.
3. **Operational receipts and task evidence have different consumers.** The HUD
   needs I/O counters and internal paths. Sol needs verified status, diagnostics,
   omissions and source references. V2 separates these representations while
   retaining every raw byte and charging processing costs.
4. **Skill continuity is caller infrastructure, not a semantic decision.** V2
   overrides only model-owned registration in identical local AGENTS files for
   both arms. The caller registers the actual emitted native thread ID in a
   task-local database and verifies the pinned skill hash. It records errors;
   no guessed session ID, global permission change or fabricated success.

No novel theorem or model cognition lower bound is claimed. The conditional
accounting identity is enough: fewer bytes help only if their avoided context
cost exceeds new admission, verification, retrieval and orchestration costs.
Native token receipts adjudicate this, not formatter byte counts.

## V2 implementation and gates

`decision_packet.py` rejects duplicate JSON keys, nonfinite values, undeclared
fields, missing fields, duplicate IDs and type-changing projections. Complete
metadata is verified against the immutable full source. Completeness is relative
to caller-declared decision fields; new task dependencies require a new contract.
Unknown future relevance is preserved in cold sources, not predicted away.

Preflight presentation strips bookkeeping only after independent packet
verification, retaining statuses, exact diagnostics, failure spans, raw refs and
omission counts. Required expansion remains explicit. The V1 command executes
once; V2 formatting does not rerun it.

`integrated_v2.py` reuses V1's task, gold artifact and grading, but launches a
**fresh control and candidate** because admission instructions changed. The
same local registration instructions and skill source bytes exist in both arms.
High, tools and semantic checks are unchanged. Two calls maximum, fixed order,
no retries by the experiment, the same post-call budget and 75/80 numeric gates.
Caller registration failures prevent qualification; launched usage remains
charged. Transport-level retries, if any, remain separately reported.

All component source hashes, prompt hashes, global instruction/config snapshot
hashes, registry receipt and cold preparation costs are retained. Capturing a
host config hash is not proof of effective hook isolation or platform compaction
restoration. The runtime still does not intercept every native tool output.

**210 engineering tests passed before launch.** This includes real task-local
registration against an emitted fixture thread ID, failed registration rejection,
source/type mutation checks, complete history, and raw failure preservation.
Native V2 outcome is recorded separately; passing these tests is not an efficiency
or general intelligence result.
