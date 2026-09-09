# Real same-thread exception recovery

**OBSERVED: one bounded native recovery passed. No paired savings claim.**

Prospectively committed driver `2151481`, manifest SHA256
`8ea94ed0189725f9acf192ecb77f32e3b5707fbcf47632ffc45981f7fe90b95c`.
One actual app-server thread, two `gpt-6-astra` High turns, ordinary tools available,
no retries. The skill was registered and explicitly attached before the first turn.
The second turn carried Engine results as tool output in the same thread.

## What happened

1. Astra reviewed the original proposal and accepted it for contract v1, identifying
   assumptions, expected checks and limitations. It did not claim execution.
2. Before Engine execution, the caller applied a frozen authoritative amendment:
   batches now contain at most two values; oversized rejection must preserve state.
3. The old state reference was refused before a check process or attempt reservation.
4. The caller delivered the version delta to the same Astra thread. Astra explicitly
   invalidated its earlier acceptance and returned a revised complete module.
5. Exact returned bytes passed the amended checker and cross-instance checker.
   The independent caller replay also passed. No reference repair was shown to Astra.

This was a deliberately injected development amendment, not an external production
incident. The revised candidate remains AWAITING_REVIEW in the research gate; no
automatic-closure policy was activated or qualified by this test.

## Actual native token accounting

| Turn | Input | Output | Cached input | Uncached input |
|---|---:|---:|---:|---:|
| Initial semantic assessment | 19,405 | 376 | 11,264 | 8,141 |
| Amendment recovery | 20,952 | 406 | 19,200 | 1,752 |
| **Whole session** | **40,357** | **782** | **30,464** | **9,893** |

Reported reasoning is a subset of output: 128 initial + 97 recovery = 225 total.
There were **zero model-issued commands**. All current-turn deltas summed exactly
to final thread cumulative usage. Raw wire and normalized event hashes matched.
Requests prove one thread/start and two turn/start calls to the same thread ID;
only the first attached the skill. The final cumulative total is counted once.

The absence of a second skill attachment does not prove restoration after
compaction or restart; neither occurred. This test does not measure such recovery.
Caller setup, validation, storage and recovery operations remain separately
recorded; complete physical/SQLite/interpreter costs and billing are not certified.

## Independent correctness checks

- Old proposal failed the v2 size constraint during preflight; an offline reference
  repair passed. That reference stayed outside the model's task evidence.
- Returned source bytes matched the staged candidate exactly.
- Staged contract and checker matched the frozen v2 authority.
- Amended finite oracle: 2,745 sequences / 8,282 transitions, plus explicit oversized
  rejection, state preservation, valid two-value batch and empty-batch recovery.
- Cross-instance oracle: 1,000 sequences / 3,000 transitions.
- Stale attempt never reserved, and no automatic replay occurred.

These finite checks support this specific repair and recovery; they do not prove
universal intelligence or workflow parity. Grading included reading the actual
assessment and revision, not treating a JSON decision alone as semantic success.

## Architectural implication

**STRENGTHENED, bounded:** semantic reconsideration can use an explicit changed
contract in the same thread without model-generated execution scaffolding or
rereading Engine implementation. The first proposal did not remain silently
accepted after authority changed. This qualifies the live continuation transport
for this run and preserves observed recovery cost.

**UNKNOWN:** whether pre-execution self-review detects the same defects as matched
post-execution review, whether unexpected check failures receive equally adequate
recovery, and whether ordinary no-change closure is safe. This run required a
changed obligation and does not establish that the no-change path needs no review.

Next: a matched review-timing comparison with identical task evidence and explicit
semantic challenges. Do not compare this 40,357-token recovery session against an
old different native task to manufacture 80% savings. The requested representative
model/task matrix, latent-future relevance and no-loss qualification remain open.

Machine result: `NATIVE_RECOVERY_RESULT.json`. Local raw receipts:
`/Users/mert/Documents/ChatGPT/Helix/research/native-recovery-v1-20260909`.
HUD uses a labelled terminal-status projection with unchanged counters/event
hashes and a hash of the original session status; the native source is retained.
