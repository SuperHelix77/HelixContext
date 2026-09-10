"""Build public, bounded evidence cards from committed adjudications, never private rollouts."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'engine/hud/release_evidence'
SHA=lambda b:hashlib.sha256(b).hexdigest()
BASE='https://github.com/SuperHelix77/HelixContext/blob/41cab63/'
def capsule(key,model,effort,task,policy,report,review,limits,finals,gate,commit='41cab63'):
    base=BASE.replace('41cab63',commit)
    p=ROOT/report; d=json.loads(p.read_text())
    arms=[]
    for r in d['rows']:
        arm=r['arm']; f=ROOT/finals[arm]
        arms.append({'arm':arm,'usage':r['usage'],'native_sha256':r['native_sha256'],
            'segments':r['segments'],'seconds':r.get('elapsed_seconds',r.get('native_elapsed_seconds',r.get('arm_elapsed_seconds'))),
            'final_sha256':SHA(f.read_bytes()),'final_url':base+finals[arm]})
    return {'id':key,'model':model,'effort':effort,'task':task,'policy':policy,'state':'BOUNDED_DEVELOPMENT_CANDIDATE',
        'gate':gate,'model_wide_parity':False,'release_median':None,'paired_tasks':1,'fixed_cohort_cells':7,
        'final_contract':'Complete model-written final after relevant execution evidence; ordinary tools and effort retained.',
        'report_url':base+report,'report_sha256':SHA(p.read_bytes()),
        'review_url':base+review,'review_sha256':SHA((ROOT/review).read_bytes()),
        'arms':arms,'limits':limits,'cost_scope':'Standard API-equivalent scenarios only. Engine, storage, recovery and coordination unpriced; total effective cost and included quota unknown.'}
def main():
    OUT.mkdir(exist_ok=True)
    entries=[]
    for model,slug,effort in [('gpt-5.6-sol','sol-high','high'),('gpt-6-astra','astra-xhigh','xhigh')]:
        report='docs/research/native-output-v1/'+('SOL_HIGH_RESULT.json' if slug=='sol-high' else 'ASTRA_XHIGH_RESULT.json')
        data=capsule(slug+'-maintenance',model,effort,'Coding / memory-search maintenance','Exact edit + checked Engine publication',report,
          'docs/research/native-output-v1/FINAL_ANSWER_REVIEW.json',
          ['One exposed development pair; not a holdout or seven-cell model median.',
           'Both arms pass23 public tests,94 independent cases and all3 model-authored probe programs.',
           'Sol control includes recovered skill/tool detours; Astra candidate output increases slightly.',
           'Desktop pre-inference interception and complete long-horizon parity remain unqualified.'],
          {a:f'docs/research/native-output-v1/artifacts/{slug}/{a}/final-answer.md' for a in ['off','on']},
          'Finite coding checks and final-answer review PASS')
        entries.append(data)
    entries.append(capsule('astra-high-cold','gpt-6-astra','high','Exact cold recovery','Caller-prepared exact evidence',
      'docs/research/cold-native-final-v1/AUDIT.json','docs/research/cold-native-final-v1/SEMANTIC_REVIEW.json',
      ['One exposed40-event snapshot, not40 live model turns or general semantic reasoning.',
       'Exact Unicode, whitespace, leading zeros, bytes and evidence identity pass in both arms.',
       'Measured binding scans total1.55GB logical reads during the pair; physical I/O and full overhead remain unknown.',
       'Best current balanced input/output Astra lane under the complete-final contract; not model-wide qualification.'],
      {a:f'docs/research/cold-native-final-v1/artifacts/{a}-final.txt' for a in ['off','on']},
      'Finite exact-recovery checks and final-answer review PASS'))
    entries.append(capsule('astra-high-w50','gpt-6-astra','high','W50 /49 resolved acknowledgements','Bound caller transitions + one semantic turn',
      'docs/research/w50-native-final-v2/AUDIT.json','docs/research/w50-native-final-v2/SEMANTIC_REVIEW.json',
      ['One exposed50-event pair; no unseen latent-relevance holdout.',
       'Exact49ACKs, restarted evidence and full model-written final pass in both arms.',
       'External display consumer ACK and normal desktop interception remain unproven.',
       'Mixed semantic W50 policy has a separate observed failure and is excluded from this lane.'],
      {a:f'docs/research/w50-native-final-v2/artifacts/{a}-final.txt' for a in ['off','on']},
      'Finite W50 state, recovery and final-answer review PASS'))
    folder='docs/research/luna-normal-final-v1-20260910/'
    luna=capsule('luna-high-maintenance','gpt-5.6-luna','high','Coding / memory-search maintenance',
       'Rejected savings policy · Engine remains available',folder+'LUNA_HIGH_RESULT.json',folder+'FINAL_REVIEW.json',
       ['Both artifacts pass23 public tests,94 independent cases and all3 previous model-authored probe programs.',
        'Candidate final is model-written, but its file:// link violates the configured final-answer contract. It is preserved unchanged.',
        'Both arms had one failed command; failures and recovery are charged. Higher cost is retained, not rerun away.',
        'Only maintenance tested in this lane; six other fixed cells and full parity remain unqualified.',
        'Historical W50/source-only savings remain separate evidence, not a replacement for this negative result.'],
       {'on':folder+'artifacts/candidate-final.md','off':folder+'artifacts/control-final.md'},
       'Finite code checks PASS · candidate final contract FAIL',commit='df2a222')
    luna['state']='REJECTED_ECONOMICS_AND_FINAL_CONTRACT';luna['comparison_gate']='FAIL';entries.append(luna)
    index={'version':'0.1.0-preview.1','lanes':[]}
    for d in entries:
        name=d['id']+'.json'; raw=(json.dumps(d,indent=2)+'\n').encode();(OUT/name).write_bytes(raw)
        index['lanes'].append({'file':name,'sha256':SHA(raw)})
    (OUT/'index.json').write_text(json.dumps(index,indent=2)+'\n')
    print(json.dumps({'capsules':len(entries),'native_calls':0}))
if __name__=='__main__':main()
