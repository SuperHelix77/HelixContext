"""Public artifact integrity and independent exact-value check; zero inference."""
import base64
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    closure = json.loads((HERE / 'CLOSURE.json').read_text())
    for name, digest in closure['files'].items():
        assert hashlib.sha256((HERE / name).read_bytes()).hexdigest() == digest, name
    fixture = json.loads((HERE / 'artifacts/fixture.json').read_text())
    matches = [(e['turn'], n) for e in fixture['source'] for n in e['data']['notes'] if n['inventory_tag'] == 'PKG_01_02']
    assert len(matches) == 1
    turn, note = matches[0]
    expected = {**note, 'evidence_turn':turn, 'label_utf8_base64':base64.b64encode(note['label_exact'].encode()).decode()}
    audit = json.loads((HERE / 'AUDIT.json').read_text())
    for row in audit['rows']:
        raw = (HERE / 'artifacts' / (row['arm'] + '-final.txt')).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == row['final_sha256']
        answer = json.loads(raw)
        assert json.dumps(answer,sort_keys=True,ensure_ascii=False) == json.dumps(expected,sort_keys=True,ensure_ascii=False)
        assert all(sum(s[k] for s in row['segment_usage']) == v for k,v in row['usage'].items())
    off, on = ({r['arm']:r for r in audit['rows']}[a] for a in ['off','on'])
    for k in ['input_tokens','output_tokens']:
        assert abs(audit['savings_percent'][k]-100*(1-on['usage'][k]/off['usage'][k])) < 1e-10
    print(json.dumps({'public_integrity':'PASS','bound_files':len(closure['files']),
                      'independent_source_final_check':'PASS','scope':'Raw stream hashes are published; full private native streams audited separately, not independently replicated here'}))


if __name__ == '__main__': main()
