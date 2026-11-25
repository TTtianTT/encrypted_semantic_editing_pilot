"""W4 (CPU): every locked prediction of v1-v5 (and v6 when merged) with its verdict, from each round's results file; appendix table
(generated/tables/predictions_all.tex), Table 2 counts (generated/tables/table2.tex) and generated/predictions_all.json.
A prediction = a node of the round's predictions file carrying 'verdict', 'pass_' or 'holds' (per-cell tables, observed blocks and the
top-level 'verdicts' summary are not descended into / not double counted). Outcome classes: confirmed (pass / holds true), failed
(fail / holds false), decided (a named hypothesis won; which one the plan predicted is recorded by the lead in claim_map.yaml), mixed
(mixed / neither / no winner), not evaluable (not evaluable / not decidable / None)."""
from common import *

ROUNDS = [('v1', 'symmetry_composability_v1', 'results/e1_predictions.json'), ('v2', 'composability_mechanisms_v1', 'results/predictions.json'),
          ('v3', 'composability_mechanisms_v2', 'results/predictions.json'), ('v4', 'composability_mechanisms_v3', 'results/predictions.json'),
          ('v5', 'composability_mechanisms_v4', 'results/predictions.json'), ('v6', 'composability_mechanisms_v5', 'results/predictions.json'),
          ('v7', 'composability_mechanisms_v6', 'results/predictions.json')]
GATES = {'v4': [('G4_0', 'g40')], 'v5': [('G5_0', 'g50')], 'v6': [('G6_0', 'g60')]}
NOTES = {('v6', 'K/K2'): '(not replicated in v7)', ('v6', 'K/Q17prime'): '(K2 not replicated in v7)'}
SKIP = {'cells', 'table', 'observed', 'S2_table', 'S3_cells', 'verdicts', 'per_seed', 'exploratory', 'lock', 'admission', 'confirm_geometry', 'consistency', 'g60'}


def outcome(n):
    if "verdict" not in n and "pass_" not in n and "holds" not in n:
        if isinstance(n.get("frozen"), bool): v = n["frozen"]             # v3 HS2 / HS3: frozen-plane signature (True = as predicted)
        elif "winner" in n: v = n["winner"] or "no winner"                 # v3 HS4: scored comparison without a unique winner
        else: v = None
    else: v = n.get("verdict", n.get("pass_", n.get("holds")))
    if v is True or v == 'pass': return 'confirmed', v
    if v is False or v == 'fail': return 'failed', v
    if v is None: return 'not evaluable', v
    s = str(v)
    if s.startswith(('not evaluable', 'not decidable')): return 'not evaluable', v
    if s in ('mixed', 'neither', 'no winner') or s.startswith(('mixed', 'tie')): return 'mixed', v
    return 'decided', v


def v7_rows(d):
    """v7 (and later): results/paper_export.json lists every locked prediction once with its kind; predictions demoted to exploratory by a
    pre-lock discriminability check are their own class. R4 combines its two parts; U4 holds iff the precision of a predicted failure is
    >= 0.90 in every family."""
    exp = read(f"experiments/{d}/results/paper_export.json"); pr = read(f"experiments/{d}/results/predictions.json"); out = []
    for e in exp:
        pid, v, kind = e["id"].split("/", 1)[1], e["verdict"], e["kind"] or ""
        if pid == "R4": v = f"A {pr['R']['R4']['A']['status']}; B {pr['R']['R4']['B']['status']}"; cls = "confirmed" if v.count("confirmed") == 2 else "failed" if "confirmed" not in v else "mixed"
        elif pid == "U4": prec = pr["U"]["U4"]["precision"]; v = all(x is not None and x >= .90 for x in prec.values()); cls = "confirmed" if v else "failed"
        elif pid == "K9": v = pr["K"]["K9"]["holds"]; cls = "confirmed" if all(v.values()) else "failed" if not any(v.values()) else "mixed"
        elif kind.startswith("exploratory"): cls = "demoted"
        else: cls = outcome(dict(verdict=v))[0]
        out.append(dict(id=pid + ("" if kind in ("primary", "") else f" ({kind.split(' (')[0]})"), verdict=v, outcome=cls))
    return out


def walk(node, path, out):
    if isinstance(node, dict):
        if path and (any(k in node for k in ("verdict", "pass_", "holds")) or isinstance(node.get("frozen"), bool) or "winner" in node): out.append((path, node))
        for k, v in node.items():
            if k in SKIP: continue
            walk(v, f'{path}/{k}' if path else k, out)


def tex_escape(s):
    return str(s).replace('\\', '/').replace('_', '\\_').replace('&', '\\&').replace('%', '\\%').replace('#', '\\#').replace('{', '\\{').replace('}', '\\}')


def main():
    require_slurm(); rows_ = []
    for r, d, f in ROUNDS:
        p = REPO / 'experiments' / d / f
        if not p.exists(): continue
        lock = read(f"experiments/{d}/protocol_lock.json")["lock_commit"][:7]
        if r == "v7":                                   # one entry per locked prediction (paper_export), with its kind
            for e in v7_rows(d): rows_.append(dict(round=r, experiment=d, lock=lock, **e))
            continue
        found = []; walk(read(p), "", found)
        for path, node in found:
            cls, v = outcome(node); rows_.append(dict(round=r, experiment=d, id=path, verdict=v, outcome=cls, lock=lock))
        for gi, gname in GATES.get(r, ()):                     # sanity gates kept in separate result files
            gs = [read(f"experiments/{d}/results/{gname}_{bb}.json") for bb in ("bart", "t5") if (REPO / f"experiments/{d}/results/{gname}_{bb}.json").exists()]
            v = all(g.get("pass") for g in gs); rows_.append(dict(round=r, experiment=d, id=gi, verdict=v, outcome="confirmed" if v else "failed", lock=lock))
    for x in rows_:
        if (x["round"], x["id"]) in NOTES: x["id"] = x["id"] + " " + NOTES[x["round"], x["id"]]
    (PAPER / 'generated').mkdir(exist_ok=True); (PAPER / 'generated/predictions_all.json').write_text(json.dumps(rows_, indent=1, ensure_ascii=False, default=str))
    L = ['% generated by paper/scripts/predictions_table.py', '\\begin{longtable}{llllll}', '\\caption{Every locked prediction of every round with its verdict (generated from the results file of each round). Outcome classes: confirmed (pass), failed, decided (one of the named hypotheses won), mixed, not evaluable, demoted (made exploratory before the lock by a discriminability pre-check, v7 on). Secondary predictions are marked.}\\label{tab:predictions-all} \\\\', '\\toprule round & experiment & prediction & verdict & outcome & lock \\\\ \\midrule \\endfirsthead', '\\toprule round & experiment & prediction & verdict & outcome & lock \\\\ \\midrule \\endhead']
    for x in rows_: L.append(' & '.join(tex_escape(x[k]) for k in ('round', 'experiment', 'id', 'verdict', 'outcome', 'lock')) + ' \\\\')
    L += ['\\bottomrule', '\\end{longtable}']; (PAPER / 'generated/tables').mkdir(parents=True, exist_ok=True); (PAPER / 'generated/tables/predictions_all.tex').write_text('\n'.join(L) + '\n')
    cls = ['confirmed', 'decided', 'failed', 'mixed', 'not evaluable', 'demoted']; T = ['% generated by paper/scripts/predictions_table.py', '\\begin{tabular}{l' + 'r' * (len(cls) + 1) + '}',
                                                                        '\\toprule round & ' + ' & '.join(cls) + ' & total \\\\ \\midrule']
    for r in sorted({x['round'] for x in rows_}):
        c = [sum(1 for x in rows_ if x['round'] == r and x['outcome'] == k) for k in cls]; T.append(f'{r} & ' + ' & '.join(map(str, c)) + f' & {sum(c)} \\\\')
    T += ['\\bottomrule', '\\end{tabular}']; (PAPER / 'generated/tables/table2.tex').write_text('\n'.join(T) + '\n')
    print('predictions', len(rows_), {k: sum(1 for x in rows_ if x['outcome'] == k) for k in cls}, flush=True)


if __name__ == '__main__':
    main()
