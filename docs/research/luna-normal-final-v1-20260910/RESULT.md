# Luna High normal-final maintenance pair

## Terminal classification

**Finite capability checks passed; economics failed; Luna is not qualified for
75/75, 80/80, or release.** This is one fresh matched maintenance cell, not the
seven-cell cohort. The other six fixed cells remain missing.

The derivative was frozen at commit `44e5f62` from the existing normal-final
maintenance pilot. It used `gpt-5.6-luna` at High effort, the unchanged frozen
`luna-coding-v1-75` base, existing bound edit-tool mechanics and task-local
caller preparation. No new notation/language intervention was used. Both arms
kept ordinary tools, semantic review and model-authored final answers; no final
renderer, output cap or lower effort was used.

| Arm | Input | Cached | Uncached | Output | Reasoning | Other output | Segments | Raw tools | Failed commands |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Candidate | 161,167 | 128,768 | 32,399 | 3,574 | 2,033 | 1,541 | 6 | 5 | 1 |
| Control | 157,828 | 126,208 | 31,620 | 1,878 | 766 | 1,112 | 7 | 6 | 0 |

Candidate versus control savings were **−2.1156% input, −90.3088% output and
−2.4636% uncached input**. Output includes reported reasoning. The failed
candidate semantic probe and recovery are retained and charged; no retry was
hidden.

Both artifacts passed the existing **23 public/regression tests and 94-case
independent oracle**. All three previously observed semantic probe programs
were replayed on both fresh artifacts: **6/6 PASS**. Manual review confirms
model authorship, post-execution placement and truthful finite test/scope claims
for both finals. The candidate final has one configured-contract defect: its
Markdown link uses `file:///private/tmp/...` instead of the required absolute
filesystem target without `file:///`. The control final passes that formatting
check. The original candidate final is preserved; no caller rewrite or rerun was
performed.

The seven-cell inventory is intervals, dependencies, transactions, maintenance,
selection, cold recovery and W50. Only maintenance has a fresh native pair in
this lane; no seven-cell median or full capability/workflow parity claim is
made. Historical Luna W50 and coding receipts remain separate bounded evidence
and are not pooled here.

Sanitized counters, hashes, limits and paired final-contract status are in
[RELEASE_ARTIFACTS.json](RELEASE_ARTIFACTS.json) and
[FINAL_REVIEW.json](FINAL_REVIEW.json).
The exact model finals and source artifacts are in the `artifacts/` directory.
Private native rollout/config traces remain under the recorded run root and are
not published.
