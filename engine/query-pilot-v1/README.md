# Request-conditioned exact-line pilot V1

Six native calls, fresh off/on controls, one exposed development task per model at High reasoning. All six exact-answer and unchanged-source checks passed. These are bounded task outcomes, not evidence of universal intelligence or workflow parity.

| Model | Input saved | Output saved |
|---|---:|---:|
| luna | 22.3% | 26.7% |
| sol | -2.3% | 21.6% |
| astra | 26.6% | 34.9% |

Total experiment usage: 239,555 input and 3,312 output tokens. Cached input and reasoning output are subsets, not additional charges. Parent work is additional and unmetered here.

The compiler matched literal request terms to original lines before inference. The 448,928-byte source produced a 1,258-byte JSON view with 13 matching lines. This payload ratio is not native token savings. Original source remained available for fallback. The compiler uses no expected-answer input.

Observed weakness: compound request identifiers such as cursor_expected do not match the separate word cursor. The projection missed required lines; the models retrieved raw evidence. The next candidate should test compound-identifier segmentation under a new version, preserving these results.

Three deterministic compiler tests passed. Model receipts were checked against exact native event hashes and usage records. Raw traces remain private. pilot.py is an archival driver requiring the original workspace layout and its shared helix-frontier runner, not a standalone installed tool; query.py tests can run locally with pytest. The dependency hash was recorded after execution, so this is not a final evaluator-closure claim.

No hooks or installed skills were changed. The 80% native input/output target remains unmet.
