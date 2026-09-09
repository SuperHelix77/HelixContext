# Preserve JSON types at packet acceptance

An offline counterexample confirmed that the previous verifier accepted boolean `false` in place of an authoritative integer exit code `0`, because Python equality considers them equal. The same class of comparison affected nested values and zero omission counts.

The verifier now compares both recursive value and type for receipt metadata, raw references, projected counts and spans. Publication rejects boolean or negative expected revisions before acceptance. Corrupt candidates leave the accepted SQLite revision and object pointer unchanged.

Validation: 49 middleware tests pass. Seven added cases cover boolean/integer/float substitution, nested span identity, omission counts, and unchanged accepted state after rejected publication. The original counterexample was reproduced before the fix. No model calls were made.

This closes a concrete mechanical evidence-integrity defect. It is not semantic sufficiency, universal capability parity, or native token-saving evidence. Existing published benchmark receipts are unchanged.
