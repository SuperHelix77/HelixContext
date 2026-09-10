"""Offline closure for the Luna normal-final maintenance derivative."""
import hashlib, json, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    tests = [HERE / "test_bound_edit_tool.py", REPO / "engine/prototype/test_completion_ledger.py", REPO / "engine/prototype/test_passive_workflow.py"]
    p = subprocess.run([sys.executable, "-m", "pytest", "-q", *map(str, tests)], cwd=REPO, capture_output=True, text=True, timeout=120,
                       env={**__import__('os').environ, "PYTHONPATH": str(HERE) + ":" + str(REPO / "engine/output") + ":" + str(REPO / "engine/prototype") + ":" + str(REPO / "docs/research/continuation-contract")})
    if p.returncode != 0: raise RuntimeError(p.stdout + p.stderr)
    result = {
        "schema": "helix.luna.normal-final-maintenance.offline.v1",
        "state": "OFFLINE_VALIDATED_NO_NATIVE_CALLS",
        "native_calls": 0,
        "candidate": {"model": "gpt-5.6-luna", "effort": "high", "base_sha256": sha(REPO / "engine/profiles/luna-coding-v1-75/base.md"), "final_renderer": None},
        "derivative": {"pilot_sha256": sha(HERE / "pilot.py"), "audit_sha256": sha(HERE / "audit_native.py"), "tool_sha256": sha(HERE / "bound_edit_tool.py"), "prereg_sha256": sha(HERE / "PREREG.md")},
        "actual_tests": {"exit_code": p.returncode, "stdout": p.stdout, "stderr": p.stderr, "test_files": [str(x) for x in tests]},
        "mechanical_scope": ["failed checks preserve source", "stale authority rejects", "duplicate call is idempotent", "restart recovery does not rerun checks", "lost publication acknowledgement reconciles without re-execution", "model final remains separate from tool receipt"],
        "semantic_limit": "Offline tests validate caller mechanics only; native model final authorship and task capability remain unobserved."
    }
    (HERE / "OFFLINE.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"state": result["state"], "native_calls": 0, "tests": p.stdout.strip()}))

if __name__ == "__main__": main()
