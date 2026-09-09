# First-call anatomy: observed bytes, native counters, unknown remainder

OBSERVED from the current prepared-evidence pair. No new inference.

| Term | Native control | Helix candidate | Evidence boundary |
|---|---:|---:|---|
| Initial native input | 19,005 | 19,560 | Reported native tokens |
| Full explicit text prompt | 694 | 854 | o200k proxy tokens |
| Task/orchestration text | 179 | 156 | Proxy, semantic categories overlap |
| Exact contract | 425 | 425 | Proxy |
| Exact proposed source | 79 | 79 | Proxy |
| Prepared receipt packet | 0 | 176 | Proxy |
| Explicitly attached skill body | None | 317 | Frozen file proxy, not serialized runtime count |
| Prior caller conversation turns | 0 | 0 | Empty thread/start turns |
| Loaded global AGENTS source | ~465 | ~465 | Current file proxy; historical path recorded, body not frozen |
| Available skill catalogue | Unknown | ~3,138 |27enabled entries rendered as JSON; injection unproven |
| Platform/system/tool-schema/wrapper tokens | UNKNOWN | UNKNOWN | Payload not exposed by these receipts |

Prompt regions exclude some labels/newline boundaries, so separately tokenized
regions need not sum to whole-prompt tokenization. Skill and catalogue counts may
overlap runtime representations. Do not subtract these proxies from native usage
and label the difference platform overhead. The script deliberately does not.

The native-control first charge is already19,005. Candidate minus control is555
native tokens in this pair. Explicit prompt difference160proxy tokens plus317skill
proxy tokens is consistent with a relatively small visible intervention, but is
not a causal explanation of all555: wrappers, tokenizer and stochastic boundaries
are not controlled component-by-component. Both use CLI0.153.4 and the same recorded
global instruction source. First-call cost is mostly shared, not demonstrably all
Helix overhead. Whether that shared material is mandatory remains UNKNOWN.

The current global instruction file has2305bytes and SHA256
`8aeab698b7ef733520f68349117df6eebf95e065e7fb14b1f2c5ec75fe5835c1`.
Only its path was recorded at thread start; current-byte measurement is explicitly
not proof of the historical injected body. No private instructions are published.

## Conditional geometry, not an irreducibility theorem

For this control130,422input, the80%budget is26,084.4. If19,560 were unavoidable
and all remaining work were free, maximum savings would be85.00%. At100,000control,
the same conditional charge permits at most80.44%. Two such charges total39,120,
already beyond the current80%budget. None of these assumptions proves that the
charge is irreducible or that later charges must equal it.

Formally `S_max = 1 - I_irreducible / I_control` is useful only once a valid
irreducible cost bound exists. We have an observed initial charge, not such a bound.
The currently defensible statement is conditional, not structural impossibility.

## Persistent-session distinction

The current research runner already creates one live native thread and issues its
user turn there. Four model segments on that same thread cost91,543input in total.
The earlier actual same-thread two-turn recovery also retained thread identity
while charging both turns. Persistence may help continuity/cache reuse; it is not
proof that the runtime stops counting shared input. Cached-input credit with zero
prior conversation turns further shows that cache and conversation history are
different concepts. Do not promise headline input savings from persistence alone.

Caller-added dynamic tools were absent. Local schema deferral for dynamic tools
cannot remove a payload not supplied by this runner. Built-in schema loading and
platform serialization remain unknown, not ruled out as contributors. The official
[App Server reference](https://learn.chatgpt.com/docs/app-server) documents dynamic
tools and thread lifecycle; it does not provide per-component token attribution.

## Next admissible evidence

A supported runtime context diagnostic or paired configuration experiment preserving
all capabilities would be needed to attribute/remediate the shared initial charge.
Do not disable tools, erase instructions, substitute models or count cache savings
as total-input savings to manufacture it. Historical fresh-invocation results use
a different runner configuration and cannot serve as a causal component ablation.

An active state-reuse experiment must distinguish genuine saved semantic work from
passive acknowledgements. The earlier W50/L40 native tests exist on an older release;
they do not qualify current persistent-session compaction or long dependent actions.
Those release/lifecycle gaps remain distinct from the initial-charge investigation.

Reproduce with `first_call_anatomy.py <native-prepared-pair-root> <output.json>`.
Machine artifact:`FIRST_CALL_ANATOMY.json`; recorded request/native event hashes
and separate text proxy measurements included. Full80/80 and no-loss remain open.
