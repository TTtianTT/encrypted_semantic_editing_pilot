"""Per-world uncertainty, rank curves and failure/probe summaries."""
from collections import defaultdict,Counter
from shared import *

def cluster(values):
    # Caller first averages repeated transitions/directions within each world.
    return dict(n_worlds=len(values),mean=float(np.mean(values)) if values else None,ci95=bootstrap_mean(values))

def main():
    verify();groups=defaultdict(list)
    for r in stream(ROOT/'results/evaluation.jsonl'):groups[r['panel'],r['model'],r['template']].append(r)
    singles=[];chains=[];residual=[]
    for (panel,model,t),rs in groups.items():
        spec={k:rs[0][k] for k in ('kind','condition','rank','seed')}
        if panel=='single':
            for cohort in ('all_legal','mask_aligned'):
                rr=[r for r in rs if cohort=='all_legal' or r['aligned']]
                for metric in ('success','target','preserved'):
                    byworld=defaultdict(list)
                    for r in rr:byworld[r['world_id']].append(r['output']['score'][metric])
                    singles.append(dict(model=model,template=t,cohort=cohort,metric=metric,**spec,n_transitions=len(rr),**cluster([np.mean(v) for v in byworld.values()])))
            aligned=[r for r in rs if r['aligned']]
            for op in ('plus','minus'):
                rr=[r for r in aligned if r['operation']==op]
                for basis_seed in SEEDS:
                    byworld=defaultdict(list);total=defaultdict(list)
                    for r in rr:
                        byworld[r['world_id']].append(r['S_coordinate_mse'][str(basis_seed)]);total[r['world_id']].append(r['token_mse'])
                    residual.append(dict(model=model,template=t,operation=op,basis_seed=basis_seed,**spec,S_mse=float(np.mean([np.mean(v) for v in byworld.values()])),token_mse=float(np.mean([np.mean(v) for v in total.values()])),n_worlds=len(byworld)))
        else:
            for seq in read(ROOT/'protocol.json')['sequences']:
                rr=[r for r in rs if r['sequence']==seq]
                for step in range(1,6):
                    success=rate(r['full_trajectory'][step-1] for r in rr)
                    prior=[r for r in rr if step==1 or r['full_trajectory'][step-2]]
                    cond=rate(r['step_successes'][step-1] for r in prior)
                    endpoint=rate(r['step_successes'][step-1] for r in rr)
                    chains.append(dict(model=model,template=t,sequence=seq,step=step,**spec,**success,conditional_n=cond['n'],conditional_k=cond['k'],conditional_rate=cond['rate'],conditional_ci95=cond['ci95'],endpoint_rate=endpoint['rate']))
    csvwrite('results/single_summary.csv',singles);csvwrite('results/chain_summary.csv',chains);csvwrite('results/residual_summary.csv',residual)
    controls=defaultdict(list)
    for r in stream(ROOT/'results/matched_controls.jsonl'):controls[r['seed'],r['context'],r['condition']].append(r)
    controlsummary=[]
    for (seed,context,condition),rs in controls.items():
        byworld=defaultdict(list)
        for r in rs:byworld[r['world_id']].append(r)
        summary=dict(seed=seed,context=context,condition=condition,n_worlds=len(byworld),n_directions=4 if condition.startswith('random') else 1,
                     mean_norm=float(np.mean([r['norm'] for r in rs])))
        for metric in ('current_exact','current_success','next_success'):
            def value(r):return r['current_exact'] if metric=='current_exact' else r['current' if metric=='current_success' else 'next']['score']['success']
            x=[float(np.mean([value(r) for r in rr])) for rr in byworld.values()]
            summary[metric]=float(np.mean(x));summary[metric+'_ci95']=bootstrap_mean(x)
            if summary['n_directions']==1:summary[metric+'_ci95']=previous.binomial_ci(int(sum(x)),len(x))
        current=[r for r in rs if r['current']['score']['success']]
        summary['conditional_next_n']=len(current);summary['conditional_next_rate']=np.mean([r['next']['score']['success'] for r in current]) if current else None
        controlsummary.append(summary)
    csvwrite('results/matched_control_summary.csv',controlsummary)
    calibration=defaultdict(list)
    for r in stream(ROOT/'results/probe_calibration.jsonl'):calibration[r['seed'],r['template'],r['component']].append(r)
    cal=[]
    for (seed,t,component),rs in calibration.items():
        byworld=defaultdict(list)
        for r in rs:byworld[r['world_id']].append(r['correct'])
        cal.append(dict(seed=seed,template=t,component=component,**cluster([np.mean(v) for v in byworld.values()])))
    csvwrite('results/probe_calibration_summary.csv',cal)
    probes=defaultdict(list)
    for r in stream(ROOT/'results/probe_states.jsonl'):probes[r['seed'],r['context']].append(r)
    ps=[]
    for (seed,context),rs in probes.items():
        out=dict(seed=seed,context=context,n_worlds=len(rs))
        for component in ('full','S','complement'):
            for role,state in [('target',0),('source',1)]:
                rr=rate(r[component+'_prediction']==state for r in rs);out[component+'_'+role+'_rate']=rr['rate'];out[component+'_'+role+'_ci95']=rr['ci95']
            out[component+'_margin']=np.mean([r[component+'_margin'] for r in rs])
        for field in ('shared_S_contribution','shared_complement_contribution','shared_bias'):out[field]=np.mean([r[field] for r in rs])
        ps.append(out)
    csvwrite('results/probe_state_summary.csv',ps)
    failures=defaultdict(list)
    for r in stream(ROOT/'results/failure_categories.jsonl'):failures[r['panel'],r['seed'],r['model'],r['template'],r['sequence'],r['step']].append(r)
    fs=[]
    for (panel,seed,model,t,seq,step),rs in failures.items():
        counts=Counter(r['category'] for r in rs);nfail=len(rs)-counts['success']
        for category,n in counts.items():fs.append(dict(panel=panel,seed=seed,model=model,template=t,sequence=seq,step=step,category=category,count=n,total=len(rs),failures=nfail,fraction_of_failures=n/nfail if nfail and category!='success' else None))
    csvwrite('results/failure_summary.csv',fs)
    dump('results/analyze_complete.json',dict(training_updates=0,chain_rows=len(chains),single_rows=len(singles),world_clustered_intervals=True))
    print('Summarized rank curves, conditional continuation, controls and probes.')

if __name__=='__main__':main()
