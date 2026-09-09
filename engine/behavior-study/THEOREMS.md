# Behavioral study: conditional propositions, audits, then implementation

Evidence: twelve existing native episodes, renderer and query V2, Luna/Sol/Astra at High. Exact trace hashes and usage are in observations.json. This study runs no models. These are newly formulated Helix contracts built from elementary mathematics, not claims of novel mathematical discoveries or universal intelligence preservation.

## Observation versus internal explanation

Astra renderer-off used two command calls; renderer-on used four, including reading helper implementations. The helper changed its visible execution plan, adding setup work. The trace does not reveal whether uncertainty, instruction-following, familiarity, or another internal cause motivated this inspection.

Luna renderer-off used ten commands and included two failed hash checks inside command calls whose aggregate exit was zero. Its generated expected digest omitted the final character. One visible explanation attributed an assertion failure to newlines instead. The later correct check and final exact artifact demonstrate recovery; they do not validate that intermediate explanation. The on arm also attempted a git check outside a repository. These are observed episodes, not stable personality traits.

Sol query V2 used three commands off and one on; Luna used one in both arms. One policy's result therefore depends on the control's visible execution plan. Across these few exposed tasks, no causal model-specific treatment effect or general reasoning-capability ranking is identified. Reasoning-token counts quantify a reported usage subset; they do not expose internal algorithms or establish the quality of reasoning.

## Proposition 1: compound savings require a joint cost boundary

Assume a fixed baseline cost represented by nonnegative weights w(e) over distinct events E. Intervention i removes a set S_i without altering surviving events. Let H be all added cost of the joint intervention. Then joint net saving in cost units is

G = sum_{e in union(S_i)} w(e) - H.

Proof: partition baseline events into removed and surviving sets; subtract surviving cost plus H from baseline. Each removed event appears once in the partition. Summing individual removals instead overcounts intersections. If the interventions change the trajectory, costs or quality, these premises fail and the formula cannot substitute for measuring the joint run.

Audit counterexample: two mechanisms each remove the same event of cost 60 from a baseline of 100. They save 60, not 120, before overhead. If joint overhead is 70, they lose 10. Consequence: do not combine typed and lexical log projections just by adding their separate percentages. Combine only identified distinct costs, and measure interaction/recovery overhead.

## Proposition 2: aggregate success cannot certify required substeps

For n>=2 arbitrary commands in a shell sequence whose reported status is the last command's status, the mapping from status vector to reported status is non-injective. Vectors (1,0) and (0,0) both map to 0. Therefore aggregate status 0 alone cannot establish that every mandatory command succeeded.

A checked sequence that records each individual status and terminates at the first nonzero status returns success if and only if every scheduled mandatory step ran and returned zero, provided execution terminates and status capture is faithful. Proof: induction on the sequence length; the first nonzero step prevents the success terminal state. This proves process-status conjunction only, not semantic correctness: a broken checker can still exit zero.

Audit: Luna's renderer-off commands 6 and 8 returned zero while their captured text contained AssertionError and source hash mismatch, respectively. These are direct counterexamples to trusting the aggregate shell status as verification success. Exact traces bind the claim; narration is not used as the grader.

Implementation justified: an opt-in sequence executor with explicit argv steps, individual raw receipts, and stop-on-failure semantics. Do not parse arbitrary shell programs or reinterpret expected nonzero results. An embedded shell chain remains opaque and is explicitly outside the guarantee. This should reduce masked failures and misleading recovery decisions; token savings remain a hypothesis.

## Proposition 3: observed totals do not identify internal cause

If an observation function maps two distinct latent execution mechanisms to the same observable record, no rule using only that record can uniquely distinguish those mechanisms. Proof: the rule has the same input in both cases and hence cannot output a distinct correct identity for both.

Here aggregate input/output counts and CLI command traces omit per-inference model-facing context and latent activations. Multiple allocations of setup, repeated context, and internal processing are compatible with them. Thus a specific subsurface causal explanation is not established. This does not imply all internal questions are unknowable; stronger measurements or controlled interventions can distinguish particular hypotheses.

## Model-specific hypotheses and falsifiers

- Luna: transcription and verification repair can dominate exact-copy work. Hypothesis: mechanically checked source identity and explicit step statuses reduce repair loops. Falsified on held-out tasks if repairs or complete costs do not decrease, or any required check is lost.
- Sol: reducing duplicated discovery/verification calls may help when the baseline uses multiple calls. Hypothesis must be tested against efficient one-call controls too. A win confined to unusually expensive controls is insufficient for routing.
- Astra: helper discovery can outweigh deterministic copy benefits. Hypothesis: a stable, already-validated execution interface helps only when its amortized discovery cost is below the avoided work. It must retain necessary verification and semantic selection. Ordinary copying remains the comparator.

These are candidate explanations, not deployed model traits. First audit deterministic contracts; later freeze a bounded, matched, model-specific joint experiment on fresh Q/A/W variants. No new native calls are authorized by this document alone. Luna owns interception. No hooks are changed here.
