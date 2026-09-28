# PostToolUse delivery probe — runbook

Status: **NOT INSTALLED.** Nothing in this directory is active on this machine.
Purpose: determine whether any schema-valid response field actually replaces the
model-facing tool result. One open question, two arms.

## Why two arms

The prior native V2 probe emitted `{"continue": false, "stopReason": ...}` and the model
reported null schemas. The cause was never established. A later assessment wrongly
concluded the shape was invalid; that was retracted after the extracted schema showed
`stopReason` **is** defined, and `jsonschema` Draft7 validation confirmed the prototype's
shape is VALID.

So both plausible shapes stay live:

| Arm | Response | Note |
|---|---|---|
| A | `{"continue": false, "stopReason": <text>}` | what the existing prototype emits |
| B | `{"hookSpecificOutput": {"hookEventName": "PostToolUse", "updatedMCPToolOutput": <text>}}` | field named for tool-output replacement |

Schema validity is not delivery. The probe must run both.

## Offline validation (already run, passing)

```
python3 engine/interception/delivery-probe/test_arms.py
```

Checks: both arms schema-valid; arms distinguishable on the wire; small output passes
through; non-Bash tools untouched; malformed input fails closed; the observation log
proves the hook fires and covers both arms.

## Prerequisite: hook trust

`native-probe/CONFIGURATION_RESULT.json` records that a task-scoped PostToolUse observer
registered as **untrusted**, and that a session-provided review hash did **not** confer
trust. Native interception does not run until the hook is trusted via the normal
configuration/review flow. Budget for this; it is the step that silently blocks.

## Install (requires explicit user approval)

1. Back up the config: `cp ~/.codex/config.toml ~/.codex/config.toml.pre-posttooluse-probe`
2. Append to `~/.codex/config.toml`:

```toml
[[hooks.PostToolUse]]
matcher = "^Bash$"
[[hooks.PostToolUse.hooks]]
type = "command"
command = "python3 /Users/mert/helix-ctx-src/engine/interception/delivery-probe/hook_arms.py"
timeout = 5
```

3. Review/trust the hook through the normal Codex approval flow so a
   `hooks.state."<config path>:post_tool_use:0:0"` entry with a `trusted_hash` appears.
   The hook stays inert until `HELIX_PROBE_MODE` is set in its environment.

4. Run arm A, then arm B, each as its own turn with the env var exported:

```
export HELIX_PROBE_MODE=A
export HELIX_PROBE_LOG=/tmp/helix-probe-A.jsonl
# then, as the agent, run a Bash command producing >12000 bytes, and ask:
#   "If you can read this, report the marker and nothing else."
```

Repeat with `HELIX_PROBE_MODE=B`.

5. Read the logs and decide:

| Observation | Conclusion |
|---|---|
| Model reports the marker under arm A only | `stopReason` delivers; B unnecessary |
| Model reports it under arm B only | `updatedMCPToolOutput` delivers; **check whether it applies to a non-MCP `Bash` tool** |
| Model reports it under both | either field works; prefer B for intent |
| Model reports it under neither | delivery via response field does not work on this runtime; close the thesis |
| Log has no `emitted` entries | the hook never fired — a configuration/trust problem, not a delivery result |

6. Remove the hook block and restore trust state. Verify with
   `grep -c "hooks.PostToolUse" ~/.codex/config.toml` -> 0.

## Hard limits

- The hook does nothing unless `HELIX_PROBE_MODE` is set. Installing it unarmed is inert.
- Matcher is `^Bash$`; other tools are untouched by construction and by test.
- No savings claim may be made from this probe. It has no paired ordinary control, and the
  earlier denominator defect stands (25,622 raw event bytes vs 4,101 actually delivered).
  Measure native input tokens, never raw event bytes against packet bytes.
- `tool_response` is observed to be a **string**, not `{output, exit_code}`. The existing
  prototype only accepts the structured envelope and passes the real native shape through
  unchanged. This probe deliberately accepts both shapes.
