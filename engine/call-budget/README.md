# Fixed-first-call cost bound from native traces

Five existing native traces were re-read. Each has two usage updates; each last-call receipt sums exactly to the final cumulative totals, including the reported cached and reasoning subsets. No new model calls were made.

In the baseline large-output run, the first call consumed 19,468 input and 75 output tokens. The complete run consumed 57,817 input and 80 output tokens. If a candidate leaves the first call unchanged, it cannot save more than 66.3% input or 6.25% output, even under the impossible best case of deleting all later tokens at zero overhead.

Proof: candidate cost is at least the unchanged first-call cost, so savings are at most one minus first-call cost divided by total baseline cost. This applies separately to input and output.

This is a conditional measured bound for the recorded fixture and restricted post-first-call intervention. It is not an impossibility result for Helix. A changed initial command, earlier input compilation, fewer future model invocations, or a different workload changes the premise. It also does not identify how much initial context is platform-controlled.

## Decision

PostToolUse-only reduction cannot satisfy the joint 80% objective on this fixture. Stop using this fixture as a prospective end-to-end target test for that mechanism. Keep it as an exact-preservation and delivery diagnostic.

The initial output here is largely command-generation work, while the final response costs five tokens. Further shortening the final response has little possible benefit. Investigate initial plan/interface costs and repeated model-boundary crossings; retain reasoning settings and all necessary decisions and checks. Do not count deterministic execution as preserved reasoning unless task outcomes and intermediate obligations are tested.

Different second-call usage despite identical command-event bytes also reinforces that event bytes do not determine native context cost. The available traces cannot isolate the cause of that difference.

Reproduce with `python3 audit.py --traces /path/to/private/native/traces --output RESULT.json`. Raw trace bodies stay private. Hash commitments and native counts are included in RESULT.json. No hooks or installed skills changed.
