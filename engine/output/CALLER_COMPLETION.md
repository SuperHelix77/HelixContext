# Caller-side completion with immutable source selections

Status: implemented offline mechanism; native savings and capability parity
unmeasured. This extends the existing exact-copy renderer and the prior ID-based
render pilot. ID selection itself is not new, and that pilot regressed Sol/Astra.

The change is the placement of the mechanical work. Previously the model wrote
an ID file, invoked a helper, inspected its output, and generated completion.
With a participating caller, the model returns its semantic selection once.
The caller parses that exact response and performs checked assembly, retaining
the response hash and exact artifact receipt. Routine success need not generate
another model turn; failed selection or publication is returned for normal
recovery, whose tokens must be counted. This is not installed Codex interception.

## API and authority

`copy_handles.freeze(store, mapping)` accepts caller-owned handles mapped to
exact source hashes and half-open byte ranges. It validates all source bytes and
ranges, then publishes an immutable catalog and metered creation receipt.
`complete_response(store, pinned_reference, model_response, destination, ...)`
accepts a JSON list of existing handles and explicit UTF-8 literals. It resolves
operations through the pinned catalog and uses the existing checked renderer.

The catalog reference stays caller-owned. A model response cannot choose another
catalog, a filesystem source path or executable expression. Unknown handles,
invalid JSON, duplicate literal keys and corrupt sources fail explicitly.
Existing output is unchanged if validation fails. Publication retains the
renderer’s cooperative-lock limitations; it is not hostile-writer isolation.
New catalogs get new references; old references still select the old exact
version. The caller must choose the currently applicable generation explicitly.

Handle mapping must be derived without duplicate source identities and verified
against the exact source. A source ID or literal containing instructions remains
data. Selection correctness is the agent’s semantic responsibility; the engine
receipt deliberately leaves `semantic_success` unknown.

Example of model-generated response: `["r-04-2","r-07-2"]`. The caller already
holds the catalog reference and output destination. No source hash, output path,
Python imports, helper discovery or reference-file generation is needed in that
response. Raw evidence must still be available if semantic metadata is
insufficient. Skipping evidence needed for selection is not an optimization.

## Audited proposition

For a fixed valid catalog C and a selection S whose handles are all defined,
let E(C,S) replace each handle with its exact range operation and preserve literal
operations. Then `assemble_handles(C,S) = assemble(E(C,S))` byte-for-byte.
Proof: expansion preserves operation order and values; both sides invoke the
same exact renderer. Duplicated selections deliberately duplicate bytes.

This is substitution correctness, not a new information-theory result, proof of
semantic selection quality, or token-saving theorem. Omitted source verification,
stale catalogs or missing evidence would violate its assumptions.

## Offline result and hidden-cost rejection

The exposed Sol render fixture has 72 records and nine selected records. Both
catalog strategies reproduce its **21,539-byte artifact exactly**.

| Representation | Selection payload tokens | Additional alias legend |
|---|---:|---:|
| Existing compact record IDs | 55 | 0 |
| New numeric aliases | 19 | 649 if injected |
| Caller completion with original IDs | 55 | 0 if IDs already in evidence |

The verbose range plan is 463 payload tokens, but using that as the only baseline
would exaggerate progress: the old native pilot already used 55-token IDs.
Numeric aliases save 36 selection tokens while potentially adding 649 input
tokens. **Do not admit numeric recoding for one use.** Retain original IDs; test
the removed model-side execution and bookkeeping instead. Catalog construction,
each catalog/source read, output writes and recovery remain additional costs.

`COPY_HANDLES_REPLAY.json` contains object I/O, hashes and local timings; these
are offline application measurements, not native-token or billing results.
`replay_copy_handles.py` reproduces the comparison from retained local artifacts.
The whole library test run is **177 passed**. Eighteen new tests cover 40 ordered
selections plus literals, binary bytes, duplicates, generation changes, tampering,
limits, malformed responses and publication failure. These tests do not ask a
model to discover the correct selection or a fact with latent future relevance.

## Next native contract

Freeze a fresh task with adequate complete semantic evidence, raw recovery,
changed revision eligibility (including no fallback to an older record), strict
booleans and exact output bytes. Give the ordinary control efficient scripting.
The candidate pays for caller preprocessing and gets no gold selection or gold
artifact digest. It emits selected original IDs; the caller validates assembly
and delivers the artifact. Include correction turns and independently grade
semantic eligibility and all source-preservation obligations.

Do not reuse the historical Sol/Astra regressions as controls for this new
interface. Do not start a matrix on payload arithmetic. First establish a bounded
native pair under one frozen model-specific policy and state the uncertainty.
