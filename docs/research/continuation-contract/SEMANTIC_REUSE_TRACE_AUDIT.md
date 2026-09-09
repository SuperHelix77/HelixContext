# Exact semantic reuse: current trace opportunity census

OBSERVED:31terminal completed/closed research streams contain81native turn/start
requests. Two streams have multiple user turns. There are **zero exact repeated
requests within a thread**, and zero exact repeated signatures across threads.
One nonterminal protocol-preflight stream was excluded. No native call launched.

The signature preserves exact input content, attachments, tool output, model and
effort; only transport identity is excluded. This tests a necessary condition of
the proposed exact-request/full-bound-world cache. Even a matching request would
still need unchanged evidence, authority, obligations and accepted prior results.
No matching request was found, so no further cache eligibility can be established
for this corpus. Paths, request/status hashes, turn signatures and native hash
verification coverage are retained in the JSON; raw prompt contents are not public.

**Verdict: do not build or benchmark an exact-request cache as the next80/80
attack on these workloads.** It has no observed hit opportunity here. The proposed
78.07%avoidance requirement has no empirical support in these traces. This is not
a universal rejection of caches or semantic reuse in other workloads.

Scope limits: current local app-server research receipts only, not all user
projects or historical CLI episodes. Independent benchmark repetitions are not
eligible workflow cache hits. Different text may be semantically equivalent,
but proving that safely is a separate unresolved problem. Internal model/tool
segments are not new user requests, so this audit does not measure duplicated
reasoning within a turn or deterministic sub-work that could be delegated.

Next-search constraint: investigate a measured internal/procedural cost term or
an independently selected workload with actual repeated semantic work. Do not
manufacture duplicate requests, normalize away changed requirements, or discard
new evidence to create a savings denominator. Preserve source authority and
required semantic review. Existing Luna V3 output remains64.43%on a post-hoc
recovered development candidate, not80%or general capability qualification.

Reproduce: `semantic_reuse_trace_audit.py <local-research-root> <output.json>`.
