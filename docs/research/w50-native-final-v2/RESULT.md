# Astra High W50 V2: full native final survives; output target does not

**OBSERVED:** one fresh, preregistered on/off pair preserves the exact 49 ACKs,
recovers every raw event and produces a correct, complete model-written final in
both arms. Candidate uses one model turn and no tools. Total input saving is
**98.32%**, uncached input **72.71%**, and output **49.62%**. This is a useful scoped
state-transition result, not 80/80, a seven-task median or a model release.

Run date:2026-09-10. Model:`gpt-6-astra`, **High** in both arms. Original client
base, current Helix skill, ordinary tools and semantic authority remain available.
Engine is active in both arms; control is ordinary continuation, not pristine
Codex. Order was frozen **on then off**. No native retry, final repair, schema
shortening, effort reduction or post-result prompt change occurred.

## Measured pair

| Measure | Ordinary control | Helix | Saving |
|---|---:|---:|---:|
| Input |1,193,197|20,099|98.32%|
| Cached input, subset of input |1,145,344|7,040|99.39%|
| Uncached input |47,853|13,059|72.71%|
| Output, including reported reasoning |528|266|49.62%|
| Reported reasoning, subset of output |34|70|−105.88%|
| Model turns / segments |50/50|1/1|98% fewer|
| Model tool calls |0|0|—|
| Arm elapsed time, including caller work |175.227s|11.858s|93.23%|

Both final answers say one violet approver is insufficient. Both preserve two
approvers, the original nonce, the exact decimal and large-integer strings, and
the E17 group amendment. Both explicitly reject E31's untrusted override. Final
answers are byte-identical to the native final-message artifacts; Engine did not
write or rewrite them. See [control](artifacts/off-final.txt) and
[candidate](artifacts/on-final.txt).

The candidate also emitted a brief skill-use announcement. That visible prose,
its full final, and 70 reported reasoning tokens are all charged. No claim is made
about the content or purpose of private reasoning.

## What this changes about semantic emulation

**STRENGTHENED, narrowly:** caller-owned transitions can remove calls whose result
is already specified. The model still makes the unresolved policy judgment. This
experiment does not implement cheaper latent reasoning or emulate Astra semantics.

**OBSERVED output residual:** the control spent 343 output tokens on49 ACKs and 185
on its final semantic turn. Candidate spent 266 on its sole semantic turn:81 more
than the control's final. Reported reasoning accounts for 36 of that numerical
difference; other output accounts for 45. This is arithmetic, not causal attribution.

At this control denominator, an 80%-saving output budget is 105.6 tokens and a 65%
budget is 184.8. Even replacing the candidate's entire final-turn cost with the
observed 185-token control final would yield 64.96% output savings. Artificially
deleting all 70 reported candidate reasoning tokens while holding everything else
fixed yields 62.88%. Neither manipulation is an implemented intervention, a lower
bound, or permission to suppress reasoning. Different trajectories could differ.

The full requested answer is doing useful work. There is no extra candidate
model segment, tool discovery, generated integration code or redundant execution
left to delete. It is unjustified to buy another generic preparation/compression
run to attack this residual. XHigh remains **unmeasured under V2**; its prospective
follow-up is not launched because High has not passed the output economic gate.
This does not establish an XHigh failure or impossibility.

## Capability and evidence boundary

**Finite checks PASS:** exact 49 ACK strings, all 49 events recovered through a
reopened ledger,49 unique delivery identities, same history hash and ledger root
in both arms, unchanged history after inference, complete final schema and exact
values, native final authorship, correct authority/amendment/vendor interpretation,
bound inputs/config/skill, and all native usage increments/raw capture hashes.

The delivery layer recorded 49 **offered** receipts. External consumer ACK and
end-to-end desktop delivery were not established. This known fixture is exposed;
it is not a new latent-future-relevance holdout, general coding test, compaction
test or independent replication. Mechanical checks do not prove universal parity.

## Hidden costs kept visible

Current official Standard API rates were fetched at
**2026-09-10T08:50:20.276467+00:00**. The dated short-context scenario gives
control **$1.650274** and candidate **$0.150930**, or **90.85% API-equivalent saving**.
The long-context scenario gives **$3.287348→$0.295210**, or **91.02%**. These are
separate tariff scenarios, not observed Codex quota, invoices or all-in ROI.
Source:[official pricing](https://developers.openai.com/api/docs/pricing.md).
The HUD continues to refresh live rates; the research snapshot stays dated.

| Caller/Engine measure | Control | Candidate |
|---|---:|---:|
| Object bytes read |1,198,072|1,182,208|
| Object bytes written |60,089|60,089|
| Object bytes hashed |1,274,025|1,242,297|
| Object reads |2,695|2,646|
| Cumulative history bytes written |453,894|453,894|
| History guard bytes read |907,788|36,236|
| Raw capture bytes read and separately written |541,058 each|79,196 each|
| Memory recall elapsed, initial plus final |0.3931s|0.3779s|
| Raw memory recall response bytes |44,065|44,063|

Preparation before the native session was 0.1667s control / 0.3463s candidate;
manifest preparation was 0.1426s. The recall totals include the final recall as
well; these timers overlap other elapsed measures and must not be blindly added.
Both recall stages returned no matching task-scoped memories. Out-of-scope records
were excluded from injection, so this is not a measured persistent-memory-reuse win.

Completion verification still rereads the prefix: approximately quadratic work
over a growing episode. These49 events are cheap in wall time, but there is no
claim that the algorithm scales linearly. Exact recovery remains intact. Full
physical SQLite/filesystem traffic, storage service internals, model-side reasoning
compute, research/coordinator usage and total project cost remain unmeasured.
Post-run audit reads are separately recorded in [AUDIT.json](AUDIT.json).

This pair consumed **1,213,296 input /794 output** tokens in total. The stopped V1
attempt remains **40,413 input /15 output** additionally, with no candidate and no
savings estimate. Together these two attempts consumed **1,253,709 input /809
output**; this is not the total Helix research bill. V1 is never substituted as a
cheaper denominator or removed from the failure record.

## Decision

- Freeze this **artifact/result**, not Astra as a qualified model.
- Retain the scoped input/cost win; label output 49.62%, not65/65 or80/80.
- V2 High cohort is **1/7**; six cells missing and release median **unknown**.
- Do not change the production base, reasoning effort or global config.
- Do not self-apply the W50 caller as a general semantic gate. The current
  coordinator has no validated pre-inference integration for arbitrary user events.
- Keep genuine semantic work in Astra. Reuse only established, dependency-bound
  decisions; failures or new/unknown semantic obligations retain model access.

The architecture supported by this result is **avoid unnecessary semantic
invocations**, not **simulate unresolved semantics for free**. The earlier
[research audit](../SEMANTIC_EMULATION_AUDIT_20260910.md) remains applicable on that
distinction. Its historical experiment pause was superseded by
[RESUMPTION.md](RESUMPTION.md), before this frozen run.

Receipts: [machine result](RESULT.json), [read-only audit](AUDIT.json),
[semantic review](SEMANTIC_REVIEW.json), [preregistration](PREREG.md),
[offline gates](OFFLINE.json), [zero-call preflight](PREFLIGHT.json).
