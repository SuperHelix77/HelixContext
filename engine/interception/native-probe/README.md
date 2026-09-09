# Native configuration probe: observer not enabled

The native app server recognized a task-scoped PostToolUse observer definition but marked it **untrusted**. Supplying the exact unchanged definition hash via a session-scoped `hooks.state` override did not change that status. Two configuration-only attempts stopped at the trust assertion, before `thread/start` or `turn/start`.

- No model inference was launched.
- No native tool envelope was captured.
- No global config was modified.
- No blanket hook-trust bypass was used.

`CONFIGURATION_RESULT.json` records the observed boundary. This only establishes that the tested session override did not confer trust; it is not evidence that all supported review flows fail.

The prepared `observe.py` archives hook-input bytes only when the reported cwd matches its adjacent `sandbox` directory. It returns `{}` and never replaces results. Normal registration/review is required before executing the native probe. The public source is not an enabled hook.

The runtime client, attempted configuration and observer driver are retained for audit. They assume the local Codex CLI path used by this project. Raw account/environment traces and private absolute configuration paths are omitted.

Next step: obtain approval for the exact temporary observer, use the normal configuration/review flow, confirm trusted status, run the synthetic native observation, then remove only that temporary registration. Compression remains disabled during observation.

## Subsequent user-authorized observation succeeded

After explicit user approval, the observer was temporarily registered in the normal configuration and its exact definition was trusted. One native Sol High turn captured one Bash hook event and finished DONE. All temporary hook/trust registrations, including a runtime-created synthetic-project trust entry, were removed. Original configuration values were restored; unrelated text was preserved.

The received `tool_response` was a **string**, exactly matching the synthetic 18,019-byte stdout. It contained no structured exit-code field. The current interception adapter correctly passes this unsupported envelope through unchanged; adapting it requires resolving metadata preservation first. No compression was enabled.

The native turn reported 46,802 input tokens and 130 output tokens, including 25,600 cached-input tokens as a subset. The hook reported `permission_mode=bypassPermissions` despite the driver's workspace-write request, so this result must not be cited as sandbox enforcement evidence. The installer changed no permission settings.

`NATIVE_OBSERVER_RESULT.json` contains the scoped result and a private-trace hash commitment. Prior failed session-only registration attempts remain preserved above.
