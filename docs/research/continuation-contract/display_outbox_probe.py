"""Offline app-server display/restart probe. One harmless fixed printf; no model.

An isolated no-auth home and loopback provider are mandatory. The operation is
explicitly initiated by this test, never by an intercepted real user message.
"""
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sys
import threading
import time

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO / 'engine/prototype'))
from native_engine_delivery_probe import Peer, CLI, sha
from delivery_outbox import DisplayOutbox
from evidence import Store
from workflow_memory import Memory


def run(root, catalog):
    root = Path(root).resolve()
    root.mkdir(parents=True, exist_ok=False)
    (root / 'workspace').mkdir(); (root / 'isolated-home').mkdir()
    (root / 'catalog.json').write_bytes(Path(catalog).read_bytes())
    production = Path('/Users/mert/.codex/config.toml')
    initial = sha(production)
    requests = []
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args): pass
        def do_POST(self):
            self.rfile.read(int(self.headers.get('Content-Length', '0')))
            requests.append(self.path)
            self.send_response(400); self.end_headers()
            self.wfile.write(b'{"error":{"message":"no model in offline probe"}}')
    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    worker = threading.Thread(target=server.serve_forever, daemon=True); worker.start()
    url = f'http://127.0.0.1:{server.server_port}'
    started = time.perf_counter(); peer = None
    report = {'state': 'RUNNING', 'classification': 'Offline native display/restart; no capability or token-saving claim',
              'source_sha256': {str(p.relative_to(REPO)): sha(p) for p in
                               [Path(__file__), HERE / 'native_engine_delivery_probe.py',
                                REPO / 'engine/prototype/delivery_outbox.py', REPO / 'engine/prototype/evidence.py',
                                REPO / 'engine/prototype/workflow_memory.py']},
              'cli_sha256': sha(CLI), 'catalog_sha256': sha(root / 'catalog.json')}
    store = Store(root / 'engine'); outbox = DisplayOutbox(Memory(store))
    try:
        peer = Peer(root, url, 'first'); peer.initialize()
        start = peer.call('thread/start', {'model': 'gpt-5.6-luna', 'modelProvider': 'capture',
                          'cwd': str(root / 'workspace'), 'approvalPolicy': 'never', 'sandbox': 'read-only'})
        thread = start['thread']['id']; report['thread_id'] = thread
        ticket = outbox.stage('synthetic-committed-E01', thread, b'ACK E01\n', 'a' * 64)
        report['ticket'] = ticket
        claimed = outbox.claim(ticket, current_authority='a' * 64, explicit_user_command=True, thread_idle=True)
        assert claimed['submit']; report['claim'] = claimed
        offset = len(peer.wire)
        peer.call('thread/shellCommand', {'threadId': thread, 'command': claimed['command'], 'timeoutMs': claimed['timeout_ms']})
        report['native_completion'] = peer.completed_since(offset)
        # Intentionally omit local reconciliation/ACK, then restart the server.
        peer.close(); peer = None
        outbox = DisplayOutbox(Memory(store))
        pending = outbox.claim(ticket, current_authority='a' * 64, explicit_user_command=True, thread_idle=True)
        assert pending == {'state': 'RECONCILE', 'submit': False}
        report['lost_local_ack'] = pending
        peer = Peer(root, url, 'restart'); peer.initialize()
        peer.call('thread/resume', {'threadId': thread, 'excludeTurns': False})
        history = peer.call('thread/read', {'threadId': thread, 'includeTurns': True})['thread']
        report['native_history'] = history
        assert len(history['turns']) == 1
        delivered = outbox.reconcile(ticket, history)
        assert delivered['state'] == 'DELIVERED'; report['delivery'] = delivered
        duplicate = DisplayOutbox(Memory(store)).claim(ticket, current_authority='a' * 64, explicit_user_command=True, thread_idle=True)
        assert duplicate == delivered; report['duplicate'] = duplicate
        blocked = outbox.stage('synthetic-committed-E02', thread, b'ACK E02\n', 'a' * 64)
        hold = outbox.claim(blocked, current_authority='b' * 64, explicit_user_command=True, thread_idle=True)
        assert hold == {'state': 'HOLD', 'submit': False}; report['stale_authority'] = hold
        report['state'] = 'PASS'
    except BaseException as exc:
        report.update(state='FAILED_RETAINED', error=repr(exc))
    finally:
        if peer: peer.close()
        server.shutdown(); server.server_close(); worker.join()
        report.update(provider_requests=requests, elapsed_seconds=time.perf_counter()-started,
                      production_config_unchanged=sha(production)==initial,
                      isolated_home_has_auth_file=(root / 'isolated-home/auth.json').exists(),
                      object_io=dict(store.metrics), wire_sha256={p.name: sha(p) for p in root.glob('*-wire.json')})
        (root / 'result.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ('state', 'provider_requests', 'elapsed_seconds', 'production_config_unchanged', 'isolated_home_has_auth_file')}))


if __name__ == '__main__':
    run(*sys.argv[1:])
