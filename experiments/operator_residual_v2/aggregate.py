"""Per-seed estimates, Wilson intervals, and paired world uncertainty."""
from core import *

def world_bootstrap(values,seed=202610111,nboot=2000):
    x=np.asarray(values,dtype=float)
    if not len(x):return None
    rng=np.random.default_rng(seed)
    return np.quantile(x[rng.integers(0,len(x),(nboot,len(x)))].mean(1),[.025,.975]).tolist()

def factorial():
    rs=rows(V1/'results/patches.jsonl');output=[]
    for seed in SEEDS:
        groups={method:[r for r in rs if r['seed']==seed and r['method']==method] for method in ('bad','read','perpendicular','full')}
        rates={k:sum(r['current_exact'] and r['next_success'] for r in v)/len(v) for k,v in groups.items()}
        for method,v in groups.items():
            successes=sum(r['current_exact'] and r['next_success'] for r in v)
            output.append(dict(seed=seed,method=method,N=len(v),successes=successes,rate=successes/len(v),ci95=binomial_ci(successes,len(v)),
                               factorial_interaction=rates['full']-rates['read']-rates['perpendicular']+rates['bad']))
    csvwrite('results/factorial_per_seed.csv',output)

def attribution():
    groups=defaultdict(list)
    for r in rows(ROOT/'results/attribution.jsonl'):
        groups[r['seed'],r['direction'],r['component'],r['alpha'],'real' if r['random_seed'] is None else 'random'].append(r)
    output=[];contrasts=[]
    for key,rs in sorted(groups.items()):
        worlds=defaultdict(list)
        for r in rs:worlds[r['world_id']].append(r)
        measurements={
            'current_exact':[np.mean([r['current_exact'] for r in v]) for v in worlds.values()],
            'next_success':[np.mean([r['next_success'] for r in v]) for v in worlds.values()],
            'repair_joint':[np.mean([r['current_exact'] and r['next_success'] for r in v]) for v in worlds.values()],
            'preserved_current_next_failure':[np.mean([r['current_exact'] and not r['next_success'] for r in v]) for v in worlds.values()]}
        out=dict(seed=key[0],direction=key[1],component=key[2],alpha=key[3],control=key[4],N=len(worlds),random_directions=0 if key[4]=='real' else 4,
                 mean_norm=float(np.mean([r['norm'] for r in rs])))
        for metric,values in measurements.items():
            estimate=float(np.mean(values));ci=binomial_ci(int(sum(values)),len(values)) if key[4]=='real' else world_bootstrap(values)
            out[metric]=estimate;out[metric+'_ci95']=ci
        output.append(out)
    for key in sorted({k[:4] for k in groups}):
        real=groups[key+('real',)];random=groups[key+('random',)];index=defaultdict(list)
        for r in random:index[r['world_id']].append(r)
        metric=(lambda r:r['current_exact'] and r['next_success']) if key[1]=='repair' else (lambda r:r['current_exact'] and not r['next_success'])
        deltas=[float(metric(r))-np.mean([metric(x) for x in index[r['world_id']]]) for r in real]
        contrasts.append(dict(seed=key[0],direction=key[1],component=key[2],alpha=key[3],N=len(real),real_minus_matched_random=float(np.mean(deltas)),ci95=world_bootstrap(deltas)))
    csvwrite('results/attribution_summary.csv',output);csvwrite('results/attribution_random_contrasts.csv',contrasts)

def visibility():
    grouped=defaultdict(list);rs=rows(ROOT/'results/visibility.jsonl')
    for r in rs:grouped[r['seed'],r['alpha'],'real' if r['random_seed'] is None else 'random'].append(r)
    summary=[]
    for key,vs in sorted(grouped.items()):
        index=defaultdict(list)
        for r in vs:index[r['world_id'],r['context']].append(r)
        ids=sorted({r['world_id'] for r in vs});pre=np.array([np.mean([r['KL'] for r in index[w,'pre']]) for w in ids]);post=np.array([np.mean([r['KL'] for r in index[w,'post']]) for w in ids])
        diff=post-pre
        summary.append(dict(seed=key[0],alpha=key[1],control=key[2],N=len(ids),KL_pre=float(pre.mean()),KL_post=float(post.mean()),
                             post_minus_pre=float(diff.mean()),difference_ci95=world_bootstrap(diff),post_over_pre=float(post.mean()/max(pre.mean(),1e-12)),
                             median_KL_pre=float(np.median(pre)),median_KL_post=float(np.median(post))))
    csvwrite('results/visibility_summary.csv',summary)

def generalization():
    groups=defaultdict(list)
    for r in rows(ROOT/'results/generalization.jsonl'):groups[r['target_seed'],str(r['basis_seed']),r['template']].append(r)
    out=[]
    for key,rs in sorted(groups.items()):
        compatible=[r for r in rs if r['same_mask']];cohort=[r for r in rs if r['eligible_mechanism']]
        def joint(r):return r['patched_current']['text']==r['reference_current']['text'] and r['patched_current']['score']['success'] and r['patched_next']['score']['success']
        k=sum(joint(r) for r in compatible);kc=sum(joint(r) for r in cohort)
        out.append(dict(target_seed=key[0],basis_seed=key[1],template=key[2],predefined=len(rs),compatible=len(compatible),mask_mismatch=len(rs)-len(compatible),
                         current_correct=sum(r['baseline_current']['score']['success'] for r in rs),canonical_next_correct=sum(r['reference_next']['score']['success'] for r in rs),
                         patched_joint_successes=k,compatible_rate=k/len(compatible) if compatible else None,ci95=binomial_ci(k,len(compatible)),
                         qualified_cohort=len(cohort),cohort_successes=kc,cohort_rate=kc/len(cohort) if cohort else None,
                         cohort_ci95=binomial_ci(kc,len(cohort))))
    csvwrite('results/generalization_summary.csv',out)

def predictions(features,name):
    groups=defaultdict(list)
    for r in features:
        groups[r['basis_seed'],r['split'],r['step']].append(r);groups[r['basis_seed'],r['split'],'pooled_steps'].append(r)
    out=[];paired=[]
    for key,rs in groups.items():
        metrics=['mahal','random_mahal']+(['reference_full_distance'] if 'reference_full_distance' in rs[0] else [])
        y=[r['failure'] for r in rs]
        index=defaultdict(list)
        for r in rs:index[r['world_id']].append(r)
        ids=sorted(index);samples={metric:[] for metric in metrics};deltas=[]
        if any(y) and not all(y):
            rng=np.random.default_rng(202610112)
            for _ in range(2000):
                sample=[r for i in rng.integers(0,len(ids),len(ids)) for r in index[ids[i]]];yy=[r['failure'] for r in sample]
                estimates={metric:auroc(yy,[r[metric] for r in sample]) for metric in metrics}
                if estimates['mahal'] is None:continue
                for metric,a in estimates.items():samples[metric].append(a)
                if 'reference_full_distance' in estimates:deltas.append(estimates['mahal']-estimates['reference_full_distance'])
        for metric in metrics:
            a=auroc(y,[r[metric] for r in rs]);out.append(dict(basis_seed=key[0],split=key[1],step=key[2],metric=metric,N=len(rs),failures=sum(y),auroc=a,
                                                             ci95=np.quantile(samples[metric],[.025,.975]).tolist() if samples[metric] else None,
                                                             status='one_class' if a is None else 'estimable'))
        if 'reference_full_distance' not in metrics or not any(y) or all(y):continue
        paired.append(dict(basis_seed=key[0],split=key[1],step=key[2],difference=auroc(y,[r['mahal'] for r in rs])-auroc(y,[r['reference_full_distance'] for r in rs]),
                           ci95=np.quantile(deltas,[.025,.975]).tolist()))
    csvwrite(f'results/{name}_auroc.csv',out);csvwrite(f'results/{name}_paired_auroc.csv',paired)

def projection():
    groups=defaultdict(list);features=[];next_features=[]
    for line in (ROOT/'results/projection.jsonl').open():
        r=json.loads(line)
        groups[r['seed'],r['template'],r['sequence'],r['method']].append({k:r[k] for k in ('world_id','full_trajectory')})
        if r['method']=='none':
            for k,step in enumerate(r['steps']):
                f=dict(dataset='natural_projection_panel',basis_seed=r['seed'],world_id=r['world_id'],split=f"template{r['template']}/{r['sequence']}",step=k+1,
                       failure=not r['step_successes'][k],mahal=step['mahal'],random_mahal=step['random_mahal'])
                features.append(f)
                if k<4 and all(r['step_successes'][:k+1]):next_features.append(dict(f,failure=not r['step_successes'][k+1]))
    output=[]
    for key,rs in sorted(groups.items()):
        worlds=defaultdict(list)
        for r in rs:worlds[r['world_id']].append(r)
        out=dict(seed=key[0],template=key[1],sequence=key[2],method=key[3],N=len(worlds),random_directions=4 if key[3]=='random_ridge' else 0)
        for length in range(1,6):
            values=[np.mean([r['full_trajectory'][length-1] for r in v]) for v in worlds.values()]
            out[f'R{length}']=float(np.mean(values));out[f'R{length}_ci95']=world_bootstrap(values) if key[3]=='random_ridge' else binomial_ci(int(sum(values)),len(values))
        output.append(out)
    csvwrite('results/projection_summary.csv',output);write('results/natural_prediction_features.jsonl',features);write('results/natural_next_prediction_features.jsonl',next_features)
    predictions(features,'natural_endpoint');predictions(next_features,'natural_next')
    costs=rows(ROOT/'results/projection_cost.jsonl');out=[]
    base=np.median([r['seconds'] for r in costs if r['method']=='reencode'])
    for method in ('none','ridge','reencode'):
        rs=[r for r in costs if r['method']==method];seconds=np.median([r['seconds'] for r in rs])
        out.append(dict(method=method,median_seconds_per_world=float(seconds/8),relative_to_reencoding=float(seconds/base),
                        encoder_calls=rs[0]['encoder_calls'],decoder_calls=rs[0]['decoder_calls'],generated_tokens=rs[0]['generated_tokens']))
    csvwrite('results/projection_cost_summary.csv',out)

def decoder():
    groups=defaultdict(list)
    for r in rows(ROOT/'results/decoder.jsonl'):groups[r['seed'],str(r['layer']),r['group'],r['condition']].append(r)
    out=[]
    for key,rs in sorted(groups.items()):
        k=sum(r['next_success'] for r in rs)
        out.append(dict(seed=key[0],layer=key[1],group=key[2],condition=key[3],N=len(rs),successes=k,rate=k/len(rs),ci95=binomial_ci(k,len(rs)),
                         mean_target_margin=float(np.mean([r['target_margin'] for r in rs])) if 'target_margin' in rs[0] else None,
                         mean_donor_recipient_query_shift=float(np.mean([r['donor_recipient_query_shift'] for r in rs])) if 'target_margin' in rs[0] else None))
    csvwrite('results/decoder_summary.csv',out)

def main():
    verify_protocol();factorial()
    for phase in ('interventions','projection','decoder'):assert (ROOT/f'results/{phase}_complete.json').exists(),phase+' not complete'
    attribution();visibility();generalization();projection();decoder()
    predictions(rows(ROOT/'results/g4_prediction_features.jsonl'),'g4')
    dump('results/aggregation_complete.json',dict(training_updates=0,all_required_panels_executed=True,protocol_sha256=sha(ROOT/'protocol.json'),code_sha256=sha(__file__)))
    print('All per-seed tables and paired estimates completed.')

if __name__=='__main__':main()
