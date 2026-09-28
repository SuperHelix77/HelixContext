"""Two-armed PostToolUse delivery probe. NOT INSTALLED.

Purpose: determine which schema-valid response field, if any, actually replaces the
model-facing tool result. Both arms are valid per the extracted codex-cli 0.156.1 schema:

    {"continue": false, "stopReason": <text>}                      # arm A (prototype's)
    {"hookSpecificOutput": {"hookEventName": "PostToolUse",
                           "updatedMCPToolOutput": <text>}}       # arm B

Arm B is the field named for MCP tool-output replacement. Arm A is what the existing
prototype emits. Validity is not delivery: the prior native probe returned null schemas
with arm A, and the cause was never established.

This hook is deliberately inert unless HELIX_PROBE_MODE is set. It never replaces a
result in normal operation, and it never touches non-Bash tools.
"""
import json, os, sys, hashlib, time
from pathlib import Path

# Only act when explicitly armed. Prevents accidental installation from rewriting results.
ARM = os.environ.get("HELIX_PROBE_MODE", "")          # "", "A", "B"
LOG  = Path(os.environ.get("HELIX_PROBE_LOG", ""))    # caller-supplied log path
MIN_BYTES = int(os.environ.get("HELIX_PROBE_MIN_BYTES", "12000"))

def packet_for(payload, tool_name, response_bytes):
    return {
        "schema": "helix.delivery-probe.v1",
        "arm": ARM,
        "tool_name": tool_name,
        "received_result_bytes": response_bytes,
        "marker": "HELIX-PROBE-MARKER-9c1f",
        "question": "If you can read this, report the marker and nothing else.",
    }

def emit(text):
    if ARM == "A":
        return {"continue": False, "stopReason": text}
    if ARM == "B":
        return {"hookSpecificOutput": {"hookEventName": "PostToolUse",
                                       "updatedMCPToolOutput": text}}
    if ARM == "C":
        # control: additive context, no result replacement, no turn stop
        return {"continue": True,
                "hookSpecificOutput": {"hookEventName": "PostToolUse",
                                       "additionalContext": text}}
    return {}

def record(entry):
    if not LOG:
        return
    try:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        with LOG.open("a") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass

def main():
    try:
        raw = sys.stdin.buffer.read()
    except Exception:
        print("{}"); return
    try:
        payload = json.loads(raw)
    except Exception:
        print("{}"); return

    event = payload.get("hook_event_name")
    tool  = payload.get("tool_name")
    # Always log observation, even when not armed: proves whether the hook fires at all.
    record({"ts": time.time(), "event": event, "tool": tool, "armed_arm": ARM or None,
            "input_bytes": len(raw),
            "response_type": type(payload.get("tool_response")).__name__,
            "response_bytes": len(str(payload.get("tool_response") or "").encode())})

    if not ARM or event != "PostToolUse":
        print("{}"); return
    if tool != "Bash":
        print("{}"); return
    resp = payload.get("tool_response")
    nbytes = len((resp if isinstance(resp, str) else json.dumps(resp, default=str)).encode())
    if nbytes < MIN_BYTES:
        record({"skipped": "below_min_bytes", "bytes": nbytes})
        print("{}"); return

    out = emit(json.dumps(packet_for(payload, tool, nbytes)))
    record({"emitted": True, "arm": ARM, "bytes": nbytes,
            "out_keys": sorted(out.keys()),
            "out_sha256": hashlib.sha256(json.dumps(out, sort_keys=True).encode()).hexdigest()})
    print(json.dumps(out))

if __name__ == "__main__":
    main()
