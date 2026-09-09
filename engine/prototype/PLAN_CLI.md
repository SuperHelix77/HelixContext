# Explicit skill-to-plan bridge

Development interface, not installed as a hook or automatic Helix policy.
`plan_cli.py` connects a caller such as Helix Context to named plans without
requiring it to generate Python glue, transcribe hashes or inspect helper modules
on every invocation. Bootstrap discovery still costs tokens and must be measured.

## Registration and invocation

Write a JSON spec with `plan_id`, positive integer `plan_version`, absolute `cwd`,
`steps` (name + argv), `files` (relative path → input/script/schema/config role),
`executables` (argv alias → absolute executable path), and optional `env_names`.
Environment values come from the calling process and are bound by hashes. Do not
place secrets in the spec. Register does not execute the steps.

```sh
python3 engine/prototype/plan_cli.py --store /absolute/evidence-store register /absolute/spec.json > /absolute/reference.json
python3 engine/prototype/plan_cli.py --store /absolute/evidence-store run /absolute/reference.json
```

Inspect the registration exit status before using its output as a reference.
References bind an immutable identity/version/hash; do not overwrite a prior
reference as an implicit update. Use a separate filename for a new version.

Run returns step receipt IDs, exit codes, workspace and aggregate status. Exit 0
means accepted process/integrity success, with semantic success explicitly null.
Exit 1 means a failed attempt; exit 2 means an invalid request or retrieval error.
CLI argument syntax errors use argparse's ordinary stderr/exit behavior.

Exact step stdout/stderr remain in the evidence store; expand them using the
existing evidence retrieval API/CLI. Full attempt and accounting details:

```sh
python3 engine/prototype/plan_cli.py --store /absolute/evidence-store receipt SHA256_FROM_DETAILS
```

The details object preserves the returned post-commit accounting in a separate
envelope. Envelope publication and physical I/O remain excluded, explicitly. The
envelope does not change acceptance or establish complete cost accounting.

## Helix Context caller contract

Give the skill a caller-owned engine path, evidence-store path and frozen plan
reference. The agent decides whether the task and authority actually match the
plan before invoking it. Keep this information in the existing workflow capsule;
avoid another registry or repeated helper discovery. A receipt reports process
results; the agent still checks the requested artifact and semantic obligations.

Do not auto-rerun a failed plan natively: inspect the completed steps and existing
side effects before deciding how to recover. Native fallback is safe before any
execution when applicability is unsupported; it is not a universal retry policy.
Do not remove required checks to shorten the invocation or final answer.

No installed skill changes occur in this increment. The interface is ready for a
controlled caller, but general activation remains gated by the unresolved ctime
rejection, isolation limits and native input/output cost evidence.

## Qualification and next experiment

The full prototype suite passes 113 tests including CLI subprocess tests. A
single-step compact response is checked below 1,800 UTF-8 bytes; that is a bounded
packet fixture assertion, not a tokenizer or whole-task savings measurement.

Before native runs, freeze a reuse experiment with identical semantic tasks and
ordinary scripts available to both arms. Include registration/skill bootstrap,
full tool receipts, retries and artifact verification in native usage totals.
Vary reuse count rather than repeating unrelated tiny tasks. Report per-model
input and output savings separately, and keep source-change recovery and later
evidence retrieval as workflow gates. A command-length saving alone cannot admit
the mechanism. Do not launch a full model sweep while correctness gates remain open.
