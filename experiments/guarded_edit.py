#!/usr/bin/env python3
"""Replace one snapshotted UTF-8 file from stdin, then execute declared tests.
Usage: python3 guarded_edit.py manifest.json [insert_before_line] < code.py
Manifest: file, sha256, test (argv). Working directory is manifest's directory.
The manifest must be caller-created from authorized current task requirements.
"""
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile


def run(manifest, replacement, insert_line=None):
    manifest = Path(manifest).resolve()
    spec = json.loads(manifest.read_text())
    base = manifest.parent
    path = base / spec['file']
    if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(base):
        raise ValueError('target must be a regular file inside manifest directory')
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != spec['sha256']:
        raise ValueError('stale snapshot; reread source before editing')
    raw.decode('utf-8')
    replacement.decode('utf-8')
    if insert_line is not None:
        lines = raw.splitlines(keepends=True)
        if not 1 <= insert_line <= len(lines) + 1:
            raise ValueError('insertion line outside file')
        if not replacement.endswith(b'\n'):
            raise ValueError('inserted text must end with newline')
        replacement = b''.join(lines[:insert_line-1]) + replacement + b''.join(lines[insert_line-1:])
    command = spec['test']
    if not isinstance(command, list) or not command or not all(isinstance(x,str) and x for x in command):
        raise ValueError('test must be nonempty argv')
    # Preserve permissions; replace only after fully preparing and rechecking.
    mode = stat.S_IMODE(path.stat().st_mode)
    fd, temp = tempfile.mkstemp(prefix='.guarded-edit-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as f:
            f.write(replacement)
        os.chmod(temp, mode)
        if path.is_symlink() or path.read_bytes() != raw:
            raise ValueError('source changed during preparation; reread before editing')
        os.replace(temp, path)
    finally:
        if os.path.exists(temp): os.unlink(temp)
    # Inherit output: complete diagnostics stay visible; no silent truncation.
    result = subprocess.run(command, cwd=base)
    print('Test exit code:', result.returncode, flush=True)
    return result.returncode if result.returncode >= 0 else 128 - result.returncode


if __name__ == '__main__':
    try:
        code = run(sys.argv[1], sys.stdin.buffer.read(), int(sys.argv[2]) if len(sys.argv)>2 else None)
    except (OSError, ValueError, KeyError, IndexError) as e:
        print(str(e), file=sys.stderr)
        code = 2
    sys.exit(code)
