"""Exact penalized reduced-rank regression with train-only hyperparameter selection."""
from shared import *

def paired_tokens(templates,op,world_ids):
    advance=semantics()[2];xs=[];ys=[];coverage=[]
    for t in templates:
        for s in range(-3,4):
            try: target=advance('time',s,op)
            except ValueError:continue
            a=canonical('train',t,s);b=canonical('train',t,target)
            length=max(a['h'].shape[1],b['h'].shape[1]);h,m=pad(a['h'],a['m'],length);g,gm=pad(b['h'],b['m'],length)
            indices=[i for i,w in enumerate(a['world_ids']) if w in world_ids]
            ok=[i for i in indices if torch.equal(m[i],gm[i])]
            coverage.append(dict(template=t,source_state=s,target_state=target,total=len(indices),aligned=len(ok)))
            if ok:
                valid=m[ok].bool();xs.append(h[ok][valid]);ys.append((g[ok]-h[ok])[valid])
    assert xs,'No aligned training transitions'
    return torch.cat(xs).double(),torch.cat(ys).double(),coverage

def sufficient(x,y):
    mx=x.mean(0);my=y.mean(0);xc=x-mx;yc=y-my
    return dict(mx=mx,my=my,cov=xc.T@xc/len(x),cross=xc.T@yc/len(x),n=len(x))

def solve(st,relative,ranks):
    c=st['cov'];lam=relative*float(c.trace()/len(c));vals,vecs=torch.linalg.eigh(c+lam*torch.eye(len(c),dtype=torch.float64))
    assert vals.min()>0
    invsqrt=(vecs*vals.rsqrt())@vecs.T
    a=invsqrt@st['cross'];u,s,vh=torch.linalg.svd(a,full_matrices=False)
    output={}
    for rank in ranks:
        left=(invsqrt@u[:,:rank])*s[:rank];right=vh[:rank];bias=st['my']-st['mx']@left@right
        output[rank]=dict(left=left.float(),right=right.float(),bias=bias.float(),rank=rank,relative_ridge=relative,
            ridge=lam,singular_values=s.tolist(),effective_rank=int((s>s[0]*1e-10).sum()),training_tokens=st['n'])
    return output

def mse(x,y,fit):
    return float((x@fit['left'].double()@fit['right'].double()+fit['bias'].double()-y).square().mean())

def main():
    p=verify();selection=[];final={};coverage=[]
    for condition,templates in p['fit_conditions'].items():
        for op in p['operators']:
            x,y,cov=paired_tokens(templates,op,set(p['fit_partition']));dx,dy,dcov=paired_tokens(templates,op,set(p['dev_partition']))
            st=sufficient(x,y);scores={};candidates={}
            for rel in p['ridge_relative_grid']:
                solved=solve(st,rel,p['ranks']);candidates[rel]=solved
                last=float('inf')
                for rank,f in solved.items():
                    val=mse(dx,dy,f);scores[rel,rank]=val
                    b=f['left'].double()@f['right'].double()
                    obj=mse(x,y,f)*x.shape[1]+f['ridge']*float(b.square().sum())
                    assert obj<=last+1e-4,'Penalized RRR objective must decrease with rank'
                    last=obj
                    selection.append(dict(condition=condition,operation=op,rank=rank,relative_ridge=rel,dev_token_mse=val,fit_token_mse=mse(x,y,f),penalized_objective=obj))
            chosen={r:min(p['ridge_relative_grid'],key=lambda rel:scores[rel,r]) for r in p['ranks']}
            ax,ay,acov=paired_tokens(templates,op,set(p['fitting_worlds']));ast=sufficient(ax,ay)
            allfits={rel:solve(ast,rel,p['ranks']) for rel in set(chosen.values())}
            for rank,rel in chosen.items():
                f=allfits[rel][rank];f.update(condition=condition,operation=op,dev_token_mse=scores[rel,rank],fit_token_mse=mse(ax,ay,f),fit_worlds=p['fitting_worlds'])
                final[condition,op,rank]=f
            coverage.extend(dict(condition=condition,operation=op,**r) for r in acov)
            print('RRR fitted',condition,op,'tokens',len(ax),'chosen',chosen,flush=True)
    save('local/rrr.pt',final);csvwrite('results/ridge_selection.csv',selection);csvwrite('results/alignment_coverage.csv',coverage)
    dump('results/fit_complete.json',dict(training_updates=0,closed_form_fitting=True,fit_sha256=sha(ROOT/'local/rrr.pt'),protocol_sha256=sha(ROOT/'protocol.json')))

if __name__=='__main__':main()
