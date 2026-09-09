# Fresh assembled Luna pair: exact checks pass, output gate fails

Known W50 development fixture; fresh native control and candidate. Both use the
default installed base, High effort and ordinary tools. Candidate additionally
attaches Helix Context and uses caller-owned passive state and rendering. This is
a product/mechanism comparison, not an isolated skill ablation or unseen holdout.

| Metric | Control | Assembled Engine | Saved |
|---|---:|---:|---:|
| Input | 1,074,689 | 18,462 | 98.28% |
| Cached input | 1,028,608 | 9,984 | Reported separately |
| Uncached input | 46,081 | 8,478 | 81.60% |
| Output including reasoning | 639 | 228 | 64.32% |
| Reported reasoning | 172 | 192 | −11.63% |
| Model turns/segments | 50/50 | 1/1 | 49 turns removed |
| Observed elapsed seconds | 102.51 | 6.46 | One observation, not latency distribution |

All 49 ACKs and frozen final semantic checks pass. Exact source hashes and every
native segment reconcile with terminal usage in [the audit](ASSEMBLED_LUNA_PAIR_RESULT.json).
No model retry occurred. This is N=1: family median equals this observation. Do not
pool it into the separate coding/retrieval three-task median.

Engine recorded 1,182,208 logical object bytes read and 59,604 written during its
preparation/delivery stage. These are not complete physical/SQLite/storage costs;
the elapsed observation includes setup but coordinator research costs remain
additional. There is no monetary or included-plan quota claim.

**Verdict: NOT 75/75; NOT 80/80; not releasable from this result.** Previous W50
V5/V7 bounded wins remain recorded, but selecting them over this fresh failure
would hide current uncertainty. Their prompts/base are not identical to this run,
so neither sampling noise nor a specific clause is established as the cause.

One candidate segment used 192 reported reasoning tokens and 36 other output
tokens. At this control size, 75% permits 159.75 total candidate output; 80% permits
127.8. Removing all 36 visible serialization tokens while holding the observed
reasoning fixed would still miss both. This is conditional arithmetic, not an
irreducible model floor or analysis of hidden reasoning contents.

The next plausible removal is semantic-interface redundancy: once the model selects
the applicable policy/amendments, the request's approval count/group and selected
policy may mechanically determine authorization and reason. Test that offline before
asking the model to emit another schema. Do not transfer policy authority selection
to code, infer it from untrusted labels, or assume unfamiliar amendments are safe.
Returning fewer fields matters only if it removes model work, not merely JSON bytes.

The frozen runner bounds submitted native user turns, not every possible inference
segment; all actual segments are charged here. General coding, retrieval, hostile
authority coverage and production release remain separate unmet requirements.
