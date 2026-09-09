# Luna output rescue V2: one segment, rejected result

OBSERVED:22,813input/264output/12,829uncached input;187reasoning output is included
in264. One native turn and one model segment, no recorded hook events. Relative
to the previous persistent native control:97.89%input,58.81%output,72.57%uncached
savings. This is an adaptive candidate with a reused control, not a fresh pair.

The returned explanation correctly identifies violet and two required approvers.
However, selected sources `[17,1]` violate the declared later-source-wins contract.
Exact caller rendering produces amber instead of violet. The semantic checker
rejects it. No sorting or answer repair was applied retroactively. The apparent
savings are the costs of a **failing candidate**, not capability-preserving savings.

Explicit caller ownership plus minimal source-selection output removed the
visible three-segment setup pattern in this attempt. Which intervention caused
that difference is not isolated. The187reported reasoning-outputtokens already
exceed the128.2total-outputbudget. That is an observation, not a universal floor.

Both candidate attempts together cost92,450input/1,534output. Including control,
the research episode costs1,174,992input/2,175output. No failed-attempt cost erased.
Next user-authorized investigation: explicit source roles and bounded amendment
scope validation, rather than precedence hidden in list order. Not implemented as
production policy and not admitted by this failed run.
