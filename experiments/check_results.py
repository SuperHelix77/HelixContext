"""Recompute published savings from extracted native receipts (no model calls)."""
from pathlib import Path
import json
root=Path(__file__).resolve().parents[1]
receipts=json.loads((root/'results/native-usage.json').read_text())
r=json.loads((root/'results/benchmarks.json').read_text())
for index,group in enumerate(['control-1','control-2']):
 selected=[x for x in receipts if x['group']==group]
 assert len(selected)==4
 for k in ['input_tokens','output_tokens']:
  assert sum(x['usage'][k] for x in selected)==r['controls'][index][k]
for name,candidate in r['candidates'].items():
 selected=[x for x in receipts if x['group']=='candidate' and x['run']==name]
 assert len(selected)==1
 assert selected[0]['usage']==candidate['usage']
 for k in ['input_tokens','output_tokens']:
  expected=round(100*(1-candidate['usage'][k]/r['mean_control'][k]),2)
  assert expected==candidate['reduction_vs_average_control_pct'][k]
 assert candidate['total_tokens']==candidate['usage']['input_tokens']+candidate['usage']['output_tokens']
 assert candidate['passed']==all(candidate['checks'].values())
print(f"Reconciled {len(receipts)} receipts and {len(r['candidates'])} candidate results.")
print('Separate 80% input/output target:', 'met by a candidate' if any(all(v['reduction_vs_average_control_pct'][k]>=80 for k in ['input_tokens','output_tokens']) for v in r['candidates'].values()) else 'NOT MET')
