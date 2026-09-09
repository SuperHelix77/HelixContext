# Verified named-plan reuse: approved design, experimental implementation

Status: user approved the design and five additions below. A partial experimental implementation exists; full isolation, complete accounting and performance admission remain open. See `engine/prototype/NAMED_PLANS_STATUS.md` from the repository root.

## Requirements and context

Preserve capability, agency and workflow before maximizing native input/output savings. Existing traces show command/hash transcription mistakes, helper discovery costs, repeated checks and large baseline variation. The fixed-first-call audit rules out post-tool-only achievement of 80% on its small fixture. Named plans are a candidate for reducing initial command-generation and repeated setup, not a demonstrated solution to the whole objective.

Existing components: immutable evidence objects, explicit checked argv steps, typed packet verification, exact retrieval, and atomic evidence/artifact bundles. Reuse these; add no shell parser, model router, background daemon or hook. Luna's interception work remains independently owned.

## Alternatives considered

1. Named immutable checked plans (recommended): predeclared steps and dependencies, compact invocation by a stable plan reference; pays setup once and revalidates applicability. Expected advantage only for repeated applicable work.
2. Generated commands every time: best for one-off or changed tasks; retains current ordinary fallback and has no plan-registration overhead.
3. Automatic learned workflow caching: potentially broader reuse but needs semantic applicability inference and stale-state handling not justified by current evidence. Excluded.

## Contract

The caller supplies a plan containing explicit step names/argv, a declared working directory, and a map of required input paths to exact content digests. Plan registration stores canonical bytes as a content-addressed object. Registration is not permission to execute; caller authorization must already cover every step.

Invocation supplies the immutable plan reference. The runner verifies the plan object, validates all fields, and checks every declared input before any step executes. A mismatch stops the invocation and requires ordinary task reassessment; there is no silent replacement of a plan version. Inputs/commands are not interpolated from arbitrary free text. Initial version has no dynamic parameters or mutable name aliases.

On passing preflight, the existing checked-step executor runs mandatory steps, preserving each raw receipt and stopping at the first unsuccessful process. Return a compact sequence reference and explicit terminal status. Semantic success remains determined by the task checker, not process exit alone.

Declared input checks cover their read-time state only. They do not pin undeclared imports, executable transitive dependencies, network state, external services, or mutable files after the check. No concurrent-writer isolation or universal replay-equivalence claim is made. Tasks requiring those guarantees are outside admission until an isolated snapshot runner exists.

No changes to global skills, hooks, tool permissions or project instructions. No plan is executed merely because it was discovered in source content.

## Conditional benefit and falsifier

Let P be one-time plan creation/registration cost, V the per-invocation validation cost, B ordinary command-generation/setup cost, and K the number of applicable invocations. Under equal semantic outcomes, equal remaining execution costs, and stable applicability, net gain is K*(B-V)-P. Positive gain requires B>V and K>P/(B-V). These quantities must be measured in the same units; input and output are assessed separately. This algebra is not empirical identification of the costs.

Falsifiers: setup/validation consumes the avoided generation budget; agents inspect the whole helper implementation on every use; changes frequently invalidate applicability; any required check or obligation disappears; baseline already reuses equally efficient ordinary scripts. In those cases retain ordinary execution. Never restrict the control's scripting/reuse abilities to manufacture a win.

## Offline acceptance before native spending

- Tampered plan object rejected.
- Invalid later step rejected before earlier side effects.
- Changed declared input rejected before any process.
- Authorized valid plan reproduces exact per-step outputs and process statuses.
- Nonzero/timeout stops subsequent steps and preserves receipts.
- A checker that exits zero despite semantic failure is not promoted to semantic PASS.
- Cost receipt includes plan bytes, all input verification bytes and sequence overhead.

## Native experiment gate

Do not launch a full model sweep automatically. First establish a concrete repeated workload and compare with an efficient reusable-script control. Freeze per-model candidate, task variants, Q/A/W checks, call budget and stop rule. Include plan setup, discovery, all invocations, invalidation and fallback. No 80% claim unless actual cumulative input and output meet it with the required capability evidence.

## Self-review

- Scope: one optional plan indirection over the existing executor.
- Dependency boundary: explicitly declared inputs only; no false transitive closure claim.
- Authorization: existing task authorization remains required.
- Semantics: no automatic capability/parity inference from process success.
- Accounting: amortization conditional; no measured benefit yet.
- Implementation: intentionally pending design approval.

## Approved additions — supersedes prior pending status and weaker dependency checks

User approved with five mandatory additions: explicit plan_id/version/hash; feasible dependency closure; TOCTOU protection; transactional successful receipts with separate failed evidence; amortization accounting.

Implementation binds declared file roles (input/script/schema/config), executable paths and content, relevant environment names and value hashes, source-directory identity, and Helix runner module hashes. Declared files execute from per-invocation copies. Source and snapshot fingerprints are checked at launch boundaries and again before success publication. A normal concurrent edit, including write-then-restore with changed ctime/inode, invalidates the invocation. No success pointer moves on a detected race. Steps must use declared relative paths in the snapshot; arbitrary host access is not sandbox-enforced. The guarantee therefore excludes hostile same-user tampering and undeclared dependencies, which must remain explicit rather than being called complete closure. External side effects are not rolled back.

The process environment is an explicit dictionary of declared variables only. Executable binaries are hash-bound and revalidated; shared libraries and OS runtime are outside complete closure. No native model experiment or global installation follows automatically.
