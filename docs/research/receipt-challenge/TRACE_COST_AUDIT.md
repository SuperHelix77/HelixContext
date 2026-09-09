# Where the stopped Astra pilot spent observable work

**OBSERVED:** the raw usage/event hashes remain bound to the stopped run. This
read-only audit adds no native calls and changes no runtime settings, skills,
tools, reasoning effort or Engine implementation. `TRACE_COST_AUDIT.json` and
`trace_cost_audit.py` record the extraction, tokenizer proxy and exact byte sizes.

## Separate native tokens from representation proxies

| Observable text | UTF-8 bytes | o200k proxy tokens |
|---|---:|---:|
| Complete caller prompt | 2,725 | 664 |
| Attached Helix skill, receipt hash verified | 1,819 | 317 |
| Global AGENTS current snapshot | 2,305 | 465 |
| Exact duplicated contract + proposal | 856 | 174 |
| Directory-discovery command | 46 | 19 |
| Evidence-read/hash-display command | 316 | 87 |
| Mixed validation command | 2,796 | 718 |
| Its mechanical binding prefix | 534 | 127 |
| Its new semantic-test suffix | 2,247 | 584 |

These proxy columns are **not native accounting partitions**. Tokenizing pieces
separately is not additive to a full prompt, and the full platform-rendered prompt
is unavailable. In particular, do not subtract these proxies from 19,397 first-
segment native input and label the remainder Helix overhead, fixed system tokens,
or removable context. The global AGENTS source path was reported by the runtime;
its current bytes are not a historical content binding. The attached skill is
bound by the native registration receipt.

The duplicated contract/proposal is exact and unnecessary as new information.
However, the evidence-read output also introduced checker/log contents and verified
local bytes. Its whole 847-proxy-token output cannot be classified as duplication.
The mixed command contains fresh semantic tests and the independently reproduced
alias counterexample. That suffix is a candidate for eventual reusable test
scaffolding, not evidence that semantic checking itself can safely disappear.

## A proposed shortcut ruled out before spending another model call

The captured `thread/start` request already sets `skills.max_context_tokens=512`.
Current official configuration documentation defines this as the initial skill
catalog budget; selected skill bodies are separate. [Configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference),
[skill loading documentation](https://learn.chatgpt.com/docs/build-skills).

**CONDITIONAL:** assuming this runtime honors that documented catalog cap, and
holding this four-segment trajectory unchanged, eliminating the entire catalog
would remove at most `4 * 512 = 2,048` input tokens: **2.52%** of 81,365.
That is an unchanged-trajectory ceiling, not an intervention result or a prediction
about output. Exact rendered catalog size is unknown. Further catalog trimming
cannot be justified as the primary 80% attack on this evidence, and disabling
capabilities to claim a saving would violate the research objective.

## Round ownership is the material remaining hypothesis

Native segment input is 19,397 / 19,581 / 20,668 / 21,719; output is
73 / 114 / 862 / 328. Later input totals 61,968 (76.16% of total). This locates
cost; it does not prove all later rounds removable. The 862-output segment includes
new tests that found a genuine contract ambiguity. A system that stops before
that challenge would be cheaper by removing useful capability.

The data therefore split the next intervention into responsibilities:

- Caller may supply a verified inventory and binding results before inference,
  eliminating a reason to discover files and regenerate hash scaffolding. It must
  charge the work and permit exact source checks on mismatch or suspicion.
- Astra retains semantic review, test intent, requirement challenges and authority
  to request additional evidence. New test generation is not mechanical just
  because its output happens to be executable code.
- Engine may execute an already selected, version-bound test procedure and return
  scoped outcomes. Reusing a procedure requires a declared dependency/mutation
  model. This pilot's public-alias ambiguity must remain in the failure record.

**UNTESTED:** whether caller-owned inventory/binding actually removes the first two
commands without compensation, and whether prepared test scaffolding reduces output
without suppressing new challenges. No further call is warranted merely to show a
smaller catalog or shorter receipt.

## Next research gate, not a new benchmark launch

Do not rerun the stopped fixture with its troublesome state silently excluded.
Before another model call, define one versioned continuation task with explicit
state ownership, preserve alias-mutation/changed-relevance challenges, and charge
initial semantic preparation plus every reuse. Compare identical full tasks and
tools; retain exact cold evidence. Qualify the evaluator using counterexamples
before measuring an amortized benefit. This targets repeated model work rather
than presenting another easy single-call selector as general 80/80 evidence.

Prepared cognition remains a hypothesis. No memory tier, generic IR, new router,
new plan system or production receipt executor was built by this audit. The
three-model representative and long-horizon parity gates remain open.
