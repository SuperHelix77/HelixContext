"""Offline falsifier: can a user-authorized Engine action produce durable native items?

This is a disposable app-server experiment, not an automatic production route.
thread/shellCommand is unsandboxed: only the two literal harmless probes below
are permitted. No provider response, production config change or credential copy.
"""
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import selectors
import subprocess
import sys
import threading
import time

CLI = Path('/Applications/ChatGPT.app/Contents/Resources/codex')
ACK = 'HELIX ENGINE / synthetic E01 / durable receipt probe; no model authored this record.'
COMMANDS = ["printf '%s\\n' '" + ACK + "'", '/usr/bin/false']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Peer:
    def __init__(self, root, url, label):
        self.root = root
        self.label = label
        self.wire = []
        self.pending = b''
        self.identity = 0
        self.stderr = (root / (label + '-stderr.txt')).open('wb')
        config = {
            'model_provider': 'capture',
            'model_providers.capture.name': 'Helix offline no-model endpoint',
            'model_providers.capture.base_url': url + '/v1',
            'model_providers.capture.wire_api': 'responses',
            'model_providers.capture.requires_openai_auth': False,
            'model_providers.capture.request_max_retries': 0,
            'model_providers.capture.stream_max_retries': 0,
            'model_catalog_json': str(root / 'catalog.json'),
        }
        args = [str(CLI), 'app-server', '--stdio']
        for key, value in config.items():
            args += ['-c', key + '=' + json.dumps(value)]
        # Child-process Codex home only; no production config/credentials copied.
        env = {k: os.environ[k] for k in ('PATH', 'TMPDIR', 'LANG', 'LC_ALL') if k in os.environ}
        env['CODEX_HOME'] = str(root / 'isolated-home')
        self.process = subprocess.Popen(args, cwd=root / 'workspace', env=env,
                                        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                        stderr=self.stderr, bufsize=0)
        self.selector = selectors.DefaultSelector()
        self.selector.register(self.process.stdout, selectors.EVENT_READ)

    def send(self, value):
        self.process.stdin.write((json.dumps(value) + '\n').encode())
        self.process.stdin.flush()
        self.wire.append({'sent': value})

    def message(self, deadline):
        while time.monotonic() < deadline:
            if b'\n' in self.pending:
                line, self.pending = self.pending.split(b'\n', 1)
                message = json.loads(line)
                self.wire.append({'received': message})
                return message
            if not self.selector.select(min(1, max(0, deadline - time.monotonic()))):
                continue
            chunk = os.read(self.process.stdout.fileno(), 65536)
            if not chunk:
                raise RuntimeError('app-server closed')
            self.pending += chunk
        raise TimeoutError('app-server event deadline')

    def call(self, method, params):
        self.identity += 1
        identity = self.identity
        self.send({'id': identity, 'method': method, 'params': params})
        deadline = time.monotonic() + 20
        while True:
            value = self.message(deadline)
            if value.get('id') == identity:
                if 'error' in value:
                    raise ValueError((method, value['error']))
                return value['result']

    def initialize(self):
        value = self.call('initialize', {'clientInfo': {'name': 'helix_offline_delivery', 'version': '1'},
                                        'capabilities': {'experimentalApi': True}})
        self.send({'method': 'initialized', 'params': {}})
        return value

    def completed_since(self, offset):
        deadline = time.monotonic() + 20
        while True:
            for event in self.wire[offset:]:
                value = event.get('received', {})
                if value.get('method') == 'turn/completed':
                    return value['params']
            self.message(deadline)

    def close(self):
        self.process.terminate()
        try:
            self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait()
        self.selector.close()
        self.stderr.close()
        (self.root / (self.label + '-wire.json')).write_text(json.dumps(self.wire, indent=2) + '\n')


def run(root, catalog):
    root = Path(root).resolve()
    root.mkdir(parents=True, exist_ok=False)
    (root / 'workspace').mkdir()
    (root / 'isolated-home').mkdir()
    (root / 'catalog.json').write_bytes(Path(catalog).read_bytes())
    production = Path('/Users/mert/.codex/config.toml')
    before = sha(production)
    requests = []

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_POST(self):
            self.rfile.read(int(self.headers.get('Content-Length', '0')))
            requests.append(self.path)
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'{"error":{"message":"offline experiment; no model response"}}')

    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    peer = None
    report = {'classification': 'Offline native delivery falsifier; no model performance evidence',
              'commands': COMMANDS, 'probe_sha256': sha(Path(__file__)),
              'catalog_sha256': sha(root / 'catalog.json'), 'cli_sha256': sha(CLI),
              'production_config_initial_sha256': before}
    started = time.monotonic()
    try:
        url = f'http://127.0.0.1:{server.server_port}'
        peer = Peer(root, url, 'first')
        report['initialize'] = peer.initialize()
        report['start'] = peer.call('thread/start', {'model': 'gpt-5.6-luna', 'modelProvider': 'capture',
                                 'cwd': str(root / 'workspace'), 'approvalPolicy': 'never', 'sandbox': 'read-only'})
        thread = report['start']['thread']['id']
        observations = []
        for command in COMMANDS:
            offset = len(peer.wire)
            peer.call('thread/shellCommand', {'threadId': thread, 'command': command, 'timeoutMs': 3000})
            completed = peer.completed_since(offset)
            read = peer.call('thread/read', {'threadId': thread, 'includeTurns': True})
            items = peer.call('thread/items/list', {'threadId': thread, 'limit': 100})
            observations.append({'completed': completed, 'read': read, 'items': items})
        report['observations'] = observations
        peer.close()
        peer = None
        peer = Peer(root, url, 'restart')
        peer.initialize()
        report['resume'] = peer.call('thread/resume', {'threadId': thread, 'excludeTurns': False})
        report['after_restart'] = peer.call('thread/read', {'threadId': thread, 'includeTurns': True})
        report['items_after_restart'] = peer.call('thread/items/list', {'threadId': thread, 'limit': 100})
        report['state'] = 'OBSERVED_AWAITING_AUDIT'
    except Exception as error:
        report.update(state='FAILED_RETAINED', error=repr(error))
    finally:
        if peer:
            peer.close()
        server.shutdown()
        server.server_close()
        worker.join()
        report['provider_requests'] = requests
        report['elapsed_seconds'] = time.monotonic() - started
        report['production_config_final_sha256'] = sha(production)
        report['production_config_unchanged'] = sha(production) == before
        report['isolated_home_has_auth_file'] = (root / 'isolated-home/auth.json').exists()
        report['wire_sha256'] = {p.name: sha(p) for p in root.glob('*-wire.json')}
        (root / 'result.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ('state', 'provider_requests', 'elapsed_seconds',
                                           'production_config_unchanged', 'isolated_home_has_auth_file')}, indent=2))


if __name__ == '__main__':
    run(*sys.argv[1:])
