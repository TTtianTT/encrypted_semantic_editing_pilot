"""CPU audit of full own-latent validation trajectories and measured costs."""
import gzip
import numpy as np
from .common import *
from .analyze import csv_write, paired_bootstrap
from .metrics import wilson

METHODS = ('Original','Plain','Output-only','Mechanism-guided','Random-site')
LENGTHS = (1,2,3,5)


def recompute(folder):
    result=[]
    for path in sorted(folder.glob('*_trajectories.jsonl')):
        tracks=rows(path)
        assert len(tracks)==20
        assert len({(r['method'],r['order'],r['direction']) for r in tracks})==20
        for r in tracks:
            assert r['split']=='validation' and len(r['steps'])==5
            for length in LENGTHS:
                success=all(step['prediction']['score']['success'] for step in r['steps'][:length])
                assert success==r['length_success'][str(length)]
                p=r['steps'][length-1]['prediction'];score=p['score']
                result.append(dict(world_id=r['world_id'],seed=r['seed'],method=r['method'],order=r['order'],direction=r['direction'],length=length,success=success,step_joint=score['success'],step_target=score['target'],step_content=score['preserved'],step_parseable=score['parseable'],step_EOS=p['ended']))
    assert len(result)==5120 and len({r['world_id'] for r in result})==64
    return result


def table(records):
    out=[]
    for seed in sorted({r['seed'] for r in records}):
        for method in METHODS:
            for length in LENGTHS:
                rs=[r for r in records if (r['seed'],r['method'],r['length'])==(seed,method,length)]
                assert len(rs)==256
                good=sum(r['success'] for r in rs)
                world_good=sum(all(r['success'] for r in rs if r['world_id']==w) for w in {r['world_id'] for r in rs})
                out.append(dict(seed=seed,method=method,length=length,complete_numerator=good,trajectory_denominator=256,rate=good/256,worlds=64,all_four_trajectories_world_numerator=world_good,world_denominator=64,world_Wilson95=wilson(world_good,64),step_joint_numerator=sum(r['step_joint'] for r in rs),step_target_numerator=sum(r['step_target'] for r in rs),step_content_numerator=sum(r['step_content'] for r in rs),step_parseable_numerator=sum(r['step_parseable'] for r in rs),step_EOS_numerator=sum(r['step_EOS'] for r in rs),scope='EXPLORATORY_VALIDATION_ONLY'))
    return out


def benchmarks(folder):
    rs=rows(folder/'inference_benchmark.jsonl')
    assert len(rs)==128 and len({r['world_id'] for r in rs})==8
    out=[]
    for method in METHODS[1:]:
        selected=[r for r in rs if r['method']==method]
        assert len(selected)==32 and len({r['editor_parameters'] for r in selected})==1
        assert all(not r['donor_used'] and not r['test_time_backward'] and len(r['measurements'])==5 for r in selected)
        vals=[m for r in selected for m in r['measurements']]
        out.append(dict(seed=selected[0]['seed'],method=method,worlds=8,conditions=32,recorded_repeats=160,discarded_warmups=32,editor_parameters=selected[0]['editor_parameters'],editor_GPU_ms_median=float(np.median([r['editor_GPU_ms'] for r in vals])),editor_GPU_ms_p95=float(np.quantile([r['editor_GPU_ms'] for r in vals],.95)),decode_and_score_wall_ms_median=float(np.median([r['decode_and_score_wall_ms'] for r in vals])),scope='FIXED_VALIDATION_BENCHMARK'))
    return out


def audit_run(source,dest,summary):
    rs=recompute(source);computed=table(rs)
    for r in summary['trajectories']:
        actual=next(x for x in computed if x['method']==r['method'] and x['length']==r['length'])
        assert actual['complete_numerator']==r['complete_numerator']
    latency=benchmarks(source)
    audit=dict(passed=True,seed=summary['seed'],worlds=64,trajectories=computed,benchmarks=latency,own_latent_states=True,independent_test_evaluations=0,scope='EXPLORATORY_VALIDATION_ONLY',original_Plain_reused=True)
    dump(dest/'NUMERICAL_AUDIT.json',audit)
    allocation=read(dest/'RUN_STATUS.json')['allocation']
    body=[]
    for method in METHODS:
        values=[next(r['complete_numerator'] for r in computed if r['method']==method and r['length']==length) for length in LENGTHS]
        body.append('| '+method+' | '+' | '.join(f'{value}/256' for value in values)+' |')
    text(dest/'REPORT.md',f"""# Selected BART editors seed{summary['seed']}: own-latent validation trajectories

COMPLETED; Slurm {allocation['job_id']}; allocation GPU-hours {allocation['GPU_hours']:.6f}. 64 validation core worlds, two locked operation orders and two directions, 256 trajectories per method. All prefixes must succeed for complete-trajectory success. Source starts are natural; subsequent memory is each method's own edited output, without resetting to gold states. Original/Plain full trajectories are SHA-verified earlier results, with identical cached H and unchanged checkpoints; they were not generated or charged twice.

| Method | 1 step | 2 steps | 3 steps | 5 steps |
| --- | --- | --- | --- | --- |
{chr(10).join(body)}

All 1,280 trajectories and every intermediate prediction are retained, including failures. NUMERICAL_AUDIT independently recomputes the full records; each seed's world-level all-four-trajectory proportion also has a Wilson interval. Inference latency is measured on a fixed eight-world subset, with identical source/operation conditions, one editor forward and native free decoding; warmups and measured repeats are explicit. No donor, target-text input, re-encoding, test-time gradient, rejection sampling or future gold activation is used by these editors.

These are validation results, not independent confirmation. The original 128-world test remains BLOCKED_TEST_INTEGRITY after five prior core exposures; no replacement pool or amended denominator is authorized. Atomic ability is evaluated in the preceding training run and cannot be inferred from these natural-start chains. Three seeds describe these fixed checkpoints. Mechanism-guided versus Output-only/Random-site requires paired world-cluster summaries, and any longer-chain improvement remains exploratory.
""")
    text(dest/'INTERPRETATION.md','Every full trajectory requires success at each preceding step. Final-step success alone does not repair earlier failures. Natural-start trajectories do not establish recovery of previously incorrect history states. Retain zero rates and distinguish method readout regularization from demonstrated long-term stability.\n')
    return audit


def summarize():
    manifest=read(ROOT/'manifests/S3_SELECTED_VALIDATION_TRAJECTORIES.json');all_records=[];cost=[];sources={}
    for seed in (42,43,44):
        folder=Path(manifest['output_root'])/f'bart_s{seed}'
        assert read(folder/'RUN_STATUS.json')['status']=='COMPLETED'
        all_records.extend(recompute(folder));cost.extend(benchmarks(folder))
        for path in folder.glob('*_trajectories.jsonl'):sources[str(path)]=sha(path)
        sources[str(folder/'inference_benchmark.jsonl')]=sha(folder/'inference_benchmark.jsonl')
    atomic(ROOT/'results/selected_validation_trajectories.jsonl.gz',gzip.compress(''.join(json.dumps(r)+'\n' for r in all_records).encode(),mtime=0))
    grouped=table(all_records);csv_write(ROOT/'results/selected_validation_trajectory_summary.csv',grouped)
    csv_write(ROOT/'results/selected_inference_benchmark.csv',cost)
    directions=[]
    for seed in (42,43,44):
        for method in METHODS:
            for length in LENGTHS:
                for order in (0,1):
                    for direction in ('forward','inverse'):
                        rs=[r for r in all_records if (r['seed'],r['method'],r['length'],r['order'],r['direction'])==(seed,method,length,order,direction)]
                        assert len(rs)==64
                        directions.append(dict(seed=seed,method=method,length=length,order=order,direction=direction,numerator=sum(r['success'] for r in rs),denominator=64,scope='EXPLORATORY_VALIDATION_ONLY'))
    csv_write(ROOT/'results/selected_validation_trajectory_by_direction.csv',directions)
    comparisons=[]
    for a,b in [('Mechanism-guided','Output-only'),('Mechanism-guided','Random-site'),('Output-only','Plain'),('Random-site','Plain')]:
        for length in LENGTHS:
            # The bootstrap's equal-source API receives identical labels solely
            # to compute the same natural-start world average; no extra units.
            adapted=[dict(world_id=r['world_id'],seed=r['seed'],method=r['method'],source=source,joint=r['success']) for r in all_records if r['length']==length for source in ('natural','history')]
            estimate=paired_bootstrap(adapted,a,b)
            per_seed={str(seed):paired_bootstrap([r for r in adapted if r['seed']==seed],a,b) for seed in (42,43,44)}
            comparisons.append(dict(a=a,b=b,length=length,scope='EXPLORATORY_VALIDATION_ONLY',source_interpretation='natural starts only; API source labels are identical copies, not independent sources',**estimate,per_seed=per_seed))
    dump(ROOT/'results/SELECTED_TRAJECTORY_NUMERICAL_AUDIT.json',dict(records=len(all_records),worlds=64,trajectories=grouped,benchmarks=cost,comparisons=comparisons,input_SHA256=sources,test_evaluations=0,scope='EXPLORATORY_VALIDATION_ONLY'))
    print(json.dumps(grouped,ensure_ascii=False))


if __name__=='__main__':summarize()
