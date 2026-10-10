"""Post-hoc CPU diagnostic of canonical-trained ridge extrapolation on cached pairs."""
from core import *
from projection import correct
from aggregate import world_bootstrap

def mse(x,m):return float((x.square()*m[...,None]).sum()/(m.sum()*x.shape[-1]))

def main():
    verify_protocol();out=[];summary=[]
    for seed in SEEDS:
        fit=load(ROOT/f'local/fit_s{seed}.pt')['projector'];q=fit['q'];beta=fit['beta']
        for r in selections(seed):
            states=load(r['state_path']);bad,good,m=(states[k] for k in ('bad','good','mask'))
            cb=correct(bad,m,fit,'ridge');cg=correct(good,m,fit,'ridge')
            clean_error=((cg-good)@q)*m[...,None];edited_error=((cb-good)@q)*m[...,None];residual=(bad-good)*m[...,None]
            prediction_shift=(residual-project(residual,q))@beta
            assert torch.allclose(edited_error-clean_error,prediction_shift,atol=2e-5,rtol=1e-5)
            out.append(dict(seed=seed,world_id=r['world_id'],canonical_estimation_mse=mse(clean_error,m),
                edited_estimation_mse=mse(edited_error,m),unrepaired_coordinate_mse=mse(residual@q,m),
                complement_shift_mse=mse(prediction_shift,m),complement_residual_norm=float(((residual-project(residual,q))*m[...,None]).norm()),
                S_residual_norm=float(((residual@q)*m[...,None]).norm()),
                diagnostic='post-hoc CPU, cached history +1 to 0, distinct from long-chain first step 0 to -1'))
        rs=[r for r in out if r['seed']==seed]
        for metric in ('canonical_estimation_mse','edited_estimation_mse','unrepaired_coordinate_mse','complement_shift_mse'):
            values=[r[metric] for r in rs]
            summary.append(dict(seed=seed,metric=metric,N=len(rs),mean=float(np.mean(values)),ci95=world_bootstrap(values),beta_spectral_norm=float(torch.linalg.matrix_norm(beta,ord=2))))
    write('results/estimator_diagnostics.jsonl',out);csvwrite('results/estimator_diagnostics_summary.csv',summary)
    dump('results/estimator_diagnostics_complete.json',dict(training_updates=0,post_hoc=True,GPU_inference=False,code_sha256=sha(__file__)))
    print('Cached-pair ridge extrapolation diagnostic completed.')

if __name__=='__main__':main()
