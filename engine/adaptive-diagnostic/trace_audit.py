"""Descriptive native trace audit. Does not launch models or infer causality."""
import hashlib,json
from pathlib import Path
import argparse
parser=argparse.ArgumentParser()
parser.add_argument('--workspace',required=True,help='Original private workspace containing work/helix-engine receipts')
ROOT=Path(parser.parse_args().workspace).resolve()
SOURCES={'typed_terminal':'pilot-v2','literal_query_v1':'query-pilot','literal_query_v2':'query-pilot-v2'}

def main():
 rows=[]
 for concept,folder in SOURCES.items():
  for model in ('luna','sol','astra'):
   for arm in ('off','on'):
    d=ROOT/'work/helix-engine'/folder/'receipts'/model/arm
    raw=(d/'events.jsonl').read_bytes();events=[json.loads(l) for l in raw.splitlines()]
    status=json.loads((d/'status.json').read_text())
    assert hashlib.sha256(raw).hexdigest()==status['events_sha256']
    usage=[e['usage'] for e in events if e.get('type')=='turn.completed']
    assert len(usage)==1 and usage[0]==status['usage']
    items=[e['item'] for e in events if e.get('type')=='item.completed']
    commands=[i for i in items if i.get('type')=='command_execution']
    rows.append({'concept':concept,'model':model,'arm':arm,'events_sha256':status['events_sha256'],'usage':usage[0],'completed_commands':len(commands),'command_output_utf8_bytes':sum(len(i.get('aggregated_output','').encode()) for i in commands),'command_text_utf8_bytes':sum(len(i.get('command','').encode()) for i in commands),'agent_message_utf8_bytes':sum(len(i.get('text','').encode()) for i in items if i.get('type')=='agent_message'),'scope':'Public CLI trace surface only; command count is not model inference count. Output may already be truncated.'})
 pairs=[]
 for concept in SOURCES:
  for model in ('luna','sol','astra'):
   p={r['arm']:r for r in rows if r['concept']==concept and r['model']==model}
   pairs.append({'concept':concept,'model':model,'commands_off':p['off']['completed_commands'],'commands_on':p['on']['completed_commands'],'input_saving':1-p['on']['usage']['input_tokens']/p['off']['usage']['input_tokens'],'output_saving':1-p['on']['usage']['output_tokens']/p['off']['usage']['output_tokens']})
 envelopes=[]
 for model in ('luna','sol','astra'):
  m=[r for r in rows if r['model']==model];off=[r for r in m if r['arm']=='off'];on=[r for r in m if r['arm']=='on']
  envelopes.append({'model':model,'optimistic_unpaired_input_saving':1-min(r['usage']['input_tokens'] for r in on)/max(r['usage']['input_tokens'] for r in off),'optimistic_unpaired_output_saving':1-min(r['usage']['output_tokens'] for r in on)/max(r['usage']['output_tokens'] for r in off),'warning':'Cherry-picked retrospective envelope only, not a paired benchmark, theoretical limit, or achievable joint point. Used only to reject further tiny local tuning as a supported route to 80% on these observations.'})
 report={'schema':'helix.trace_diagnostic.v1','native_calls_reused':18,'new_native_calls':0,'rows':rows,'pairs':pairs,'optimistic_unpaired_envelopes':envelopes,'causality':'Associations only. CLI receipts lack per-inference usage and full model-facing context, so hidden context versus extra inference versus tool-output contribution cannot be decomposed exactly.'}
 out=ROOT/'outputs/HelixContext/engine/adaptive-diagnostic'
 (out/'TRACE_AUDIT.json').write_text(json.dumps(report,indent=2)+'\n')
 lines=['# Trace diagnosis and stop decision','','All 18 existing terminal diagnosis calls were read back and hash/usage checked. No new native calls were made.','','| Model | Mechanism | Commands off → on | Input saved | Output saved |','|---|---|---:|---:|---:|']
 for p in pairs:lines.append(f"| {p['model']} | {p['concept']} | {p['commands_off']} → {p['commands_on']} | {p['input_saving']:.1%} | {p['output_saving']:.1%} |")
 lines+=['','## What changes the next action','','Every equal-command-count pair regressed in input in these observations. Pairs with fewer commands usually improved input, but Luna typed projection is a counterexample. Thus fewer commands is a useful diagnostic signal, not a causal proof or sufficient admission rule. CLI command counts are not counts of model inferences.','','Astra consistently moved from two commands to one across these three candidates; input savings stayed around 26–32%. Sol varied between one and three control commands; its approximately 50% wins coincide with three-command controls, while the one-command control beats query V1 on input. Luna varied similarly and did not gain from V2 when its control already used one command. These results do not establish a stable model-specific advantage for every candidate.','','The compound-token fix increased selected evidence coverage but did not remove the final source check. Further lexical tuning is not currently supported as a route to the requested 80% joint target. Stop this short-log candidate sweep.','','## Composition requirements','','Keep model/task routing, but distinguish a candidate from a validated policy. Astra query projection is the most consistent diagnostic candidate here; Sol projection and Luna renderer need stronger confirmation in their respective workloads. Do not combine multiple log projections: they target overlapping costs and would duplicate evidence. Exact retrieval batching and source-copy belong only in workflows that actually require multiple spans or copying.','','The next useful joint test must exercise sustained workflow state, evidence retrieval and exact artifact output in the same episode, with an efficient control allowed the same ordinary batching/copying. First implement or verify the relevant interface and offline capability checks. Do not spend on another microtask matrix expecting its percentages to compound.','','Per-inference context delivery remains unobserved in these CLI traces. Native interception is Spark-owned. Do not change hooks or claim a causal token decomposition from these receipts. All public results remain bounded development evidence, with the 80% and capability-parity goals unestablished.']
 (out/'TRACE_DIAGNOSIS.md').write_text('\n'.join(lines)+'\n')
 print('\n'.join(lines[4:15]))

if __name__=='__main__':main()
