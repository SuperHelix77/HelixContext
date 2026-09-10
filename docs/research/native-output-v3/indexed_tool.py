"""Indexed semantic edits; caller-owned scope and exact execution receipts.

Preserves the V1 publication/recovery state machine and V2 exact-diff semantics.
No changed model answer, automatic edit repair or semantic sufficiency verdict.
"""
import difflib
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / 'engine/prototype'))
from indexed_edits import compile_edits, lines
from checked_tool import BoundEditTool, digest


SPEC = {'type': 'function', 'name': 'helix_apply_edits',
    'description': 'Apply simultaneous LF-line edits to the caller-bound source version. '
        'One-based start_line and delete_lines address the ORIGINAL snapshot; insert is exact new text. '
        'Caller copies unchanged bytes, stages/runs required checks, publishes, then returns exact diff, '
        'source hash and actual Git scope/check results. The model owns semantic choices and its normal '
        'final answer. Ordinary tools and semantic probes remain available.',
    'inputSchema': {'type': 'object', 'properties': {
        'expected_version': {'type': 'integer', 'minimum': 0},
        'edits': {'type': 'array', 'items': {'type': 'object', 'properties': {
            'start_line': {'type': 'integer', 'minimum': 1},
            'delete_lines': {'type': 'integer', 'minimum': 0},
            'insert': {'type': 'string'}},
            'required': ['start_line', 'delete_lines', 'insert'], 'additionalProperties': False}}},
        'required': ['expected_version', 'edits'], 'additionalProperties': False}}


def scope_snapshot(cwd, files):
    """Actual local Git observations; not an exclusive lock or semantic proof."""
    cwd = Path(cwd); start = time.perf_counter(); rows = []
    commands = [['git', 'rev-parse', 'HEAD'],
                ['git', 'status', '--porcelain=v1', '-z', '--untracked-files=all'],
                ['git', 'diff', '--no-ext-diff', '--check']]
    for args in commands:
        r = subprocess.run(args, cwd=cwd, capture_output=True, timeout=15)
        rows.append({'argv': args, 'exit_code': r.returncode,
                     'stdout': r.stdout.decode('utf-8'), 'stderr': r.stderr.decode('utf-8')})
    if rows[0]['exit_code'] or rows[1]['exit_code']:
        raise ValueError('Git state unavailable')
    return {'schema': 'helix.scope.v1', 'cwd': str(cwd.resolve()),
            'head': rows[0]['stdout'].strip(), 'status_z': rows[1]['stdout'],
            'diff_check_exit': rows[2]['exit_code'],
            'files': {n: digest((cwd / n).read_bytes()) for n in files},
            'commands': rows, 'seconds': time.perf_counter()-start,
            'limit': 'Observed local state; no exclusive workspace custody or semantic completeness'}


class IndexedEditTool(BoundEditTool):
    compile = staticmethod(compile_edits)
    DIFF_LIMIT = 4096

    def __init__(self, *args, scope_observer, **kwargs):
        self.scope_observer = scope_observer
        super().__init__(*args, **kwargs)

    def response(self, value, success):
        if success and value.get('status') == 'APPLIED':
            with self.db() as db:
                version, source = db.execute('SELECT version,source FROM state WHERE id=0').fetchone()
            if value['version'] != version+1:
                raise ValueError('Review source generation changed')
            before = self.store.get(source); after = self.store.get(value['source_sha256'])
            if digest(self.target.read_bytes()) != value['source_sha256']:
                raise ValueError('Review source changed after publication')
            difference = difflib.unified_diff([line.decode() for line in lines(before)],
                [line.decode() for line in lines(after)],
                fromfile='before/'+self.target.name, tofile='after/'+self.target.name)
            diff = ''.join(line if line.endswith('\n') else line+'\n\\ No newline at end of file\n'
                           for line in difference).encode()
            diff_ref = self.store.put(diff)['sha256']
            observed = self.scope_observer()
            self.guard()  # Recheck protected scope/dependencies after observation.
            if (digest(self.target.read_bytes()) != value['source_sha256']
                    or observed['files'].get(self.target.name) != value['source_sha256']):
                raise ValueError('Observed scope does not bind the published source')
            scope_ref = self.store.put(json.dumps(observed, sort_keys=True).encode())['sha256']
            value = {**value, 'review': {'schema': 'helix.review.v3',
                'prior_source_sha256': source, 'diff_sha256': diff_ref,
                'diff_bytes': len(diff), 'diff_complete': len(diff)<=self.DIFF_LIMIT,
                'exact_diff': diff.decode() if len(diff)<=self.DIFF_LIMIT else None},
                'scope': {'head': observed['head'], 'status_z': observed['status_z'],
                    'diff_check_exit': observed['diff_check_exit'], 'source_bound': True,
                    'caller_declared_protected_scope_rechecked': True, 'evidence_ref': scope_ref,
                    'limit': observed['limit']}}
        return super().response(value, success)
