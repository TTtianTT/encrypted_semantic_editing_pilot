"""World-aware summary tables and standalone publication figures."""
from cutil import *

def mean(v):return float(np.mean(v)) if v else None
def metric_summary(rs):
    ms=[r['token_mse'] for r in rs if r.get('aligned')];return dict(n=len(rs),success=old.rate(r['output']['score']['success'] for r in rs),preserved=old.rate(r['output']['score']['preserved'] for r in rs),trajectory=old.rate(r['trajectory_success'] for r in rs) if 'trajectory_success' in rs[0] else None,aligned_n=len(ms),token_mse=mean(ms),S_coordinate_mse={str(s):mean([r['S_coordinate_mse'][str(s)] for r in rs if r.get('aligned')]) for s in SEEDS})
def main():
    allsum={}
    for kind,keys in [('closure',['template','path','step']),('dose',['seed','lambda_','template','path','step']),('mixsingle',['seed','lambda_','template','source_state','operation']),('chain',['group','seed','checkpoint','template','path','step']),('single',['group','seed','checkpoint','template','source_state','operation'])]:
        if not (ROOT/f'results/{kind}.jsonl').exists():continue
        rs=rows(ROOT/f'results/{kind}.jsonl');summary=aggregate(rs,keys,metric_summary);dump(f'results/{kind}_summary.json',summary);allsum[kind]=summary
    if (ROOT/'results/overshoot.jsonl').exists():
        rs=rows(ROOT/'results/overshoot.jsonl')
        def over(v):return dict(n=len(v),joint_overshoot=old.rate(r['joint_overshoot'] for r in v),mean_coefficient=mean([r['projection_coefficient'] for r in v]),positive_projection=old.rate(r['projection_coefficient']>0 for r in v),mean_logp_token_gain=mean([r['ce_logp_token']-r['canonical_logp_token'] for r in v]),higher_confidence=old.rate(r['ce_logp_token']>r['canonical_logp_token'] for r in v),mean_orthogonal_norm=mean([r['orthogonal_norm'] for r in v]),mean_residual_norm=mean([r['residual_norm'] for r in v]))
        summary=aggregate(rs,['seed','template'],over);dump('results/overshoot_summary.json',summary);allsum['overshoot']=summary
    if (ROOT/'results/injection.jsonl').exists():
        def inj(v):
            eligible=[r for r in v if r['current']['score']['success'] and r['baseline_next']['score']['success']]
            retained=[r for r in eligible if r['injected_current']['score']['success']]
            return dict(n=len(v),baseline_eligible=len(eligible),current_preservation=old.rate(r['injected_current']['score']['success'] for r in eligible),conditional_next_failure=old.rate(not r['injected_next']['score']['success'] for r in retained),unconditional_next_success=old.rate(r['injected_next']['score']['success'] for r in v))
        summary=aggregate(rows(ROOT/'results/injection.jsonl'),['group','seed','template'],inj);dump('results/injection_summary.json',summary);allsum['injection']=summary
    plots(allsum);dump('results/summary.json',allsum)
    lines=['# Canonical-objective experiment (exploratory)','',f'Protocol SHA256: `{sha(ROOT/"protocol.json")}`. Historical 80 worlds; no independent confirmation.','',
      'Fixed rank 16; seeds 42/43/44; 600 updates, batch 8, AdamW lr 0.001 per group/seed. All 96 training worlds, template 0 only. C2/C3 L2 is divided by train ideal-write energy; coefficients for normalized L2 and continuation KL are 1. No test-based hyperparameter or checkpoint selection.','',
      'Aligned paths were chosen post hoc in the preceding round and locked before this round. Original reordered source-0 paths cross length-changing transitions unsupported by C1–C4. C5 has all legal transitions. Rk denotes complete trajectory through k, not endpoint success. Wilson intervals are per seed and world; across-state rows must not be treated as independent worlds.','']
    if 'closure' in allsum:
        lines+=['## Finite closure check','', '| Template | Cycle | step | full success / 80 | token MSE |','|---|---|---:|---:|---:|']
        for r in allsum['closure']:
            if r['step'] in (1,10,20,50):lines.append(f"| {r['template']} | {r['path']} | {r['step']} | {r['trajectory']['k']}/{r['n']} | {r['token_mse']:.6g} |")
        lines+=['','Finite bounded residuals do not prove arbitrary-length closure. Decoding and residuals are recorded at every step.','']
    if 'overshoot' in allsum:
        lines+=['## Overshoot','', '| seed | template | mean projection coefficient | mean token logp gain | joint overshoot |','|---:|---:|---:|---:|---:|']
        for r in allsum['overshoot']:lines.append(f"| {r['seed']} | {r['template']} | {r['mean_coefficient']:.5g} | {r['mean_logp_token_gain']:.5g} | {r['joint_overshoot']['rate']:.1%} |")
        lines+=['','Repeated transitions of a world are correlated. These are descriptive proportions, not independent binomial observations. Joint positive direction projection and higher likelihood supports overshoot in these states; C4 is needed to test active drift under CE.','']
    if 'chain' in allsum:
        lines+=['## Final complete trajectories','', '| group | seed | template | path | R1 | R2 | R3 | R4 | R5 [95% Wilson] |','|---|---:|---:|---|---:|---:|---:|---:|---|']
        selected=[r for r in allsum['chain'] if r['checkpoint']==600];g=defaultdict(dict)
        for r in selected:g[r['group'],r['seed'],r['template'],r['path']][r['step']]=r
        for key,v in sorted(g.items()):
            x=v[5]['trajectory'];ci=x['ci95'];lines.append('| '+' | '.join(map(str,key))+' | '+' | '.join(f"{v[k]['trajectory']['rate']:.1%}" for k in range(1,5))+f" | {x['rate']:.1%} [{ci[0]:.1%}, {ci[1]:.1%}] |")
        lines+=['','## C4 drift','', '| seed | update | IID aligned +1 R1 | R5 | first-step token MSE |','|---:|---:|---:|---:|---:|']
        indexed={(r['seed'],r['checkpoint'],r['step']):r for r in allsum['chain'] if r['group']=='C4' and r['template']==0 and r['path']=='aligned_from_plus_one'}
        for seed in SEEDS:
            for ck in read(ROOT/'protocol.json')['training']['evaluation_C4_checkpoints']:
                a=indexed[seed,ck,1];b=indexed[seed,ck,5];lines.append(f"| {seed} | {ck} | {a['trajectory']['rate']:.1%} | {b['trajectory']['rate']:.1%} | {a['token_mse']:.6g} |")
        lines+=['','Detailed single-step preservation, frozen-S coordinate residuals, per-transition intervals, other C4 paths, injection eligibility and subspace energy/eigengaps are in the linked result tables. Near-zero residuals or small eigengaps make principal angles hard to interpret.','',
          '[Single edits](results/single_summary.json) · [Trajectories](results/chain_summary.json) · [S intervention](results/injection_summary.json) · [PCA energy/gap](results/residual_pca.csv) · [Cross-seed angles](results/cross_seed_angles.jsonl)','']
    lines+=['## Figures','', '![Dose](results/dose.svg)','', '![C4](results/c4_drift.svg)','', '![Closure](results/closure.svg)','',
      '## Limits and confirmation','', 'One fixed budget and coefficient cannot rule out optimization difficulty or establish a universal benefit of an objective. C1 changes coverage relative to historical CE; C4 directly tests drift from the canonical initializer under this optimizer. C2 failure at 600 updates does not establish SGD impossibility. C5 trains one-step distributional equivalence, which does not guarantee arbitrary-length equivalence.','',
      'Final confirmation requires five seeds and freshly generated worlds under a locked selected method. It is not part of this exploratory run. Computational savings are not the claimed motivation; previous reencoding was already inexpensive.','']
    (ROOT/'REPORT.md').write_text('\n'.join(lines))

def plots(s):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    if 'dose' in s:
        fig,ax=plt.subplots(2,2,figsize=(10,7))
        for j,t in enumerate((0,3)):
          for seed in SEEDS:
            rs=[r for r in s['dose'] if r['seed']==seed and r['template']==t and r['path']=='aligned_from_plus_one' and r['step']==5];rs.sort(key=lambda r:r['lambda_'])
            ax[0,j].plot([r['lambda_'] for r in rs],[r['trajectory']['rate'] for r in rs],'o-',label=f'seed{seed}')
            ax[1,j].semilogy([r['lambda_'] for r in rs],[r['S_coordinate_mse'][str(seed)] for r in rs],'o-')
          ax[0,j].set(title=f'template {t}, aligned +1',ylabel='R5',ylim=(-.03,1.03));ax[0,j].legend();ax[1,j].set(xlabel='RRR mixture weight',ylabel='step-5 frozen-S coordinate MSE')
        fig.tight_layout();fig.savefig(ROOT/'results/dose.svg');plt.close(fig)
    if 'chain' in s:
        fig,ax=plt.subplots(1,3,figsize=(13,3.6))
        for seed in SEEDS:
            rs=[r for r in s['chain'] if r['group']=='C4' and r['seed']==seed and r['template']==0 and r['path']=='aligned_from_plus_one'];a=sorted([r for r in rs if r['step']==1],key=lambda r:r['checkpoint']);b=sorted([r for r in rs if r['step']==5],key=lambda r:r['checkpoint'])
            ax[0].semilogy([r['checkpoint'] for r in a],[r['token_mse'] for r in a],'o-',label=f'seed{seed}');ax[1].plot([r['checkpoint'] for r in a],[r['trajectory']['rate'] for r in a],'o-');ax[2].plot([r['checkpoint'] for r in b],[r['trajectory']['rate'] for r in b],'o-')
        for a,label in zip(ax,['first-step token MSE','R1','R5']):a.set(xlabel='CE updates from RRR',ylabel=label)
        ax[0].legend();fig.tight_layout();fig.savefig(ROOT/'results/c4_drift.svg');plt.close(fig)
    if 'closure' in s:
        fig,ax=plt.subplots(1,2,figsize=(10,3.5))
        for j,t in enumerate((0,3)):
            for path in read(ROOT/'protocol.json')['closure']['paths']:
                rs=sorted([r for r in s['closure'] if r['template']==t and r['path']==path],key=lambda r:r['step']);ax[j].semilogy([r['step'] for r in rs],[r['token_mse'] for r in rs],label=path)
            ax[j].set(xlabel='step',ylabel='token MSE',title=f'template {t}');ax[j].legend(fontsize=7)
        fig.tight_layout();fig.savefig(ROOT/'results/closure.svg');plt.close(fig)

if __name__=='__main__':main()
