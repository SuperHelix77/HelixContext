"""Atomic pointer to verified evidence and an exact rendered artifact.

Cold objects may survive failed transactions. The bundle pointer alone is
canonical; exporting its artifact to a mutable file is a separate operation.
"""
import json,re,sqlite3
from verification import verify
from renderer import assemble


def commit(store,name,candidate,plan,expected_revision):
    if type(expected_revision) is not int or expected_revision<0:
        raise ValueError('Invalid expected revision')
    if not isinstance(name,str) or not re.fullmatch(r'[a-zA-Z0-9_.-]{1,128}',name):
        raise ValueError('Invalid bundle name')
    verify(store,candidate)
    artifact,render_receipt=assemble(store,plan)
    source_receipt=store.receipt(candidate['receipt'])
    allowed={source_receipt[s]['sha256'] for s in ('stdout','stderr')}
    if not set(render_receipt['source_sha256']).issubset(allowed):
        raise ValueError('Copy source is not bound to candidate evidence')
    packet=store.put(json.dumps(candidate,sort_keys=True,separators=(',',':')).encode())
    output=store.put(artifact)
    manifest={'schema':'helix.bundle.v1','packet':packet,'artifact':output,'render_receipt':render_receipt}
    ref=store.put(json.dumps(manifest,sort_keys=True,separators=(',',':')).encode())
    with sqlite3.connect(store.root/'bundles.sqlite3',isolation_level=None) as db:
        db.execute('PRAGMA synchronous=FULL')
        db.execute('BEGIN IMMEDIATE')
        try:
            db.execute('CREATE TABLE IF NOT EXISTS bundles(name TEXT PRIMARY KEY, revision INTEGER NOT NULL, object TEXT NOT NULL)')
            row=db.execute('SELECT revision FROM bundles WHERE name=?',(name,)).fetchone()
            revision=row[0] if row else 0
            if revision!=expected_revision:raise ValueError('Stale bundle revision')
            db.execute('INSERT OR REPLACE INTO bundles VALUES(?,?,?)',(name,revision+1,ref['sha256']))
            db.execute('COMMIT')
        except BaseException:
            db.execute('ROLLBACK');raise
    return {'name':name,'revision':revision+1,'bundle_sha256':ref['sha256'],'artifact':output}


def load(store,name):
    # The read URI avoids creating a database for a missing bundle.
    db_path=store.root/'bundles.sqlite3'
    if not db_path.exists():raise KeyError(name)
    with sqlite3.connect(db_path.as_uri()+'?mode=ro',uri=True) as db:
        row=db.execute('SELECT revision,object FROM bundles WHERE name=?',(name,)).fetchone()
    if row is None:raise KeyError(name)
    manifest=json.loads(store.get(row[1]))
    packet=json.loads(store.get(manifest['packet']['sha256']))
    verify(store,packet)
    artifact=store.get(manifest['artifact']['sha256'])
    if len(artifact)!=manifest['artifact']['bytes']:raise ValueError('Artifact length mismatch')
    return {'revision':row[0],'bundle_sha256':row[1],'packet':packet,'artifact':artifact}
