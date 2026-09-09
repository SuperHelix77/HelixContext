# Integrated V3: native skill attachment

V2 reached 70.53% input / 73.10% output saving, but retained one model-side
command to read the local skill. It missed the integer 75% allowances by 4,809
input and 46 output tokens. Those aggregate gaps do not identify the exact cost
of that command or prove deleting it would suffice.

V3 changes the attachment boundary rather than weakening the workflow. The
[official app-server documentation](https://learn.chatgpt.com/docs/app-server#skills)
specifies a `skill` input alongside the text invocation so the server injects the
instructions. The installed runtime's generated schema confirms the input's
`type`, `name` and `path` fields. A zero-inference preflight verified Sol High,
workspace-write sandbox and discoverability of the exact local skill.

The caller creates an ephemeral native thread, validates its returned model and
effort, and registers the exact skill snapshot against that actual ID before
`turn/start`. Candidate text invokes `$helixcontext`, with a separate native skill
input pointing at `.agents/skills/helixcontext/SKILL.md`. Inline duplication of the
skill body is removed. Both arms retain identical source files and local
registration instructions. Original semantic rules, High, tools, exact-copy
checks and recovery access remain unchanged. No skill-loading instruction is
silently ignored.

Both arms use fresh app-server turns. The older CLI control is not reused. This
is a new development pair on a reused fixture, not a clean single-component
causal ablation against V2, a holdout, or general capability proof. App-server
loads its normal configuration, unlike the earlier CLI's ignore-user-config
flag; source/config hashes are retained. Comparison is strictly within V3.

Raw received RPC messages are stored exactly in `native-events.jsonl`. Requests,
thread-start response, skill listing, registration receipt and stderr are also
retained. `events.jsonl` is an explicitly derived CLI-shaped projection for the
existing HUD and grader. It is not mislabeled as the original wire. Normalization
keeps command output, Unicode and nonzero exit status; hidden reasoning content
stays cold and is not presented as an explanation of model behavior.

Usage is the **last cumulative** `thread/tokenUsage/updated.total` in the fresh
thread, not the sum of updates. Invalid subsets, nonmonotonic counters, missing
usage, failed turns, identity mismatches or unexpected interactive requests stop
qualification. Server-request errors are recorded; the runner does not silently
approve them. Failed launched usage remains in the receipts. The existing
150,000-input/6,000-output post-call budget, two-call cap and 75/80 gates remain.
No model retry or tuning loop is added.

213 engineering tests passed before launch. The preflight opened a thread but
sent **zero `turn/start` calls**, hence performed no native inference. These
checks establish protocol/engineering readiness, not a V3 token saving. The
paired result is recorded separately after completion.
