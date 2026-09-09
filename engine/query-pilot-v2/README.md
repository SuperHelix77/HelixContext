# Request-conditioned exact-line pilot V2

Compound identifiers now match their components while retaining the original token. This is a new candidate; V1 receipts remain unchanged. Six compiler tests passed. The partial view includes 21 matched lines, with full raw-source fallback still available.

| Model · High | Input saved | Output saved | Commands off / on |
|---|---:|---:|---:|
| luna | -3.5% | -0.2% | 1 / 1 |
| sol | 49.6% | 50.0% | 3 / 1 |
| astra | 25.7% | 38.6% | 2 / 1 |

All exact-answer, recursive type and unchanged-source checks passed: True.
Native experiment cost: 218,254 input and 2,742 output tokens. Parent research is additional.

These are six development runs on an exposed task, not a final capability gate. The compiler is request-conditioned, not answer-conditioned. Its byte reduction is not native token savings. No global hooks or skills were changed. The 80% joint target is not established.

The archived pilot driver requires the original workspace layout and shared native runner. Direct candidate and shared runner hashes were checked before/after execution; full transitive environment closure and OS isolation were not established. Native runner uses --ignore-user-config. Raw native traces stay local; their hashes and usage are preserved here.
