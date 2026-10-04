"""Explicit optional-stage gate; never launches backbone/editor training."""
from .common import ROOT,read,dump

def decide():
    paths=[ROOT/f'results/{m}_method_lock.json' for m in ('bart','t5gemma')]
    assert all(p.exists() for p in paths),'Both model discovery/validation must finish before SAE decision'
    locks=[read(p) for p in paths]
    assert all(x['test_intervention_unread'] for x in locks)
    reason='The actual editor is tokenwise affine and the simple editor/PCA subspaces already give a fully specified difference decomposition; the additional SAE ambiguity gate is not met.' if all(x['gate_passed'] for x in locks) else 'At least one model fails the prespecified S2 validation gate; core independent tests and negative results take priority.'
    result=dict(status='SKIPPED',reason=reason,training_performed=False,allocated_GPU_hours=0,decision_before_independent_test=True)
    dump(ROOT/'results/SAE_STATUS.json',result);return result
