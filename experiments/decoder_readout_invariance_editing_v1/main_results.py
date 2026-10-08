"""CPU aggregation of selected three-seed methods; validation is explicit."""
import csv
import gzip
import numpy as np
from .common import *
from .analyze import csv_write,paired_bootstrap,holm
from .finalize import summarize_atomic
from .metrics import wilson


def checkpoint_lock():
    sm=read(ROOT/'manifests/S3_SELECT.json');sf=Path(sm['output_root'])/'bart_s42'
    selection=read(ROOT/'configs/TRAINING_SELECTION_LOCK.json');items=[]
    for chosen in selection['methods']:
        p=Path(chosen['path']);items.append(dict(seed=42,method=chosen['method'],path=str(p),sha256=sha(p),validation=str(p.parent/(p.parent.name+'_validation.jsonl'))))
    mm=read(ROOT/'manifests/S3_MAIN.json')
    for seed in (43,44):
        folder=Path(mm['output_root'])/f'bart_s{seed}';assert read(folder/'RUN_STATUS.json')['status']=='COMPLETED'
        for chosen in read(folder/'TRAINING_SUMMARY.json'):
            p=Path(chosen['path']);items.append(dict(seed=seed,method=chosen['method'],path=str(p),sha256=sha(p),validation=str(p.parent/(chosen['method']+'_validation.jsonl'))))
    assert len(items)==12
    for item in items:
        item['validation_sha256']=sha(item['validation'])
    lock=dict(checkpoints=items,selection_sha256=sha(ROOT/'configs/TRAINING_SELECTION_LOCK.json'),
        keep_review_sha256=sha(ROOT/'configs/KEEP_MASK_REVIEW_LOCK.json'),
        mechanism_lock_sha256=sha(ROOT/'configs/MECHANISM_LOCK.json'),
        hyperparameter_lock_sha256=sha(ROOT/'configs/TRAINING_HYPERPARAMETER_LOCK.json'),
        test_status='BLOCKED_TEST_INTEGRITY',test_unseal_authorized=False,methods_ready=True)
    dump(ROOT/'configs/FINAL_METHOD_CHECKPOINT_LOCK.json',lock);return lock


def summarize():
    lock=read(ROOT/'configs/FINAL_METHOD_CHECKPOINT_LOCK.json');records=[]
    for item in lock['checkpoints']:
        assert sha(item['validation'])==item['validation_sha256']
        for r in rows(item['validation']):
            p=r['prediction'];s=p['score']
            records.append(dict(world_id=r['world_id'],seed=item['seed'],method=item['method'],source=r['source'],state=r['state'],operation=r['operation'],current_correct=r['current']['score']['success'],joint=s['success'],target=s['target'],content=s['preserved'],parseable=s['parseable'],grammar=s['grammar'],EOS=p['ended'],exact_match=p['text']==p['gold_text'],update_norm=r['update_norm']))
    original=read(ROOT/'manifests/S3_VALIDATION_TRAJECTORIES.json')
    for seed in (42,43,44):
        folder=Path(original['output_root'])/f'bart_s{seed}'
        for path in folder.glob('*_editing.jsonl'):
            for r in rows(path):
                p=r['prediction'];records.append({k:r[k] for k in ('world_id','seed','method','source','state','operation','current_correct','joint','target','content','parseable','EOS','update_norm')}|dict(exact_match=p['text']==p['gold_text'],grammar=p['score']['grammar']))
    assert len(records)==23040
    atomic(ROOT/'results/selected_validation_atomic.jsonl.gz',gzip.compress(''.join(json.dumps(r)+'\n' for r in records).encode(),mtime=0))
    tables=[];boundaries=[];bins=read(ROOT/'configs/METHOD_COMPARISON_LOCK.json')['norm_bins']
    methods=['Original','Plain','Output-only','Mechanism-guided','Random-site']
    for seed in (42,43,44):
        for method in methods:
            base=[r for r in records if r['seed']==seed and r['method']==method];assert len(base)==1536
            for source in ('all_50_50','natural','history'):
                rs=base if source=='all_50_50' else [r for r in base if r['source']==source]
                tables.append(summarize_atomic(rs,seed=seed,method=method,source=source,grouping='source',stratum=source))
            for dimension in ('operation','state','current_correct'):
                for val in sorted({r[dimension] for r in base}):
                    rs=[r for r in base if r[dimension]==val]
                    tables.append(summarize_atomic(rs,seed=seed,method=method,source='all',grouping=dimension,stratum=val))
            for low,high in zip(bins,bins[1:]):
                rs=[r for r in base if low<=r['update_norm']<high]
                tables.append(summarize_atomic(rs,seed=seed,method=method,source='all',grouping='update_norm',stratum=f'[{low},{high})'))
            good=sum(all(r['joint'] for r in base if r['world_id']==w) for w in {r['world_id'] for r in base})
            boundaries.append(dict(seed=seed,method=method,world_all_24_operations_numerator=good,world_denominator=64,Wilson95=wilson(good,64)))
    csv_write(ROOT/'results/selected_validation_atomic_summary.csv',tables)
    failure_components=[];cost=[]
    for seed in (42,43,44):
        for method in methods:
            rs=[r for r in records if r['seed']==seed and r['method']==method]
            failure_components.append(dict(seed=seed,method=method,denominator=1536,grammar_numerator=sum(r['grammar'] for r in rs),grammar_failed=sum(not r['grammar'] for r in rs),EOS_failed=sum(not r['EOS'] for r in rs),content_failed=sum(not r['content'] for r in rs),target_failed=sum(not r['target'] for r in rs),failure_categories_may_overlap=True))
    for item in lock['checkpoints']:
        meta=read(Path(item['path']).parent/'TRAINING_COMPLETE.json')
        cost.append(dict(seed=item['seed'],method=item['method'],updates=400,parameters=meta['editor_parameters'],train_wall_seconds=meta['wall_seconds'],student_forwards=400*meta['student_forwards_per_update'],teacher_forwards=400*meta['teacher_forwards_per_update'],backwards=400*meta['backwards_per_update'],checkpoint_sha256=item['sha256'],reused_completed_Plain=item['method']=='Plain',allocation_GPU_hours_in_resource_ledger=True))
    csv_write(ROOT/'results/selected_validation_failure_components.csv',failure_components)
    csv_write(ROOT/'results/selected_training_costs.csv',cost)
    comparisons=[]
    for a,b in [('Mechanism-guided','Output-only'),('Mechanism-guided','Random-site'),('Output-only','Plain'),('Random-site','Plain')]:
        result=paired_bootstrap(records,a,b)
        per_seed={}
        for seed in (42,43,44):
            rs=[r for r in records if r['seed']==seed]
            per_seed[str(seed)]=paired_bootstrap(rs,a,b)
        comparisons.append(dict(a=a,b=b,primary_family=a=='Mechanism-guided',scope='EXPLORATORY_VALIDATION_ONLY',**result,per_seed=per_seed))
    adjusted=holm([r['p_value'] for r in comparisons if r['primary_family']])
    for r,p in zip([r for r in comparisons if r['primary_family']],adjusted):r['Holm_adjusted_p']=p
    dump(ROOT/'results/SELECTED_VALIDATION_NUMERICAL_AUDIT.json',dict(records=len(records),worlds=64,methods=methods,fixed_seeds=[42,43,44],atomic=tables,world_boundary_intervals=boundaries,comparisons=comparisons,failure_components=failure_components,training_costs=cost,test_evaluations=0,confirmation_status='BLOCKED_TEST_INTEGRITY',checkpoint_lock_sha256=sha(ROOT/'configs/FINAL_METHOD_CHECKPOINT_LOCK.json')))
    status=read(ROOT/'results/main_method_status.json');status['executed_methods']=methods;status['unavailable']=[]
    status['validation_comparisons_path']='SELECTED_VALIDATION_NUMERICAL_AUDIT.json'
    status['confirmatory_family_executed']=False
    dump(ROOT/'results/main_method_status.json',status)
    print(json.dumps(dict(overall=[r for r in tables if r['grouping']=='source' and r['source']=='all_50_50'],comparisons=[{k:r[k] for k in ('a','b','estimate','CI95')} for r in comparisons]),ensure_ascii=False))


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--lock',action='store_true');p.add_argument('--summarize',action='store_true');args=p.parse_args()
    if args.lock:checkpoint_lock()
    if args.summarize:summarize()
