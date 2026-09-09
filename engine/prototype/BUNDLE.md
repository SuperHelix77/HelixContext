# Atomic evidence and artifact bundles

`bundle.commit(store, name, candidate, copy_plan, expected_revision)` verifies the evidence packet, assembles the exact artifact, checks that copy references belong to the packet's stdout/stderr evidence, and stores both in cold content-addressed storage. One SQLite transaction advances the named bundle pointer using revision comparison. A failed verification, copy, or stale revision never advances that pointer.

`bundle.load(store, name)` reads the canonical bundle, verifies its packet against the retained source, and hash-checks the artifact. It rejects corrupted evidence rather than silently using a stale projection. Byte strings retain exact numeric spelling and line endings.

This API addresses a composition gap: separate atomic packet and file publications do not constitute one atomic workflow update. The canonical artifact here is the content-addressed object referenced by the bundle. Export to a mutable filesystem path remains a separate operation; do not claim two-file transactionality. The prior standalone packet/file APIs remain available and are not silently synchronized with bundles.

Validation: 56 middleware tests passed. Seven integration cases cover capture → batch retrieval → rendering → restart, failed late copy, unbound source, stale revision, type substitution, corrupted source, and two writers competing for the same revision. Only one concurrent writer advances the pointer. These are deterministic component/integration tests, not model capability or native-token benchmarks.

Costs and limits: full source verification and assembly are charged in the existing store counters; output bytes are stored as an additional object. Failed commits may leave unused cold objects, which are not accepted workflow state and still cost storage. SQLite/OS metadata, physical disk traffic, CPU and remote inference remain separate unmetered categories. No hostile same-user writer or power-loss durability guarantee is made. Literal output and source selection still require semantic validation by the caller. No model calls, hook changes or installed-skill changes were made.
