# Arena Astra boundary attack: adjudication against newer native evidence

## Provenance and evidence ordering

**EXTERNAL:** read the complete `ARENA_ASTRA_BOUNDARY_ATTACK_DOSSIER.md` and intake
README from GitHub branch `research/council-intake-20260909`, pinned at
`a9704ff5652f1cd7c32d8c51bc8a1e5751510818`. Dossier introduction commit:
`c41d140544e5f46a7ca109bb2de0f647dee9a0ad`; dossier SHA256:
`665afb79a9edb8709f76123befa4e1360a47a931565b8b40636d27d7e5e14146`.
No checkout switch or merge occurred.

The researcher had no GitHub access, ran no native benchmarks, and used no external
sources. This is independent architectural criticism based on a supplied brief,
not empirical replication. Its recent publication date must not be confused with
its evidence cut: its numeric brief omits the newer caller-patch coding pairs and
publication fault audit. Current receipts remain authoritative.

[Dossier at pinned commit](https://github.com/SuperHelix77/HelixContext/blob/a9704ff5652f1cd7c32d8c51bc8a1e5751510818/docs/research-council/2026-09-09/ARENA_ASTRA_BOUNDARY_ATTACK_DOSSIER.md)

## The substantive disagreement

Arena prefers **B: Astra patch decision → caller apply/check → Astra semantic
review**. Our recent caller-patch experiments instead exercised a restricted
**C: prior semantic assessment → exact caller application/checks → completion**.
These are different intervention boundaries. Successful C fixture runs do not
measure the safety or cost of B, and must not be described as having retained a
post-execution Astra review opportunity.

The earlier council synthesis favored exception-only re-entry as a hypothesis.
Arena identifies its missing burden of proof: a clean mechanical result may still
benefit from reconsideration of changed code, test adequacy or unexpected context.
An empty unresolved list before execution does not prove no later semantic issue
can arise. Conversely, the dossier does not prove every successful deterministic
execution requires another model turn. That is precisely the unmeasured question.

## Reconciliation

| Arena position | Newer evidence | Current verdict |
|---|---|---|
| Transfer fixed mechanics to caller | Astra caller patch V1: 101,159→19,940 input, 1,135→387 output; V2: 101,113→20,038 and 955→507. Both candidate arms used zero commands and passed finite checks. | **STRENGTHENED**, bounded coding evidence |
| Never treat mechanical PASS as semantic proof | Earlier receipt pilot elicited a real alias-state counterexample; expected ACCEPT was unsound/ambiguous. | **STRENGTHENED**; discovery occurred during review, not proof about timing |
| Preserve post-execution semantic review | Caller-patch trials had no candidate post-execution model turn; tests and matching repair ASTs do not establish no-loss from omitting it. | **UNTESTED necessity; conservative next-test requirement** |
| Reject stale dependencies and unsafe retries | Frozen caller stage can miss a contract change during checking and overwrite an intervening write; failed checks leave proposed source installed. | **STRENGTHENED** by offline injected faults, not observed native incidents |
| Small familiar receipts rather than new abstraction | Report V2 did not reduce candidate output; output rose 387→507 across separate runs. | **CONDITIONAL**; no causal proof from separate pairs |
| Custom harness saving is not native-skill deployability | Registration and execution were supplied by our app-server harness; ordinary installed-skill batching/deployment is not qualified by those receipts. | **SURVIVES** |
| Autonomous repair generation remains missing | Newer coding arms generated their own repairs from broken code, without a supplied reference repair; both repair AST pairs match. | **SUPERSEDED for this bounded fixture only** |
| Do not blame all regression on bootstrap or source rereads | Catalog already requested at 512; novel semantic tests occupied substantial visible command output. | **STRENGTHENED** |

## What changes now

**INFERRED:** preserve a post-execution Astra review opportunity in the next matched
boundary test. Treat C as an unqualified conditional optimization, not the default
architecture for general coding. This is a change in research priority; no runtime,
Engine, skill, router or model configuration was changed by this intake.

Before that native test, close or explicitly exclude unsupported publication races
at the deterministic boundary. A final review cannot undo a lost concurrent edit
or a duplicated side effect. Review is complementary to immutable staging,
validated authority, atomic publication and reconciliation—not a replacement for
those requirements.

The smallest testable host capability is one **apply-and-check** composite operation
returning an exact diff, actual results, remaining obligations and retrieval handles
to the ongoing model turn. Astra then accepts or repairs. Test the interface the
installed skill can really invoke; do not assume a custom callback is transparently
available in the normal application. Keep tools, High reasoning, complete task and
semantic review opportunity equivalent in the A/B pair.

The earlier stale challenge explicitly announced a mismatch, which is appropriate
for a deterministic preflight but does not test independent stale detection by
Astra. New adverse cases need neutral identifiers and a clear distinction between
preflight-detected faults and faults Astra is expected to discover semantically.
No adverse case may be averaged into the valid-pair savings denominator.

## Economics must include the retained review

The newer caller-patch candidates each used approximately 20k input in one segment.
A second similarly sized segment would make the illustrative candidate roughly
40k input against a roughly 101k control—about 60% savings, not 80%. This is
**CONDITIONAL illustration**, not a measured B result or a fixed model floor.
The actual continuation size, tool exposure and cached/uncached split are unknown.

Do not omit review to rescue the headline without evidence of safety. Do not pad
the native baseline with needless separate commands to pay for it. The 80/80 goal
remains; a lower-cost boundary must earn it while retaining necessary semantics.
Output savings remain below target, and reporting-wording optimization is stopped.

## Decision

**MODIFY THE NEXT FALSIFIER, NOT THE CURRENT IMPLEMENTATION.** Arena's most useful
contribution is the precise disagreement over who closes the task after execution.
The new evidence supports caller-owned mechanics but leaves that closure decision
unqualified. Preserve review in the next boundary comparison, separately test
publication/recovery, and measure the full cost. No new model calls were made for
this adjudication, and the research intake branch was not merged.
