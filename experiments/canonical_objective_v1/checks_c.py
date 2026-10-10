"""Numerical and structural preflight checks without GPU execution."""
from cutil import *

def main():
    train=worlds('train');test=worlds('eval');key=lambda w:tuple(w[k] for k in ('object','color','quantity','status'))
    assert not(set(map(key,train))&set(map(key,test)))
    assert len(train)==96 and len(test)==80
    aligned=transition_items('train');allitems=transition_items('train',False)
    assert all(len(v)==96*8//2 for v in aligned.values()),{k:len(v) for k,v in aligned.items()}
    assert all(len(v)==96*6 for v in allitems.values())
    fs=load(PRIOR/'local/rrr.pt')
    for op in ('plus','minus'):
        f=fs['iid_only',op,16];b=f['left'].double()@f['right'].double();u,s,vh=torch.linalg.svd(b,full_matrices=False);left=u[:,:16]*s[:16].sqrt();right=s[:16].sqrt()[:,None]*vh[:16]
        assert float((left@right-b).abs().max())<1e-10
        a=canonical('train',0,0);h=a['h'][:2];m=a['m'][:2]
        x=old.apply_rrr(h,m,f);balanced=h+(h@left.float()@right.float()+f['bias'])*m[...,None]
        assert torch.allclose(x,balanced,atol=2e-6,rtol=1e-5)
        assert torch.equal(x[~m.bool()],h[~m.bool()])
    # Mixture endpoints and the KL direction/label mask, with gradient routing.
    torch.manual_seed(123);a=torch.randn(2,3,7,requires_grad=True);b=torch.randn(2,3,7);labels=torch.tensor([[0,2,-100],[1,-100,-100]])
    val=kl(b,a,labels);manual=(b[0,:2].softmax(-1)*(b[0,:2].log_softmax(-1)-a[0,:2].log_softmax(-1))).sum(-1).mean()
    assert torch.allclose(val[0],manual);val.mean().backward();assert a.grad[0,2].abs().sum()==0 and a.grad[1,1:].abs().sum()==0
    assert torch.allclose(kl(b,b,labels),torch.zeros(2),atol=1e-7)
    dump('checks.json',dict(passed=True,aligned_per_operator=len(aligned['plus']),all_legal_per_operator=len(allitems['plus']),checks=['core disjoint worlds','coverage and legality','balanced RRR map equality','padding untouched','teacher-to-student masked KL and gradients']))
    print('checks passed')

if __name__=='__main__':main()
