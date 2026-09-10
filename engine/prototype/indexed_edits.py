"""Compile version-bound LF-line edits to the existing exact-copy plan.

The model chooses positions and every inserted byte. Caller supplies the immutable
source identity. No semantic repair, fuzzy matching, normalization or execution.
Lines are split only on LF; CRLF and Unicode bytes remain unchanged. A terminal LF
does not create another line. Position n+1 permits insertion at EOF.
"""
import hashlib


def lines(raw):
    parts=raw.split(b'\n')
    return [p+b'\n' for p in parts[:-1]]+([parts[-1]] if parts[-1] else [])


def compile_edits(raw, expected_sha256, response):
    if not isinstance(raw,bytes) or hashlib.sha256(raw).hexdigest()!=expected_sha256:
        raise ValueError('Caller source version changed')
    raw.decode('utf-8')  # This interface handles exact UTF-8 source, not arbitrary binary.
    if not isinstance(response,dict) or set(response)!={'edits'} or not isinstance(response['edits'],list):
        raise ValueError('Indexed edits required')
    offsets=[0]
    for line in lines(raw):offsets.append(offsets[-1]+len(line))
    spans=[]
    for edit in response['edits']:
        if (not isinstance(edit,dict) or set(edit)!={'start_line','delete_lines','insert'}
                or type(edit['start_line']) is not int or type(edit['delete_lines']) is not int
                or not isinstance(edit['insert'],str)):
            raise ValueError('Invalid indexed edit')
        at=edit['start_line']-1;count=edit['delete_lines'];insert=edit['insert']
        if not 0<=at<len(offsets) or count<0 or at+count>=len(offsets):
            raise ValueError('Line range outside bound source')
        insert.encode('utf-8')
        spans.append((offsets[at],offsets[at+count],insert))
    operations=[];cursor=0;copied=0;inserted=0;previous_start=None
    for start,end,insert in sorted(spans):
        if start<cursor or start==previous_start:
            raise ValueError('Overlapping or co-located edits are ambiguous')
        if cursor<start:
            operations.append({'source_sha256':expected_sha256,'start_byte':cursor,'end_byte':start})
            copied+=start-cursor
        operations.append({'literal_utf8':insert});inserted+=len(insert.encode())
        cursor=end;previous_start=start
    if cursor<len(raw):
        operations.append({'source_sha256':expected_sha256,'start_byte':cursor,'end_byte':len(raw)});copied+=len(raw)-cursor
    return {'schema':'helix.copy.v1','operations':operations}, {
        'source_sha256':expected_sha256,'source_bytes':len(raw),'source_lines':len(offsets)-1,
        'edits':len(spans),'copied_bytes':copied,'literal_bytes':inserted,
        'semantics':'Not checked by indexed addressing or assembly'}
