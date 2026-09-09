# Luna V7: base-only intervention

OBSERVED: one fresh Luna High candidate with the compact delegation base completed
in one segment, preserving all 49 ACKs, exact final fields, selected authority and
the independent rejection-reason check. Its task prompt is byte-identical to V5.
No tool/effort reduction, schema change or native retry occurred.

| | Original W50 control | V5 | V7 |
|---|---:|---:|---:|
| Input | 1,082,542 | 18,439 | 15,905 |
| Output including reasoning | 641 | 160 | 156 |
| Uncached input | 46,766 | 8,455 | 10,017 |
| Reported reasoning output | 169 | 124 | 120 |

V7 saves 98.53% total input, 75.66% output and 78.58% uncached input against the
reused original control. It does not achieve 80/80. V5 remains better on uncached
input; V7 is not universally superior. Single-run cache differences and adaptive
development selection prohibit a monetary or quota conclusion.

INFERRED: the client base intervention reduced supplied text but did not materially
reduce this task's output. Non-reasoning output remained 36 tokens. This does not
prove a reasoning floor: reported counts vary, and no hidden reasoning is analyzed.
Conditionally holding the observed 120 reasoning tokens fixed would leave only
eight tokens for all other output at an 80% target. That arithmetic rules out
expecting large gains from ordinary JSON whitespace cleanup on this observation;
it is not an information-theoretic lower bound.

The existing V5/V7 renderer is scoped to the known policy schema and one amendment
scope. It cannot be advertised as general agent execution. Positive authorization
is deliberately unresolved by the independent negative-reason checker. Ordinary
tools are available, but the benchmark runner does not yet demonstrate successful
semantic re-entry after an unsupported renderer decision. Those are qualification
obligations, not permission to suppress difficult tasks.

Next qualification must cover actual code repair with preserved user files,
semantic selection with exact data and hostile notes, and delayed relevance with
exact recovery. Use fresh paired receipts and same task-specific base in both arms
for Engine attribution; separately report a complete native-product comparison if
the base differs. Existing frozen tasks can serve as development regressions, not
unseen holdouts. Unsupported cells must visibly use ordinary execution; zero
savings there must remain in the result. No further final-format-only sampling.

Public evidence: [JSON](LUNA_KERNEL_V7_RESULT.json), `luna_kernel_v7_audit.py`.
Local raw evidence: `research/native-luna-base-v7-20260909`. Complete task, history,
base, driver and native-stream hashes are bound. Capability/agentic parity and
the original three-model, three-task qualification remain incomplete.
