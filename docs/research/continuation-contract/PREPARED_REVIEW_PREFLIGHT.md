# Prepared review evidence: research preflight v1

OBSERVED engineering result, not native model evidence or token savings.

`prepared_review.py` stages exact proposed source, contract and three existing
checkers in separate private directories, executes each once, retains raw stdout
and stderr, binds their hashes, and publishes a final receipt by atomic rename.
A failed/timed-out checker or detected file mutation stops subsequent checks.
An existing attempt directory is never reused or silently rerun. An interrupted
attempt has no usable READY receipt and requires inspection.

`validate` takes a caller-retained receipt digest and checks receipt identity,
current input roots, limited runtime identity, snapshot files and raw output hashes.
READY means these three mechanical checks passed on the recorded snapshot. It is
not semantic ACCEPT and does not publish the proposal to a working tree.

## Verification

Seven focused pytest cases pass: valid receipt/no rerun, stale original contract,
changed snapshot, altered output, altered receipt, failed checker and mutated input
(the parameterized tampering test contributes four cases).

Actual frozen Queue suites were then executed on two proposals:

| Proposal | All three checks | Independent semantic witness |
|---|---|---|
| Original valid | PASS | PASS |
| Known 4093-drop defect | PASS | FAIL |

Preparation took about0.302s /0.294s respectively; retained raw output278B each.
These single-run timings are not performance estimates. Explicit preparation file
reads54,390B /54,534B; snapshot writes33,066B /33,174B. Counts exclude interpreter
and checker I/O, validator reads, OS traffic, storage maintenance and model costs.
Do not present these as complete effective economics.

The negative row is an intentional trust-boundary test: a perfectly intact
mechanical receipt can describe semantically wrong code. This known development
mutant must not be represented as a future unseen safety case.

## Candidate boundary and remaining admission work

Caller prepares and validates evidence before inference. Astra receives exact
proposal and contract plus the limited completed-check statement; source/checker
files and ordinary tools stay available. Helix Context should require no new API
tutorial. Astra retains semantic acceptance, adequacy review and new test creation.
Nothing in this component grants automatic acceptance or restricts model tools.

Before native execution, freeze a prompt and driver that charge preparation,
validation and every model segment; bind all fixture/skill/driver hashes; and use
a fresh uncovered defect to test resistance to a misleading mechanical PASS.
Only a successful native semantic gate admits fresh paired economics. No model
call was launched in this preflight.

## Limits

Trusted local fixture only. This is not a sandbox against adversarial Python or
external side effects. Runtime identity includes Python version/platform/path,
not executable/library/environment dependency closure. Source observations before
and after execution cannot detect mutate-and-restore races. The snapshot captures
the bytes actually provided but live-source applicability can change after
validation; a future publication path must revalidate under its existing state
transaction. No production publication path is added here. A thrown exception
leaves the attempt unusable rather than triggering a retry. Hashes establish
identity, not semantic truth or authenticity without a trusted expected digest.

## Reproduce

`python3 -m pytest docs/research/continuation-contract/test_prepared_review.py -q`

`python3 docs/research/continuation-contract/prepared_review_preflight.py /path/to/native-prereview-pair-v1-20260909/on /new/output/path`

Machine result: `PREPARED_REVIEW_PREFLIGHT.json`.
Raw local evidence: `/Users/mert/Documents/ChatGPT/Helix/research/prepared-review-preflight-v1-20260909`.
