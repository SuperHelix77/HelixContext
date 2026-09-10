"""Replay all three previously observed semantic probe programs on both fresh artifacts."""
import hashlib, json, os, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
PROBES = sorted((REPO / "docs/research/native-output-v1/artifacts").glob("*/*/probe-*.py"))

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main(root):
    root = Path(root).resolve(); assert len(PROBES) == 3, PROBES
    rows=[]
    for arm in ("on", "off"):
        cwd=root / arm
        for probe in PROBES:
            env={**os.environ, "PYTHONPATH": str(cwd) + ":" + str(REPO / "engine/prototype")}
            p=subprocess.run([sys.executable, "-B", "-"], input=probe.read_bytes(), cwd=cwd, env=env, capture_output=True, timeout=60)
            rows.append({"arm":arm,"probe_sha256":sha(probe),"exit_code":p.returncode,
                         "stdout":p.stdout.decode(errors="replace"),"stderr":p.stderr.decode(errors="replace")})
    result={"schema":"helix.luna.normal-final.semantic-probe-replay.v1","native_calls":0,
            "probe_count":len(PROBES),"artifacts":2,"rows":rows,
            "all_pass":all(r["exit_code"]==0 for r in rows),
            "scope":"Offline replay of three previously observed model-authored probes; not universal semantic proof."}
    (HERE / "PROBE_REPLAY.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({"probe_count":3,"artifacts":2,"all_pass":result["all_pass"]}))
    if not result["all_pass"]: raise SystemExit(1)

if __name__ == "__main__": main(sys.argv[1])
