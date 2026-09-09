# Explicit input rebinding for reusable procedures

`rebind_inputs(store, reference, new_version)` creates a new immutable named-plan
version using current bytes for files already declared as `input`. It preserves
the fixed contract: plan identity, input names/roles, steps, scripts, schemas,
configuration, executable bindings, environment and working-directory assumptions.
The new manifest binds its parent reference. Existing versions remain unchanged.

The operation checks fixed dependencies before registration and compares the new
manifest against the old fixed contract afterward. Normal registration also
revalidates before publication. A changed script during input loading is rejected;
it cannot be silently accepted as part of the new procedure. Existing host-wide
TOCTOU limitations and ctime-only false invalidations remain unresolved.

This saves the caller from reconstructing the full registration specification
when only declared data changes. It does not infer semantic applicability, relax
step checks, execute automatically or authorize a new task. The caller decides
that the existing procedure is appropriate for the new input.

```sh
python3 engine/prototype/plan_cli.py --store /absolute/store \
  rebind-inputs /absolute/plan-v1.json 2 > /absolute/plan-v2.json
```

Check successful exit before invoking the new reference with the existing `run`
command. A failed registration's stdout is an error receipt, not a valid plan
reference. Use a new reference filename; do not overwrite the old version.

Rebinding validation time and object traffic are recorded separately under
`creation_cost(...)["rebind_preflight"]`; ordinary registration costs remain in
their existing fields. Sum both phases for comparison. Complete physical I/O,
failed-registration and final-publication accounting remains unfinished. Fewer
model-generated setup bytes are a hypothesis, not a measured native saving.

Seven new tests cover changed data with exact output, unchanged old manifests,
changed script/config/schema/environment rejection, version rejection, a logic
change during registration and CLI creation without execution. Full suite:
**154 passed**. No native call or installed skill/hook change accompanied this
increment. The 80% joint target and general no-loss claim remain open.
