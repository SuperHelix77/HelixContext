import json
import pytest
from usage_segments import segments


def event(i,o,last_i=None):
    def u(a,b):return {'inputTokens':a,'outputTokens':b,'cachedInputTokens':0,'reasoningOutputTokens':0,'totalTokens':a+b}
    return {'method':'thread/tokenUsage/updated','params':{'threadId':'x','tokenUsage':{'total':u(i,o),'last':u(i if last_i is None else last_i,o if last_i is None else 2)}}}


def test_duplicates_not_counted_and_unrelated_threads_ignored(tmp_path):
    p=tmp_path/'events';e=event(10,1);other=event(999,99);other['params']['threadId']='other'
    p.write_text('\n'.join(map(json.dumps,[e,e,other,event(25,3,15)])))
    r=segments(p,'x');assert len(r['reported_segments'])==2 and r['total']['input_tokens']==25


def test_ambiguous_missing_update_is_not_claimed_one_segment(tmp_path):
    p=tmp_path/'events';p.write_text(json.dumps(event(25,3,15)))
    with pytest.raises(ValueError):segments(p,'x')
