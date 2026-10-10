"""Derived world-level estimates; this script does not change locked inference."""
from cutil import *

def clustered(rs,fn):
    by=defaultdict(list)
    for r in rs:by[r['world_id']].append(fn(r))
    v=[float(np.mean(x)) for x in by.values()]
    return dict(mean=float(np.mean(v)),worlds=len(v),ci95_world_bootstrap=old.bootstrap_mean(v))
def main():
    # Post-hoc stability explanation after seeing finite closure drift; no refit.
    fs=load(PRIOR/'local/rrr.pt');maps={op:torch.eye(768,dtype=torch.float64)+fs['iid_only',op,16]['left'].double()@fs['iid_only',op,16]['right'].double() for op in ('plus','minus')};spectrum=[]
    cycles={'original_alternating':['plus','minus'],'aligned_from_plus_one':['plus','plus','minus','minus'],'aligned_from_minus_one':['minus','minus','plus','plus']}
    for name,ops in cycles.items():
        a=torch.eye(768,dtype=torch.float64)
        for op in ops:a=a@maps[op]
        ev=torch.linalg.eigvals(a);rho=float(ev.abs().max());spectrum.append(dict(path=name,cycle_length=len(ops),spectral_radius=rho,asymptotic_per_step_radius=rho**(1/len(ops)),unstable_eigenvalues=int((ev.abs()>1+1e-6).sum()),post_hoc=True))
    dump('results/closure_spectrum.json',spectrum)
    if (ROOT/'results/closure.jsonl').exists():
        rs=rows(ROOT/'results/closure.jsonl');out=[]
        for t in (0,3):
          for path in read(ROOT/'protocol.json')['closure']['paths']:
            cycle=2 if path=='original_alternating' else 4
            subset=[r for r in rs if r['template']==t and r['path']==path]
            by=defaultdict(list)
            for r in subset:by[r['world_id']].append(r)
            for phase in range(cycle):
                slopes=[];ratios=[];last=[];lopes=[]
                for v in by.values():
                    z=sorted([r for r in v if (r['step']-1)%cycle==phase],key=lambda x:x['step']);k=np.array([r['step'] for r in z]);rms=np.sqrt([r['token_mse'] for r in z]);slopes.append(float(np.polyfit(k,rms,1)[0]));lopes.append(float(np.polyfit(k,np.log(rms),1)[0]));ratios.append(float(rms[-1]/rms[0]));last.append(float(rms[-1]))
                out.append(dict(template=t,path=path,phase=phase+1,worlds=80,mean_rms_slope_per_step=float(np.mean(slopes)),slope_ci95_world_bootstrap=old.bootstrap_mean(slopes),mean_log_rms_slope_per_step=float(np.mean(lopes)),mean_last_first_rms_ratio=float(np.mean(ratios)),mean_last_rms=float(np.mean(last))))
        write('results/closure_growth.jsonl',out)
    if (ROOT/'results/overshoot.jsonl').exists():
        rs=rows(ROOT/'results/overshoot.jsonl');out=[]
        for seed in SEEDS:
          for t in (0,3):
            v=[r for r in rs if r['seed']==seed and r['template']==t]
            out.append(dict(seed=seed,template=t,joint_overshoot=clustered(v,lambda r:float(r['joint_overshoot'])),coefficient=clustered(v,lambda r:r['projection_coefficient']),logp_token_gain=clustered(v,lambda r:r['ce_logp_token']-r['canonical_logp_token']),orthogonal_norm=clustered(v,lambda r:r['orthogonal_norm'])))
        dump('results/overshoot_clustered.json',out)
    if (ROOT/'results/single.jsonl').exists():
        rs=rows(ROOT/'results/single.jsonl');summary=[]
        for g in ('C1','C2','C3','C4','C5'):
          for seed in SEEDS:
            for t in (0,3):
              for scope in ('aligned','all_legal'):
                v=[r for r in rs if r['group']==g and r['seed']==seed and r['checkpoint']==600 and r['template']==t and (scope=='all_legal' or r['aligned'])]
                aligned=[r for r in v if r['aligned']]
                summary.append(dict(group=g,seed=seed,template=t,scope=scope,success=clustered(v,lambda r:r['output']['score']['success']),preserved=clustered(v,lambda r:r['output']['score']['preserved']),token_mse=clustered(aligned,lambda r:r['token_mse']),own_frozen_S_mse=clustered(aligned,lambda r:r['S_coordinate_mse'][str(seed)])))
        dump('results/final_single_clustered.json',summary)
    if (ROOT/'results/mixsingle_summary.json').exists():
        rs=read(ROOT/'results/mixsingle_summary.json');summary=[]
        for seed in SEEDS:
          for t in (0,3):
            for lam in read(ROOT/'protocol.json')['dose']['lambdas']:
                v=[r for r in rs if r['seed']==seed and r['template']==t and r['lambda_']==lam]
                summary.append(dict(seed=seed,template=t,lambda_=lam,min_single_transition_success=min(r['success']['rate'] for r in v),min_single_transition_preservation=min(r['preserved']['rate'] for r in v)))
        dump('results/dose_single_minima.json',summary)
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        chain=read(ROOT/'results/dose_summary.json');fig,axes=plt.subplots(2,3,figsize=(13,7),sharex=True,sharey=True)
        for row,t in enumerate((0,3)):
          for col,seed in enumerate(SEEDS):
            ax=axes[row,col]
            for path,label in [('aligned_from_plus_one','R5 aligned +1'),('aligned_from_minus_one','R5 aligned -1')]:
              z=sorted([r for r in chain if r['seed']==seed and r['template']==t and r['path']==path and r['step']==5],key=lambda r:r['lambda_']);ax.plot([r['lambda_'] for r in z],[r['trajectory']['rate'] for r in z],'o-',label=label)
            z=sorted([r for r in summary if r['seed']==seed and r['template']==t],key=lambda r:r['lambda_']);ax.plot([r['lambda_'] for r in z],[r['min_single_transition_success'] for r in z],'s--',label='worst aligned atomic cell')
            ax.set(title=f'seed {seed}, template {t}',ylim=(-.03,1.03),xlabel='RRR mixture weight',ylabel='success rate')
        axes[0,0].legend(fontsize=8);fig.tight_layout();fig.savefig(ROOT/'results/dose_atomic_guard.svg');fig.savefig(ROOT/'results/dose_atomic_guard.png',dpi=160);plt.close(fig)
    if (ROOT/'results/chain_summary.json').exists():
        rs=read(ROOT/'results/chain_summary.json');idx={(r['group'],r['seed'],r['checkpoint'],r['template'],r['path'],r['step']):r for r in rs};conditional=[]
        for key,r in idx.items():
            step=key[-1];n=80 if step==1 else idx[(*key[:-1],step-1)]['trajectory']['k'];k=r['trajectory']['k']
            conditional.append(dict(**{a:r[a] for a in ('group','seed','checkpoint','template','path','step')},prefix_success_n=n,next_success_k=k,conditional_rate=k/n if n else None,ci95=old.previous.binomial_ci(k,n)))
        dump('results/conditional_continuation.json',conditional)
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        fig,axes=plt.subplots(2,3,figsize=(13,7));steps=read(ROOT/'protocol.json')['training']['evaluation_C4_checkpoints']
        for row,t in enumerate((0,3)):
          for seed in SEEDS:
            r=sorted([x for x in rs if x['group']=='C4' and x['seed']==seed and x['template']==t and x['path']=='aligned_from_plus_one' and x['step']==1],key=lambda x:x['checkpoint']);r5=sorted([x for x in rs if x['group']=='C4' and x['seed']==seed and x['template']==t and x['path']=='aligned_from_plus_one' and x['step']==5],key=lambda x:x['checkpoint'])
            axes[row,0].semilogy(steps,[x['token_mse'] for x in r],'o-',label=f'seed{seed}');axes[row,1].plot(steps,[x['trajectory']['rate'] for x in r],'o-');line=axes[row,2].plot(steps,[x['trajectory']['rate'] for x in r5],'o-')[0]
            axes[row,2].fill_between(steps,[x['trajectory']['ci95'][0] for x in r5],[x['trajectory']['ci95'][1] for x in r5],color=line.get_color(),alpha=.1)
          for col,label in enumerate(('first-step token MSE','R1','R5')):
            ax=axes[row,col];ax.set_xscale('symlog',linthresh=10);ax.set_xticks(steps);ax.set_xticklabels(steps,rotation=45,fontsize=8);ax.set(xlabel='CE updates from RRR initialization',ylabel=label,title=f'template {t}')
            if col:ax.set_ylim(-.03,1.03)
        axes[0,0].legend();fig.tight_layout();fig.savefig(ROOT/'results/c4_drift_early.svg');fig.savefig(ROOT/'results/c4_drift_early.png',dpi=160);plt.close(fig)

if __name__=='__main__':main()
