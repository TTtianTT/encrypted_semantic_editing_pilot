"""Exact real-coordinate affine differences, with measured dtype rounding."""
import torch
from .state_patching import basis,project

@torch.no_grad()
def analyze(ed,bad,good,mask,operation):
    op=ed[operation];d=(good.float()-bad.float())*mask[...,None]
    predicted=d+op.u(op.v(d))*mask[...,None]
    actual=(op(good,mask).float()-op(bad,mask).float())*mask[...,None]
    err=actual-predicted;readq=basis(op.v.weight,16);writeq=basis(op.u.weight.T,16)
    result=dict(dtype=str(bad.dtype),absolute_prediction_error_max=float(err.abs().max()),absolute_prediction_error_mean=float(err.abs().mean()),relative_prediction_error=float(err.norm()/actual.norm().clamp_min(1e-12)),difference_norm=float(d.norm()),next_difference_norm=float(actual.norm()),norm_ratio=float(actual.norm()/d.norm().clamp_min(1e-12)),read_subspace_fraction=float(project(d,readq).norm().square()/d.norm().square().clamp_min(1e-12)),write_subspace_fraction=float(project(d,writeq).norm().square()/d.norm().square().clamp_min(1e-12)),increment_norm=float((actual-d).norm()),bias_token_norm=float(op.b.norm()),bad_absolute_norm=float((bad.float()*mask[...,None]).norm()),good_absolute_norm=float((good.float()*mask[...,None]).norm()),bias_total_norm=float(op.b.norm()*mask.sum().sqrt()),prediction_formula='row-vector delta + delta @ V.T @ U.T, mask included; output dtype cast measured')
    for name,h in [('bad',bad),('good',good)]:
        h=h.float()*mask[...,None]
        result[name+'_read_absolute_norm']=float(project(h,readq).norm())
        result[name+'_write_absolute_norm']=float(project(h,writeq).norm())
        result[name+'_mean_bias_alignment']=float((h*op.b).sum(-1).sum()/mask.sum()/op.b.norm().clamp_min(1e-12))
    increment=actual-d
    result.update(increment_read_fraction=float(project(increment,readq).norm().square()/increment.norm().square().clamp_min(1e-12)),increment_write_fraction=float(project(increment,writeq).norm().square()/increment.norm().square().clamp_min(1e-12)))
    return result
