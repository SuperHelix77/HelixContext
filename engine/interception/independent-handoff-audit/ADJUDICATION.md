# Independent adjudication of the Spark/Luna interception handoff

Verdict: **observation confirmed; native replacement inconclusive**. This is narrower than interpreting OBSERVATION_ONLY as a proven platform limitation.

Verified directly from retained raw data and five event traces:

- The fixture has 9,200,129 bytes and the reported raw SHA-256 matches.
- Each native command item has 1,048,607 bytes and the same reported native SHA-256. The middle sentinel is absent. This upstream truncation is real and is not lossless Helix compression.
- The replacement arm's hook failed. Its handler assumes a dictionary-shaped tool_response. With the observed string shape it calls `.get()` on a string and exits 1 before emitting a packet. An isolated offline reproduction confirmed this with empty stdout and AttributeError; no shared handler or hook configuration was changed.
- The additional-context arm was rejected as invalid. These failed attempts do not establish that a correctly formed replacement mechanism is impossible.
- The report transcribes the compact-replacement event digest incorrectly: the actual digest begins `66a010b3`, not `66a01001`. The complete verified digest is in receipt.json.

An unchanged commandExecution event emitted before the hook does not by itself prove that later model-facing messages are unchanged. Our earlier main-lane bridge emitted stopReason successfully but did not pass model marker/schema recognition. Together these results establish no working replacement path; they do not establish a universal impossibility result.

The handoff's command-wrapper alternative is consistent with the existing prototype: own process capture before output enters the native tool, retain exact raw streams, and return a compact packet with retrieval. That path should be evaluated as a distinct system intervention, not as successful native hook interception. Avoid another expensive large-output hook sweep: the existing failed-marker evidence already warrants focusing on the wrapper boundary unless the owner identifies a new supported contract.

No native model calls were made for this adjudication. Its offline reproduction only tests the concrete handler type error. Native token totals and configuration-restoration claims were not independently re-audited here. Original handoff files remain unchanged in their owner checkout. This is a research finding, not deployment approval or an 80% savings claim.
