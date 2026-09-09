# Memory / reducer functional coverage and usage admission

2026-09-09. Verdict: **partial functional overlap, not feature parity**. This is a
bounded repository/primary-document audit, not comparative product certification.

External capabilities were checked against the current upstream
[Claude-Mem README](https://github.com/thedotmack/claude-mem#how-it-works) and
[RTK README](https://github.com/rtk-ai/rtk#what-rtk-does). Upstream claims are not
independent measurements, and upstream can change. Claude-Mem documents lifecycle
capture, persistent observations, search/timeline/detail retrieval, configurable
context, privacy exclusions and hybrid search. RTK documents broad command
adapters, automatic rewriting, raw passthrough and usage analytics. Their reported
reductions must not be imported as Helix whole-task savings.

| Useful capability | Current Helix evidence | Status |
|---|---|---|
| Persistent project/session evidence | `workflow_memory.Memory.record`, SQLite and immutable raw objects | Implemented; logical scope is not an ACL |
| Search → timeline → exact batch retrieval | `search`, `timeline`, `retrieve`, `replay` | Implemented deterministic lexical path; no semantic-search parity |
| Restart/corruption recovery | `rebuild_index`, versioned `memory_epoch` | Tested bounded recovery; expensive validation remains |
| Automatic observation and next-session context injection | Caller integrations plus skill registry; no equivalent universal lifecycle established | Partial / native deployment qualification missing |
| Semantic summaries and hybrid/vector retrieval | No equivalent in inspected memory path | Missing; inference/index cost must be justified first |
| Privacy exclusion controls before archival | No equivalent policy gate in inspected `Memory.record` | Missing for automatic capture; do not activate indiscriminate capture |
| Typed development-command reduction | `reducer_runtime.choose` recognizes constrained pytest/compiler argv | Implemented narrow subset |
| Git/search/package/toolchain adapter breadth | Unknown producers bypass in inspected router | Below RTK coverage |
| Archive, verify, small-output bypass, reducer-failure fallback | `present`/`execute`; exact stream evidence | Implemented, execute-once semantics tested |
| Transparent native command integration | `post_tool` plus metadata bridge; structured-envelope and native route limitations | Experimental/partial, not universal transparent rewriting |
| Per-command metrics and HUD | JSON byte counters, timings, evidence and native usage projections | Partial; no complete physical-I/O or quota ledger |

Verification this turn: 45 tests passed across `test_workflow_memory.py`,
`test_memory_epoch.py`, `test_reducer_runtime.py`, `test_post_tool.py` and
`test_metadata_bridge.py`. These check our implementation's stated invariants;
they do not establish equivalence with either external project.

## Cost decision

OBSERVED in code: every lexical search validates the project's indexed bodies
against archived sources. Correctness protections are present, but the search path
can reread the full project. Frozen epochs provide a separate exact-read path.
Do not remove validation without an equivalent invalidation/integrity mechanism.
Prior recovery amplification and general memory economics remain separate issues.

OBSERVED: unsupported or shell-wrapped argv bypass the typed reducer router.
This leaves an integration gap for model-issued shell commands. Adding adapters
alone cannot fix a runtime path that does not invoke them. Unknown response shapes
and upstream truncation also limit post-tool capture. Exact recovery claims must
refer to the bytes actually captured, not unavailable upstream output.

INFERRED admission: broader adapters and automatic memory may help ordinary noisy,
long-running coding tasks, but savings on current Luna V5 are not supported. Its
native path already has one final semantic segment and no command-output work to
reduce. Extra summaries, a new index or model-facing setup would add costs to that
measured path. No new adapter suite or semantic summarizer is justified as its
output rescue. Feature count is not an optimization objective.

Next feature work, when a trace identifies a material repeated term, must measure
capture coverage, exact recovery under late relevance, preprocessing/retrieval
traffic, injected tokens, extra model turns and complete native input/output.
Archive/privacy scope must be explicit before automatic capture. Safe unknown
producer bypass and no rerun on reducer failure remain mandatory. Do not claim
full parity until lifecycle and command coverage are actually exercised.

Per user sequencing: resume Luna output and capability qualification now; keep
the broader parity gaps open rather than charging Luna for unrelated features.
