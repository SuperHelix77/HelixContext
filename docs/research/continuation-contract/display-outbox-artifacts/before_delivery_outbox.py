"""Submit-once display of already completed Engine output, never task execution.

The caller supplies a committed delivery identity, current authority and explicit
user-command permission. This library does not infer permission or completion.
It emits a fixed printf command for the supported userShell adapter; it cannot
silently intercept chat. Unknown delivery is reconciled, never resubmitted.
SQLite must remain intact/trusted; no hostile-host or rolled-back-index guarantee.
"""
import base64
import hashlib
import json
import shlex
from workflow_memory import encode, identity

VERSION = 'helix.display-outbox.v1'


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def frame(delivery_id, raw):
    text = raw.decode('utf-8')
    if '\x00' in text:
        raise ValueError('Native display requires text without NUL')
    return f'HELIX ENGINE / delivery {delivery_id}\n' + text


class DisplayOutbox:
    def __init__(self, memory):
        self.memory = memory
        with memory.db() as db:
            db.execute('''CREATE TABLE IF NOT EXISTS display_outbox(
                identity TEXT PRIMARY KEY, request_hash TEXT NOT NULL,
                phase TEXT NOT NULL, evidence_hash TEXT)''')

    def stage(self, delivery_id, thread_id, output, authority_root):
        identity(delivery_id, thread_id, authority_root)
        if not isinstance(output, bytes):
            raise ValueError('Exact completed output required')
        if len(authority_root) != 64 or any(c not in '0123456789abcdef' for c in authority_root):
            raise ValueError('Caller-bound authority root required')
        key = digest(encode([VERSION, thread_id, delivery_id]))
        display = frame(key, output)
        packet = dict(schema=VERSION, delivery_id=delivery_id, thread_id=thread_id,
                      authority_root=authority_root, output_base64=base64.b64encode(output).decode(),
                      display=display, command="/usr/bin/printf '%s' " + shlex.quote(display))
        ref = self.memory.store.put(encode(packet))['sha256']
        with self.memory.db() as db:
            db.execute('BEGIN IMMEDIATE')
            old = db.execute('SELECT request_hash FROM display_outbox WHERE identity=?', (key,)).fetchone()
            if old and old[0] != ref:
                raise ValueError('Conflicting delivery identity')
            if not old:
                db.execute('INSERT INTO display_outbox VALUES(?,?,?,NULL)', (key, ref, 'PREPARED'))
            db.execute('COMMIT')
        return {'identity': key, 'request_hash': ref}

    def _read(self, db, ticket):
        if not isinstance(ticket, dict) or set(ticket) != {'identity', 'request_hash'}:
            raise ValueError('Exact caller ticket required')
        row = db.execute('SELECT request_hash,phase,evidence_hash FROM display_outbox WHERE identity=?',
                         (ticket['identity'],)).fetchone()
        if not row or row[0] != ticket['request_hash']:
            raise ValueError('Missing or changed delivery request')
        packet = json.loads(self.memory.store.get(row[0]))
        if packet['schema'] != VERSION or digest(encode([VERSION, packet['thread_id'], packet['delivery_id']])) != ticket['identity']:
            raise ValueError('Delivery identity mismatch')
        raw = base64.b64decode(packet['output_base64'], validate=True)
        display = frame(ticket['identity'], raw)
        if packet['display'] != display or packet['command'] != "/usr/bin/printf '%s' " + shlex.quote(display):
            raise ValueError('Invalid display operation')
        if row[1] not in ('PREPARED', 'CLAIMED', 'DELIVERED', 'FAILED'):
            raise ValueError('Invalid delivery phase')
        return packet, row[1], row[2]

    def claim(self, ticket, *, current_authority, explicit_user_command, thread_idle):
        """One caller gets SUBMIT_ONCE; crashes before/after send never reset it.

        The idle/authority facts are caller assertions, not atomic app locks.
        Production integration must bind them at the real submission boundary.
        """
        with self.memory.db() as db:
            db.execute('BEGIN IMMEDIATE')
            packet, phase, evidence = self._read(db, ticket)
            if phase in ('DELIVERED', 'FAILED'):
                if not evidence:
                    raise ValueError('Terminal delivery lacks evidence')
                self.memory.store.get(evidence)
                return {'state': phase, 'evidence': evidence, 'submit': False}
            if phase == 'CLAIMED':
                return {'state': 'RECONCILE', 'submit': False}
            if explicit_user_command is not True or thread_idle is not True or current_authority != packet['authority_root']:
                return {'state': 'HOLD', 'submit': False}
            db.execute("UPDATE display_outbox SET phase='CLAIMED' WHERE identity=?", (ticket['identity'],))
            db.execute('COMMIT')
            return {'state': 'SUBMIT_ONCE', 'submit': True, 'thread_id': packet['thread_id'],
                    'command': packet['command'], 'timeout_ms': 3000}

    def reconcile(self, ticket, native_thread):
        """Consume caller-fetched authoritative thread history, not a quoted receipt.

        Exact command/output and native item identity establish display only.
        A completed turn alone cannot establish delivery or semantic correctness.
        Missing/duplicate/partial/contradictory items stay uncertain with no retry.
        """
        with self.memory.db() as db:
            db.execute('BEGIN IMMEDIATE')
            packet, phase, prior = self._read(db, ticket)
            if phase == 'PREPARED':
                raise ValueError('Unsubmitted delivery cannot be reconciled')
            if native_thread.get('id') != packet['thread_id']:
                raise ValueError('Wrong native thread')
            matches = []
            for turn in native_thread.get('turns', []):
                for item in turn.get('items', []):
                    if item.get('type') == 'commandExecution' and item.get('command') == packet['command']:
                        matches.append((turn, item))
            if len(matches) != 1:
                return {'state': 'RECONCILE', 'submit': False, 'reason': 'No unique exact native operation'}
            turn, item = matches[0]
            if (turn.get('status') != 'completed' or item.get('source') != 'userShell'
                    or not isinstance(turn.get('id'), str) or not turn['id']
                    or not isinstance(item.get('id'), str) or not item['id']):
                return {'state': 'RECONCILE', 'submit': False, 'reason': 'Incomplete native binding'}
            code = item.get('exitCode')
            if item.get('status') == 'completed' and type(code) is int and code == 0 and item.get('aggregatedOutput') == packet['display']:
                final = 'DELIVERED'
            elif item.get('status') == 'failed' and type(code) is int and code != 0:
                final = 'FAILED'
            else:
                return {'state': 'RECONCILE', 'submit': False, 'reason': 'Conflicting or incomplete execution evidence'}
            evidence = dict(schema=VERSION, request_hash=ticket['request_hash'], thread_id=packet['thread_id'],
                            turn_id=turn['id'], item=item, phase=final,
                            scope='Native Engine display; task completion and semantic correctness are separate')
            raw = encode(evidence)
            if phase in ('DELIVERED', 'FAILED'):
                if final != phase or prior != digest(raw):
                    raise ValueError('Contradictory terminal delivery')
                self.memory.store.get(prior)
                return {'state': phase, 'submit': False, 'evidence': prior}
            ref = self.memory.store.put(raw)['sha256']
            if self.memory.store.get(ref) != raw:
                raise ValueError('Delivery evidence readback mismatch')
            db.execute('UPDATE display_outbox SET phase=?,evidence_hash=? WHERE identity=?',
                       (final, ref, ticket['identity']))
            db.execute('COMMIT')
            return {'state': final, 'submit': False, 'evidence': ref}
