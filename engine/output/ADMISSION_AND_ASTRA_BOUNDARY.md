# Admission gate and Astra's first-segment boundary

The new `prototype/admission.py` dispatches before optimization preparation. It
passes the original request/payload to exactly one caller callback. Unsupported
production requests use native execution; no production parity qualification
exists. Only explicitly requested, exact-fixture research can use a pinned profile.
Model, effort and caller-verified contract must match. Profile/evidence/source
hashes, finite checks and separate native 80/80 measurements are verified before
selecting the optimized callback. A failure after callback execution starts
propagates; it never silently reruns potentially side-effecting work natively.

This is a caller API with tested dispatch behavior, **not a global Codex hook**.
The qualification registry is trusted caller configuration, never model-supplied
source instructions. The caller must derive the contract hash from the actual
verified task. The gate cannot infer task similarity or prevent concurrent source
mutation during callback execution. These limits preclude production promotion.
The exact Sol research manifest binding is included; its original profile and all
16 frozen implementation hashes are unchanged.

## Cost charged, not hidden

The [real-profile engineering probe](ADMISSION_AUDIT.json) admits only the exact
Sol research binding. Astra/Luna cross-model attempts and all production requests
bypass before any gate file reads. The caller still has its own request/config
construction cost, which is outside this gate-only meter. Sol verification read
120,179 logical bytes in approximately 1.67 ms on this local run. No inference was
used, no native execution was performed by the probe, and physical I/O is unknown.
Admission has no savings claim; native bypass is zero optimization savings, not
80% and not proof of general parity. Do not sum these timings with token counts.

## Better diagnosis from existing native evidence

[Reported segment receipts](ASTRA_PATCH_SEGMENTS.json) independently reconcile
native cumulative counters with each update's `last` usage. Duplicate updates do
not count twice; inconsistent/missing segment boundaries are rejected. No private
reasoning content is inspected or inferred.

| Native input segments | Control | Helix |
|---|---:|---:|
| First reported segment | 18,575 | 19,748 |
| Subsequent reported segments | 79,676 | 107,649 |
| Number of reported segments | 5 | 6 |
| Total | 98,251 | 127,397 |

An 80% input saving permits 19,650.2 tokens against this control. Helix's recorded
initial charge already exceeds that allowance by 97.8 tokens. **Conditional on
that charge remaining unchanged**, even eliminating all later model input cannot
reach 80%. This is a property of this trace, not an irreducible model lower bound,
not a proof that all fixed platform context is removable, and not a causal
estimate from a randomized repeated sample. Cached-input savings remain distinct.

Both arms used four commands, so command count alone concealed an extra reported
usage segment. The next justified architectural experiment is caller-owned patch
application and verification after a semantic response, with real failures returned
to the model and every additional call charged. It must preserve the original
contract/tests, retain normal tools when needed, and avoid telling the model the
repair. Reformatting terminal output alone cannot fix the observed first-input
excess. That experiment has not been run or claimed successful here.

The broader 80/80, representative three-model matrix and native long-horizon
no-loss gates remain open. The admission gate protects against misapplication; it
does not satisfy those research objectives by refusing unsupported tasks.
