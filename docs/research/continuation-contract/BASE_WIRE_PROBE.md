# Installed client base-override serialization capture

OBSERVED: six requests were captured from the installed CLI against an isolated,
loopback-only custom provider, with no credentials and no hosted model execution.
All requests intentionally received400after capture. This exit is expected and
is not a failed native model benchmark. Production configuration was unchanged.

| Model | Default input-text proxy | Marker override | Difference |
|---|---:|---:|---:|
| Sol |4,349|815|−3,534|
| Luna |4,349|815|−3,534|
| Astra |5,156|1,064|−4,092|

In every capture, the Lite header is true, top-level instructions are empty,
and tools use an `additional_tools` input item. The custom marker appears inside
a developer message. The client-side base fragment is replaced by the marker;
it is not added alongside the old fragment in this outgoing payload. The initial
marker matcher mistakenly required the trailing newline; corrected inspection
matches the exact identifier after CLI whitespace trimming. Original captures
are preserved; no new request was needed to correct that detector.

**What this settles:** the installed serializer honors the configured file as the
source of the client-side base fragment on this custom-provider Lite route.
**What it does not settle:** whether the hosted authenticated service supplies
additional instructions independently. The mock does not implement that service.
The external issue about service-side addition is therefore neither proved nor
falsified by this capture. Provider capabilities also differ from the hosted path.

Do not call these proxy differences native token savings. No behavioral kernel,
capability reduction, tool removal or production transport toggle was activated.
The benign marker is only an instrumentation probe, not an adequate task policy.
Any next kernel trial needs preserved operational invariants, native transport
verification and same-base controls; a shorter client payload alone proves no
intelligence or workflow equivalence.

Raw requests remain local at`research/base-wire-probe-v1-20260909`; publishedJSON
contains only identities, sizes and serialization metadata. The reproducible
script uses a disposable isolated home and no credentials, and rejects requests
without generating a model response.
