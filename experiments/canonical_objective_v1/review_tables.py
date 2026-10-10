"""Derived world-level estimates; this script does not change locked inference."""
from cutil import *

def clustered(rs,fn):
    by=defaultdict(list)
    for r in rs:by[r['world_id']].append(fn(r))
    v=[float(np.mean(x)) for x in by.values()]
    return dict(mean=float(np.mean(v)),worlds=len(v),ci95_world_bootstrap=old.bootstrap_mean(v))
def main():
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

if __name__=='__main__':main()
