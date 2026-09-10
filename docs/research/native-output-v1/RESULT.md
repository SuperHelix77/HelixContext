# Native final-answer pilot: interface passes, models not qualified

2026-09-10. Frozen implementation `6a57243`, active `Helix-Output` branch.
These are two fresh maintenance-task pairs: Astra Extra High and Sol High.
Both randomized orders resolved to control then Helix. No reused controls or
discarded native attempts. This is known development material, not a holdout.

## Observed receipts

| Model / effort | Control input / output | Helix input / output | Input saved | Output saved | Uncached saved |
|---|---:|---:|---:|---:|---:|
| Astra XHigh | 153,042 / 1,943 | 103,615 / 1,952 | 32.30% | -0.46% | 17.37% |
| Sol High | 190,261 / 3,663 | 101,255 / 1,858 | 46.78% | 49.28% | 18.26% |

Both arms of each pair produced byte-identical final source, independently passed
23 public/regression tests and 94 finite oracle cases, and wrote normal final
answers after actual execution. All three model-authored semantic probe programs
were subsequently replayed against **all four artifacts** and passed. That is
bounded behavioral evidence, not universal intelligence or workflow equivalence.

The new output contract is satisfied on this task. Final answers are native model
messages, not caller-rendered selections. Required report content is present in all
four: changed API, literal AND/OR behavior, validation before the empty return,
preserved existing behavior, actual validation results, scope, and no outstanding
issues known to the run. Test-count, source-hash and scope claims agree with the
retained execution receipts. No exact prose match is required.

The frozen machine audit leaves `final_answer_semantic_review` pending because
it cannot decide completeness by string shape alone. This document and the separate
`FINAL_ANSWER_REVIEW.json` record that explicit evidence review; original audits
remain unchanged. Both code outputs in a pair share an exact source hash. Their
finite checks and cross-probes support the bounded "no outstanding issues" reports;
they do not prove the absence of every possible defect.

## Observable execution, not hidden reasoning

| Arm | Model segments | Internal Engine calls | Completed shell commands | Reported reasoning tokens |
|---|---:|---:|---:|---:|
| Astra control | 6 | 0 | 7 | 156 |
| Astra Helix | 4 | 1 | 2 | 828 |
| Sol control | 8 | 0 | 15 | 1,675 |
| Sol Helix | 4 | 2 | 1 | 764 |

Shell command counts are completed `commandExecution` items, not raw outer tool
call counts: orchestration calls can contain several commands. Reported reasoning
counters describe quantity only; no private reasoning content is used here.

**OBSERVED — Astra.** Its initial command reread the 1,819-byte skill, a source
excerpt and file inventory despite the full skill being present in native input
and all four task files in the prompt. The first segment cost 24,474 input /135
output. The successful internal edit/check/publication used the next segment.
Afterward Astra inspected the changed source and authored 12 semantic assertions
covering literal operators, Unicode/FTS behavior, exact binary recovery and corruption
outside the result limit. That segment cost 26,032 input /1,187 output, including
516 reported reasoning tokens. The final answer segment cost 27,618 /236.
Its semantic probes cannot honestly be classified wholesale as mechanical waste.

**OBSERVED — Sol.** Its first internal call copied the entire function as an old/new
selector, doubling a regex backslash in that selector. Exact matching rejected it
before any checker or publication. Sol recovered using three smaller exact edits.
The failed proposal segment cost 24,167 input /762 output; recovery cost 24,980 /405.
Sol then inspected the diff/current source/scope in one shell command, costing
25,534 /228, followed by its final segment at 26,574 /463. Rejection and recovery
are included in all totals. The Engine did not silently repair the model's edit.

Sol control also incurred an unsolicited `codexworkflow` skill detour, a malformed
`printenv` command and a missing `pytest` executable before recovering with
`python3 -m pytest`. Those observed control costs stay in the result. They weaken
any claim that this one pair isolates a general model advantage. Both final artifacts
pass; neither arm nor these failures was dropped after seeing the outcome.

## Cost and limits

At the [official Standard tariffs](https://developers.openai.com/api/docs/pricing)
fetched 2026-09-10 05:40 UTC, the short-context API-equivalent scenarios are:

| Pair | Control | Helix | Saved |
|---|---:|---:|---:|
| Astra XHigh | $0.556210 | $0.454070 | 18.36% |
| Sol High | $0.268902 | $0.175377 | 34.78% |

Long-context scenarios save 19.22% and 33.72% respectively. These are not actual
Codex quota/billing, chosen tariff tiers or full effective-cost claims. Snapshot
source/hash and both scenarios are in `artifacts/COST.json`; the HUD refreshes prices
and expires stale rates independently.

All four native streams total **548,173 input, 9,416 output**, including 425,728
cached input and 3,423 reported reasoning tokens (already part of output).
Uncached input totals 122,445. All native final continuations and the rejected edit
are charged. The raw provider evidence occupies 806,599 bytes; capturing/re-reading
it is not free. Research/coordinator usage is separately exposed by the HUD and is
not included in these four-stream totals.

Caller group setup took 2.294 seconds. Candidate object-store logical read/write
traffic was 42,899/24,968 bytes (Astra) and 52,902/27,541 bytes (Sol). Hashing,
memory preflight, checker timings, raw capture and post-audit re-execution are
retained in the audits. Staging/file/SQLite/physical disk traffic and full process
cost are not completely instrumented: zero-valued generic store counters must not
be interpreted as zero whole-system staging cost. Native elapsed scopes were
88.12→79.84 seconds for Astra and 142.82→74.87 for Sol; separate setup/audit costs
must be added for whole-workflow accounting.

## Adjudication and next boundary

**OBSERVED:** actual native dynamic-tool registration, identity-bound invocation,
safe rejected edit, successful checked publication, continued ordinary tool access,
and native model-written final answers all worked. The 18 focused transport/effort/
publication tests also pass, including stale authority, duplicate delivery, restart,
interrupted checking and lost publication acknowledgement. These engineering tests
do not establish normal Codex-app pre-inference interception or hostile-host safety.

**CONDITIONAL:** the internal interface is usable for the remaining cohort tasks.
Neither model freezes: this is one of seven predefined cells, and the complete
release medians/capability gates remain pending. A poor maintenance cell alone
does not mathematically rule out the seven-cell median. Conversely, historical
selector-shaped 90/90 wins cannot fill missing native-answer cells.

**INFERRED:** Sol's avoidable residual is exact edit transmission and obtaining a
reviewable published diff. Astra has duplicate loading plus genuine semantic probes.
The next small interface correction should preserve exact source text without JSON
escaping in its presentation and return the actual bound diff/scope facts with the
execution receipt. This can remove a reason for separate inspection; it does not
authorize suppressing independent review or guarantee another segment disappears.

Do not remove semantic probes, final model authorship, reported reasoning costs or
failed calls to make the numbers pass. Do not attribute this regression causally to
normal prose alone: these are different model/effort and protocol cells from the
older compact-final results. The final answer itself is only part of total output.

Before another native call, replay this correction against exact frozen artifacts
and hostile stale/restart cases. Kill it as a primary output attack if it merely
adds receipt bytes without removing observed work. After that, qualify the fixed
task mix under a newly frozen version; retain these V1 failures rather than replace
them with the improved candidate. No new native call was spent on the cross-audit.

## Reproduction

`python3 docs/research/native-output-v1/verify_artifacts.py` verifies public
derivative hashes/counters and reruns all four artifacts and all three probes.
Public usage excerpts are not independent provider attestations; full private
native streams/configuration were checked by the frozen `audit_native.py`.
Original local results remain `AWAITING_AUDIT` as written by the runner; separate
audit artifacts contain the adjudication. No inference or original-state rewriting
is performed by the public verifier.
