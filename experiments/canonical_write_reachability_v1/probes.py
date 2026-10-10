"""Canonical-only seven-way ridge probes and calibrated component diagnostics."""
from shared import *

def fit_probe(x,labels,relative):
    x=x.double();mx=x.mean(0);xc=x-mx;y=torch.nn.functional.one_hot(labels+3,7).double();my=y.mean(0)
    c=xc.T@xc/len(x);lam=relative*float(c.trace()/len(c))
    beta=torch.linalg.solve(c+lam*torch.eye(len(c),dtype=torch.float64),xc.T@(y-my)/len(x))
    return dict(mean=mx.float(),bias=my.float(),beta=beta.float(),ridge=lam)
def prediction(x,f):return (x-f['mean'])@f['beta']+f['bias']

def main():
    p=verify();xs=[];labels=[]
    for state in p['probe_states']:
        c=canonical('train',0,state);xs.append(pool(c['h'],c['m']));labels.extend([state]*len(c['h']))
    x=torch.cat(xs);labels=torch.tensor(labels);full=fit_probe(x,labels,p['probe_ridge_relative'])
    probes={};records=[];calibration=[]
    for seed in SEEDS:
        q=load(V2/f'local/fit_s{seed}.pt')['q'];sx=x@q;cx=x-project(x,q)
        sf=fit_probe(sx,labels,p['probe_ridge_relative']);cf=fit_probe(cx,labels,p['probe_ridge_relative']);probes[seed]=dict(q=q,S=sf,complement=cf,full=full)
        for t in p['eval_templates']:
            for state in p['probe_states']:
                c=canonical('eval',t,state);z=pool(c['h'],c['m'])
                results={'full':prediction(z,full),'S':prediction(z@q,sf),'complement':prediction(z-project(z,q),cf)}
                for component,out in results.items():
                    for i,w in enumerate(c['world_ids']):calibration.append(dict(seed=seed,template=t,state=state,world_id=w,component=component,predicted_state=int(out[i].argmax())-3,correct=int(out[i].argmax())-3==state))
        for pair in previous.selections(seed):
            c=load(pair['state_path']);m=c['mask'];bad=c['bad'];good=c['good']
            for context,h in [('edited',bad),('canonical_target',good)]:
                z=pool(h,m);slog=prediction(z@q,sf);clog=prediction(z-project(z,q),cf);flog=prediction(z,full)
                centered=z-full['mean'];sc=project(centered,q)@full['beta'];pc=(centered-project(centered,q))@full['beta'];assert torch.allclose(sc+pc+full['bias'],flog,atol=2e-5)
                # Historical pairs are source +1 -> target 0. Margins are
                # target-minus-source; decomposition includes an explicit bias.
                records.append(dict(seed=seed,world_id=pair['world_id'],context=context,source_state=1,target_state=0,
                    full_prediction=int(flog[0].argmax())-3,S_prediction=int(slog[0].argmax())-3,complement_prediction=int(clog[0].argmax())-3,
                    full_margin=float(flog[0,3]-flog[0,4]),S_margin=float(slog[0,3]-slog[0,4]),complement_margin=float(clog[0,3]-clog[0,4]),
                    shared_S_contribution=float(sc[0,3]-sc[0,4]),shared_complement_contribution=float(pc[0,3]-pc[0,4]),shared_bias=float(full['bias'][3]-full['bias'][4])))
    save('local/probes.pt',probes);write('results/probe_calibration.jsonl',calibration);write('results/probe_states.jsonl',records)
    dump('results/probes_complete.json',dict(training_updates=0,probe_fit_worlds=p['fitting_worlds'],probe_fit_templates=[0],probe_sha256=sha(ROOT/'local/probes.pt')))
    print('Canonical probe calibration',len(calibration),'paired state probes',len(records))

if __name__=='__main__':main()
