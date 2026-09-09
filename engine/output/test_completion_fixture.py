import json
from completion_pair import fixture,index_source,expected_ids


def choose(rows, *, fallback=False, truthy=False, exclusive=False):
    result=[]
    test=(lambda value:bool(value)) if truthy else (lambda value:value is True)
    def eligible(row):
        return test(row['approved']) and (row['expires_day']>30 if exclusive else row['expires_day']>=30)
    for group in sorted({r['group'] for r in rows}):
        candidates=[r for r in rows if r['group']==group and test(r['published']) and (not fallback or eligible(r))]
        if candidates:
            newest=max(candidates,key=lambda r:r['revision'])
            if eligible(newest):result.append(newest['id'])
    return result


def test_frozen_expectation_and_adversarial_mutants():
    rows=[json.loads(line) for line in fixture().splitlines()]
    assert choose(rows)==expected_ids()
    assert choose(rows,fallback=True)!=expected_ids()
    assert choose(rows,truthy=True)!=expected_ids()
    assert choose(rows,exclusive=True)!=expected_ids()


def test_complete_metadata_and_exact_ranges():
    raw=fixture();metadata,ranges,lines=index_source(raw)
    assert len(metadata)==len(ranges)==len(lines)==36
    for row in metadata:
        source=json.loads(lines[row['id']])
        assert row=={k:v for k,v in source.items() if k!='payload'}
        span=ranges[row['id']]
        assert raw[span['start_byte']:span['end_byte']]==lines[row['id']]
        assert lines[row['id']].endswith(b'\n')
