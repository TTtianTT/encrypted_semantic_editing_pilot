"""Closed-form PCA, canonical covariance, and ridge projections; training worlds only."""
from core import *

def stats(x,q):
    y=x.double()@q.double();mu=y.mean(0);yc=y-mu;cov=yc.T@yc/len(y)
    jitter=read(ROOT/'protocol.json')['mahal_ridge']*cov.trace()/q.shape[1]
    return dict(mean=mu.float(),inverse=torch.linalg.inv(cov+jitter*torch.eye(q.shape[1],dtype=torch.float64)).float(),cov=cov.float(),jitter=float(jitter))

def projector(x,q):
    x=x.double();q=q.double();mx=x.mean(0);xc=x-mx;mean=mx@q;comp=xc-(xc@q)@q.T
    ridge=read(ROOT/'protocol.json')['regression_ridge']
    cov=comp.T@comp/len(x);cross=comp.T@(xc@q)/len(x)
    beta=torch.linalg.solve(cov+ridge*torch.eye(x.shape[1],dtype=torch.float64),cross)
    assert (q.T@beta).abs().max()<1e-6,'Regressor must not read target coordinates'
    error=(comp@beta-xc@q).square().mean()
    return dict(q=q.float(),x_mean=mx.float(),mean=mean.float(),beta=beta.float(),ridge=ridge,training_mse=float(error))

def main():
    protocol=verify_protocol();canonical=load(ROOT/'local/canonical.pt');g4=load(ROOT/'local/g4_canonical_pooled.pt')['pooled']
    basislist={};output={}
    for seed in SEEDS:
        residual=load(ROOT/f'local/training_residual_s{seed}.pt');x=residual['tokens'].double();xc=x-x.mean(0)
        vals,vecs=torch.linalg.eigh(xc.T@xc/len(x));q=vecs[:,-4:].flip(1).float();basislist[seed]=q
        randoms={r:random_basis(768,4,r) for r in protocol['random_seeds']}
        output[seed]=dict(q=q,values=vals[-4:].flip(0).tolist(),fit_worlds=residual['worlds'],
                          projector=projector(canonical['tokens'],q),canonical_stats=stats(canonical['pooled'],q),g4_stats=stats(g4,q),
                          random_projectors={r:projector(canonical['tokens'],qq) for r,qq in randoms.items()},
                          random_stats={r:stats(canonical['pooled'],qq) for r,qq in randoms.items()},
                          random_g4_stats={r:stats(g4,qq) for r,qq in randoms.items()})
        assert not(set(residual['worlds'])&set(protocol['eval_world_ids']))
        save(f'local/fit_s{seed}.pt',output[seed]);print('fit',seed,len(residual['worlds']),'ridgeMSE',output[seed]['projector']['training_mse'],flush=True)
    angles=[]
    for a in SEEDS:
        for b in SEEDS:
            s=torch.linalg.svdvals(basislist[a].double().T@basislist[b].double()).clamp(0,1)
            angles.append(dict(source_seed=a,target_seed=b,angles_deg=torch.rad2deg(torch.acos(s)).tolist(),mean_cos2=float(s.square().mean())))
        s=torch.linalg.svdvals(basislist[a].double().T@old_basis(a).double()).clamp(0,1)
        angles.append(dict(source_seed=a,target_seed='old_discovery',angles_deg=torch.rad2deg(torch.acos(s)).tolist(),mean_cos2=float(s.square().mean())))
    write('results/shared_subspace_angles.jsonl',angles)
    # Historical G4 current-correct examples never participate in S or covariance fitting.
    archive=rows(REPO/'experiments/algebraic_generalization_v1/G3_trajectories.jsonl')
    index={(r['split'],r['world_id'],r['path'],r['step']):r for r in archive}
    vectors=load(REPO/'experiments/projection_hypothesis_v1/pooled_representations.pt')
    records=[]
    for source_seed in SEEDS:
        fit=output[source_seed];q=fit['q'];st=fit['g4_stats']
        for r in archive:
            key=(r['split'],r['world_id'],r['path'],r['step']+1)
            if r['path']!='plus_chain' or not r['endpoint_success'] or key not in index:continue
            z=vectors[f"pure/{r['split']}/{r['world_id']}/{r['step']}"];v=z['edited'];sig=v@q-st['mean'];dist=float(sig@st['inverse']@sig)
            random=[]
            for seed,rs in fit['random_g4_stats'].items():
                rq=fit['random_projectors'][seed]['q'];d=v@rq-rs['mean'];random.append(float(d@rs['inverse']@d))
            records.append(dict(dataset='historical_G4',basis_seed=source_seed,world_id=r['world_id'],split=r['split'],step=r['step'],
                                failure=not index[key]['endpoint_success'],mahal=dist,random_mahal=float(np.mean(random)),
                                reference_full_distance=float((z['edited']-z['gold']).norm()),
                                no_reference=True,normalizer='G4 training-world canonical encodings only',S_fit='separate 96 canonical-P training worlds'))
    write('results/g4_prediction_features.jsonl',records)
    dump('results/fit_complete.json',dict(training_updates=0,closed_form_fitting=True,protocol_sha256=sha(ROOT/'protocol.json'),
                                         files={str(p.relative_to(ROOT)):sha(p) for p in sorted((ROOT/'local').glob('fit_*.pt'))}))

if __name__=='__main__':main()
