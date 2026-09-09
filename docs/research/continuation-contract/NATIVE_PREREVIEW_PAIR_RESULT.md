# Fresh valid pair: semantic pre-review plus caller execution

**OBSERVED: 32.75% input savings, 9.59% output savings; uncached input +102.29%.**
**Disposition: DO NOT PROMOTE as an 80/80 policy.**

Prospective driver `b71c864`; manifest SHA256
`cc9b4363a81ae2c470ad626c5c985c75671727ca156c0f83fc92cb14f696252c`.
Two fresh Astra High native turns, candidate then control, no retries or recovery
turn used. The same-thread research runner was used for both arms. Candidate skill
was explicitly attached; control had the same discoverable skill but no attachment.

Both received the same exact valid proposal, contract, full finite checker and
cross-instance checker. Tools and supplemental semantic tests remained available.
Both were asked for the same JSON assessment/obligations, and both were explicitly
told no separate report file was required. Native could batch commands freely.
Native staged and ran both checkers then reviewed. Candidate reviewed before
caller-owned exact staging and checking, predicting both checks would pass.

| Metric | Native | Helix pre-review | Saved |
|---|---:|---:|---:|
| Input | 126,477 | 85,055 | 32.75% |
| Output | 1,606 | 1,452 | 9.59% |
| Cached input subset | 113,664 | 59,136 | — |
| Uncached input | 12,813 | 25,919 | **−102.29%** |
| Reasoning output subset | 146 | 96 | — |
| Model segments | 6 | 4 | — |
| Commands | 6 | 3 | — |
| Visible tool-output bytes | 8,957 | 10,670 | — |
| Native elapsed seconds | 66.96 | 59.10 | — |
| Final disposition | ACCEPT | ACCEPT | — |
| Independent declared checks | PASS | PASS | — |

No monetary-savings claim: cache behavior differs and complete effective cost is
unqualified. Caller candidate staging/checking took approximately 0.386 seconds;
setup/preflight receipts are retained. Physical/SQLite/interpreter/recovery costs
are not collapsed into a fabricated dollar total. Cached and reasoning tokens are
subsets, not extra charges added to the native totals.

## Critical observation

**All 85,055 candidate input tokens occurred before delegated application.**
There was no post-execution model invocation and no unexpected check outcome.
Therefore this run's expensive self-review cannot be blamed on a mandatory final
re-entry. One user turn contained four model segments.

The candidate:

1. Discovered task files.
2. Read the attached skill, source, contract and both checker implementations.
3. Generated/executed supplemental semantic probes, reporting 35 passing cases.
4. Returned acceptance with explicit expected check outcomes and limitations.

The caller then staged the exact proposal and ran the required checks. Both passed.
Moving the review earlier removed some execution work, but did not remove the
model's inspection and semantic testing. No tool prohibition, reduced reasoning,
or forced omission of tests was used to reach the observed numbers.

## Verification

Both model assessments were read substantively, not graded solely by JSON fields.
Both cover private validation before mutation, exact-int validation, exception
identity, alias/list identity, stale-cursor behavior, empty batches, independence
and domain limitations. Candidate explicitly states the declared checks had not
run and predicts their successful execution. Native cites actual check results.

The audit verifies all frozen inputs unchanged; staged module byte-identical to
the proposal; staged contract and checkers identical to their originals; raw
native/normalized hashes; per-segment sums and final cumulative usage. Independent
replay passes 2,745 sequences / 8,282 transitions and the separate 1,000-sequence /
3,000-transition cross-instance checker for both arms. Original base modules remain
unchanged. The candidate is AWAITING_REVIEW in the research gate: no production
semantic-closure decision has been silently activated.

These are finite development checks, not proven equality of generated test suites
or universal intelligence/workflow parity. A previously exposed supplemental-suite
gap must not be presumed eliminated beyond the added checker’s actual coverage.

## Adjudication

- **WEAKENED:** moving semantic review before delegation alone restores near-80/80
  on this workflow. The fresh pair does not support that prediction.
- **SURVIVES, bounded:** early semantic review can catch the tested defect, and
  real same-thread amendment recovery works in its separate test.
- **OBSERVED:** initial semantic work can itself contain repeated model-context
  cycles. “Review once” is not equivalent to “one model segment.”
- **UNKNOWN:** causal roles of exact wording, case selection, order and caching.
  Do not compare the prior recovery turn’s 19k input as a matched counterfactual;
  that turn had different task evidence and instructions.

The 80% budgets here were 25,295.4 input and 321.2 output. This candidate substantially
exceeds both. Do not repair that headline with removed semantic tests, old controls,
a narrower assessment, or a favorable cache-only presentation.

Stop review-timing-only micro-optimization on this fixture. Any next proposal must
attack measured first-turn inspection/test-generation costs while retaining their
semantic function and charging replacement machinery. The representative model /
task matrix and long-horizon/recovery tests remain required for the full objective.

Machine result: `NATIVE_PREREVIEW_PAIR_RESULT.json`. Raw prompts/manifests/events:
`/Users/mert/Documents/ChatGPT/Helix/research/native-prereview-pair-v1-20260909`.
HUD presents this pair using labelled terminal status projections with unchanged
native counters and event hashes, separately from safety/recovery experiments.
