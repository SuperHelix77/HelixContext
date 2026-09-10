# Sol native-answer V2: do not promote

Frozen `db1566f`; manifest
`47cf9978a9fa2cbf4c27c9263cbd22a61a3d72d518486d23f73580f50fc3c932`.
One fresh known maintenance pair, control then Helix, no reused control or omitted
attempt. High effort verified in native requests/replies. Engine stayed active.

| Metric | Control | Helix | Saved |
|---|---:|---:|---:|
| Native input | 182,276 | 100,637 | 44.79% |
| Native output | 2,385 | 2,151 | 9.81% |
| Uncached input | 29,956 | 27,421 | 8.46% |
| Reported reasoning, included in output | 873 | 1,046 | -19.82% |
| Model segments | 8 | 4 | 50% |

**OBSERVED:** both artifacts pass the unchanged23 public/regression tests and94
independent finite cases. The control's additional search-mode/literal-operator
probe passes on both artifacts. The candidate's internal edit succeeds on its first
attempt. The native receipt contains the exact bound1,121-byte diff; independently
applying it to the archived original reconstructs the actual published source.
Receipt identity, before/after hashes and actual native tool output agree.

**FALSIFIED on this run:** providing that diff did not eliminate a separate final
inspection. Candidate sequence:

| Segment | Observable operation | Input | Output | Reported reasoning |
|---|---|---:|---:|---:|
|1|Read current source and Git status despite supplied source|23,772|356|165|
|2|Submit full-function old/new edit; Engine checks and publishes|24,352|745|189|
|3|Run Git status, diff/check and `shasum` after the diff receipt|25,690|762|605|
|4|Write normal final answer|26,823|288|87|

No private reasoning content is used. The observed605 reasoning tokens share a
segment with mechanical inspection; they cannot all be classified as redundant
mechanics. Removing that whole segment is not a proven capability-preserving action.

V1 also had four candidate segments. Its failed selector/repair was replaced here
by an initial source/status inspection; final inspection remained. V2 candidate
input is only0.61% below V1 and output is15.77% higher. These are descriptive
cross-run differences, not isolated causal effects; the fresh controls differ too.
V2 control had no V1 `codexworkflow` detour, but did recover from the same missing
`pytest` executable using `python3 -m pytest`. All costs remain included.

## Output and accounting

The final answer is model-written ordinary prose after execution. Its API, test,
source hash and scope claims match retained evidence. However it uses a `file://`
local link, contrary to the configured absolute-path Markdown link convention.
That defect is preserved in the artifact and marked `FAIL_FILE_URI` by
`REVIEW_AUDIT.json`; the caller does not rewrite the answer to hide it. Do not claim
complete final-answer conformance or release this profile from finite coding PASS.

The current [official Standard pricing](https://developers.openai.com/api/docs/pricing)
snapshot (2026-09-10 06:04 UTC) estimates $0.228452→$0.181990 for the short-context
scenario:20.34% saved. Long-context scenario:20.92%. These are API-equivalent
scenarios, not included-plan quota, a bill, or full effective cost. Live HUD prices
refresh and expire; static snapshot source/hash remain in `artifacts/COST.json`.

Both streams total282,913 input/4,536 output, with225,536 cached input and1,919
reported reasoning tokens already included in output. Preparation took1.088s.
Candidate object-store logical reads/writes/hashing were63,095/29,093/92,188 bytes.
The1,862-byte receipt is a real recurring input cost. Native elapsed scope was
96.84→88.50s; setup, audit and complete physical I/O are separate. Raw native
captures occupy374,524 bytes. Research/coordinator costs remain separately visible
in the HUD and are not hidden inside a token-savings claim.

## Decision

**REJECT V2 as a qualified savings policy.** Exact source/diff primitives remain
tested infrastructure; a usable interface is not an economic qualification.
Stop further native runs of this variant. Preserve V1 and V2 separately. No model
freeze, no completed cohort median, and no normal-app integration claim.

The evidence narrows the next question: the model still acquires current workspace
and scope facts independently even when source/diff bytes are supplied. A diff is
not a complete scope certificate. Any later proposal must identify the exact
missing mechanical fact and bind it, or show why the inspection is required.
Do not add another vague "trust Helix" instruction or suppress semantic review.

The fixed seven-task cohort remains incomplete. This per-area failure neither
establishes nor rules out its eventual median; incompatible historical selector
wins are not substituted. Further broad native spending on this unchanged policy
is not justified by the pilot. Resume only after a specific offline falsifier
supports a revised boundary, or to measure a prospectively chosen remaining task
under an explicitly frozen cohort policy, without selectively hiding weak cells.

Reproduce task evidence with
`python3 docs/research/native-output-v2/verify_artifacts.py`.
This runs no inference and does not overwrite the published verification receipt.
Full private native streams were checked separately by the frozen machine audit;
public excerpts are not independent provider attestations.
