"""Compose research kernels and bind sizes; no runtime/config mutation."""
import hashlib
import json
from pathlib import Path
import tiktoken

root = Path(__file__).resolve().parent
enc = tiktoken.get_encoding('o200k_base')
manifest = {'status': 'RESEARCH_ONLY_UNQUALIFIED', 'tokenizer': 'o200k_base',
            'native_savings': None, 'files': {}}
for model in ('sol', 'astra'):
    parts = [root / 'common-v1.md', root / f'{model}-v1.fragment.md']
    text = '\n'.join(p.read_text() for p in parts)
    target = root / f'{model}-v1.md'
    target.write_text(text)
    manifest['files'][target.name] = {
        'sha256': hashlib.sha256(text.encode()).hexdigest(),
        'bytes': len(text.encode()), 'proxy_tokens': len(enc.encode(text)),
        'sources': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in parts}}
(root / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
print(json.dumps(manifest, indent=2))
