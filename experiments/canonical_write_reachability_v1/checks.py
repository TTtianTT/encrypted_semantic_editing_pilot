"""Numerical checks for exact RRR, affine bias, masking and error taxonomy."""
from shared import *
from fit import sufficient,solve,mse
from failures import classify

def main():
    torch.manual_seed(31);x=torch.randn(400,12,dtype=torch.float64);truth=torch.randn(12,3,dtype=torch.float64)@torch.randn(3,12,dtype=torch.float64);b=torch.randn(12,dtype=torch.float64);y=x@truth+b
    st=sufficient(x,y);sol=solve(st,1e-6,[1,3,12]);assert mse(x,y,sol[3])<1e-7
    f=sol[12];lam=f['ridge'];ols=torch.linalg.solve(st['cov']+lam*torch.eye(12,dtype=torch.float64),st['cross'])
    assert torch.allclose(f['left'].double()@f['right'].double(),ols,atol=2e-6)
    obj=[]
    for r in (1,3,12):
        f=sol[r];B=f['left'].double()@f['right'].double();obj.append(mse(x,y,f)*12+lam*float(B.square().sum()))
        assert int(torch.linalg.matrix_rank(B,atol=1e-5))<=r
    assert obj[0]>obj[1]>=obj[2]-1e-6
    h=x[:8].float().reshape(2,4,12);m=torch.tensor([[1,1,1,0],[1,1,0,0]])
    z=apply_rrr(h,m,sol[3]);assert torch.equal(z[m==0],h[m==0])
    render,gold,advance,states,score=semantics();w=rows(V2/'eval_worlds.jsonl')[0]
    def output(s,text=None):
        t=render(w,s,0) if text is None else text
        return dict(text=t,ended=True,score=score(t,gold(w,-1,0),w,True))
    assert classify(output(0),0,-1,[0],'plus',0)['category']=='edit_not_executed'
    assert classify(output(-2),0,-1,[0],'plus',0)['wrong_state_subtype']=='overshoot_one'
    assert classify(output(-1),0,-1,[0],'plus',0)['category']=='success'
    assert classify(output(-1,'nonsense'),0,-1,[0],'plus',0)['category']=='unparseable_or_invalid_grammar'
    print('Passed exact ridge solution, reduced rank, noiseless recovery, affine intercept, padding and classification checks.')

if __name__=='__main__':main()
