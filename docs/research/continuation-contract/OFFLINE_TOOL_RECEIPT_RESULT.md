# Tool receipt blind spot: reproduced offline

OBSERVED with installed Codex 0.153.4, isolated credential-free Codex homes, loopback Responses provider, read-only sandbox and fixed synthetic output. Nine local response requests across five exploratory probes; **zero hosted model calls**. Production configuration was unchanged. Synthetic token counters are not economics evidence.

1. A successful fixed `printf` command appears as a completed command event in both CLI and app-server surfaces.
2. The same harmless command with a nonexistent working directory fails before process creation. App-server emits no completed command item, but its next outgoing request contains the exact custom tool call and error: process creation failed with OS error 2.
3. Ephemeral `thread/read` with `includeTurns` rejects history inspection; the installed `thread/items/list` returns unsupported. The first successful app-server probe therefore stopped during post-turn inspection; its successful command and original wire remain retained.
4. A persistent thread records the otherwise missing tool call and output in its raw rollout. The verified snapshot contains 34,074 bytes and one matched call/output pair, SHA256 `33f6a7223a2b5776eb55c01fbaaf072980be905848962e36451998077d63484f`.

The captured provider requests independently establish what was returned to the client and then supplied to the next model request. No real model was needed to discover this behavior.

## What this changes

The Luna V2 native control showed unmatched pre-tool hooks and a filesystem sandbox violation. This offline reproduction demonstrates why completed-command counts cannot explain every continuation. It does **not** prove that the native control attempted the same nonexistent-directory operation. Its exact command and failure remain UNKNOWN, because the original ephemeral stream did not retain them.

Do not attribute those extra segments to commentary, hidden reasoning or Engine discovery from command counts alone. Do not loosen sandbox restrictions. Do not retry V2 to overwrite its economic result.

`engine/output/observed_session.py` provides a versioned alternative for future research: persistent thread history, exact private raw capture after shutdown, thread binding, tool-call/output byte references, and detection of config.toml changes during a run. Existing frozen session code is untouched. Four offline tests cover preserved failed attempts, byte hashes, foreign/truncated history rejection, no-extra-inference capture and config drift.

The capture adds one logical read and one write of the raw rollout, plus an index. Full physical storage, SQLite, flush and metadata costs remain unmetered. Raw history must stay private and is not added to model context. The index is evidence metadata, not semantic authority. A config hash does not bind every referenced executable; future benchmark manifests must also pin applicable hook sources and runtime versions.

## Next research action

Use observed sessions in the next already-justified coding/retrieval qualification, with the same sandbox, tools and effort in both arms. Inspect exact failed calls before changing instructions or mechanisms. The unresolved economic goal remains 80/80 with capability/workflow parity across task families; this diagnostic only makes the next cost diagnosis reliable.
