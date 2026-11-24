"""New v7 editors (GPU, BART, before the lock; train only, admission on dev only; PLAN v7 B5, B7, B9). --part C|K. Idempotent.
C (unit U, family F1): C3 (lambda = 1, single step, as v6 C3n) on weekday and month, seeds 45 / 46 / 47 (never used by any earlier C3;
seed_registry.json), one 1200-update run per seed with snapshots at 300, 450, 600, 900, 1200 (identical to separate runs of those lengths).
Deliberately under-trained: no admission; every snapshot enters F1 and its dev L2 ratio to RRR-16 is recorded (PLAN B5).
K (unit K): Att2L-U8 (S <= 8, 8000 updates), Att2L-U4 (S <= 4, 4000) and Att1-U8 (S <= 8, 8000), seeds 45-49, on bind3, name3, bind3fix;
OR-U8 (oracle routing, diagnostic; S <= 8, 8000 updates; bind3, bind3fix), seeds 42-44 (a new editor family; its batch sequence differs from
v6 OR-U4's because S is drawn from another set). Settings as v6 (AdamW 1e-3, batch 16, clip 1). Admission (B5): on name3 and bind3fix,
dev single >= 0.95 and dev in-horizon one-way R_S >= 0.90 (S = 4 or 8); otherwise one retrain with twice the updates; otherwise
'cannot learn'. bind3 is not gated."""
import time
from lib7 import *

SNAPS7 = (300, 450, 600, 900, 1200)
C3_SEEDS = (45, 46, 47)
K_SEEDS = (45, 46, 47, 48, 49)
K7 = [('Att2L', 8000, tuple(range(1, 9)), K_DOMAINS, K_SEEDS), ('Att2L', 4000, (1, 2, 3, 4), K_DOMAINS, K_SEEDS),
      ('Att1', 8000, tuple(range(1, 9)), K_DOMAINS, K_SEEDS), ('OR', 8000, tuple(range(1, 9)), ['bind3', 'bind3fix'], (42, 43, 44))]


def k7_name(kind, upd, Sset):
    return f"{kind}U{max(Sset)}"


def c3_run7(eng, d, s):
    if all(new7_path('bart', f'C3n{u}', d, s, u).exists() for u in SNAPS7): return
    source_path(); from backend import editors
    ed, hist, scale = train_editor(eng, 'bart', d, 'natural', 'C3', s, updates=max(SNAPS7), snapshots=SNAPS7[:-1])
    write(f'results/train_new/bart_C3n_{d}_s{s}_u{max(SNAPS7)}.jsonl', hist)
    for u in SNAPS7:
        sd = ed.snapshots[u] if u in ed.snapshots else {k: x.cpu() for k, x in ed.state_dict().items()}
        e2 = editors(eng.d, s); e2.load_state_dict(sd); e2 = e2.eval().requires_grad_(False)
        r = dev_single(eng, 'bart', d, 'natural', {op: e2[op] for op in ('plus', 'minus')})
        save(new7_path('bart', f'C3n{u}', d, s, u), dict(editor=sd, seed=s, dev_single=r, l2_scale=scale, updates=u, group='C3',
                                                          note=f'snapshot of one {max(SNAPS7)}-update run'))


def k_editor7(eng, kind, name, d, s, upd, Sset):
    f = ROOT / f'local/k7_{name}_{d}_s{s}_u{upd}.pt'
    if f.exists(): c = load(f); return c['dev_single'], c['dev_horizon']
    ed, hist = train_k(d, s, kind, updates=upd, Sset=Sset)
    ops = k_ops(kind, ed, slots('bart', d, 'dev'), name_positions(d, 'dev') if kind == 'OR' else None)
    r = dev_single(eng, 'bart', d, 'natural', ops); rh = dev_chain(eng, 'bart', d, 'natural', ops, ['plus'] * max(Sset))[-1]
    save(f, dict(editor={k: x.cpu() for k, x in ed.state_dict().items()}, seed=s, kind=kind, name=name, Sset=list(Sset), dev_single=r, dev_horizon=rh, updates=upd))
    write(f'results/train_new/k7_{name}_{d}_s{s}_u{upd}.jsonl', hist); return r, rh


@torch.no_grad()
def l2_ratios(eng, res):
    """Dev L2 of every new C3 snapshot relative to RRR-16 (recorded, not used for grouping; design rule 5)."""
    out = {}
    for d in C_DOMAINS:
        scale = l2_scales('bart', d, 'natural'); f, r = base_fit('bart', d); rrr = dev_l2({op: RRRop(f[op, 16]) for op in ('plus', 'minus')}, 'bart', d, 'natural', scale)
        for s in C3_SEEDS:
            for u in SNAPS7:
                v = dev_l2(load_editor(eng, new7_path('bart', f'C3n{u}', d, s, u)), 'bart', d, 'natural', scale)
                out[f'{d}/C3n{u}_s{s}'] = dict(dev_l2=v, rrr16=rrr, ratio=v / rrr)
    return out


def main():
    require_slurm(); part = sys.argv[sys.argv.index('--part') + 1]; t0 = time.time(); eng = engine5('bart')
    out = ROOT / f'results/train_new_bart_{part}.json'; res = read(out) if out.exists() else {}
    if part == 'C':
        for d in C_DOMAINS:
            for s in C3_SEEDS:
                c3_run7(eng, d, s)
                for u in SNAPS7:
                    r = load(new7_path('bart', f'C3n{u}', d, s, u))['dev_single']
                    res[f'C3n{u}/{d}/s{s}'] = dict(updates=u, dev=r, status='ok', path=str(new7_path('bart', f'C3n{u}', d, s, u).relative_to(ROOT)))
                    print('train C3', d, s, u, round(r['rate'], 4), flush=True)
                dump(out, res)
        res['l2_ratio'] = l2_ratios(eng, res); dump(out, res)
    else:
        for kind, upd, Sset, doms, seeds in K7:
            name = k7_name(kind, upd, Sset)
            for d in doms:
                for s in seeds:
                    st = None; gated = d in ('name3', 'bind3fix')
                    for u in (upd, 2 * upd):
                        r, rh = k_editor7(eng, kind, name, d, s, u, Sset); st = u
                        ok = r['rate'] >= .95 and rh['rate'] >= .90
                        res[f'{name}/{d}/s{s}/u{u}'] = dict(dev_single=r, dev_horizon=rh, admitted=ok if gated else None)
                        print('K train', name, d, s, u, round(r['rate'], 4), round(rh['rate'], 4), flush=True)
                        if not gated or ok: break
                    ok = (not gated) or res[f'{name}/{d}/s{s}/u{st}']['admitted']
                    res[f'{name}/{d}/s{s}'] = dict(kind=kind, Sset=list(Sset), updates=st, admitted=ok, status='ok' if ok else 'cannot learn',
                                                   path=f'local/k7_{name}_{d}_s{s}_u{st}.pt')
                    dump(out, res)
    res['seconds'] = time.time() - t0; res['resources'] = eng.resources(); dump(out, res)


if __name__ == '__main__':
    main()
