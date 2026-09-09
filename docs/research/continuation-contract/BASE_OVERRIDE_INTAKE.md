# Base override and quota claims: current-source adjudication

The setting exists. The [official configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference)
documents `model_instructions_file` as a built-in instruction replacement.
Our earlier blanket treatment of all client base text as non-configurable was
too broad. This does not establish replacement of server-owned instructions.

Transport matters: [Codex issue38355](https://github.com/openai/codex/issues/38355)
reports that custom instructions become additive developer content under Responses
Lite. This is an external bug report, not local service verification. The current
[upstream client implementation](https://raw.githubusercontent.com/openai/codex/main/codex-rs/core/src/client.rs)
places instruction fragments in the input on the Lite branch and uses the top-level
instructions field otherwise. Source inspection corroborates the different
serialization path; it does not reveal service-side instructions or establish that
upstream main exactly matches our installed binary. No transport toggle was changed.

Current local catalog: Sol/Luna3,552base proxy tokens each; Astra4,110. All three
have `use_responses_lite=true`. Six local prompt-input reconstructions, with/without
an isolated benign marker file override, show no marker and unchanged text-list
sizes: Sol/Luna3,193; Astra3,087. The diagnostic omits this layer, so these observations
prove neither successful replacement nor an ignored configuration. There were
zero native inference calls and no global configuration edits. Raw diagnostics
remain local in `research/base-override-diagnostic-v1-20260909`.

Before building a500–1000token kernel, verify actual replacement/serialization on
the installed native route. A smaller additive file may increase cost. Do not
force a transport change without tool/recovery parity checks. Do not use model
self-report about hidden instructions as proof. Once the boundary is verified,
map operational invariants before compression and test a2x2design: ordinary/kernel
base crossed with native/Helix execution. Same-base pairs isolate Engine benefit;
deployment comparison may include both, labelled explicitly.

## Credit equivalents versus included quota

The [current official rate card](https://help.openai.com/en/articles/11481834)
lists Luna5uncached/0.5cached/30outputcredits per milliontokens. Applied to the recorded
counters, V3 yields0.770948control versus0.076057candidate:90.1345%weighted savings.
V5 yields0.052067candidate:93.2464%weighted savings. These are calculated credit
**equivalents**, not observed debits or total research economics. V3 also required
post-hoc schema recovery; its comparison reused the original control.

[Personal-plan credit guidance](https://help.openai.com/en/articles/12642688-using-credits-for-flexible-usage-in-chatgpt-free-go-plus-pro-sora)
distinguishes purchased credits from included usage. Neither this documentation
nor the receipts establishes the mapping to the five-hour/weekly meter. Therefore
an88–95%included-quota range is not a defensible bound from these data. Nor does
50to1turns bound that meter without its conversion rule. Use90.13%as a V3weighted
credit estimate, not a weekly quota promise. Current-rate estimates should carry
a source/date and update when the rate card changes.
