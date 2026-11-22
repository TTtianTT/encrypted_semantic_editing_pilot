"""E0.1 metrics (CPU): encoder geometry symmetry of the four existing domains. Exploratory (all worlds used before)."""
import time
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from symutil import *


def spec(name, states):
    S = len(states)
    if name.startswith('time'):   # plus lowers relative date: s -> s-1
        return [(i, i - 1) for i in range(1, S)], 'open'
    if name.startswith('emotion'):
        return [(i, i + 1) for i in range(S - 1)], 'open'
    return [(i, (i + 1) % S) for i in range(S)], 'cyclic'  # person Z3, space Z4 in REL order


def main():
    require_slurm(); t0 = time.time(); res = {}; nulls = []; per_world = {}
    names = ['time_t0', 'person_t0', 'space_t0', 'space_t1', 'emotion_t0']
    data = {n: load(ROOT / f'local/e0_{n}.pt') for n in names}
    for n in names:
        V = data[n]['pooled'].double().numpy(); st = data[n]['states']; pairs, kind = spec(n, st)
        out, nr, ew = geometry_report(V, st, pairs, kind, name=n)
        res[n] = out; nulls += nr; per_world[n] = ew
        print(n, 'E_iso', out['E_iso'], 'R2', out.get('R2_G'), flush=True)
    # time three-state segment {+1, 0, -1}: indices of states 1, 0, -1 ; plus: +1->0, 0->-1
    st = data['time_t0']['states']; ix = [st.index(1), st.index(0), st.index(-1)]
    V = data['time_t0']['pooled'].double().numpy()[:, ix]
    seg, nr, ew = geometry_report(V, [1, 0, -1], [(0, 1), (1, 2)], 'open', name='time_t0_segment')
    res['time_t0_segment'] = seg; nulls += nr; per_world['time_t0_segment'] = ew
    res['time_segment_minus_person'] = boot_diff(per_world['time_t0_segment'], per_world['person_t0'])
    res['time_segment_minus_person']['ci_excludes_0_below'] = res['time_segment_minus_person']['ci95'][1] < 0
    res['per_world_E_iso'] = {k: v.tolist() for k, v in per_world.items()}
    res['note'] = 'Exploratory: all 152 worlds per domain were used by earlier experiments. Space states indexed by relation word (front,left,back,right = plus order, asserted in e0_encode).'
    res['seconds'] = time.time() - t0
    dump('results/e0_geometry.json', res); csvwrite('results/e0_geometry_null.csv', nulls)
    fig, axs = plt.subplots(1, 5, figsize=(16, 3.4))
    for ax, n in zip(axs, names):
        st = data[n]['states']; pairs, _ = spec(n, st)
        pca_plot(ax, data[n]['pooled'].double().numpy(), st, f"{n}  E_iso={res[n]['E_iso']['mean']:.3f}", pairs)
    fig.tight_layout(); (ROOT / 'figs').mkdir(exist_ok=True); fig.savefig(ROOT / 'figs/e0_state_pca.png', dpi=150)


if __name__ == '__main__':
    main()
