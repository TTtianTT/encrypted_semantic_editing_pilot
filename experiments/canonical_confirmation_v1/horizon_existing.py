"""Test, rather than assume, a scalar amplification-plus-forcing horizon."""
from futils import *
from scipy.optimize import least_squares
def main():
 rs=list(old.stream(EX/'results/closure.jsonl'));models={r['template']:r for r in read(ROOT/'results/continuation_risk_models.json') if r['metric']=='entering_token_mse'};spectra={r['path']:r['spectral_radius'] for r in read(EX/'results/closure_spectrum.json')};out=[]
 for t in (0,3):
  for path in ('original_alternating','aligned_from_plus_one','aligned_from_minus_one'):
   one=[r for r in rs if r['template']==t and r['path']==path];train=[r for r in one if int(hashlib.sha256(r['world_id'].encode()).hexdigest(),16)%2==0];test=[r for r in one if int(hashlib.sha256(r['world_id'].encode()).hexdigest(),16)%2==1];cycle=2 if path=='original_alternating' else 4;phases=[]
   for phase in range(1,cycle+1):
    steps=[k for k in range(1,51) if (k-1)%cycle==phase-1];fit_steps=[k for k in steps if k<=10];values=np.array([np.mean([np.sqrt(r['token_mse']) for r in train if r['step']==k]) for k in fit_steps]);a=float(values[0]);times=np.arange(len(values),dtype=float)
    rho=spectra[path]
    forcing=np.expm1(times*np.log(rho))/(rho-1);eta=max(0,float(forcing@(values-a*rho**times)/max(float(forcing@forcing),1e-30)))
    def curve(n):return a*rho**n+eta*np.expm1(n*np.log(rho))/(rho-1)
    tau=np.sqrt(models[t]['threshold_50']);predicted=curve(np.arange(len(steps)));first=next((k+1 for k,v in zip(steps,predicted) if v>tau),None)
    phases.append(dict(phase=phase,fit_steps=fit_steps,epsilon_first=a,rho_per_cycle=rho,rho_source='Exact full-cycle spectral radius; scalar proxy, not induced norm',forcing_per_cycle=eta,tau_RMS=tau,predicted_failure_entry_step=first,fit_relative_RMSE=float(np.sqrt(np.mean((curve(times)-values)**2))/a),last_observed_RMS=float(np.mean([np.sqrt(r['token_mse']) for r in test if r['step']==steps[-1]])),last_predicted_RMS=float(predicted[-1])))
   worldmap=defaultdict(list)
   for r in test:worldmap[r['world_id']].append(r)
   firstfails=[next((r['step'] for r in sorted(rr,key=lambda z:z['step']) if not r['trajectory_success']),51) for rr in worldmap.values()];pred=min([r['predicted_failure_entry_step'] for r in phases if r['predicted_failure_entry_step'] is not None] or [51]);out.append(dict(template=t,path=path,fit='Train-half worlds only, first10steps, phase-specific nonnegative forcing; rho fixed to known closed-map spectrum. Threshold from pooled logistic risk on train-half worlds including all50 closure steps. Thus held-world diagnostic, not length-extrapolation training claim.',phases=phases,predicted_first_failure_capped51=min(pred,51),held_worlds=len(firstfails),observed_first_failure_mean_capped51=float(np.mean(firstfails)),observed_no_failure_through50=sum(k==51 for k in firstfails),horizon_MAE_capped51=float(np.mean(np.abs(np.array(firstfails)-min(pred,51))))))
 dump('results/scalar_horizon_test.json',out)
if __name__=='__main__':main()
