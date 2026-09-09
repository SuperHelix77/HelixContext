# Local context diagnostic and global instruction compaction

OBSERVED: installed CLI exposes `codex debug prompt-input` and `codex debug models`.
Both are diagnostics; no inference turn was requested. Prompt reconstruction used
the recorded model, High effort, skill limit512, approval never, workspace-write,
task cwd and exact task text. It cannot reproduce the explicit skill input item
used by app-server and is not the original transmitted native request.

The matched candidate reconstruction contains4,250o200k proxy tokens across its
input-text blocks. The current catalogue contains a4,110proxy-token base template;
`base_instructions` and `model_messages.instructions_template` are byte-identical
and must not be added as separate costs. Do not add all catalogue policy variants
or assume which were selected. These observations expose additional components,
not an additive native19,560-token decomposition. Tool schemas and the remaining
serialization boundary stay UNKNOWN. Raw diagnostic/instruction contents remain
local; only sizes, identities and limitations are published.

## User-authorized AGENTS.md optimization

The loaded global file `/Users/mert/.codex/AGENTS.md` was compacted in place:

| | Before | After |
|---|---:|---:|
| UTF-8 bytes | 2,305 | 1,790 |
| o200k proxy tokens | 465 | 383 |

**17.63% fewer instruction proxy tokens.** Manual review and25explicit coverage
checks preserve recall timing/commands, relevance and evidence rules, failure
fallback, verified memory recording, excluded memory content, actual skill
activation/session identity/mode changes/retirement, post-compaction restoration,
user authority, peer dependency/event handling, liveness cautions and child scope.
No new helper, indirection or deferred instruction loading was introduced.

The exact original is backed up locally at
`research/agents-md-optimization-v1-20260909/AGENTS.before.md` under the user workspace.
An optimistic byte equality check prevented overwrite of an intervening edit;
replacement retained file permissions and was atomic. A new matched diagnostic
contains the entire new body and falls from4,250to4,168text proxy tokens, exactly82
fewer. This is renderer verification, not an actual native billing or general
behavioral-parity test. No native benchmark was rerun to measure this small change.

All future paired experiments must use and bind the same new global instruction
version in both arms. Frozen historical receipts were not regraded or modified.
The82-token reduction cannot explain or solve the bulk shared19kcharge.

Machine artifact:`CONTEXT_DIAGNOSTIC_RESULT.json`.
Local backups, raw diagnostics and semantic coverage receipt remain in
`/Users/mert/Documents/ChatGPT/Helix/research/agents-md-optimization-v1-20260909` and
`/Users/mert/Documents/ChatGPT/Helix/research/first-context-diagnostic-v1-20260909`.
