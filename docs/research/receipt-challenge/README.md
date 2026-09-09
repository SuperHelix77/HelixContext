# Astra receipt challenge: offline evaluator preflight

**OBSERVED:** zero model calls; no Engine, skill, routing or production receipt
implementation changes. This is research task data and an executable fixture audit
following §21 of the council synthesis. It does not establish any token savings,
Astra behavior, transactionality, intelligence parity or workflow parity.

| Supplied proposal / evidence condition | Limited mechanical checker | Independent finite semantic checker | Expected later decision |
|---|---|---|---|
| Valid exact-int transactional batch | PASS | PASS | Assess adequacy, then accept |
| `isinstance` permits bool/int subclasses | PASS, authentic source/log hashes | FAIL | Reject or repair; PASS scope is insufficient |
| Old contract root versus current contract | Root mismatch observed; no apply attempted | Not a semantic verdict | Invalidate reuse and review current obligations |

Eight preflight assertions pass. Four additional contract mutations—reversed
batch order, list-identity replacement, double consumption, and incorrect cursor
updates—are rejected by the corrected semantic checker. Full stdout and stderr
were preserved separately, with hashes and sizes; the public result normalizes
local command paths. Python elapsed time was about 0.25 seconds for this audit;
physical I/O and coordinator model cost are not measured here and are not zero.

## Hostile audit and correction before inference

The first semantic checker missed reversed batch order: it checked the count
and list identity after the one-pass iterable but omitted the resulting sequence.
The mechanical checker would catch that mutation, but relying on its presence
would conceal a defect in the independent semantic checker. An exact expected
sequence assertion was added. The other three mutations were already rejected.
The initial local artifact directory was retained, and the corrected run used a
new directory. No model result was adjudicated with either checker.

This finding narrows the next action: freeze an audited evaluator before native
measurement. It is not a reason to weaken the task or count a broken checker as
model success. The fixture is deliberately related to an existing public failure
family; it is development evidence, never a holdout.

## Scope boundaries

The example receipts label unchecked semantic obligations explicitly. Hashes bind
bytes; they do not validate meaning. The stale-root assertion demonstrates a
mismatch only. No production stale-state rejection, atomic application, TOCTOU
protection, restart recovery or native tool bridge was implemented or certified.
The script never applies a proposed patch and does not invoke a model.

Both future matching arms must receive the same public contract and proposed
patch. Only the candidate receives the caller's narrow mechanical execution
receipt. The independent semantic checker stays outside model-visible task data;
the public contract remains complete in both arms. Adverse receipt conditions
are safety falsifiers and must not be averaged into the valid-pair savings result.

## Reproduce

From the repository root, choose a new output directory:

```sh
python3 docs/research/receipt-challenge/audit_fixture.py /tmp/helix-receipt-preflight-new
```

The script refuses to overwrite an existing directory. `PREFLIGHT_RESULT.json`
contains observed checks, identities, output hashes and limitations. Next gate:
freeze matching prompts, caller responsibility boundaries, tools, randomized pair
order and recovery/resource rules before any native experiment. No new mechanism
or benchmark is automatically authorized by this research artifact. The original
80% input AND output target, with capability/workflow preservation first, remains
unmet for Astra and for the representative three-model benchmark.
