# Delivery falsifier: raw injection is insufficient

Installed 0.153.4, isolated homes and a non-model loopback provider. No production
configuration changes or native model calls. [Receipts](PREINFERENCE_DELIVERY_RESULT.json).

1. Injected an explicitly Engine-labelled record, inspected `thread/items/list`
   and `thread/turns/list`, repeated injection, then resumed the loaded thread.
   Normal item/turn lists remained empty. Resume here is not a process restart.
2. Created a real turn with the trusted blocking UserPromptSubmit hook. Waited for
   its authoritative `turn/completed` notification before injection. The turn API
   reported completed, but item lists remained empty before/after duplicate
   insertion and resume. Provider request count remained zero.

Raw records were persisted twice for two accepted identical submissions in the
completed probes. The injection primitive does not supply delivery deduplication.
It must not be substituted for a committed, visible Engine ACK. This falsifies this
tested raw-item path, not every possible supported app-server completion interface.

One earlier composition attempt used an idle snapshot as its completion condition
and terminated before the hook completed. It is preserved and excluded from the
completion conclusion. The corrected probe waits for the real terminal event;
no model failure or native benchmark was retried.

**Decision:** keep pre-submit inhibition as verified. Reject raw injection alone as
the delivery adapter. Do not fabricate assistant-generation events or alter native
history storage directly to manufacture UI success. Investigate an explicitly
attributed Engine completion surface or supported client integration; desktop
75/75 release remains unqualified until exact ACK delivery/recovery is established.
