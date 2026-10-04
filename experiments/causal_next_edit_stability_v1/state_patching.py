"""All state patches act before T, use valid memory positions, and keep bad padding."""
import torch

def basis(weight,rank):
    _,_,v=torch.linalg.svd(weight.float(),full_matrices=False)
    return v[:min(rank,v.shape[0])].T.contiguous()

def project(delta,q):return (delta.float()@q)@q.T

def patch(bad,good,mask,spec,q=None):
    valid=mask.bool()[...,None];delta=(good.float()-bad.float())*valid
    if spec['method'] in ('bad','noop','self') or spec.get('alpha',1)==0:return bad.clone(),torch.zeros_like(delta),{}
    if spec['method']=='good':return good.clone(),delta,{}
    if spec['method']=='full':
        result=torch.where(valid,good,bad);return result,(result.float()-bad.float())*valid,{}
    if spec['method']=='global': component=delta
    elif spec['method']=='token':
        selected=torch.zeros_like(mask,dtype=torch.bool)
        for i in spec['positions']:selected[:,i]=True
        component=delta*selected[...,None]
    else: component=project(delta,q)*valid
    component=component*spec.get('alpha',1)
    result=(bad.float()+component).to(bad.dtype)
    result=torch.where(valid,result,bad)
    return result,component,{}

def matched_random(delta,mask,rank,norm,seed,positions=None):
    generator=torch.Generator(device='cpu').manual_seed(seed)
    d=delta.shape[-1];meta=dict(random_seed=seed,resamples=0)
    for attempt in range(5):
        q=torch.linalg.qr(torch.randn(d,min(rank,d),generator=generator),mode='reduced')[0].to(delta.device)
        projected=project(delta,q)*mask[...,None]
        if positions is not None:
            selected=torch.zeros_like(mask)
            selected[:,positions]=1;projected*=selected[...,None]
        n=projected.norm()
        if float(n)>1e-7:
            meta['resamples']=attempt;return projected*(norm/n),meta
    raise RuntimeError('Random projection norm too small after 5 fixed resamples')

def reverse(good,component,mask):
    return torch.where(mask.bool()[...,None],(good.float()-component).to(good.dtype),good)
