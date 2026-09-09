"""One adaptive composition: frozen Luna V7 base plus V3 caller-owned coding.

No novel kernel text, reduced effort, output cap, tool restriction or blind retry.
Earlier fresh native/default-base candidate streams are retained comparisons.
An apparent win needs prospective qualification, not a release declaration.
"""
import json
import sys
from pathlib import Path
import luna_coding_decision_v3 as v3
import observed_session
import native_kernel_pair as kernel

ROOT = Path('/Users/mert/Documents/ChatGPT/Helix/research')


def prepare(root, prior):
    root = Path(root).resolve()
    v3.prepare(root, prior)
    path = root / 'manifest.json'
    m = json.loads(path.read_text())
    old = ROOT / 'native-luna-base-v7-20260909'
    old_manifest = json.loads((old / 'manifest.json').read_text())
    source = Path(old_manifest['base_file'])
    assert v3.v2.cap.kd.sha(source) == old_manifest['sha256'][str(source)]
    base = root / 'luna-base-v7.md'
    base.write_bytes(source.read_bytes())
    previous = ROOT / 'luna-coding-fresh-pair-v1-20260910'
    default = ROOT / 'luna-coding-decision-v3-20260910'
    # The caller prompt/skill/local instruction are unchanged apart from native
    # runtime path identities. Memory packet carries a newly validated receipt.
    assert (root / 'prompt.txt').read_bytes() == (default / 'prompt.txt').read_bytes()
    for rel in ('on/AGENTS.md', 'on/.agents/skills/helixcontext/SKILL.md'):
        assert (root / rel).read_bytes() == (default / rel).read_bytes()
    m.update(classification='One adaptive coding composition: frozen V7 base + frozen V3 caller path; retained fresh control and default-base candidate',
             base_file=str(base), fresh_reference=str(previous), max_new_candidate_streams=1,
             hypothesis='Compact delegation base may reduce the single-segment coding cost after caller setup and mechanics are removed',
             stop='Retain every result. No unchanged retry. Behavioral, scope, binding or raw-receipt failure stops qualification; numerical pass remains exploratory.')
    paths = [Path(__file__), Path(kernel.__file__), base, source, old / 'manifest.json',
             previous / 'off-run/status.json', previous / 'off-run/native-events.jsonl',
             previous / 'run/status.json', previous / 'run/native-events.jsonl']
    for p in paths: m['sha256'][str(p.resolve())] = v3.v2.cap.kd.sha(p)
    v3.v2.cap.kd.save(path, m)
    print(json.dumps({'manifest_sha256':v3.v2.cap.kd.sha(path), 'base_sha256':v3.v2.cap.kd.sha(base), 'base_bytes':base.stat().st_size, 'prompt_unchanged':True}))


def run(root):
    root = Path(root)
    m = json.loads((root / 'manifest.json').read_text())
    v3.v2.cap.verify(m)
    original = observed_session.RPC
    assert original is kernel.OriginalRPC
    observed_session.RPC = kernel.rpc_with_base(Path(m['base_file']))
    try:
        v3.v2.run(root)
    finally:
        observed_session.RPC = original


if __name__ == '__main__':
    {'prepare':prepare, 'run':run}[sys.argv[1]](*sys.argv[2:])
