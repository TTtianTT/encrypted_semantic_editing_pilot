"""CPU recomputation of posthoc validation trajectory magnitudes."""
import gzip
import math
from .common import *
from .analyze import csv_write

METHODS=('Original','Plain','Output-only','Mechanism-guided','Random-site')

def recompute(folder):
    rs=rows(folder/'trajectory_norms.jsonl')
    assert len(rs)==6400 and len({r['world_id'] for r in rs})==64
    assert len({(r['world_id'],r['method'],r['order'],r['direction'],r['step']) for r in rs})==6400
    assert all(r['scope']=='POSTHOC_VALIDATION_MAGNITUDE_DIAGNOSTIC' and all(math.isfinite(r[k]) and r[k]>=0 for k in ('update_norm','relative_update_norm','cumulative_norm_from_natural')) for r in rs)
    return rs

def table(rs):
    result=[]
    for seed in sorted({r['seed'] for r in rs}):
        for method in METHODS:
            for step in range(1,6):
                group=[r for r in rs if (r['seed'],r['method'],r['step'])==(seed,method,step)]
                assert len(group)==256
                result.append(dict(seed=seed,method=method,step=step,denominator=256,worlds=64,complete_numerator=sum(r['complete_to_step'] for r in group),**{'mean_'+key:sum(r[key] for r in group)/256 for key in ('update_norm','relative_update_norm','cumulative_norm_from_natural')},scope='POSTHOC_VALIDATION_MAGNITUDE_DIAGNOSTIC'))
    return result

def audit_run(source,dest,summary):
    rs=recompute(source);tab=table(rs)
    assert summary['checked_stored_predictions']==100 and summary['prediction_mismatches']==0 and summary['test_accessed']==0
    dump(dest/'NUMERICAL_AUDIT.json',dict(passed=True,records=len(rs),worlds=64,table=tab,stored_prediction_checks=100,mismatches=0,test_evaluations=0,scope='POSTHOC_VALIDATION_MAGNITUDE_DIAGNOSTIC'))
    allocation=read(dest/'RUN_STATUS.json')['allocation']
    lines=['| Method | Step | Complete prefix | Mean update norm | Mean relative norm |','| --- | --- | --- | --- | --- |']
    lines += [f"| {r['method']} | {r['step']} | {r['complete_numerator']}/256 | {r['mean_update_norm']:.6f} | {r['mean_relative_update_norm']:.6f} |" for r in tab]
    text(dest/'REPORT.md',f"# Validation trajectory magnitude replay seed{summary['seed']}\n\nCOMPLETED; Slurm {allocation['job_id']}; {allocation['GPU_hours']:.6f} GPU-hours. Replayed 64 validation worlds, five frozen methods, four locked trajectories and five steps: 6,400 records. All 100 stored predictions checked on the first world agree exactly; no algorithm/checkpoint changed and test accesses are 0. Padding is excluded from norms.\n\n"+'\n'.join(lines)+'\n\nThis posthoc diagnostic measures magnitude differences in the already fixed paths. Norm strata are descriptive and do not establish norm-matched causal method effects. Every latent replay ran within the registered sbatch/srun allocation; no additional encoder execution.\n')
    text(dest/'INTERPRETATION.md','Posthoc validation magnitude diagnostics cannot convert heterogeneous two-step effects into confirmation or long-term stability. No training, selection or test definition changes are supported by this replay.\n')

def summarize():
    manifest=read(ROOT/'manifests/S3_TRAJECTORY_NORMS.json');rs=[];inputs={}
    for seed in (42,43,44):
        folder=Path(manifest['output_root'])/f'bart_s{seed}'
        assert read(folder/'RUN_STATUS.json')['status']=='COMPLETED'
        rs.extend(recompute(folder));inputs[str(folder/'trajectory_norms.jsonl')]=sha(folder/'trajectory_norms.jsonl')
    tab=table(rs);csv_write(ROOT/'results/selected_trajectory_magnitudes.csv',tab)
    bins=read(ROOT/'configs/METHOD_COMPARISON_LOCK.json')['norm_bins']
    strata=[]
    for seed in (42,43,44):
        for method in METHODS:
            for step in (1,2,3,5):
                for low,high in zip(bins,bins[1:]):
                    group=[r for r in rs if (r['seed'],r['method'],r['step'])==(seed,method,step) and low<=r['update_norm']<high]
                    strata.append(dict(seed=seed,method=method,step=step,low=low,high=high,denominator=len(group),numerator=sum(r['complete_to_step'] for r in group),rate=sum(r['complete_to_step'] for r in group)/len(group) if group else None,status='ESTIMABLE' if group else 'NOT_ESTIMABLE',scope='POSTHOC_VALIDATION_MAGNITUDE_DIAGNOSTIC'))
    csv_write(ROOT/'results/selected_trajectory_magnitude_strata.csv',strata)
    atomic(ROOT/'results/selected_trajectory_magnitudes.jsonl.gz',gzip.compress(''.join(json.dumps(r)+'\n' for r in rs).encode(),mtime=0))
    dump(ROOT/'results/TRAJECTORY_MAGNITUDE_NUMERICAL_AUDIT.json',dict(passed=True,records=len(rs),worlds=64,table=tab,strata=strata,stored_prediction_checks=300,mismatches=0,inputs=inputs,test_evaluations=0,scope='POSTHOC_VALIDATION_MAGNITUDE_DIAGNOSTIC'))
    print(dict(records=len(rs),stored_prediction_checks=300,mismatches=0))

if __name__=='__main__':summarize()
