"""v8 synthetic self-tests (CPU, before the lock; PLAN v7 design rule 9). Every new decision rule and helper of v8 on constructed inputs
whose answer is known: analyze8 rules (N1, N2, editor rule N3 / G1, freeze rule N4 / G3 with dropped conditions, prediction rule N5, Q24,
per-backbone combination, D separation, identical-cell dedupe, world tables), rstar_pred on ideal Fourier codes (Proposition 1), the U
calibration tie rule, the month-nat parser and scorer, and the E2 rank option (rank 32 unchanged: same parameters as v7's OR editor for
the same seed). Output: results/selftest8.json (pass iff every check holds)."""
import numpy as np
import torch
from symutil import *


def main():
    require_slurm(); import analyze8 as A; import lib8; import dev8; import sym5_semantics as S; import sym5_evaluator as Ev
    chk = {}
    chk['n1'] = [A.n1(x) for x in (.95, .9, .7, .5, .1)] == ['holds', 'holds', 'mixed', 'opposing', 'opposing']
    chk['n2'] = [A.n2(x) for x in (.8, .5, .3)] == ['H-transfer', 'mixed', 'H-no-transfer']
    chk['editor_rule'] = A.editor_rule(.95, .1, .9) and not A.editor_rule(.85, .1, .9) and not A.editor_rule(.95, .3, .9) and not A.editor_rule(.95, .1, .7) and not A.editor_rule(None, .1, .9)
    o = dict(F1_plus=.1, F1_alt=.85, Fempty_alt=.9, Fnot1_plus=.05)
    f_all = A.freeze_rule(o, dict(F1_plus=True, F1_alt=True, Fnot1_plus=True)); f_drop = A.freeze_rule(dict(o, Fnot1_plus=.5), dict(F1_plus=True, F1_alt=True, Fnot1_plus=False))
    f_fail = A.freeze_rule(dict(o, F1_alt=.7), dict(F1_plus=True, F1_alt=True, Fnot1_plus=True)); f_none = A.freeze_rule(o, {})
    chk['freeze_rule'] = f_all['holds'] is True and f_drop['holds'] is True and f_drop['conditions']['Fnot1_plus'] is None and f_fail['holds'] is False and f_none['holds'] is None
    chk['prediction_rule'] = A.prediction_rule(.9, .01, .85) and not A.prediction_rule(.84, .01, .85) and not A.prediction_rule(.9, 0, .85) and not A.prediction_rule(.9, .01, .79)
    chk['q24'] = A.q24('holds', True, True) == 'H-natural' and A.q24('mixed', True, True) == 'H-template-bound' and A.q24('holds', False, True) == 'mixed' and A.q24('holds', None, True) == 'mixed'
    chk['combine'] = A.combine(['H-natural', 'H-natural']) == 'H-natural' and A.combine(['H-natural', 'mixed']) == 'mixed (per backbone)'
    sep = A.d_separation([dict(D=.9, family='CE')] * 9 + [dict(D=.1, family='state')] * 9 + [dict(D=.3, family='state'), dict(D=None, family='CE')])
    chk['d_separation'] = sep['n'] == 19 and abs(sep['frac'] - 18 / 19) < 1e-9 and sep['holds']
    s1 = dict(m=[[1, 2]], rho=[[0, 0]], path='plus'); s2 = dict(m=[[1, 2]], rho=[[0, 0]], path='plus'); s3 = dict(m=[[1, 3]], rho=[[0, 0]], path='plus')
    keep, groups = A.dedupe({'a/x/plus': s1, 'a/y/plus': s2, 'a/z/plus': s3}); chk['dedupe'] = keep == {'a/x/plus', 'a/z/plus'} and groups == {'a/x/plus': ['a/x/plus', 'a/y/plus']}
    recs = [dict(world_id='w0', step=t, trajectory_success=t < 2, success=t < 2, decoded_state=3) for t in (1, 2, 3)] + \
           [dict(world_id='w1', step=t, trajectory_success=True, success=True, decoded_state=None if t == 1 else 1) for t in (1, 2, 3)]
    sim = dict(world_ids=['w0', 'w1'], argmax=[[2, 0, 0], [1, 1, 1]], pred=dict(slot=[False, True], U=[False, False]))
    tab = A.world_tab(recs, sim, 3)
    chk['world_tab'] = tab['w0'] == dict(pred=False, predU=False, obs=False, naive=True, D1=True, R={1: True, 2: False}) and tab['w1']['D1'] is None and tab['w1']['obs'] is True
    # Proposition 1 on ideal codes: N states on planes with amplitudes (1, 0.5, 0.02): r*_pred counts planes with a_k >= 5% of the largest
    amp = {1: dict(dim=2, a=1.0), 2: dict(dim=2, a=.5), 3: dict(dim=2, a=.02), 6: dict(dim=1, a=.3)}
    chk['rstar_pred'] = lib8.rstar_pred(amp) == 5 and lib8.rstar_pred({1: dict(dim=2, a=1.)}) == 2
    cells = [(dict(argmax=[[0, 1]], states=[[0, 1]], m=[[.05, .05]], rho=[[0, 0]], world_ids=['a']), [True])]
    best, _ = dev8.calibrate_u(cells); chk['calibrate_u_ties'] = best['tau_m'] is None and best['tau_r'] is None
    w = dict(domain=S.NAT, prefix='It opened in ', suffix=' 1999.', start_state=2)
    g = S.gold(w, 2); good = S.render(w, 2); bad = S.render(w, 3)
    chk['nat_score'] = Ev.score(good, g, w, True)['success'] and not Ev.score(bad, g, w, True)['success'] and not Ev.score(good, g, w, False)['success'] and \
        Ev.parse_state(bad, S.NAT, gold=g)[0] == 3 and Ev.parse_state('It opened in Smarch 1999.', S.NAT, gold=g)[0] is None and S.base(S.NAT) == 'month'
    a = lib8.k_pair('OR', 16, 42); b = lib8.k_pair('OR', 16, 42, 32); c = lib8.k_pair('OR', 16, 42, None)
    chk['or_rank'] = all(torch.equal(x, y) for x, y in zip(a.state_dict().values(), b.state_dict().values())) and c['plus'].u.weight.shape == (16, 16) and float(c['plus'].u.weight.abs().sum()) == 0
    res = dict(checks=chk, pass_=all(chk.values())); dump(ROOT / 'results/selftest8.json', res); print(json.dumps(res), flush=True)


if __name__ == '__main__':
    main()
