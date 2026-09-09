# Engine receipt delivery contract

Research implementation: `engine/prototype/receipt_delivery.py`.
No Codex hook activated, native message fabricated or model called.

The Engine feed projects a caller-pinned completion snapshot into ordered pages.
Each item has a stable scope/receipt-bound delivery ID, Engine attribution, exact
base64 payload and digest. Retry returns the same items. A consumer must persist
its own deduplication/acknowledgement state; the feed says **offered**, never delivered.
It does not interpret payloads as semantic PASS or execute embedded instructions.

```sh
python3 engine/prototype/receipt_delivery.py \
  --store /absolute/store --scope workflow-id --head VERIFIED_ROOT --limit 50
```

The command initializes existing Memory/ledger schemas if absent; projection does
not append completion events. It requires a trusted head supplied by the caller.
Pagination is within one immutable snapshot. Newly committed events require a new
head; do not silently apply an old numeric offset to an unrelated snapshot.
Full-chain retrieval remains charged and is not constant-time pagination.

**OBSERVED:** seven delivery/ledger tests passed. Delivery checks replay 49 exact
payloads, reopen the store, add a later event without changing the pinned page,
deduplicate a repeated page in a simulated consumer, and reject invalid cursors,
wrong scope and corrupt root. This is not a persistent network consumer, full HUD,
normal-app integration, native savings benchmark or power-loss certification.

This supplies a small Engine-owned boundary that the CLI/HUD can consume now and
a Codex adapter can consume later. It avoids relying on the failed raw-injection
delivery path. The user allowed Codex integration later; Engine packaging and
desktop integration remain distinct release gates rather than permanently blocking
all packaging on the current app's message surface.

Luna qualification remains open: W50 has bounded >=75/75 evidence, broader coding
does not. The feed changes no existing benchmark counters and supplies no new
capability proof. Next qualification must use the assembled lifecycle, exact ACKs
and semantic re-entry with native bypass preserved; raw feed tests are insufficient.
