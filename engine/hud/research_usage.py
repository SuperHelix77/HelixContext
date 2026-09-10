"""Incremental, read-only coordinator accounting; never reads prompt text into UI.

Native usage counters can restart. Reconstruct observed epochs, not
only the last counter. This is an append-stream observation, not a provider bill
or an integrity guarantee against rewriting an already-read historical prefix.
"""
import hashlib
import json
from pathlib import Path

FIELDS = ('input_tokens', 'cached_input_tokens', 'cache_write_input_tokens',
          'output_tokens', 'reasoning_output_tokens')


def counters(value):
    if not isinstance(value, dict):
        raise ValueError('Missing usage counters')
    result = {k: value.get(k) for k in FIELDS}
    if any(type(v) is not int or v < 0 for v in result.values()):
        raise ValueError('Invalid usage counters')
    if result['cached_input_tokens'] > result['input_tokens']:
        raise ValueError('Cache exceeds input')
    if result['reasoning_output_tokens'] > result['output_tokens']:
        raise ValueError('Reasoning exceeds output')
    if value.get('total_tokens') != result['input_tokens'] + result['output_tokens']:
        raise ValueError('Inconsistent native total')
    return result


class Ledger:
    def __init__(self, path):
        self.path = Path(path)
        self.logical_bytes_read = 0
        self._reset()

    def _reset(self):
        self.offset = 0
        self.pending = b''
        self.digest = hashlib.sha256()
        self.processed = 0
        self.identity = None
        self.signature = None
        self.closed = dict.fromkeys(FIELDS, 0)
        self.latest = None
        self.epochs = 0
        self.updates = 0
        self.duplicates = 0
        self.models = set()
        self.first_at = self.latest_at = None
        self.error = None

    def consume(self, line):
        record = json.loads(line)
        if not isinstance(record, dict):
            raise ValueError('Invalid native record')
        payload = record.get('payload') or {}
        if record.get('type') == 'turn_context':
            model = payload.get('model')
            if isinstance(model, str):
                self.models.add(model)
        if record.get('type') != 'event_msg' or payload.get('type') != 'token_count':
            return
        info = payload.get('info') or {}
        if info.get('total_token_usage') is None:
            return  # Rate-limit-only notification, not a usage observation.
        total = counters(info['total_token_usage'])
        if total == self.latest:
            self.duplicates += 1
            return
        if self.latest is None:
            self.epochs = 1
        elif any(total[k] < self.latest[k] for k in FIELDS):
            last = counters(info.get('last_token_usage'))
            # Accept only the fresh-counter shape observed in the native ledger.
            # Ambiguous corrections do not silently become another paid epoch.
            if total != last or not all(total[k] <= self.latest[k] for k in FIELDS):
                raise ValueError('Ambiguous counter decrease')
            for key in FIELDS:
                self.closed[key] += self.latest[key]
            self.epochs += 1
        self.latest = total
        self.updates += 1
        self.latest_at = record.get('timestamp')
        if self.first_at is None:
            self.first_at = self.latest_at

    def scan(self, max_bytes=16_000_000):
        try:
            stat = self.path.stat()
            identity = (stat.st_dev, stat.st_ino)
            signature = (stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns)
            if (self.identity is not None and
                    (identity != self.identity or stat.st_size < self.offset or
                     (stat.st_size == self.offset and signature != self.signature))):
                self._reset()  # Rebuild instead of adding replacement history twice.
            self.identity = identity
            self.signature = signature
            if self.error is None:
                with self.path.open('rb') as stream:
                    stream.seek(self.offset)
                    raw = stream.read(min(max_bytes, stat.st_size - self.offset))
                self.logical_bytes_read += len(raw)
                self.offset += len(raw)
                block = self.pending + raw
                lines = block.split(b'\n')
                self.pending = lines.pop()
                for line in lines:
                    if len(line) > 16_000_000:
                        raise ValueError('Native record exceeds size limit')
                    self.consume(line)
                    self.digest.update(line + b'\n')
                    self.processed += len(line) + 1
                if len(self.pending) > 16_000_000:
                    raise ValueError('Native record exceeds size limit')
            caught_up = self.offset == stat.st_size
            state = ('INVALID' if self.error else 'INDEXING' if not caught_up else
                     'AWAITING_USAGE' if self.latest is None else 'OBSERVED')
        except (OSError, ValueError, TypeError, AttributeError, UnicodeError) as error:
            self.error = type(error).__name__
            state = 'INVALID'
        usage = None
        if state == 'OBSERVED':
            usage = {k: self.closed[k] + self.latest[k] for k in FIELDS}
            usage['uncached_input_tokens'] = usage['input_tokens'] - usage['cached_input_tokens']
        return {'state': state, 'usage': usage, 'epochs': self.epochs,
                'latest_native_counter': self.latest,
                'accounting_method': 'Epoch reconstruction: full decreases with total equal to last usage are treated as new epochs; provider billing semantics are not attested.',
                'usage_updates': self.updates, 'duplicate_updates_ignored': self.duplicates,
                'first_usage_at': self.first_at, 'latest_usage_at': self.latest_at,
                'models_observed': sorted(self.models), 'error': self.error,
                'source_prefix_bytes': self.processed,
                'source_prefix_sha256': self.digest.hexdigest(),
                'pending_line_bytes': len(self.pending),
                'logical_file_bytes_read': self.logical_bytes_read,
                'scope': 'Observed coordinator thread epochs, including pre-goal work; child runs excluded. Not a bill, quota ratio or benchmark denominator. Already-read history rewrites followed by append require explicit rescan.'}
