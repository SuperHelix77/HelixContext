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
