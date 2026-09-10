# Reuse the witness mechanics; keep probe choice with Astra

2026-09-10. Offline research only. The last goal turn was progress: it closed a
new native falsifier and changed which composition should receive further work.
The 80/80 goal, capability-first priority, seven-task scope and full model-written
final-answer requirement remain unchanged.

## Measured residual and proposed change

The resident-evidence hostile run retained four segments and 2,343 output tokens.
Its third segment generated one Python witness and cost 861 output, of which
240 was reported reasoning. We cannot label the remaining 621 tokens entirely
removable code, nor delete the entire segment: it included a new semantic choice.
The source is now exact, inspected evidence at commit `787b5b4`.

Can a caller reuse those exact mechanics on a newly model-chosen query, instead
of requiring another program to set up stores, loop over modes and render results?
The smallest candidate is a qualified parameterization of the already executed
program. It changes only its five query literals. No generated control flow,
semantic approval, model-facing plan discovery or new memory tier is needed.

Astra still chooses the query, judges whether this finite procedure applies,
interprets its results, constructs different probes when needed, and writes the
ordinary final review after evidence. The caller binds the original task/reference,
candidate, evidence module, program, executor and Python runtime. It owns copying
inputs into a disposable test directory, executing the exact parameterized
procedure once, and retaining raw stdout/stderr and code. It cannot infer a new
semantic decision from a successful process exit.

The existing `dynamic_tool_rpc` transport could eventually expose one ordinary
internal tool taking a query string. That is an integration possibility, not a
native test authorized here. No global config, skill or production tool changes.

## Authority and known limitations

This witness compares a small synthetic corpus, three scenarios, default/all/any
calls and trailing-whitespace controls. It applies only to the frozen search
compatibility task and old reference. It is not a generic test generator or proof
of arbitrary search equivalence. Candidate changes are tested inputs; task or
reference changes need a new semantic qualification, even with fresh hashes.
The method is differential/metamorphic reuse under the sources already read in
[the earlier design](../differential-obligations-v1/DESIGN.md); those papers do not
validate Helix economics. No new claim about hosted-model latent computation.

Parameterization must use parsed string-token positions and safe literal encoding,
never executable string interpolation. All non-query source bytes remain exact.
The byte-bound original program has already been inspected; arbitrary scripts or
input paths are not accepted through the prospective model interface. Ordinary
tools remain available for unsupported scenarios. This offline runner executes
trusted research modules; it is not a sandbox for malicious Python candidates.

Raw process observations are evidence, not PASS/FAIL semantic verdicts. If a bound
file changes, Python fails, output is malformed, or binding cannot be revalidated,
retain failure evidence and publish no valid observation receipt. Never rerun a
failed command automatically. Disposable synthetic stores are regenerated from
the retained exact program and query; this is not a production state-recovery test.

## Offline falsifiers, fixed before execution

1. Original query: parameterized code must be byte-identical to the native program
   and reproduce its nine failures and nine controls on the defective source.
2. The valid candidate must produce zero failures and nine controls.
3. Fresh query literals: `alpha`, `café`, `other evidence`, a quote-bearing string,
   and a code-looking string. Bind matching query-specific source variants before
   running. The procedure must catch the corresponding early return without
   executing query text. Queries not targeting a variant must remain clean.
4. A changed task/reference with fresh hashes still rejects. Stale candidate or
   executor binding rejects before execution; drift observed after execution
   publishes no success. Interrupted/duplicate starts never invoke twice.
5. Process failures and non-observation output stay failures, not empty success.

These are constructed/exposed calibration checks, not held-out capability cases.
Measure serialized request, schema/description and original command byte/token
proxies separately, plus setup, execution and retained evidence. Use native
segment counters only for explicitly conditional arithmetic. No old unrelated
control is a measured denominator. If this cannot plausibly remove a material
task-level term after its admission tax, do not spend a native benchmark on it.
