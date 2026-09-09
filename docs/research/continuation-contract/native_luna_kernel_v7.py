"""One Luna base-policy intervention; unchanged V5 semantic interface and runner."""
import json
import sys
from pathlib import Path
import native_luna_ack_output_v5 as v5
import native_kernel_pair as kernel_driver


def prepare(root, prior):
    root = Path(root).resolve()
    v5.prepare(root, prior)
    kernels = Path(__file__).parent/'kernels'
    # Mechanically compose the same delegation policy with a correct model label.
    base = (kernels/'common-v1.md').read_text()+'\n'+(kernels/'sol-v1.fragment.md').read_text().replace('SOL POLICY', 'LUNA POLICY', 1)
    (root/'luna-base-v1.md').write_text(base)
    paths = [Path(__file__), kernels/'common-v1.md', kernels/'sol-v1.fragment.md',
             root/'luna-base-v1.md', Path(kernel_driver.__file__)]
    m = json.loads((root/'manifest.json').read_text())
    m['changes'] = ['Replace client base with compact delegation kernel; preserve exact V5 task prompt, schema, evidence and High effort.']
    m['classification'] = 'One adaptive known-fixture base-policy intervention; original W50 control and V5 reused; no general parity claim'
    m['base_file'] = str(root/'luna-base-v1.md')
    m['sha256'].update({str(p): v5.sha(p) for p in paths})
    v5.save(root/'manifest.json', m)
    print(v5.sha(root/'manifest.json'))


def run(root):
    root = Path(root); m = json.loads((root/'manifest.json').read_text())
    v5.verify(m)
    kernel_driver.research_session.RPC = kernel_driver.rpc_with_base(Path(m['base_file']))
    try:
        v5.run(root)
    finally:
        kernel_driver.research_session.RPC = kernel_driver.OriginalRPC


if __name__ == '__main__':
    globals()[sys.argv[1]](*sys.argv[2:])
