"""Small versioned App Server dynamic-tool transport. No model or final renderer.

The caller supplies a pre-authorized handler. Unknown requests are rejected;
thread/turn/call identity must match. In-process duplicate delivery reuses the
exact response; conflicting reuse stops. Side-effect handlers additionally need
durable application/receipt state: this transport is not crash-safe execution.
"""
import json
import os
import time
from app_server_native import RPC


def rpc_type(specs, handler):
    names = {s['name'] for s in specs}
    if len(names) != len(specs) or any(s.get('type') != 'function' for s in specs):
        raise ValueError('Unique simple function specifications required')

    class ToolRPC(RPC):
        def __init__(self, *args):
            super().__init__(*args)
            self.bound_thread = None; self.active_turn = None; self.delivered = {}

        def call(self, method, params):
            if method == 'thread/start': params = {**params, 'dynamicTools': specs}
            if method == 'turn/start':
                if params['threadId'] != self.bound_thread: raise ValueError('Wrong native thread')
                self.active_turn = None
            reply = super().call(method, params)
            if method == 'thread/start': self.bound_thread = reply['thread']['id']
            if method == 'turn/start': self.active_turn = reply['turn']['id']
            return reply

        def dispatch(self, event):
            p = event.get('params', {})
            if (event.get('method') != 'item/tool/call' or p.get('threadId') != self.bound_thread
                    or not self.active_turn or p.get('turnId') != self.active_turn
                    or p.get('tool') not in names or p.get('namespace') is not None
                    or not isinstance(p.get('callId'), str) or not p['callId'] or 'arguments' not in p):
                raise ValueError('Unknown or unbound native server request')
            identity = (p['threadId'], p['callId'])
            binding = json.dumps(p, sort_keys=True, separators=(',', ':'), allow_nan=False)
            if identity in self.delivered:
                prior, response = self.delivered[identity]
                if prior != binding: raise ValueError('Conflicting duplicate native call')
                return response
            response = handler(p)
            if (not isinstance(response, dict) or set(response) != {'success', 'contentItems'}
                    or type(response['success']) is not bool or not isinstance(response['contentItems'], list)
                    or any(not isinstance(x, dict) or set(x) != {'type', 'text'}
                           or x['type'] != 'inputText' or not isinstance(x['text'], str) for x in response['contentItems'])):
                raise ValueError('Invalid native tool response')
            self.delivered[identity] = binding, response
            return response

        def read(self):
            while b'\n' not in self.buffer:
                remaining = self.deadline-time.monotonic()
                if remaining <= 0: raise TimeoutError('Native deadline')
                if not self.selector.select(min(remaining, 10)): continue
                raw = os.read(self.p.stdout.fileno(), 65536)
                if not raw: raise RuntimeError('Native server closed')
                self.buffer += raw
            line, self.buffer = self.buffer.split(b'\n', 1)
            self.raw.write(line+b'\n'); self.raw.flush()
            event = json.loads(line); self.events.append(event)
            p = event.get('params', {})
            if event.get('method') == 'turn/started' and p.get('threadId') == self.bound_thread:
                self.active_turn = p['turn']['id']
            if 'method' in event and 'id' in event:
                try: response = self.dispatch(event)
                except BaseException:
                    self.send({'id': event['id'], 'error': {'code': -32000, 'message': 'Unqualified native tool request; caller stopped'}})
                    raise
                self.send({'id': event['id'], 'result': response})
            return event
    return ToolRPC
