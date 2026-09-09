# Renderer versus efficient ordinary file copying

This prospective pilot gives each of Luna High, Sol High and Astra High the same record-selection and exact-file-delivery task, with one ordinary arm and one renderer arm. Both can use Python and normal file copying. Both must deliver `result.jsonl`, leave the input unchanged and finish with `DONE`; neither is required to reproduce the artifact in chat.

The model selects the latest published record per group, then applies strict JSON boolean eligibility and expiry. It preserves the original selected JSONL bytes. The renderer arm writes selected IDs and calls a provided deterministic assembly helper. The helper resolves IDs to immutable hash-bound ranges but does not choose eligibility. The ordinary arm performs its own efficient processing and verification.

The expected 21,539-byte artifact was frozen before execution. Independent explicit selected-group checks were run before freezing. The model does not receive the oracle artifact hash or selected groups in its prompt. Raw sources remain available in both arms.

## Limits

This is one assembly task per model, not the requested complete multi-task quality/workflow gate. Eligibility values do not vary across revisions within a group, so this fixture cannot expose every incorrect fallback-to-older-revision implementation. It is not a full semantic test of that rule. It also does not test native compaction, delayed relevance, failed publication recovery or repeated trials. Those limitations cannot be repaired by a passing artifact hash.

The driver and dependency hashes are archived, but the relative native harness imports refer to the original workspace layout. These are audit sources, not a standalone reproduction package. Exact usage and per-arm artifact/source checks are in `results.json`. Private raw traces are represented by hash commitments; account and environment context are excluded.

Native input/output includes all calls in each arm. Renderer counters expose source-object and destination application bytes. Preprocessing for both arms, Python interpreter startup, filesystem metadata, physical storage, remote compute and parent research costs are not fully priced. No dollar-saving claim follows from the token table.

## Measured outcome

| Model / High | Input off → on | Input savings | Output off → on | Output savings | Scored checks |
|---|---:|---:|---:|---:|---|
| Luna | 297,228 → 218,350 | 26.5% | 6,410 → 4,620 | 27.9% | Both passed |
| Sol | 58,386 → 113,760 | **−94.8%** | 1,636 → 1,857 | **−13.5%** | Both passed |
| Astra | 43,710 → 82,703 | **−89.2%** | 673 → 850 | **−26.3%** | Both passed |

All six artifacts matched the frozen bytes, sources remained unchanged, and final answers were DONE. The renderer is **not admitted as a general token-saving strategy**: Sol and Astra regress, and no model reaches 80% input/output savings. Luna's ordinary run dumped large source regions and repeated checks; its relative gain is not evidence against a consistently optimized ordinary implementation. One paired run does not establish stability.

These six calls consumed 814,137 input tokens and 16,046 output tokens. Together with the preceding two diagnostic pilots, the 18 native calls consumed **1,376,398 input and 24,919 output tokens**. These figures include rejected candidates and the diagnostic evaluator mistake. Earlier research and parent coordination remain additional costs. No research break-even or dollar-saving claim is made.

A future iteration should move identity checks and final byte validation into deterministic caller-owned operations, retain semantic selection with the model, and compare the whole resulting workflow against efficient ordinary controls. Passing byte-copy tests alone is insufficient for admission.
