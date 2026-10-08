"""CPU-only independent recomputation of executed validation evidence.

This module never loads a model/checkpoint and never changes split membership.
"""
from collections import Counter
import gzip
import numpy as np
from .common import *
from .analyze import csv_write, paired_bootstrap
from .metrics import wilson


def stage_folder(stage, seed=42, model='bart'):
    return Path(read(ROOT/f'manifests/{stage}.json')['output_root'])/f'{model}_s{seed}'


def summarize_atomic(rs, **keys):
    n=len(rs)
    out=dict(**keys, status='EXPLORATORY_VALIDATION', records=n,
             independent_worlds=len({r['world_id'] for r in rs}))
    for field in ('joint','target','content','parseable','EOS','exact_match'):
        good=sum(r[field] for r in rs)
        out.update({field+'_numerator':good,field+'_denominator':n,
                    field+'_rate':good/n if n else None})
    out['mean_update_norm']=float(np.mean([r['update_norm'] for r in rs])) if n else None
    return out


def run():
    atomics=[];chains=[];source_hashes={}
    for seed in (42,43,44):
        pf=stage_folder('S3_PLAIN',seed);vf=stage_folder('S3_VALIDATION_TRAJECTORIES',seed)
        pp=pf/'Plain/Plain_validation.jsonl';source_hashes[str(pp)]=sha(pp)
        for r in rows(pp):
            p=r['prediction'];s=p['score']
            atomics.append(dict(world_id=r['world_id'],seed=seed,method='Plain',
                source=r['source'],state=r['state'],operation=r['operation'],
                current_correct=r['current']['score']['success'],joint=s['success'],
                target=s['target'],content=s['preserved'],parseable=s['parseable'],
                EOS=p['ended'],exact_match=p['text']==p['gold_text'],update_norm=r['update_norm']))
        for path in sorted(vf.glob('*_editing.jsonl')):
            source_hashes[str(path)]=sha(path)
            for r in rows(path):
                p=r['prediction']
                atomics.append({k:r[k] for k in ('world_id','seed','method','source','state',
                    'operation','current_correct','joint','target','content','parseable','EOS','update_norm')} |
                    dict(exact_match=p['text']==p['gold_text']))
        for path in sorted(vf.glob('*_trajectories.jsonl')):
            source_hashes[str(path)]=sha(path)
            for r in rows(path):
                for length in (1,2,3,5):
                    good=all(s['prediction']['score']['success'] for s in r['steps'][:length])
                    assert good==r['length_success'][str(length)]
                    chains.append(dict(world_id=r['world_id'],seed=seed,method=r['method'],
                        order=r['order'],direction=r['direction'],length=length,success=good,
                        step_joint=r['steps'][length-1]['prediction']['score']['success'],
                        step_content=r['steps'][length-1]['prediction']['score']['preserved'],
                        step_EOS=r['steps'][length-1]['prediction']['ended']))
    assert len(atomics)==9216 and len(chains)==6144
    jsonl(ROOT/'results/validation_atomic_recomputed.jsonl',atomics)
    jsonl(ROOT/'results/validation_trajectories_recomputed.jsonl',chains)
    for name in ('validation_atomic_recomputed','validation_trajectories_recomputed'):
        path=ROOT/f'results/{name}.jsonl'
        atomic(path.with_suffix('.jsonl.gz'),gzip.compress(path.read_bytes(),mtime=0));path.unlink()
    tables=[]
    for seed in (42,43,44):
        for method in ('Original','Plain'):
            base=[r for r in atomics if r['seed']==seed and r['method']==method]
            assert len(base)==1536 and len({r['world_id'] for r in base})==64
            for source in ('all_50_50','natural','history'):
                rs=base if source=='all_50_50' else [r for r in base if r['source']==source]
                tables.append(summarize_atomic(rs,seed=seed,method=method,source=source,
                    grouping='source',stratum=source))
            for dimension in ('operation','state','current_correct'):
                for val in sorted({r[dimension] for r in base}):
                    rs=[r for r in base if r[dimension]==val]
                    tables.append(summarize_atomic(rs,seed=seed,method=method,source='all',
                        grouping=dimension,stratum=val))
    csv_write(ROOT/'results/validation_atomic_summary.csv',tables)
    trajectories=[]
    for seed in (42,43,44):
        for method in ('Original','Plain'):
            for length in (1,2,3,5):
                rs=[r for r in chains if r['seed']==seed and r['method']==method and r['length']==length]
                assert len(rs)==256
                world_values={w:np.mean([r['success'] for r in rs if r['world_id']==w])
                    for w in sorted({r['world_id'] for r in rs})}
                all_world=int(sum(v==1 for v in world_values.values()))
                trajectories.append(dict(seed=seed,method=method,length=length,
                    complete_numerator=sum(r['success'] for r in rs),trajectory_denominator=256,
                    rate=float(np.mean(list(world_values.values()))),independent_worlds=64,
                    all_orders_world_numerator=all_world,all_orders_world_denominator=64,
                    all_orders_world_Wilson95=wilson(all_world,64),
                    step_joint_numerator=sum(r['step_joint'] for r in rs),
                    step_content_numerator=sum(r['step_content'] for r in rs),
                    step_EOS_numerator=sum(r['step_EOS'] for r in rs),
                    status='EXPLORATORY_VALIDATION_ONLY'))
    csv_write(ROOT/'results/validation_trajectory_summary.csv',trajectories)
    stratified=[]
    for seed in (42,43,44):
        for method in ('Original','Plain'):
            for length in (1,2,3,5):
                for order in (0,1):
                    for direction in ('forward','inverse'):
                        rs=[r for r in chains if (r['seed'],r['method'],r['length'],r['order'],r['direction'])==(seed,method,length,order,direction)]
                        stratified.append(dict(seed=seed,method=method,length=length,order=order,
                            direction=direction,numerator=sum(r['success'] for r in rs),denominator=len(rs),
                            status='EXPLORATORY_VALIDATION_ONLY'))
    csv_write(ROOT/'results/validation_trajectory_by_direction.csv',stratified)
    bootstrap={field:paired_bootstrap(atomics,'Plain','Original',field=field) for field in ('joint','target','content')}
    # Bootstrap already clusters all operations, sources and fixed training seeds by world.
    trajectory_bootstrap={}
    for length in (1,2,3,5):
        adapted=[dict(world_id=r['world_id'],method=r['method'],source=s,joint=r['success'])
            for r in chains if r['length']==length for s in ('natural','history')]
        # Duplicated source labels solely reuse the equal-weight bootstrap function.
        # There are no history-start trajectories; each world's value is unchanged.
        result=paired_bootstrap(adapted,'Plain','Original')
        result['source_interpretation']='natural starts only; two labels above are identical copies, not independent sources'
        trajectory_bootstrap[str(length)]=result
    missing=[dict(method=m,seed=s,status='BLOCKED_MASK_REVIEW',joint=None,target=None,content=None,
        reason='human keep-slot review required by protocol 6.2; no reviewed lock')
        for m in ('Output-only','Mechanism-guided','Random-site') for s in (42,43,44)]
    dump(ROOT/'results/main_method_status.json',dict(executed_methods=['Original','Plain'],
        unavailable=missing,comparisons=[dict(a='Mechanism-guided',b=b,status='NOT_ESTIMABLE_NOT_RUN',
        estimate=None,CI95=None,p_value=None,Holm_adjusted_p=None) for b in ('Output-only','Random-site')],
        confirmatory_family_executed=False))
    audit=dict(atomic_rows=9216,trajectory_length_rows=6144,worlds=64,fixed_training_seeds=[42,43,44],
        atomic=tables,trajectories=trajectories,paired_cluster_bootstrap=bootstrap,
        paired_trajectory_bootstrap=trajectory_bootstrap,source_sha256=source_hashes,
        bootstrap_scope='20,000 paired world-cluster draws; exploratory validation; fixed three seeds',
        independent_test_scans=0,confirmation_status='BLOCKED_TEST_INTEGRITY')
    dump(ROOT/'results/VALIDATION_NUMERICAL_AUDIT.json',audit)
    # Recalculate literal NEXT_EDIT_FORK separately from legacy correctness XOR.
    bridge=[]
    for model,stage in [('bart','S1_NATIVE'),('t5gemma','T5_QUALIFICATION')]:
        f=stage_folder(stage,model=model)
        paths=sorted(f.glob('*_bridge.jsonl')) if model=='bart' else [f/'bridge.jsonl']
        for path in paths:
            for r in rows(path):
                a=r.get('a_next',r.get('a'));b=r.get('b_next',r.get('b'))
                bridge.append(dict(model=model,world_id=r['world_id'],split=r['split'],
                    source_pair=r['source_pair'],operation=r['operation'],
                    native_token_fork=a['token_ids']!=b['token_ids'],
                    raw_text_fork=a['text']!=b['text'],
                    accuracy_fork=a['score']['success']!=b['score']['success'],
                    a_next_joint=a['score']['success'],b_next_joint=b['score']['success']))
    csv_write(ROOT/'results/next_edit_bridge_recomputed.csv',bridge)
    grouped=[]
    for model,split in sorted({(r['model'],r['split']) for r in bridge}):
        rs=[r for r in bridge if (r['model'],r['split'])==(model,split)]
        grouped.append(dict(model=model,split=split,records=len(rs),independent_worlds=len({r['world_id'] for r in rs}),
            next_native_token_fork=sum(r['native_token_fork'] for r in rs),
            next_raw_text_fork=sum(r['raw_text_fork'] for r in rs),
            legacy_accuracy_fork=sum(r['accuracy_fork'] for r in rs),
            a_next_joint=sum(r['a_next_joint'] for r in rs),b_next_joint=sum(r['b_next_joint'] for r in rs)))
    csv_write(ROOT/'results/next_edit_bridge_summary.csv',grouped)
    dump(ROOT/'results/BRIDGE_DEFINITION_AUDIT.json',dict(definition='A plus different next native output tokens',
        legacy='old worker panel_B field stored correctness XOR; immutable raw runs retained',summary=grouped))
    print(json.dumps(dict(atomic_overall=[r for r in tables if r['grouping']=='source' and r['source']=='all_50_50'],
        trajectories=trajectories,bridge=grouped),ensure_ascii=False))


if __name__=='__main__':run()
