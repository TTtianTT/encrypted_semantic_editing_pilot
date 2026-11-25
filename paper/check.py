"""W8 (CPU): consistency check, run before every paper commit (a failure blocks the commit).
1. every macro used in main.tex / sections/*.tex is defined in generated/numbers.tex or in main.tex's preamble;
2. every claim id cited in the text ('% CL..' comments or \\claim{..}) exists in claims.yaml;
3. every claim marked confirmed cites at least one locked prediction of a round with a lock commit;
3b. every cited prediction resolves to a row of the predictions table (generated/predictions_all.json); a prediction cited as support is
    confirmed or decided (failed, mixed, not evaluable or demoted ones go to counter_predictions); a claim marked confirmed or decided has
    at least one confirmed or decided supporting prediction;
4. no bare decimal numbers in the section text outside macros (numbers come from numbers.tex), except in comments.
Exit status 1 on failure."""
import re
import sys
import yaml
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent / 'scripts'))
from common import *


def main():
    require_slurm(); errs = []
    defined = set(re.findall(r'\\newcommand\{\\([A-Za-z]+)\}', (PAPER / 'generated/numbers.tex').read_text()))
    main_tex = (PAPER / 'main.tex').read_text(); defined |= set(re.findall(r'\\(?:new|renew|provide)command\{?\\([A-Za-z]+)\}?', main_tex))
    claims = {c['id']: c for c in yaml.safe_load((PAPER / 'claims.yaml').read_text())['claims']}
    texts = {'main.tex': main_tex} | {f'sections/{p.name}': p.read_text() for p in sorted((PAPER / 'sections').glob('*.tex'))}
    for name, t in texts.items():
        for m in set(re.findall(r'\\(CL[A-Za-z]+)\b', t)):
            if m not in defined: errs.append(f'{name}: undefined number macro \\{m}')
        for cid in set(re.findall(r'%\s*(CL\d+b?)', t)) | set(re.findall(r'\\claim\{(CL\d+b?)\}', t)):
            if cid not in claims: errs.append(f'{name}: unknown claim id {cid}')
        for i, line in enumerate(t.split('\n'), 1):
            body = line.split('%')[0]
            if name.startswith('sections/') and re.search(r'(?<![\\\w{])\d+\.\d+', body): errs.append(f'{name}:{i}: bare decimal number outside a macro: {body.strip()[:80]}')
    rows = json.loads((PAPER / "generated/predictions_all.json").read_text())
    def resolve(pid):
        r, name = pid.split("/", 1); cand = [x for x in rows if x["round"] == r and (lambda i: i == name or i.endswith("/" + name) or i.startswith(name + "/") or "/" + name + "/" in i)(x["id"].split(" ")[0])]
        return min(cand, key=lambda x: len(x["id"])) if cand else None
    for cid, c in claims.items():
        if str(c["nature"]).startswith("confirmed") and not any(v for v in c["lock_commits"].values()): errs.append(f"{cid}: confirmed without a locked prediction")
        sup = []
        for kind in ("predictions", "counter_predictions"):
            for pid in c.get(kind, []):
                x = resolve(pid)
                if x is None: errs.append(f"{cid}: {pid} not found in the predictions table"); continue
                if kind == "predictions" and x["outcome"] in ("failed", "mixed", "not evaluable", "demoted"): errs.append(f"{cid}: {pid} is {x['outcome']} but cited as support (move it to counter_predictions)")
                if kind == "predictions": sup.append(x["outcome"])
        if str(c["nature"]).startswith(("confirmed", "decided")) and not any(o in ("confirmed", "decided") for o in sup): errs.append(f"{cid}: nature {c['nature'][:20]} without a confirmed or decided supporting prediction")
    print('\n'.join(errs) if errs else 'check passed', flush=True); sys.exit(1 if errs else 0)


if __name__ == '__main__':
    main()
