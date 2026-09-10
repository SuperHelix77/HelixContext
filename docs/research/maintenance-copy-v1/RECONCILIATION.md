# Post-publication observer stop: narrow offline reconciliation

Original experiment and all native receipts remain unchanged. Frozen commit:
`edc77d5`; manifest: `d6d16686ce678041b14532627667a322fb28e3110ada07f6e2f5efa38fe2f5cc`.

Both arms completed one native user turn and passed the public/regression and
independent oracle checks. Candidate publication then succeeded. The final scope
checker rejected `workflow_memory.py.helix-lock`, an empty untracked file created
by the already-frozen `renderer.publish`. Its advisory lock is intentionally
persistent. The runner allowed only a modified target and forgot its own metadata.
Original state remains `STOPPED_PENDING_AUDIT`; no clean frozen-protocol PASS.

`reconcile.py` is an explicit derivative of the frozen `audit.py`. It preserves
all source hashes, native counter reconciliation, raw identities, effective High
settings, base/skill attachment, exact reconstruction and independent regrading.
Its only scope amendment admits that exact zero-byte regular lock file in the
candidate directory, alongside the expected target modification. It additionally
requires zero candidate raw tool calls, exactly one candidate turn, a successful
retained publication receipt and a matching final source hash. Other file drift,
nonempty/symlink lock, missing publication or another stop cause is rejected.

Two row fields lost after the stop are recovered from retained evidence: source
identity and object-store counters from the publication receipt. Candidate elapsed
time comes from the closed native-session receipt; it excludes construction setup
and is labelled accordingly. This does not invent an absent original timer value.

The auditor writes new `reconciled-audit.json` / `RECONCILED_RESULT.json` and new
check logs. It never changes `results.json`, native status, prompts, task artifacts,
the frozen manifest, runner, or original auditor. No new inference or model repair
is authorized by this amendment. Paired economics, if validated, are a recovered
bounded development result, with this protocol defect disclosed.

The future caller must declare its own publication metadata before execution.
This recovery does not turn the current research caller into a production release.
