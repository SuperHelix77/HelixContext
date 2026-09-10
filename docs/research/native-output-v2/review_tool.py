"""V2 receipt presentation atop unchanged V1 checked publication/recovery.

Returns a reviewable exact diff from immutable before/after bytes. Adds no
semantic verdict and cannot stop native review. Not yet native-qualified.
"""
import difflib
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent.with_name('native-output-v1')))
from bound_edit_tool import BoundEditTool, SPEC, digest


def exact_diff(before, after, name):
    lines = difflib.unified_diff(before.decode('utf-8').splitlines(keepends=True),
                                 after.decode('utf-8').splitlines(keepends=True),
                                 fromfile='before/'+name,tofile='after/'+name)
    return ''.join(line if line.endswith('\n') else line+'\n\\ No newline at end of file\n' for line in lines)


class ReviewEditTool(BoundEditTool):
    DIFF_LIMIT = 4096

    def response(self, value, success):
        if success and value.get('status') == 'APPLIED':
            # Called while the durable state still binds the prior source, before
            # the completed response/state transition is committed transactionally.
            with self.db() as db: version, source = db.execute('SELECT version,source FROM state WHERE id=0').fetchone()
            if value['version'] != version+1: raise ValueError('Review source generation changed')
            before = self.store.get(source); after = self.store.get(value['source_sha256'])
            if digest(self.target.read_bytes()) != value['source_sha256']:
                raise ValueError('Review output differs from published source')
            diff = exact_diff(before, after, self.target.name).encode()
            ref = self.store.put(diff)['sha256']
            value = {**value, 'review': {'schema':'helix.review.v1','prior_source_sha256':source,
                'diff_sha256':ref,'diff_bytes':len(diff),'diff_complete':len(diff)<=self.DIFF_LIMIT,
                'exact_diff':diff.decode() if len(diff)<=self.DIFF_LIMIT else None,
                'binding':'Caller-declared authority revalidated; not undeclared dependency or semantic completeness'}}
        return super().response(value,success)
