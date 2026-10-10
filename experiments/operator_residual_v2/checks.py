"""Check causal signs, conditional projection algebra, norm controls and donor-free routing."""
from core import *
from projection import correct

torch.manual_seed(17)
q=random_basis(32,4,17);r=random_basis(32,6,18);m=torch.tensor([[1,1,1,0],[1,1,0,0]])
good=torch.randn(2,4,32);bad=good+torch.randn_like(good)*m[...,None]
e=(bad-good)*m[...,None];es=project(e,q);er=project(es,r);ep=es-er
assert torch.allclose(er+ep,es,atol=1e-6)
assert float((ep@r).abs().max())<1e-6
assert torch.allclose(bad-es,good+(e-es),atol=1e-6)
assert torch.allclose(good+es,bad-(e-es),atol=1e-6)
rq=random_basis(32,4,19,r,True);norm=es.flatten(1).norm(dim=1)
random=matched_random(e,rq,m,norm)
assert torch.allclose(random.flatten(1).norm(dim=1),norm,atol=1e-6)
assert not random[m==0].any()
fit=dict(q=q,x_mean=torch.randn(32),mean=torch.randn(4),beta=torch.randn(32,4))
shift=project(torch.randn_like(good),q)
a=correct(good,m,fit,'ridge');b=correct(good+shift,m,fit,'ridge')
assert torch.allclose((a@q)[m.bool()],(b@q)[m.bool()],atol=1e-5),'Prediction may not use corrupted target coordinates'
assert torch.equal(a[m==0],good[m==0])
assert binomial_ci(0,80)[1]>0 and binomial_ci(80,80)[0]<1
assert auroc([0,1],[1,1])==.5
print('Passed: residual sign, S decomposition, random norm/support, no target-coordinate input, padding, Wilson edge cases.')
