# Native middleware pilots: mixed results

These prospective pilots compare ordinary source-file inspection against the same access plus a verified, partial pytest evidence packet. Both arms use identical native model/High settings and tools. No ordinary arm is forced to load the complete log into its prompt. Missing evidence must be recovered from the original file. This tests packet-assisted diagnosis, not automatic tool interception or the whole Helix skill.

## Corrected V2 results

| Model (High) | Input off → on | Input saving | Output off → on | Output saving | Exact-answer / source-integrity checks |
|---|---:|---:|---:|---:|---|
| Luna | 56,170 → 60,034 | **−6.9%** | 724 → 1,275 | **−76.1%** | Both passed |
| Sol | 62,402 → 28,771 | 53.9% | 611 → 496 | 18.8% | Both passed |
| Astra | 44,286 → 30,191 | 31.8% | 213 → 141 | 33.8% | Both passed |

One fresh diagnostic task per model, one observation per arm. This does not establish three-task, repair, long-horizon or general capability parity. No model reaches 80% input and output savings here. Luna regresses in both components. This candidate is not admitted as a general efficiency improvement.

The fixture includes exact numeric strings, JSON boolean/string distinctions, early configuration facts, and a primary failure beyond the reducer's bounded diagnostic list. The original file stays available. Both arms must return the same complete answer, including facts absent from the packet.

## Preserved evaluator failure

V1's prompt requested primary failures with expected/observed evidence, but its frozen equality grader expected only name strings. All six V1 outputs were marked false by that inconsistent grader. V1 remains preserved with its costs; it is not a clean quality gate. V2 fixes the array schema explicitly and changes decisive fixture values before execution. V2 is a prospective correction, not an independent broad holdout.

## Accounting and reproducibility

Both pilots together consumed **562,261 native input tokens and 8,873 output tokens across 12 calls**, including the invalid-grader V1. Cached input and reasoning output are subsets. `ACCOUNTING.json` and per-version `results.json` retain exact usage, elapsed native time, source integrity, generated answers, application preprocessing byte counters and private raw-trace hash commitments.

Each on arm reads roughly 899 KB, writes 449 KB of content-addressed objects and hashes 1.35 MB during packet creation and verification. The original source file is also retained. These byte counts are not dollar costs. Parent coordination, earlier research, index experiments, preprocessing wall time, physical disk allocation and remote compute are outside this pilot accounting, not free.

The original driver and frozen dependency hashes are archived per version. Their relative imports refer to the original workspace harness, so these snapshots are audit sources rather than a portable one-command reproduction package. Raw native traces and account/environment context are intentionally excluded from this public artifact. `../../benchmarks/frozen-high/` contains the earlier native harness sources; current middleware sources are in `../prototype/`.

## Next acceptance gate

Improve the integrated strategy and test fresh tasks against efficient ordinary controls before adoption. Preserve exact recovery, required verification and complete answers. Include diagnosis, actual repair and delayed-relevance workflow tasks for each requested model. Require each model's measured input and output gains separately; aggregate wins cannot hide Luna's regression. Full recurring accounting and independent repeats remain necessary.
