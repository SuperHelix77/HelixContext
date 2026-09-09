# Experimental native tool-result interception adapter

**Not installed. Native compatibility and model benchmarks are pending.**

The [official Codex hook documentation](https://learn.chatgpt.com/docs/hooks) describes `PostToolUse` continuation feedback that replaces the model-facing result. `decision: block` rejects a nested code-mode promise, whereas `continue: false` supplies feedback without that rejection. The dedicated `updatedMCPToolOutput` field is not supported. These documented differences motivated the prototype; they do not demonstrate its runtime compatibility.

`post_tool.py` accepts only an explicitly recognized structured Bash response with a string `output` and integer `exit_code`. Large outputs are projected; unknown shapes, small outputs, other tools and explicit full-output retrieval pass through unchanged. This schema is a synthetic test envelope, not yet a verified native Bash envelope.

Before returning replacement feedback, the adapter stores and reads back the exact hook-input bytes in a caller-supplied task-local archive. All non-output result metadata stays in the packet. The projection is explicitly partial. Archive failure produces `{}`, leaving native output processing unchanged. No hook command executes the source command or changes its permissions.

An explicit `HELIX_FULL_OUTPUT=1` marker in a retrieval command disables reduction, allowing archive expansion without recursion. This is a prototype convention, not native platform functionality. The archive retains the received tool result, not bytes already truncated upstream. Input archives can include private commands and tool content and should remain local; none of the real native traces are published here.

No `additionalContext` is emitted: quoted tool data should not become developer instructions. The adapter uses `continue: false` and `stopReason`. It must still be tested against real direct and nested tool callers; maintaining promise success alone does not prove preservation of the returned value's schema or workflow behavior.

## Offline checks

```sh
python3 -m pytest -q engine/interception/test_post_tool.py
```

**6 passed.** Checks cover exact archival, nonzero exit preservation, output budget fallback, unsupported inputs, explicit expansion and archive failure. `fixture-result.json` records the synthetic received/replacement sizes and application byte counters. This is not a native input/output-token benchmark.

## Remaining gates

1. Capture the actual native hook envelope in an isolated task without reducing anything.
2. Verify exact reviewed hook configuration and test continuation feedback in direct and code-mode calls; do not bypass tool permissions or hook review.
3. Validate explicit archive expansion, upstream truncation detection, metadata preservation and failure recovery.
4. Measure complete native usage and recurring process/archive overhead on all requested models against efficient ordinary controls.

Until those gates pass, this adapter is an experimental source file, not an enabled compression policy.

## Metadata bridge and native attempt

`metadata_bridge.py` records immutable command-completion metadata keyed by session, turn and tool-call ID. The adapter can consume a native string only when the corresponding metadata exists and the complete output digest matches. Missing, conflicting, cross-turn, corrupt or changed output fails open. Receipts correlate data; they are not an access-control boundary against another process with write access.

**12 adapter/bridge tests pass.** Offline replay of earlier captured native events correctly correlates identical text with exits 0 and 7, preserving exact hook-input archives (`BRIDGE_REPLAY_RESULT.json`).

A subsequent native Sol High replacement attempt **did not pass** (`BRIDGE_NATIVE_RESULT.json`). The app-server events contained 25,622 output bytes per command, but the hook received 4,101-byte strings with native truncation warnings. The strict output-hash guard rejected both replacements. The model returned correct exit codes and null packet schemas, confirming that ordinary output remained in use.

The native attempt consumed 64,517 input tokens and 393 output tokens. The temporary hook was removed and original configuration values restored. A pre-existing passive observer was left unchanged and contributes latency to this run.

This result changes the accounting baseline: raw terminal-event bytes can substantially exceed the output already delivered by Codex. Future work must preserve the raw event separately, handle upstream truncation explicitly, and compare actual native token usage rather than advertising raw-to-packet size reduction as savings. Exact event ordering, nested code-mode compatibility and end-to-end quality remain open.
