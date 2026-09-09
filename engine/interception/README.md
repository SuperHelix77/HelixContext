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
