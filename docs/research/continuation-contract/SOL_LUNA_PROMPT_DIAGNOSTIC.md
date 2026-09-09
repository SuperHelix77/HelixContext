# Sol/Luna prompt anatomy: local diagnostics, no inference

OBSERVED: current `codex debug models` gives **byte-identical Sol and Luna base
instructions**:17,766UTF-8bytes /3,552o200k_base proxytokens. SHA256:
`a91357a1cd2727a0be06d461248d6e3a7274746e38108f548a3adf2cc2430415`.
For each model, `base_instructions` equals `instructions_template`; count once,
not twice. The inspected tool mode, shell type, skill/plugin/app-instruction flags,
default verbosity and Responses-lite metadata also match. This does not establish
identical weights, reasoning behavior, all backend instructions or complete requests.

Four fresh `debug prompt-input` reconstructions use the exact frozen SolV3 off/on
prompt texts and task directories, High effort, skill limit512, approvalnever and
workspace-write. Both text prompts were checked byte-for-byte against the original
native `turn/start` requests. Each model receives the same task for this comparison;
there is no conversation replay or new model inference. Luna here is a renderer
comparison, not a new execution of the Sol task.

| Reconstructed component (proxy tokens) | Native task | Helix task |
|---|---:|---:|
| Skill instructions/catalog block |853|854|
| Permission block |145|145|
| Connector block |146|146|
| Plugin instructions |209|209|
| Recommended plugin inventory |1,329|1,329|
| AGENTS block including wrapper/other context |631|631|
| Environment |326|326|
| Exact task text |1,141|1,879|
| **Sum of input-text blocks** |**4,780**|**5,519**|

These values are identical for Sol and Luna. Textbytes17,106native /19,437Helix.
The739proxy-token difference is738tasktext plus1skillcatalogblock. The rest is
shared within this reconstruction:3,639/3,640proxy tokens excluding the task.
The present globalAGENTS file occurs exactly once in each list:2,246bytes /
462proxy tokens. It is a subset of the631AGENTSblock, not an additional charge.

The317proxy-token Helix skill body is measured separately. Its exact body is
absent from the diagnostic lists. Original native off input was text-only; on was
text plus explicit skill input. `debug prompt-input` cannot reproduce that skill
input attachment. Therefore317is a standalone size, not an observed additive
attachment cost. Likewise the3,552catalog base is absent as exact text from the
input list: do not sum the two artifacts into a claimed native total.

## Ownership and unknowns

- Platform/model-owned: catalog base and runtime instruction/tool surfaces. No
  system text changed, no tools disabled, no inference/reasoning settings reduced.
- User/workspace controlled: global/projectAGENTS, Helix skill, task construction,
  caller-owned state and invocation placement.
- Native tools/schemas: **UNKNOWN** from this diagnostic. Tool metadata is not the
  serialized tool definitions. No caller-added tool cost is inferred from it.
- Backend/platform remainder, token framing, actual native tokenizer, repeated
  serialization and cache treatment: **UNKNOWN** here. The diagnostic is not the
  complete transmitted request. Fresh reconstruction does not establish a billed
  first-turn or irreducible floor.

The recommended-plugin block is a visible shared component. Its size alone does
not justify deleting capabilities or claim a supported deferral setting. This
request changes neither plugins nor platform instructions.

## Architectural implication

INFERRED: different catalog base wording is not supported as the explanation for
Sol/Luna's observed behavior differences. The prompt renderer likewise shows no
model-specific size difference on this controlled task. Model-specific behavior
must be investigated through actual execution and interface responses, without
claiming access to hidden reasoning.

Helix's controlled prompt currently **adds**739proxy tokens before considering
explicit skill attachment. Sol's earlier gain therefore came despite this visible
admission tax, consistent with removing later model interactions and caller-owned
mechanics. This diagnostic alone does not establish causality or the unobserved
native floor. Shaving this prompt cannot be credited with removing the entire
17–20k native first segment.

Design Sol around one semantic decision where warranted, caller-owned registration,
exact execution and reporting, and re-entry on genuinely unresolved/new semantic
information. Preserve task authority and ordinary recovery. Bound and attach
state before invocation; avoid reintroducing full setup instructions on each
continuation. A future experiment must compare total/uncached/output separately
and charge all preparation and failed attempts. No new native re-attack is admitted
merely by these proxy sizes; no80/80 or capability claim follows.

Raw catalog and reconstructed instructions remain local under
`research/sol-luna-prompt-diagnostic-v1-20260909`; public JSON contains sizes, hashes,
component occurrences and explicit limits. Reproduce using
`sol_luna_prompt_diagnostic.py <new-local-output-root> <metrics.json>`.
