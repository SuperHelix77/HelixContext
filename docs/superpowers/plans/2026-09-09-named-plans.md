# Named Plans Implementation Plan

> Execute inline using executing-plans and test-driven-development; no additional model agents are needed for this bounded implementation.

**Goal:** Implement the five approved requirements without claiming model-token savings.
**Architecture:** Content-addressed manifests + immutable (id,version) registration; snapshot-based checked execution; SQLite success pointer committed only after final validation. Failed attempts retain independent receipts. Cost vectors and strict break-even arithmetic preserve unknown measurements.
**Tech Stack:** Python standard library, existing evidence/checked-step engine, SQLite, pytest.

**Follow-on integration:** [Skill entry point and Huashu HUD requirements](../specs/2026-09-09-hud-and-skill-integration.md). Freeze execution/accounting telemetry before HUD implementation; maintain both skill-only and skill-plus-engine optimization lanes.

## Task 1 — identity and dependencies
- [ ] Add `engine/prototype/test_named_plans.py` tests that register a valid plan, reject a changed plan under the same identity, detect tampered manifests and changed input/config/schema/executable/environment, and preserve version references.
- [ ] Run `python3 -m pytest -q engine/prototype/test_named_plans.py`; verify missing API assertion fails.
- [ ] Implement `named_plans.py` register/load/invoke and dependency helper module `plan_dependencies.py`. `register` returns `{plan_id,plan_version,plan_hash}`. Validate entire steps list before executing any step. Hash-only environment values in stored manifests.

## Task 2 — TOCTOU and publication
- [ ] Test a step that modifies an original bound file between steps: expect FAILED, no next-step side effect, and unchanged last-success pointer.
- [ ] Test source write/restore, snapshot mutation, nonzero step, timeout, environment isolation, and successful exact snapshot output.
- [ ] Reuse `checked_steps.execute` for each step, add optional explicit `env` propagation to existing APIs. Verify snapshots and original stamps around steps. Insert attempt receipt and update last-success pointer in one SQLite transaction only when every step and final validation pass. Never mark semantic correctness from exit status alone.

## Task 3 — accounting and delivery
- [ ] Add `plan_costs.py` and tests: `break_even(10,5,3)` is 6 for strict positive benefit; equal/negative recurring benefit has no finite break-even; unknown input stays unknown. Use Decimal and reject invalid/negative values.
- [ ] Record creation, validation, snapshot copying, execution and publication costs in their own phases; native token costs remain unknown unless supplied from actual receipts.
- [ ] Run all prototype tests, inspect diff for boundaries and stale-state failures, document CLI/API and limits. Commit and publish only explicit feature files; preserve coordinator files. Do not start native benchmarks.

## Completion checks
- [ ] Every approved addition maps to tests and documented boundaries.
- [ ] No claim that ordinary copy scripts or model reasoning are superseded.
- [ ] No new native model calls, hook writes or installed skill modifications.
