# JSONL text-line extraction

The native memory follow-up printed full matching JSONL records and then inspected
the full timeline. `jsonl_extract.py` provides an explicit typed reader for that
surface: select literal matching lines inside each decoded `text` field, keeping
the event ID, physical JSONL record line and decoded text-line position. The raw
JSONL bytes remain archived by hash. Decoded text is exact string evidence, not
the original serialized JSON byte range; retrieval of the raw object preserves
escapes and original byte spelling.

```sh
python3 engine/prototype/jsonl_extract.py --store /absolute/store history.jsonl 'Release envelope'
```

The CLI verifies source/query binding, ordered source positions and match/omission
counts using a checker that does not call the extractor. Unsupported schemas,
duplicate keys, malformed JSON and invalid text encodings retain the raw object
and return an explicit unsupported status. The reader never executes source text,
rewrites shell commands or retries a task. Other fields and nonmatching lines
remain omitted, explicitly; structural verification is not semantic sufficiency.

Budgets omit entire matches and count omissions instead of truncating values.
An oversized early match does not prevent a later smaller match from fitting.
Sources are fully read/parsed, so output bounds are not memory or I/O bounds.

## Offline evidence

On the exposed native fixture, both envelope update lines fit in 679 packet bytes;
the original source has 78,905 bytes. Archive/extract/verify took about 1.5 ms in a
single local observation. `JSONL_EXTRACTION_REPLAY.json` pins the measured source
and implementation. The subsequent CLI wiring invokes the already-tested verifier
automatically; that wiring is later than the report's pinned source hash.

The preceding candidate's 7,471 terminal bytes cover several operations, whereas
679 covers one extraction. These are not equivalent accounting boundaries and
must not be used to claim whole-task savings. Ten extraction tests pass; the full
prototype suite passes 138 tests. No new native run or installed skill change was
made. Efficient ordinary controls must retain equivalent targeted parsing tools.
