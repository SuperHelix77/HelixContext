"""Offline validation of the two delivery arms. No model, no native hook, no network."""
import json, os, subprocess, sys, tempfile, pathlib
from jsonschema import Draft7Validator

HERE = pathlib.Path(__file__).resolve().parent
SCHEMA = json.loads((HERE.parent / "schema" / "post-tool-use.command.output.schema.json").read_text())
HOOK = HERE / "hook_arms.py"
v = Draft7Validator(SCHEMA)

def run_hook(payload, arm, log):
    env = {**os.environ, "HELIX_PROBE_MODE": arm, "HELIX_PROBE_LOG": str(log),
           "HELIX_PROBE_MIN_BYTES": "1000"}
    p = subprocess.run([sys.executable, str(HOOK)], input=json.dumps(payload).encode(),
                       capture_output=True, env=env, timeout=30)
    assert p.returncode == 0, p.stderr.decode()[:400]
    return json.loads(p.stdout.decode() or "{}")

def big_payload(n=20000):
    return {"hook_event_name": "PostToolUse", "tool_name": "Bash", "session_id": "probe",
            "tool_input": {"command": "echo hi"},
            "tool_response": "x" * n,   # observed native shape: a STRING
            "turn_id": "t1"}

def main():
    fails = []
    with tempfile.TemporaryDirectory() as td:
        log = pathlib.Path(td) / "log.jsonl"

        print("== 1. both arms are schema-VALID ==")
        for arm in ("A", "B"):
            out = run_hook(big_payload(), arm, log)
            errs = list(v.iter_errors(out))
            ok = not errs
            print(f"  arm {arm}: keys={sorted(out)} -> {'VALID' if ok else 'INVALID'}")
            if not ok: fails.append(f"arm {arm} invalid: {errs[0].message[:120]}")

        print("== 2. arms are distinguishable on the wire ==")
        a = run_hook(big_payload(), "A", log)
        b = run_hook(big_payload(), "B", log)
        if a == b: fails.append("arms produced identical output; probe would be ambiguous")
        print(f"  A != B: {a != b}")

        print("== 3. small output passes through untouched ==")
        for arm in ("A", "B"):
            out = run_hook(big_payload(500), arm, log)
            if out != {}: fails.append(f"arm {arm} replaced a small result")
            print(f"  arm {arm}: {{}} -> {out == {}}")

        print("== 4. non-Bash tool passes through ==")
        pl = big_payload(); pl["tool_name"] = "Read"
        for arm in ("A", "B"):
            out = run_hook(pl, arm, log)
            if out != {}: fails.append(f"arm {arm} touched a non-Bash tool")
            print(f"  arm {arm}: untouched -> {out == {}}")

        print("== 5. malformed input never crashes ==")
        env = {**os.environ, "HELIX_PROBE_MODE": "A", "HELIX_PROBE_LOG": str(log)}
        p = subprocess.run([sys.executable, str(HOOK)], input=b"not json at all",
                           capture_output=True, env=env, timeout=30)
        safe = p.returncode == 0 and p.stdout.decode().strip() == "{}"
        if not safe: fails.append("malformed input did not fail closed")
        print(f"  fail-closed on garbage: {safe}")

        print("== 6. observation log proves the hook fires ==")
        lines = [json.loads(x) for x in log.read_text().splitlines() if x.strip()]
        emitted = [x for x in lines if x.get("emitted")]
        # 2 arms x 2 big-payload invocations (validity check + distinguishability check)
        expected = 4
        print(f"  log lines={len(lines)} emitted={len(emitted)} (expected {expected})")
        if len(emitted) != expected:
            fails.append(f"expected {expected} emissions, got {len(emitted)}")
        arms_seen = sorted({x.get("arm") for x in emitted})
        if arms_seen != ["A", "B"]:
            fails.append(f"emissions did not cover both arms: {arms_seen}")
        print(f"  both arms observed on the wire: {arms_seen == ['A','B']}")

    print()
    if fails:
        print("FAIL"); [print("  -", f) for f in fails]; sys.exit(1)
    print("PASS: both arms valid, distinguishable, scoped, and fail-closed")

if __name__ == "__main__":
    main()
