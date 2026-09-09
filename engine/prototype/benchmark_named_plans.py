"""Offline overhead falsifier; no model calls or token savings claims.

Compare identical scripts and captured step outputs. The ordinary arm uses the
existing checked executor; the plan arm adds dependency validation and snapshots.
This measures the incremental cost of those guarantees, not equivalent isolation.
"""
import argparse
import hashlib
import json
import platform
import statistics
import sys
import time
from pathlib import Path

import checked_steps
from evidence import Store
import named_plans
from plan_costs import break_even


def retained(root):
    return sum(p.stat().st_size for p in root.rglob('*') if p.is_file())


def run_case(base, size, repeats, release_inputs=False):
    root=base/str(size);root.mkdir()
    source=root/'source';source.mkdir()
    data=b'x'*size
    (source/'input.bin').write_bytes(data)
    script='import hashlib\nfrom pathlib import Path\nprint(hashlib.sha256(Path("input.bin").read_bytes()).hexdigest())\n'
    (source/'job.py').write_text(script)
    expected=(hashlib.sha256(data).hexdigest()+'\n').encode()
    ordinary=Store(root/'ordinary');planned=Store(root/'planned')
    ordinary_steps=[{'name':'hash','argv':[sys.executable,'-I','-S','job.py']}]
    start=time.perf_counter()
    ref=named_plans.register(planned,'hash-input',1,cwd=source,
        steps=[{'name':'hash','argv':['python','-I','-S','job.py']}],
        files={'input.bin':'input','job.py':'script'},
        executables={'python':sys.executable},environment={})
    creation=time.perf_counter()-start
    creation_retained=retained(planned.root)
    samples=[]
    for index in range(repeats):
        # Alternate arm ordering to reduce one-sided warm-cache bias.
        pair={}
        for arm in (('ordinary','planned') if index%2==0 else ('planned','ordinary')):
            store=ordinary if arm=='ordinary' else planned
            before=retained(store.root);io_before=dict(store.metrics)
            start=time.perf_counter()
            if arm=='ordinary':
                result=checked_steps.execute(store,ordinary_steps,source,'offline-plan-control',env={})
                success=result['process_success'];validation=None
            else:
                result=named_plans.invoke(store,ref,environment={})
                success=result['status']=='SUCCEEDED'
                validation=result['costs']['validation']['bytes_read']
                final=result['publication']['validation']
                validation+=final['bytes_read'] if final else 0
            elapsed=time.perf_counter()-start
            io={k:store.metrics[k]-io_before[k] for k in io_before}
            # Validation reads are outside execution timing and counters in both
            # arms; equality is checked from immutable raw output, not prose.
            receipt=store.receipt(result['steps'][0]['receipt'])
            exact=store.get(receipt['stdout']['sha256'])==expected
            assert success and exact and receipt['exit_code']==0
            release=None
            if arm=='planned' and release_inputs:
                # This fixture produces only stdout. Exact comparison completes
                # the last workspace consumer; releasing inputs is now valid.
                release=named_plans.release_inputs(store,ref,result['attempt_hash'])
                assert release['status']=='RELEASED'
                elapsed+=release['total_seconds']
            pair[arm]={'seconds':elapsed,'retained_growth_bytes':retained(store.root)-before,
                       'store_io':io,'dependency_validation_bytes_read':validation,
                       'release':release,'exact_output':exact,'exit_code':receipt['exit_code']}
        samples.append(pair)
    medians={arm:statistics.median(p[arm]['seconds'] for p in samples) for arm in ('ordinary','planned')}
    return {'input_bytes':size,'repeats':repeats,'creation_seconds':creation,
        'creation_retained_bytes':creation_retained,'samples':samples,
        'median_seconds':medians,'incremental_median_seconds':medians['planned']-medians['ordinary'],
        'latency_break_even_reuses_constant_median_assumption':break_even(creation,medians['ordinary'],medians['planned']),
        'total_seconds_including_creation':{arm:sum(p[arm]['seconds'] for p in samples)+(creation if arm=='planned' else 0) for arm in medians},
        'retained_bytes':{arm:retained(store.root) for arm,store in [('ordinary',ordinary),('planned',planned)]}}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);parser.add_argument('--artifacts',required=True);parser.add_argument('--repeats',type=int,default=7);parser.add_argument('--release-inputs',action='store_true')
    args=parser.parse_args()
    if args.repeats<2:parser.error('At least two repetitions required')
    directory=Path(args.artifacts).resolve();directory.mkdir(parents=True,exist_ok=False)
    cases=[run_case(directory,size,args.repeats,args.release_inputs) for size in (256,1048576)]
    modules=['benchmark_named_plans.py','named_plans.py','plan_dependencies.py','plan_costs.py','checked_steps.py','evidence.py']
    report={'schema':'helix.plan_overhead.v1','classification':'offline infrastructure overhead; no native model evidence',
        'python':platform.python_version(),'platform':platform.platform(),
        'sources':{name:hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() for name in modules},
        'cases':cases,'release_inputs_after_last_consumer':args.release_inputs,'native_input_tokens':None,'native_output_tokens':None,
        'artifacts':str(directory),'artifact_manifest':{str(p.relative_to(directory)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(directory.rglob('*')) if p.is_file()},
        'limits':['Single local process; OS caches uncontrolled; alternating order, no confidence interval.',
                  'Logical retained file bytes, not physical I/O or allocated storage.',
                  'Ordinary control has exact status/output capture but no plan dependency isolation.',
                  'No model plan creation, reasoning, command generation or skill costs measured.',
                  'Raw evidence and plan snapshots retained at artifacts path with per-file hashes.']}
    Path(args.output).write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'output':args.output,'cases':[{'bytes':c['input_bytes'],'median_seconds':c['median_seconds'],'latency_break_even':c['latency_break_even_reuses_constant_median_assumption'],'retained_bytes':c['retained_bytes']} for c in cases]}))


if __name__=='__main__':main()
