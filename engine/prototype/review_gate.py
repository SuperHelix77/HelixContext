"""Research-only immutable attempts and post-execution semantic review gate.

Owns only a SQLite version reference and private snapshots, never caller files.
Trusted caller supplies semantic verdicts. This is not a process sandbox, a model
review implementation, automatic retry machinery, or a production-qualified route.
"""
from contextlib import contextmanager
import json
from pathlib import Path
import re
import sqlite3
import time
import checked_steps


def encode(v):return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def ident(v):
    if not isinstance(v,str) or v in {'.','..'} or not re.fullmatch(r'[A-Za-z0-9_.-]{1,128}',v):raise ValueError('Invalid identity')
    return v


class Gate:
    def __init__(self,store):
        self.store=store;self.path=store.root/'review-gate.sqlite3'
        with self.db() as db:db.executescript('''
CREATE TABLE IF NOT EXISTS heads(task TEXT PRIMARY KEY, root TEXT NOT NULL, revision INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS attempts(id TEXT PRIMARY KEY, task TEXT, base TEXT, revision INTEGER, candidate TEXT, status TEXT, evidence TEXT, review TEXT);
''')

    @contextmanager
    def db(self):
        db=sqlite3.connect(self.path,isolation_level=None);db.row_factory=sqlite3.Row
        db.execute('PRAGMA synchronous=FULL')
        try:yield db
        finally:db.close()

    def bundle(self,files):
        if not isinstance(files,dict) or not files:raise ValueError('Files required')
        entries={}
        for name,raw in files.items():
            ident(name) # Flat research snapshots only; no symlink/path traversal.
            if type(raw) is not bytes:raise ValueError('Exact bytes required')
            entries[name]=self.store.put(raw)['sha256']
        return self.store.put(encode({'schema':'helix.review.files.v1','files':entries}))['sha256']

    def files(self,root):
        bundle=self.store.receipt(root)
        if bundle.get('schema')!='helix.review.files.v1' or not isinstance(bundle.get('files'),dict):raise ValueError('Bad bundle')
        return {ident(name):self.store.get(ref) for name,ref in bundle['files'].items()}

    def initialize(self,task,root):
        ident(task);self.files(root)
        with self.db() as db:db.execute('INSERT INTO heads VALUES(?,?,1)',(task,root))
        return self.head(task)

    def head(self,task):
        with self.db() as db:row=db.execute('SELECT * FROM heads WHERE task=?',(task,)).fetchone()
        if row is None:raise ValueError('Unknown task')
        return dict(row)

    def advance(self,task,expected,root):
        """Trusted caller imports changed authority, with monotonic revision (ABA-safe)."""
        if expected.get('task')!=task:raise ValueError('Wrong task scope')
        self.files(root)
        with self.db() as db:
            changed=db.execute('UPDATE heads SET root=?,revision=revision+1 WHERE task=? AND root=? AND revision=?',
                               (root,task,expected['root'],expected['revision'])).rowcount
        if changed!=1:raise ValueError('Changed base')
        return self.head(task)

    def attempt(self,key):
        with self.db() as db:row=db.execute('SELECT * FROM attempts WHERE id=?',(key,)).fetchone()
        if row is None:raise ValueError('Unknown attempt')
        return dict(row)

    def stage(self,key,task,expected,replacements,*,steps,environment_id,env=None,timeout=30):
        ident(key);ident(task)
        if expected.get('task')!=task:raise ValueError('Wrong task scope')
        # Reserve before any process; an existing ID never reruns a possibly effectful check.
        with self.db() as db:
            db.execute('BEGIN IMMEDIATE')
            try:
                head=db.execute('SELECT * FROM heads WHERE task=?',(task,)).fetchone()
                if head is None or head['root']!=expected['root'] or head['revision']!=expected['revision']:raise ValueError('Stale base')
                db.execute('INSERT INTO attempts VALUES(?,?,?,?,?,?,NULL,NULL)',(key,task,head['root'],head['revision'],None,'STARTED'))
                db.execute('COMMIT')
            except BaseException:db.execute('ROLLBACK');raise
        started=time.perf_counter();before=dict(self.store.metrics);evidence={};candidate=None;snapshot_bytes=0
        try:
            files=self.files(expected['root'])
            if not replacements or any(k not in files for k in replacements):raise ValueError('Only bound files may be replaced')
            if any(type(v) is not bytes for v in replacements.values()):raise ValueError('Exact replacements required')
            files.update(replacements);candidate=self.bundle(files)
            workspace=self.store.root/'review-attempts'/key;workspace.mkdir(parents=True,exist_ok=False)
            for name,raw in files.items():
                snapshot_bytes+=(workspace/name).write_bytes(raw)
            evidence['validation']=checked_steps.execute(self.store,steps,workspace,environment_id,timeout=timeout,env=env)
            evidence['snapshot_unchanged']=all((workspace/name).read_bytes()==raw for name,raw in files.items())
            status='AWAITING_REVIEW' if evidence['validation']['process_success'] and evidence['snapshot_unchanged'] else 'CHECK_FAILED'
        except Exception as exc:
            status='CHECK_FAILED';evidence['error']=type(exc).__name__+': '+str(exc)
        evidence.update(attempt_id=key,base=expected,candidate=candidate,status=status,seconds=time.perf_counter()-started,
            snapshot_bytes_written=snapshot_bytes,
            store_io_before_receipt_publication={k:self.store.metrics[k]-before[k] for k in before},
            scope='Declared snapshot and process status only. Semantic review required; external process effects and physical/SQLite I/O not certified.')
        ref=self.store.put(encode(evidence))['sha256']
        with self.db() as db:db.execute('UPDATE attempts SET candidate=?,status=?,evidence=? WHERE id=?',(candidate,status,ref,key))
        return self.attempt(key)

    def review(self,key,*,approve,reviewer,evidence_ref):
        if type(approve) is not bool:raise ValueError('Explicit verdict required')
        ident(reviewer);self.store.get(evidence_ref)
        with self.db() as db:
            db.execute('BEGIN IMMEDIATE')
            try:
                row=db.execute('SELECT * FROM attempts WHERE id=?',(key,)).fetchone()
                if row is None:raise ValueError('Unknown attempt')
                if row['status']!='AWAITING_REVIEW':raise ValueError('Not awaiting review; no replay')
                # Verify cold evidence before authoritatively publishing its candidate root.
                evidence=self.store.receipt(row['evidence'])
                if (evidence.get('attempt_id')!=key
                    or evidence.get('base')!={'task':row['task'],'root':row['base'],'revision':row['revision']}
                    or evidence.get('candidate')!=row['candidate']
                    or evidence.get('status')!='AWAITING_REVIEW'
                    or evidence.get('snapshot_unchanged') is not True
                    or evidence.get('validation',{}).get('process_success') is not True):
                    raise ValueError('Evidence does not certify this attempt')
                self.files(row['candidate'])
                review={'approve':approve,'reviewer':reviewer,'evidence_ref':evidence_ref}
                if not approve:status='REJECTED'
                else:
                    n=db.execute('UPDATE heads SET root=?,revision=revision+1 WHERE task=? AND root=? AND revision=?',
                        (row['candidate'],row['task'],row['base'],row['revision'])).rowcount
                    status='ACCEPTED' if n==1 else 'CONFLICT'
                db.execute('UPDATE attempts SET status=?,review=? WHERE id=?',(status,json.dumps(review),key))
                db.execute('COMMIT')
            except BaseException:db.execute('ROLLBACK');raise
        return self.attempt(key)
