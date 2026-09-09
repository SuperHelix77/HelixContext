# Astra transfer: exact success, below 80/80

The first fresh Astra High app-server pair measured **67.35% input / 65.78%
output savings**. Both exact artifacts and source-preservation checks passed.
No freeze: the 80/80 objective remains unmet.

| Metric | Control | Helix |
|---|---:|---:|
| Native input including cached | 63,449 | 20,716 |
| Native output including reported reasoning | 751 | 257 |
| Cached input, subset | 40,832 | 11,264 |
| Reported reasoning output, subset | 0 | 198 |
| Command calls | 2 | 0 |
| Exact artifact bytes | 6,102 | 6,102 |

Total reported cost: **84,165 input / 1,008 output tokens**, two calls, no
experiment-level retries, no budget amendment. Both arms stayed within the
prospective 200,000-input / 6,000-output per-call ceilings. Neither raw stream
reported an error notification. Raw native counters and normalized HUD totals
were independently compared, and every supplied source hash was rechecked.

The transfer resolved the earlier helper-discovery failure mode: the candidate
made no commands and used native skill attachment plus caller completion.
The control was already efficient at two commands. Consequently, the relative
saving is smaller than Sol's on this task. This is measured task behavior, not
an inference about private model cognition or a universal Astra characteristic.

## Residual boundary

At 80%, this control permits at most 12,689 input and 150 output tokens after
integer rounding. The candidate used 20,716 input and 257 output. Its 198 reported
reasoning-output tokens alone exceed the total-output allowance if held fixed.
That is conditional arithmetic, not proof of irreducible reasoning. High remains
unchanged; reported zero reasoning in control does not mean no reasoning occurred.

No post-tool optimization can help this particular zero-tool candidate. The next
intervention must address pre-inference admission, avoid unnecessary computation,
or establish a legitimate different workflow's economics. Do not inflate the
control, delete required source evidence, suppress checks, lower High, or add
more post-tool reducers in response to this result.

A diagnostic tokenizer proxy counts 1,881 tokens in supplied task text, 317 in
the attached skill and 124 in local AGENTS using `o200k_base`. Those are **not
native input-token partitions**: the actual model tokenizer and internally
supplied context are not fully observed. The native thread lists global and
local AGENTS as instruction sources. The remainder is unattributed, not a proved
removable overhead or fixed lower bound. A full admission rewrite requires
capability/workflow falsifiers before another costly measurement.

Next work should cover a genuinely distinct task and native failure/recovery or
latent-future-relevance behavior. This one reused development fixture does not
satisfy the requested three-task matrix or long-horizon no-loss condition. Sol
remains frozen; Astra stays the active research model before Luna.

[Raw-metric adjudication and hashes](ASTRA_TRANSFER_RESULT.json).
[Prior Astra behavior audit and prospective protocol](ASTRA_TRANSFER_AUDIT.md).
