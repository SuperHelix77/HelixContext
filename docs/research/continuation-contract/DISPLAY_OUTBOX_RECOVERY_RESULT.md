# Engine delivery survives a lost local acknowledgement

**OBSERVED:** one explicitly initiated, harmless Engine display command produced
a Codex native item that survived process restart. The new display tracker then
reconciled a simulated lost local ACK without submitting again. Duplicates return
the stored delivery evidence. No model turn started; the loopback provider saw
zero requests. Production configuration was unchanged; no credentials copied.

This implements a missing delivery primitive for the W50 call-elimination path.
It does not change benchmark counters, qualify coding or complete app integration.
Engine task effects and display delivery remain separate states.

The initial native probe **failed safely**: it expected a literal command, while
Codex stored a `/bin/zsh -lc` envelope. The tracker left the request `CLAIMED` for
reconciliation. Original failed result/store/wires remain untouched. Corrected
readback accepts a caller-bound shell envelope and compares its complete parsed
argv. It never executes or loosely strips the shell string.

Recovery used a **cloned store and retained native item**, with no second native
execution. The [audit](DISPLAY_OUTBOX_RECOVERY_RESULT.json) retains the failure,
source-before/source-after hashes, wire hashes and costs. The original source was
reconstructed and matched to its recorded SHA before archival. Public derivatives
can be verified without a native process or model:

```sh
python3 docs/research/continuation-contract/display-outbox-artifacts/verify.py
python3 -m pytest -q engine/prototype/test_delivery_outbox.py engine/prototype/test_completion_ledger.py engine/prototype/test_passive_workflow.py engine/prototype/test_semantic_execution.py
```

**39 focused tests passed**: concurrent claimants, stale authority, missing user
permission, busy thread, conflicting identity, request corruption, failed receipt
writes, failed execution, wrong native attribution, literal shell metacharacters,
exact wrapper parsing and duplicate suppression.

`stage` records already-completed output against delivery ID, thread and authority;
it cannot decide task completion. `claim` grants one `SUBMIT_ONCE` transactionally.
A claimed request survives restart as `RECONCILE`. `reconcile` checks caller-fetched
native history and stores `DELIVERED` or `FAILED` with exact evidence. The library
never executes a task, starts a model or resends uncertain work. Its command is
a fixed absolute `printf` with literal data, not instructions from stored evidence.

The original native trial took 0.501 seconds including failed readback; offline
recovery took approximately 0.009 seconds. These are local observations, not
latency distributions. Object traffic and cloned-store logical bytes are retained;
SQLite/physical I/O, energy and parent research are not silently zeroed. No provider
token receipt arrived: zero loopback requests are not native zero-token benchmarks.

The [official app-server contract](https://learn.chatgpt.com/docs/app-server)
restricts `thread/shellCommand` to explicit user-initiated commands and states that
it runs outside the thread sandbox. This is that authorized display port, not an
automatic chat hook or permission bypass. A suitable authorized desktop surface
is still required before transparent use.

The caller supplies authentic completion identity, native history, permission and
current authority. SQLite integrity is assumed: an attacker rolling the index back
can defeat submit-once behavior. No hostile-host or exactly-once external-effects
guarantee is claimed. A crash after claim but before an observable native item stays
uncertain; native idempotency or explicit reconciliation is needed.

Idle/authority preflight is not an atomic app lock. Automatic pre-submit composition,
desktop rendering, rollback custody and UI acknowledgement remain open. Display
proves neither semantic correctness nor underlying task success.
