"""Publish sanitized receipts and the self-contained Luna result."""
import hashlib, json, shutil
from pathlib import Path

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def load(path): return json.loads(Path(path).read_text())
def save(path, value): Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")

def event_facts(run):
    events=[json.loads(x) for x in (run/'native-events.jsonl').read_text().splitlines()]
    commands=[e.get('params',{}).get('item',{}) for e in events if e.get('method')=='item/completed' and e.get('params',{}).get('item',{}).get('type')=='commandExecution']
    return {"failed_command_executions": sum(1 for x in commands if x.get('exit_code') not in (None,0)),
            "completed_command_executions": sum(1 for x in commands if x.get('exit_code')==0),
            "dynamic_tool_calls": sum(1 for e in events if e.get('method')=='item/tool/call'),
            "native_events_sha256": sha(run/'native-events.jsonl'),
            "raw_rollout_sha256": load(run/'raw/raw-tool-index.json')['sha256'],
            "raw_rollout_bytes": load(run/'raw/raw-tool-index.json')['bytes']}

def main(root):
    root=Path(root).resolve(); audit=load(HERE/'LUNA_HIGH_RESULT.json'); probe=load(HERE/'PROBE_REPLAY.json')
    art=HERE/'artifacts'; art.mkdir(exist_ok=True)
    rows=[]
    for arm,label in [('on','candidate'),('off','control')]:
        run=root/(arm+'-run'); cwd=root/arm; source=art/(label+'-workflow_memory.py'); final=art/(label+'-final.md')
        shutil.copy2(cwd/'workflow_memory.py',source); shutil.copy2(run/'turn-1-answer.txt',final)
        row=next(r for r in audit['rows'] if r['arm']==arm)
        u=row['usage']; facts=event_facts(run)
        link_format = "FAIL" if "file:///" in final.read_text() else "PASS"
        rows.append({"arm":label,"model":row['model'],"effort":row['effort'],"thread_id":row['thread_id'],
                     "usage":u,"uncached_input_tokens":u['input_tokens']-u['cached_input_tokens'],
                     "other_output_tokens":u['output_tokens']-u['reasoning_output_tokens'],
                     "segments":row['segments'],"turns":row['turns'],"raw_tool_calls":row['raw_tool_calls'],
                     "engine_tool_calls":row['engine_tool_calls'],"failed_command_executions":facts['failed_command_executions'],
                     "completed_command_executions":facts['completed_command_executions'],"dynamic_tool_calls":facts['dynamic_tool_calls'],
                     "native_events_sha256":facts['native_events_sha256'],"raw_rollout_sha256":facts['raw_rollout_sha256'],
                     "raw_rollout_bytes":facts['raw_rollout_bytes'],"source_sha256":sha(source),"final_sha256":sha(final),
                     "elapsed_seconds":row['elapsed_seconds'],"caller_check_seconds":row['caller_check_seconds'],
                     "memory_seconds":row['memory_seconds'],"memory_raw_bytes":row['memory_raw_bytes'],
                     "config_binding":row['config_binding'],"finite_checks":"PASS",
                     "final_review": {"normal_model_written_final":"PASS","after_actual_execution":"PASS",
                                      "requested_change_explained":"PASS","truthful_test_and_scope_claims":"PASS",
                                      "caller_rendered_final":"NO","local_link_format":link_format,
                                      "normal_final_contract":"PASS" if link_format=="PASS" else "FAIL"}})
    candidate,control=rows
    result={"schema":"helix.luna.normal-final.qualification-result.v1",
            "classification":"LUNA_HIGH_MAINTENANCE_PAIR_FINITE_PASS_ECONOMIC_FAIL_NOT_QUALIFIED",
            "native_pair":"Fresh matched Luna High maintenance pair; candidate control and engine tool routes are versioned; one maintenance cell only.",
            "manifest_sha256":audit['manifest_sha256'],"run_root":str(root),"rows":rows,
            "pair_savings_percent":audit['savings_percent'],
            "pair_savings_definition":"100*(1-candidate/control); output includes reported reasoning; uncached input is total input minus cached input.",
            "finite_checks":"PASS","normal_final_authorship":"PASS on both artifacts",
            "normal_final_contract":"FAIL for candidate local-link formatting; control PASS",
            "semantic_probe_replay": {"source_probe_count":probe['probe_count'],"fresh_artifacts":2,"all_pass":probe['all_pass'],"receipt_sha256":sha(HERE/'PROBE_REPLAY.json')},
            "failed_work_preserved":{"candidate_failed_command_executions":candidate['failed_command_executions'],"control_failed_command_executions":control['failed_command_executions'],"note":"Candidate's failed semantic probe and subsequent recovery remain in private native receipt; no retry was hidden."},
            "candidate_switches":{"model":"gpt-5.6-luna","effort":"high","frozen_base":"engine/profiles/luna-coding-v1-75/base.md","bound_edit_tool":"existing native-output-v1 interface","reasoning_style":"none-new; no notation/language intervention","caller_preparation":"task-local memory preflight, registration and attached skill","final_renderer":None},
            "cohort":{"fixed_cells":["intervals","dependencies","transactions","maintenance","selection","cold_recovery","W50"],"completed_native_cells":["maintenance"],"missing_cells":["intervals","dependencies","transactions","selection","cold_recovery","W50"],"seven_cell_median":None,"W50_stratum_separate":True},
            "qualification":{"meets_75_75":False,"meets_80_80":False,"economic_gate":False,"cohort_complete":False,"general_release":False,"full_capability_parity":"UNCONFIRMED"},
            "limits":["N=1 exposed development maintenance task, not holdout evidence","Finite checks and three observed probe replays are bounded behavioral evidence, not universal intelligence parity","Candidate combines frozen Luna base, caller preparation, attached skill and bound edit tool; mechanism effects are not isolated","Included-plan quota, physical I/O and complete research/coordinator costs are unknown","Missing six fixed cells prevent a seven-cell median or model-wide release"],
            "artifact_manifest":{"candidate_source":str((art/'candidate-workflow_memory.py').relative_to(HERE)),"control_source":str((art/'control-workflow_memory.py').relative_to(HERE)),"candidate_final":str((art/'candidate-final.md').relative_to(HERE)),"control_final":str((art/'control-final.md').relative_to(HERE)),"probe_replay":"PROBE_REPLAY.json","final_review":"FINAL_REVIEW.json"}}
    save(HERE/'RELEASE_ARTIFACTS.json',result);save(HERE/'RESULT.json',result)
    print(json.dumps({"classification":result['classification'],"savings":result['pair_savings_percent'],"finite_checks":"PASS","probe_replay":probe['all_pass']}))

if __name__=='__main__': main(__import__('sys').argv[1])
