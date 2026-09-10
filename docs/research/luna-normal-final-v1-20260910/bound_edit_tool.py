"""Research adapter: exact edits/tests as an internal tool, never a final answer.

One trusted caller owns paths, source versions, checks and authority. An incomplete
claim stops replay; recover_published validates retained prepared evidence before
closing an already-published operation. No hidden semantic repair or tool rerun.
SQLite/CAS and the external authority callback must remain trustworthy.
"""
import hashlib
import json
from pathlib import Path
import sqlite3
import time
import sys

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / 'engine/prototype'))
from evidence import Store
from literal_edits import compile_edits
import renderer


SPEC = {'type': 'function', 'name': 'helix_apply_edits',
        'description': 'Apply exact simultaneous old/new edits to caller-bound workflow_memory.py at expected_version. Stage and run task checks before publication; return actual receipts. Failed checks keep the original. Mechanical checks do not establish semantic adequacy. Ordinary tools and model-written final answers remain available.',
        'inputSchema': {'type': 'object', 'properties': {
            'expected_version': {'type': 'integer', 'minimum': 0},
            'edits': {'type': 'array', 'items': {'type': 'object', 'properties': {
                'old': {'type': 'string', 'minLength': 1}, 'new': {'type': 'string'}},
                'required': ['old', 'new'], 'additionalProperties': False}}},
            'required': ['expected_version', 'edits'], 'additionalProperties': False}}


def encoded(value): return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()
def digest(raw): return hashlib.sha256(raw).hexdigest()


class BoundEditTool:
    def __init__(self, directory, target, initial_source, authority, checker, *, expected_binding):
        if not isinstance(expected_binding, str) or len(expected_binding) != 64:
            raise ValueError('Explicit caller authority binding required')
        self.directory = Path(directory); self.directory.mkdir(parents=True, exist_ok=True)
        self.target = Path(target); self.authority = authority; self.checker = checker
        self.expected_binding = expected_binding; self.guard()
        self.store = Store(self.directory / 'objects'); self.db_path = self.directory / 'calls.sqlite3'
        with self.db() as db:
            db.executescript('CREATE TABLE IF NOT EXISTS binding(id INTEGER PRIMARY KEY, root TEXT, target TEXT);'
                             'CREATE TABLE IF NOT EXISTS state(id INTEGER PRIMARY KEY, version INTEGER, source TEXT);'
                             'CREATE TABLE IF NOT EXISTS calls(id TEXT PRIMARY KEY, request TEXT, phase TEXT, prepared TEXT, response TEXT);')
            prior = db.execute('SELECT root,target FROM binding WHERE id=0').fetchone()
            if prior and prior != (expected_binding, str(self.target.resolve())):
                raise ValueError('Prior caller authority/target differs')
            if not prior: db.execute('INSERT INTO binding VALUES(0,?,?)', (expected_binding, str(self.target.resolve())))
            if not db.execute('SELECT 1 FROM state').fetchone():
                if self.target.read_bytes() != initial_source: raise ValueError('Initial source mismatch')
                ref = self.store.put(initial_source)['sha256']
                db.execute('INSERT INTO state VALUES(0,0,?)', (ref,))

    def db(self): return sqlite3.connect(self.db_path)

    def guard(self):
        if self.authority() != self.expected_binding: raise ValueError('Caller authority changed')

    def response(self, value, success):
        return {'success': success, 'contentItems': [{'type': 'inputText', 'text': json.dumps(value, separators=(',', ':'))}]}

    def recover_published(self, call):
        """Close only an exact already-published result; never re-execute checks/edit."""
        self.guard()
        with self.db() as db:
            db.execute('BEGIN IMMEDIATE')
            row = db.execute('SELECT phase,prepared FROM calls WHERE id=?', (call,)).fetchone()
            if not row or row[0] != 'CLAIMED' or not row[1]: raise ValueError('No prepared publication to reconcile')
            p = json.loads(self.store.get(row[1])); version, source = db.execute('SELECT version,source FROM state WHERE id=0').fetchone()
            if version != p['prior_version'] or source != p['prior_source']: raise ValueError('State changed during recovery')
            if digest(self.target.read_bytes()) != p['output_source']: raise ValueError('Publication not established; do not retry')
            self.store.get(p['output_source']); self.store.get(p['check_ref'])
            reply = self.response(p['packet'], True); ref = self.store.put(encoded(reply))['sha256']
            db.execute('UPDATE state SET version=?,source=? WHERE id=0', (version+1, p['output_source']))
            db.execute('UPDATE calls SET phase=?,response=? WHERE id=?', ('COMPLETED', ref, call))
            return reply

    def __call__(self, params):
        begin = time.perf_counter(); self.guard()
        args = params['arguments']; identity = digest(encoded([params['threadId'], params['callId']]))
        request = self.store.put(encoded(params))['sha256']
        with self.db() as db:
            db.execute('BEGIN IMMEDIATE')
            old = db.execute('SELECT request,phase,response FROM calls WHERE id=?', (identity,)).fetchone()
            if old:
                if old[0] != request: raise ValueError('Conflicting tool delivery')
                if old[1] != 'COMPLETED': raise ValueError('Uncertain prior call; reconcile, do not re-execute')
                return json.loads(self.store.get(old[2]))
            if db.execute("SELECT 1 FROM calls WHERE phase='CLAIMED'").fetchone(): raise ValueError('Unreconciled earlier operation')
            version, source = db.execute('SELECT version,source FROM state WHERE id=0').fetchone()
            if digest(self.target.read_bytes()) != source: raise ValueError('Source drift; semantic refresh required')
            db.execute('INSERT INTO calls VALUES(?,?,?,NULL,NULL)', (identity, request, 'CLAIMED'))
        raw = self.store.get(source)  # Integrity failure is not a repairable edit error.
        try:
            if (not isinstance(args, dict) or set(args) != {'expected_version', 'edits'}
                    or type(args['expected_version']) is not int or args['expected_version'] != version):
                raise ValueError('Expected source version does not match')
            plan, edits = compile_edits(raw, source, {'edits': args['edits']})
            output, assembly = renderer.assemble(self.store, plan)
        except (ValueError, UnicodeError) as exc:
            reply = self.response({'status': 'REJECTED_BEFORE_PUBLICATION', 'version': version, 'error': str(exc)}, False)
            return self._complete(identity, reply)
        output_ref = self.store.put(output)['sha256']
        check = self.checker(output, self.directory / identity)
        self.guard()
        if digest(self.target.read_bytes()) != source: raise ValueError('Source changed during checks')
        check_ref = self.store.put(encoded(check))['sha256']
        if check['checks'] != 'PASS':
            return self._complete(identity, self.response({'status': 'CHECKS_FAILED', 'version': version, 'checks': check}, False))
        packet = {'status': 'APPLIED', 'artifact': self.target.name, 'version': version+1,
                  'checks': check.get('summary', 'Required finite task checks PASS'), 'source_sha256': output_ref,
                  'evidence_ref': check_ref, 'semantic_adequacy': 'Model responsibility'}
        prepared = {'prior_version': version, 'prior_source': source, 'output_source': output_ref,
                    'check_ref': check_ref, 'packet': packet, 'edits': edits, 'assembly': assembly}
        prepared_ref = self.store.put(encoded(prepared))['sha256']
        with self.db() as db: db.execute('UPDATE calls SET prepared=? WHERE id=?', (prepared_ref, identity))
        self.guard()
        receipt = renderer.publish(self.store, plan, self.target, expected_sha256=source)
        self.store.put(encoded({'publication': receipt, 'seconds': time.perf_counter()-begin}))
        return self.recover_published(identity)

    def _complete(self, identity, response):
        ref = self.store.put(encoded(response))['sha256']
        with self.db() as db: db.execute('UPDATE calls SET phase=?,response=? WHERE id=?', ('COMPLETED', ref, identity))
        return response
