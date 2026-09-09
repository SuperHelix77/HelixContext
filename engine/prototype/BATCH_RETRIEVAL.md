# Batch exact retrieval

`evidence.py --store STORE get-many RECEIPT --range 1 4 --range 90 95`

Multiple ordered inclusive spans share one freshly hash-verified source read. Binary spans use base64; CRLF, duplicate requests and request ordering are preserved. A corrupt source or any out-of-range span rejects the whole batch. This operation writes no durable workflow state. Each subsequent call verifies again, avoiding a persistent cache that could conceal changed evidence.

The deterministic benchmark retrieves 1, 5 and 20 ranges from the same source. Compared with separate retrieval calls, application object reads fall by 0%, 80% and 95%, respectively, with exact matching returned bytes and hashes. This measures application I/O only. It does **not** establish model token savings, CPU savings, physical disk savings or intelligence/workflow parity. The full source is still read once per batch; use the existing verified index for a different sparse-access tradeoff.

Validation: 42 middleware tests passed, including batch CLI, invalid ranges, exact binary data, duplicate ordering and corruption between calls. Reproduce the I/O receipt with `python3 benchmark_batch.py`.

Batching is appropriate when several evidence spans are already known to be needed. Do not fetch speculative spans just to inflate the batch size or claim savings against an inefficient control.
