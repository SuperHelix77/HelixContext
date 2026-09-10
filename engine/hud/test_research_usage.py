import json

from research_usage import Ledger


def usage(n, cached=0):
    return dict(input_tokens=n, cached_input_tokens=cached, cache_write_input_tokens=0,
                output_tokens=n // 10, reasoning_output_tokens=0, total_tokens=n+n//10)


def event(total, last=None):
    return (json.dumps({'type': 'event_msg', 'timestamp': '2026-09-10T00:00:00Z',
        'payload': {'type': 'token_count', 'info': {
            'total_token_usage': total, 'last_token_usage': last or total}}})+'\n').encode()


def test_append_duplicate_and_restart_epochs_are_counted_once(tmp_path):
    p=tmp_path/'trace';first=event(usage(100))+event(usage(200))+event(usage(200))
    p.write_bytes(first);ledger=Ledger(p);a=ledger.scan()
    assert a['usage']['input_tokens']==200 and a['epochs']==1
    assert a['duplicate_updates_ignored']==1
    assert ledger.scan()['logical_file_bytes_read']==len(first)
    extra=event(usage(30))+event(usage(80))
    with p.open('ab') as f:f.write(extra)
    b=ledger.scan();assert b['usage']['input_tokens']==280 and b['epochs']==2
    assert b['logical_file_bytes_read']==len(first+extra)
    assert Ledger(p).scan()['usage']==b['usage']


def test_partial_append_and_scan_limit_never_expose_partial_totals(tmp_path):
    p=tmp_path/'trace';raw=event(usage(100));p.write_bytes(raw[:-2]);ledger=Ledger(p)
    assert ledger.scan(max_bytes=5)['state']=='INDEXING'
    assert ledger.scan()['state']=='AWAITING_USAGE'
    with p.open('ab') as f:f.write(raw[-2:])
    result=ledger.scan();assert result['usage']['input_tokens']==100
    assert result['pending_line_bytes']==0


def test_ambiguous_counter_correction_is_not_an_epoch(tmp_path):
    p=tmp_path/'trace';p.write_bytes(event(usage(100))+event(usage(80),usage(20)))
    ledger=Ledger(p);result=ledger.scan()
    assert result['state']=='INVALID' and result['usage'] is None
    assert ledger.scan()['logical_file_bytes_read']==result['logical_file_bytes_read']


def test_truncation_and_replacement_rebuild_without_double_count(tmp_path):
    p=tmp_path/'trace';p.write_bytes(event(usage(100))+event(usage(200)))
    ledger=Ledger(p);ledger.scan();p.write_bytes(event(usage(50)))
    assert ledger.scan()['usage']['input_tokens']==50
    other=tmp_path/'new';other.write_bytes(event(usage(60)));other.replace(p)
    assert ledger.scan()['usage']['input_tokens']==60


def test_invalid_subset_or_missing_counter_is_not_zero_cost(tmp_path):
    p=tmp_path/'trace';p.write_bytes(event(usage(100,101)))
    assert Ledger(p).scan()['usage'] is None
    invalid=usage(100);del invalid['output_tokens'];p.write_bytes(event(invalid))
    assert Ledger(p).scan()['state']=='INVALID'


def test_prompt_content_is_never_exported(tmp_path):
    p=tmp_path/'trace';secret='private prompt content'
    p.write_text(json.dumps({'type':'response_item','payload':{'content':secret}})+'\n')
    with p.open('ab') as f:f.write(event(usage(100,60)))
    result=Ledger(p).scan();assert secret not in json.dumps(result)
    assert result['usage']['uncached_input_tokens']==40
