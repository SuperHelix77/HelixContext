# Helix Engine0.1.0-preview.1

This release ships a local evidence console and the existing deterministic Engine primitives. It does **not** qualify a general savings policy for Luna, Sol or Astra. Selected development pairs preserve finite checks and complete model-written final answers. The required seven-cell medians, independent holdout capability and normal desktop pre-inference integration remain unqualified.

## Run

Requires Python3.10+ and `curl` for current official prices. No model credentials, Node installation, inference call or Codex configuration change is required to view the console.

```sh
python3 helix_hud.py
```

Open `http://127.0.0.1:8769/`. The packaged view starts with genuine published evidence capsules and no registered live runs. It never invents live telemetry. To observe your own registered runs:

```sh
python3 helix_hud.py --config /absolute/path/config.json --port 8769
```

See `engine/hud/README.md` for registration fields. The default data directory is `~/.helix/hud`; `--data-dir` selects another directory. Stop with Ctrl-C. Removing that data directory removes local observer history; it does not remove research artifacts or change Codex. A port conflict exits without terminating another process.

## What ships

- Responsive release console; model/task filtering, current-price paired comparisons, cost frontier, live execution events, explicit missing metrics, stale-data signals and public evidence export.
- Research ledger retained at `/research`; native hashes, usage, failed attempts, coordinator costs, scoped medians and exact receipt drill-down.
- Python Engine sources for durable evidence, memory, typed reduction, checked publication, plans, completion ledger and semantic reentry. These are explicit-call primitives; they do not automatically intercept the Codex app.
- Current Helix Context skill source for supported installation through Codex. The skill cannot eliminate a model call before it begins. No experimental profile is silently installed.

Run primitive help with `python3 engine/prototype/evidence.py --help` or `python3 engine/prototype/plan_cli.py --help`. Read `engine/README.md` and the relevant primitive contract before routing work. Internal exact rendering is not permission to replace the user's model-written final answer.

## Evidence contract

Capsule hashes bind the published data. Native raw evidence was audited locally; public extracts are not independent provider attestations. Every displayed comparison uses its own same-model/effort control. Different policies, task types and efforts are not pooled into a release median. Historical source-only or caller-rendered finals remain separate from the current contract.

The current-price source is official OpenAI pricing. It refreshes every120seconds and expires after300seconds; schema changes or expiry withhold costs. Short/long are separate tariff scenarios. API-equivalent savings are not included-plan quota, actual invoices or total effective cost. Unpriced Engine/recovery/storage/research overhead stays unknown. The UI's frontier uses finite task gates, not a fabricated intelligence score.

## Integration boundary

The caller binds task state, policy/version, evidence and authorized operations before a semantic turn. Helix Context supplies concise operational guidance. Engine performs only mechanically entailed work, preserves exact cold evidence and returns checked deltas. The model retains interpretation, semantic adequacy, unresolved obligations, ordinary tools and final authorship. Stale authority or conflicting execution requires recovery/reentry; optional memory failure may fall back to ordinary context. No automatic universal task classifier is released here.

The normal Codex desktop still needs a supported pre-inference lifecycle attachment to reproduce the largest ACK-elimination wins. This preview makes that boundary explicit rather than presenting a research caller as installed desktop behavior.
