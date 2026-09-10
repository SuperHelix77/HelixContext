"""Versioned ACK wording correction; original stopped driver remains immutable."""
import importlib.util
import json
from pathlib import Path
import re
import sys
import time

HERE = Path(__file__).resolve().parent
OLD = HERE.with_name('w50-native-final-v1') / 'pilot.py'
spec = importlib.util.spec_from_file_location('w50_original_driver', OLD)
original = importlib.util.module_from_spec(spec); spec.loader.exec_module(original)
BaseSession = original.session_api.Session


def literal_ack(text):
    """Only replace the frozen caller trailer, never text inside an event."""
    match = re.search(r'\nReturn exactly (ACK E[0-9]+)\.$', text)
    if not match: return text
    return (text[:match.start()] + '\nThe required reply is exactly ' + json.dumps(match.group(1)) +
            ', without quotation marks or trailing punctuation.')


class LiteralAckSession(BaseSession):
    def turn(self, text=None, tool_output=None):
        return super().turn(literal_ack(text) if text is not None else None, tool_output)


def prepare(root, effort):
    started = time.perf_counter()
    original.prepare(root, effort)
    root = Path(root).resolve(); path = root / 'manifest.json'
    m = json.loads(path.read_text())
    m['protocol'] = 'helix.w50-native-final.v2'
    m['amendment'] = 'Exact ACK string quoted; semantic final, strict grader, base, tools and effort unchanged'
    m['prior_stopped_attempt'] = 'w50-native-final-v1/STOPPED.json; 40413 input/15 output, no candidate'
    for p in (Path(__file__), HERE / 'PREREG.md', HERE / 'test_ack_literal.py',
              HERE / 'RESUMPTION.md', HERE / 'OFFLINE.json',
              HERE.with_name('w50-native-final-v1') / 'STOPPED.json'):
        m['bindings'][str(p.resolve())] = original.sha(p)
    m['preparation_seconds'] = time.perf_counter() - started
    original.save(path, m)
    print(json.dumps({'frozen_v2_manifest_sha256': original.sha(path), 'model_turns': 0}))


def run(root):
    original.session_api.Session = LiteralAckSession
    try: original.run(root)
    finally: original.session_api.Session = BaseSession


if __name__ == '__main__':
    if sys.argv[1] == 'prepare': prepare(sys.argv[2], sys.argv[3])
    else: {'run': run}[sys.argv[1]](sys.argv[2])
