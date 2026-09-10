"""Verify public native-readback derivatives without network or inference."""
import base64
import hashlib
import json
from pathlib import Path
import sys
import tempfile

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(REPO / 'engine/prototype'))
from delivery_outbox import DisplayOutbox
from evidence import Store
from workflow_memory import Memory


def main():
    r = json.loads((HERE.parent / 'DISPLAY_OUTBOX_RECOVERY_RESULT.json').read_text())
    for name, expected in r['artifacts'].items():
        assert hashlib.sha256((HERE / name).read_bytes()).hexdigest() == expected
    assert hashlib.sha256((REPO / 'engine/prototype/delivery_outbox.py').read_bytes()).hexdigest() == r['source_after_sha256']
    packet = json.loads((HERE / 'request.json').read_text())
    native = json.loads((HERE / 'native-readback.json').read_text())
    expected_receipt = json.loads((HERE / 'reconciled-receipt.json').read_text())
    with tempfile.TemporaryDirectory(prefix='helix-public-display-') as tmp:
        store = Store(tmp); b = DisplayOutbox(Memory(store))
        ticket = b.stage(packet['delivery_id'], packet['thread_id'],
                         base64.b64decode(packet['output_base64'], validate=True), packet['authority_root'])
        assert ticket['request_hash'] == hashlib.sha256((HERE / 'request.json').read_bytes()).hexdigest()
        args = dict(current_authority=packet['authority_root'], explicit_user_command=True, thread_idle=True)
        assert b.claim(ticket, **args)['submit']
        assert DisplayOutbox(Memory(store)).claim(ticket, **args) == {'state': 'RECONCILE', 'submit': False}
        result = b.reconcile(ticket, native, native_shell=tuple(r['readback_shell_binding']))
        assert result == r['delivery'] and result['state'] == 'DELIVERED'
        assert json.loads(store.get(result['evidence'])) == expected_receipt
        assert b.claim(ticket, **args) == result
    print('PASS: source/artifact bindings, exact native envelope, lost-ACK reconciliation and duplicate suppression; no native process or model.')


if __name__ == '__main__': main()
