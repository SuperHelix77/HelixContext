"""Expand exact snapshot entries selected by the model; no model or tool calls.
A caller creates {id: text} for all candidate source excerpts, pins its SHA256,
and renders {{id}} references after generation. No recursive interpretation.
"""
import hashlib,json,re
from pathlib import Path
MARKER=re.compile(r'\{\{([A-Za-z][A-Za-z0-9_-]*(?:[,\:][0-9]+)*)\}\}')

def render(template, catalog_path, expected_sha256):
    raw=Path(catalog_path).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=expected_sha256:
        raise ValueError('catalog hash mismatch')
    def pairs(items):
        d={}
        for k,v in items:
            if k in d:raise ValueError('duplicate catalog key')
            d[k]=v
        return d
    catalog=json.loads(raw,object_pairs_hook=pairs)
    if not isinstance(catalog,dict) or not all(isinstance(v,str) for v in catalog.values()):
        raise ValueError('catalog must map identifiers to strings')
    def replace(match):
        key=match.group(1)
        if ',' in key or ':' in key:
            m=re.fullmatch(r'([A-Za-z]+)([0-9]+)([:,][0-9]+)+',key)
            if not m:raise ValueError('invalid source selector')
            prefix=m.group(1);numbers=re.split(r'[:,]',key[len(prefix):])
            if ':' in key:
                if ',' in key or len(numbers)!=2:raise ValueError('invalid source range')
                lo,hi=map(int,numbers)
                if hi<lo or hi-lo+1>len(catalog):raise ValueError('invalid source range')
                keys=[prefix+str(i) for i in range(lo,hi+1)]
            else:keys=[prefix+n for n in numbers]
            if any(k not in catalog for k in keys):raise ValueError('unknown source reference')
            return '\n'.join(catalog[k] for k in keys)
        if key not in catalog:raise ValueError('unknown source reference: '+key)
        return catalog[key]
    # Source text is opaque. Marker-like source text is not expanded again.
    return MARKER.sub(replace,template)
