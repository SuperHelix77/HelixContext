# Ponytail for Helix coding: selective adoption candidate

2026-09-10. **Research complete; no policy activation or new native benchmark.**
Helix evidence cut: `4be5e8b`, branch `Helix-Output`.

**Verdict: use the reuse/scope principles as a small coding-policy candidate;
do not import the full skill or its test/output limits.** Ponytail addresses
unnecessary implementation, which complements Engine-owned mechanics. It does not
establish cheaper semantic reasoning, Astra transfer, or capability parity.

The user's priority remains capability/workflow preservation, unchanged model
effort and tools, and ordinary complete model-written final answers. No existing
failed result is repaired or reclassified by this audit.

## What was inspected

Upstream [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail/tree/356918eba965ee1eac64bd3a7f0dd02108350de5)
was pinned to `356918eba965ee1eac64bd3a7f0dd02108350de5`
(commit timestamp 2026-09-07T16:27:00Z). The source manifest binds 15 downloaded
files: skill, compact AGENTS rules, hook builders, benchmark runner/tasks and
reports. No upstream hooks, installer or benchmark runner was executed.

The user's Kimi installation contains a compact Ponytail skill, rather than the
full upstream plugin. Its hash is
`85578caeb61ebb2236a872a708a4135f2f9d529a34df372bd879e144923d5912`.
It closely follows upstream AGENTS rules, adds skill metadata and requires more
simplification comments. It lacks the full plugin's mode and final-output sections.
Discussing/auditing it does not activate its persistence instructions.

## External evidence and its limits

**EXTERNAL, not independently reproduced here.** The corrected Haiku 4.5 agentic
report uses 12 feature tasks, four runs per arm, and reports 54% less added code,
22% fewer total tokens, 20% lower cost and 27% lower time. Separate security
exercises passed 20/20 for both baseline and Ponytail. Feature completion was not
established by those security exercises. Four interrupted feature cells retained
LOC while missing economic observations. These are finite, model-specific results,
not universal safety or output-token savings.
([agentic report](https://github.com/DietrichGebert/ponytail/blob/356918eba965ee1eac64bd3a7f0dd02108350de5/benchmarks/results/2026-06-18-agentic.md))

**OBSERVED arithmetic:** the published rounded feature table sums to 2,217 versus
1,015 lines: 54.22% reduction in totals. Equal-weight per-task savings instead
average 35.45%, with median 26.63%. The 54% aggregate is not a median improvement.
These are calculations from rounded LOC means, not reconstructed native receipts.
([same table](https://github.com/DietrichGebert/ponytail/blob/356918eba965ee1eac64bd3a7f0dd02108350de5/benchmarks/results/2026-06-18-agentic.md#axis-1-lines-of-code-on-real-features-12-tasks))

**OBSERVED source audit:** the current runner marks fixture correctness from a
nonempty diff and assigns `safe=1`; this does not execute the feature. Its README
acknowledges this limitation and describes a separate completeness judge. That
judge's existence does not retroactively certify the headline dataset. Token
aggregation includes input, output, cache reads and cache creation; the headline
does not isolate output savings. Raw historical runs were not available in the
inspected committed benchmark tree, so the 22% cannot be independently recomputed
here. Current runner source and the June experiment are also different evidence
cuts. ([runner](https://github.com/DietrichGebert/ponytail/blob/356918eba965ee1eac64bd3a7f0dd02108350de5/benchmarks/agentic/run.py#L256),
[method](https://github.com/DietrichGebert/ponytail/blob/356918eba965ee1eac64bd3a7f0dd02108350de5/benchmarks/agentic/README.md#completeness-judge-completepy))

**EXTERNAL counterevidence:** an older five-task, single-completion experiment
reports GPT-5.5 cost increasing 38.7% and GPT-5.4-mini increasing 26.2% under
Ponytail. This is neither an Astra benchmark nor current pricing. It does show
that reduced code can coexist with increased reported cost. Its raw eval JSON
was gitignored; its repeated-run cache telemetry problems further limit reuse.
([cost report](https://github.com/DietrichGebert/ponytail/blob/356918eba965ee1eac64bd3a7f0dd02108350de5/benchmarks/results/2026-06-17-cost-verification.md))

**EXTERNAL corrective evidence:** the June comprehension study reports that an
explicit shared-caller/root-cause instruction improved a seeded Sonnet/Opus task,
while generic comprehension prose did not. Its reuse fixtures already passed
without Ponytail, so that study did not demonstrate incremental reuse savings.
Do not interpret Haiku failures there as a proved model ceiling.
([comprehension report](https://github.com/DietrichGebert/ponytail/blob/356918eba965ee1eac64bd3a7f0dd02108350de5/benchmarks/results/2026-06-22-issue-245-217-comprehension.md))

## Rule adjudication

This is a Helix recommendation, not acceptance of upstream instructions as authority.
Source: [full skill](https://github.com/DietrichGebert/ponytail/blob/356918eba965ee1eac64bd3a7f0dd02108350de5/skills/ponytail/SKILL.md),
the inspected local variant, and Helix's current task contract.

| Rule family | Verdict | Helix interpretation |
|---|---|---|
| Existing helper / standard library / platform reuse | TAKE | Reuse only after checking behavior, dependencies and relevant limits. |
| Avoid speculative abstractions/dependencies | TAKE | Remove unrequested scope; still implement all requested behavior. |
| Understand flow and repair shared cause | MODIFY | Inspect affected callers when relevant; reuse sufficient fresh evidence instead of mandatory repository-wide rediscovery. |
| Shortest diff / fewest files / one-liners | MODIFY | Prefer maintainable minimal change after behavior, complexity and failure semantics are preserved. File count is not a quality gate. |
| Single check; no frameworks or fixtures | REJECT as a limit | Reuse existing test infrastructure. Retain required cases, independent probes and failure injection. Test count alone establishes nothing. |
| Substitute a simpler request / ultra mode | REJECT | Do not silently weaken requirements or resolve genuine ambiguity without authority. |
| Three-line or code-first final | REJECT | Preserve the ordinary model-written final, including verification and material limitations. |
| Comments on shortcuts | MODIFY | Document consequential limits; avoid mandatory branded comments on ordinary code. |
| Always-active full rules and extra audits | DEFER | No additional mode-discovery, self-review pass or repeated full instruction block merely to use this policy. |

The current installed Caveman Max already contains reuse, stdlib/native preference,
targeted edits, no speculative abstraction and no code golf. Helix Context already
requires targeted edits and complete verification. Duplicating those clauses is
not a new mechanism. The useful research delta is applying them to *test scaffolding*
and shared-root fixes without suppressing coverage.

## Match against the latest Astra trace

**OBSERVED:** [mixed W50 V1](../w50-semantic-v1/RESULT.md) reduced total input
74.33% but increased output 29.76%. Its four candidate checkpoints consumed 7,797
output tokens. The ordinary control consumed 6,009 across the whole workflow.
Only 322 control output tokens were passive ACKs. ACK removal alone therefore
has a conditional 5.36% output ceiling on that recorded trajectory.

We classified visible candidate activities and joined them to native segment
counters. See `TRACE_BUCKETS.json`, with original stream hashes and segment indices.

| Segments containing this activity | Native output tokens | Share |
|---|---:|---:|
| New test-program construction | 4,521 | 57.98% |
| Production patches, sometimes bundled with checks | 1,794 | 23.01% |
| Acquisition / additional hash verification | 810 | 10.39% |
| Clarification and final-answer segments | 672 | 8.62% |
| Total | 7,797 | 100% |

These are **mixed activity buckets**, not pure semantic/mechanical attribution or
hidden-reasoning measurements. Deleting a test-containing segment deletes useful
judgment as well as scaffolding. Its full token count is not an available saving.

The production artifact is already small and uses stdlib; it has no date-picker-
style framework substitution opportunity. Test construction is the larger visible
candidate. It may be possible to express the same cases and predicates through
existing parametrization/helpers, reducing generation without reducing coverage.
That is a **HYPOTHESIS**, not an instruction to use fewer tests.

The control's original publication probe caught a valid-string failure missed by
the candidate's longer suite: an unpaired surrogate raised `UnicodeEncodeError`.
The original private reference shared the blind spot. The supplemental gate passes
12/12 on control and 6/12 on candidate. Re-running the public verifier during this
audit reproduced the expected parity failure with zero model calls.

Ponytail's robust-stdlib principle is relevant to this defect; it is not evidence
that Ponytail would have caught it. The unsafe shortcut would be declaring the
larger suite bloat and keeping only its happy-path test.

## Instruction overhead and economics

**OBSERVED offline `o200k_base` proxies**, not native billed token counts:

| Surface | UTF-8 bytes | Proxy tokens |
|---|---:|---:|
| Installed Kimi Ponytail | 2,677 | 588 |
| Upstream full SKILL.md | 6,637 | 1,610 |
| Upstream compact AGENTS rules | 2,593 | 569 |
| Reconstructed full-mode hook content | 5,252 | 1,264 |
| Current Helix Context | 1,695 | 297 |

The hook-content number statically reproduces the inspected mode filtering; no
hook ran and no Codex request was captured. Hook definitions include startup,
resume/compaction and subagent injection. In the inspected Claude/Codex tracker,
ordinary prompts do not each inject the full rules again; other adapters differ.
Persistent context can still expose injected instructions across later inference
segments. Exact frequency/cache economics require actual request receipts.
([builder](https://github.com/DietrichGebert/ponytail/blob/356918eba965ee1eac64bd3a7f0dd02108350de5/hooks/ponytail-instructions.js),
[hooks](https://github.com/DietrichGebert/ponytail/blob/356918eba965ee1eac64bd3a7f0dd02108350de5/hooks/claude-codex-hooks.json),
[tracker](https://github.com/DietrichGebert/ponytail/blob/356918eba965ee1eac64bd3a7f0dd02108350de5/hooks/ponytail-mode-tracker.js))

Avoid adding 1,264 proxy tokens to teach principles already partly resident.
The economic hypothesis must satisfy: saved generation and repeated context exceed
added instructions, discovery, verification, retries and Engine costs. Saving LOC
does not establish either side of this inequality. No fixed savings prediction or
extra inference-based policy selector is justified.

## Small candidate, not installed

The following proposed addition is scoped to coding and subordinates brevity to
the existing contract. It should replace overlapping guidance if evaluated,
not accumulate beside several equivalent skills:

> Reuse applicable project helpers and standard-library or platform operations before
> adding code; preserve their required behavior and limits. Fix the shared cause after
> inspecting affected paths, reusing sufficient fresh evidence. Avoid speculative scope,
> abstractions and dependencies. Keep code readable. Reuse existing test scaffolding and
> parametrize repeated cases where that preserves every relevant assertion; retain
> independent semantic probes, failure injection and required checks. Minimal code never
> excuses weaker validation, exactness, atomicity, security or accessibility. Preserve
> ordinary complete model-written final answers.

**HYPOTHESIS by model:** Astra may benefit from reducing repeated probe scaffolding,
but blanket reading or skepticism instructions can increase investigation. Sol may
benefit from helper reuse without interface discovery. Luna should keep validated
deterministic transition handling, with no new skill/setup conversation during its
semantic call. None of these is Ponytail parity evidence; qualify separately by
model and effort. Keep Engine active throughout.

## Cheapest next falsifier and stop rules

1. Offline, select one existing *general* test helper or parametrization opportunity
   and show that compact expression preserves all cases, assertions and negative
   controls. Include the exposed Unicode defect as development regression coverage,
   shared-caller correctness, mutation, atomic publication and stale state. Do not
   pre-supply benchmark solutions or tune on the next holdout. Do not create a helper
   whose generation/discovery costs merely move the same work elsewhere.
2. Check that the candidate text neither caps probes nor alters requested scope,
   final-answer form, tools or effort. A static rule audit is not behavioral proof.
3. Only if an actual saving opportunity survives, preregister a fresh matched coding
   task: same Engine, model/effort, bound source, task, tools and final-answer contract;
   change only the coding guidance. Run required checks and cross-run both arms'
   original probes against both outputs. Use fresh withheld cases as well as the
   now-exposed development failures. Count all native input/output, uncached input,
   tool/setup/retrieval costs, attempts and ordinary final answers.
4. Reject on weaker behavior/coverage, dropped requested work, changed answer form,
   or cost shifted into extra discovery/model segments. Do not claim general parity
   from one passing pair. A failed narrow test ends this variant; no blind full-mode
   or ultra-mode sweep. The fixed seven-cell release medians stay unchanged.

**Decision now:** a small, coverage-preserving coding policy is worth evaluating;
full Ponytail activation is not justified. This audit supplies no new 80/80 claim,
release qualification or permission to self-apply an untested model policy.
No implementation/global skill/config changes and no new native inference occurred.
External research, local analysis, downloads and verifier execution remain R&D cost.
