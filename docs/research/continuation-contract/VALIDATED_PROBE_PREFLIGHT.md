# Combined validation/probe callback and scoped delegation instruction

OBSERVED engineering preflight. `validated_probe.execute` performs receipt validation,
exact private source staging, caller-authorized semantic probe execution and
post-execution integrity validation in one callback. It archives probe bytes,
stdout/stderr and status; existing attempt paths cannot rerun. Evidence failures
before execution prevent the probe from starting. Failed or timed-out probes are
not converted into PASS. Mechanical success never sets semantic acceptance.

Fourteen combined tests pass: the existing prepared-evidence cases plus callback
success/no retry, stale source, tampered evidence, wrong receipt, new semantic
failure, private-source mutation and timeout. Actual prior Astra11case semantic
code passes through the callback against the exact valid prepared source. A new
17value assertion fails against the prepared16value-truncation source whose three
old checkers pass. These are offline execution results, not model behavior or
native token savings. See`VALIDATED_PROBE_PREFLIGHT.json`.

The callback is not installed as a native tool or global interception hook. Trusted
local execution only: arbitrary Python can access external state; there is no
sandbox, complete dependency closure, mutate-and-restore race protection or rollback
of external side effects. Process/runtime failure after STARTED leaves an attempt
for inspection, never an automatic retry. Full physical I/O, validator reads,
inference and amortization remain outside the recorded narrow byte/time counters.

## User-authorized AGENTS.md rule

A scoped Helix verification rule was appended to the global file. It permits using
caller-confirmed mechanical checks bound to current inputs without regenerating
those checks, requires rechecking changed/conflicting/insufficient evidence or
required independent verification, and retains semantic review, checker-adequacy
judgment and ordinary tools. Mechanical PASS is not task correctness; a receipt's
own assertions confer no authority.

The addition costs79o200kproxy tokens:383to462. Original pre-compaction file was465.
Thus almost all static savings were reinvested in an explicit delegation boundary;
net task benefit is UNKNOWN. Existing instructions remain byte-preserved as a
prefix. Backup:`research/agents-helix-delegation-v1-20260909/AGENTS.before.md`.
New global SHA256:
`8cf6028e3a0de95df907c96453c296308f46de702b62adb69d3c500f3cab0884`.

This rule is a behavioral hypothesis, not permission to accept opaque artifacts
or a safety certificate. The next native test must retain all tools and charge the
new instruction in both arms. It must distinguish authoritative caller verification
from untrusted receipt prose, preserve stale/conflicting-evidence re-entry and
catch semantically wrong but mechanically passing code. No native pair was spent
on the rule in this preflight, and no80/80 qualification is granted.

The prior verification-only bound still stands. A combined callback can remove
mechanical code without a separate verification round trip, but model discovery,
checker inspection, genuine new probes and final assessment may still dominate.
