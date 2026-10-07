"""CPU aggregation/selection, exact denominators and paired world statistics."""
import argparse
import csv
import gzip
import io
import random
import numpy as np
from .common import *
from .metrics import wilson

def csv_write(p,records):
    if not records:text(p,'status\nNOT_RUN\n');return
    keys=sorted(set().union(*(r.keys() for r in records)));s=io.StringIO();writer=csv.DictWriter(s,fieldnames=keys);writer.writeheader();writer.writerows(records);text(p,s.getvalue())

def readout(stage='S1_NATIVE'):
    m=read(ROOT/f'manifests/{stage}.json');folder=Path(m['output_root'])/'bart_s42'
    scores=rows(folder/'readout_scores.jsonl');curves=rows(folder/'perturbation_curves.jsonl');conditions=rows(folder/'causal_conditions.jsonl')
    by={}
    for r in scores:by.setdefault((r['split'],r['source_pair']),[]).append(r)
    summary=[]
    for (split,pair),rs in sorted(by.items()):
        summary.append(dict(split=split,source_pair=pair,worlds=len({r['world_id'] for r in rs}),token_denominator=len(rs),mean_JS=float(np.mean([r['JS'] for r in rs])),max_JS=max(r['JS'] for r in rs),p95_JS=float(np.quantile([r['JS'] for r in rs],.95)),max_KL_ab=max(r['KL_ab'] for r in rs),max_abs_margin_change=max(abs(r['b_margin']-r['a_margin']) for r in rs)))
    csv_write(ROOT/'results/readout_summary.csv',summary)
    bycurve={}
    for r in curves:bycurve.setdefault((r['split'],r['source_pair'],r['direction'],r['alpha']),[]).append(r)
    cs=[]
    for (split,pair,direction,alpha),rs in sorted(bycurve.items()):
        cs.append(dict(split=split,source_pair=pair,direction=direction,alpha=alpha,records=len(rs),worlds=len({r['world_id'] for r in rs}),preserved_numerator=sum(r['tokens_preserved'] for r in rs),preserved_denominator=len(rs),preservation=sum(r['tokens_preserved'] for r in rs)/len(rs),mean_norm=float(np.mean([r['delta_norm'] for r in rs])),max_per_token_energy_error=max(r['per_token_energy_max_error'] for r in rs)))
    csv_write(ROOT/'results/perturbation_curves.csv',cs)
    coarse={}
    for r in conditions:
        if r['split']=='discovery' and r['condition']=='VALUE_ZERO_OOD':coarse.setdefault(r['module'],[]).append(r['content_margin_shift'])
    ranked=sorted(coarse,key=lambda name:(np.mean(coarse[name]),name));assert ranked
    rng=random.Random(81001);candidate=ranked[0];randomsite=rng.choice([n for n in sorted(coarse) if n!=candidate])
    selection=dict(candidate=candidate,head=0,random_site=randomsite,ranked_discovery_mean_margin={n:float(np.mean(coarse[n])) for n in ranked},choice='most negative content-margin change under discovery value zeroing; independently validate normal color resampling; fixed head0 supplementary',random_seed=81001,max_candidates=1,validation_gate=dict(min_worlds=20,content_damage_min=.1,content_damage_gte_target_damage=True,mean_content_margin_shift_max=-.2),test_accessed=0)
    dump(ROOT/'configs/S2_CANDIDATES.json',selection)
    text(ROOT/'S1_READOUT_REPORT.md','# Discovery/validation readout results\n\n'+json.dumps(summary,ensure_ascii=False,indent=2)+'\n\n配对只要求当前正确、exact native tokens/raw text、shape/mask及非底噪差异；不以next fork筛选。旧PCA replay单列。当前共同文本不等于概率/内部等价。曲线保留非单调/重入，未二分搜索。独立test仍封存。\n\nSDPA native projection self-patch误差0；eager候选backend对齐失败另报，未用于此run。SDPA不物化attention probs；AV/W_O及residual/norm实际hook值与观测传播保存。推断注意力pattern仅作后续诊断，不能声称是materialized fused-kernel内部张量。matched-current-preservation随机幅度尚待validation锁定；未称完整S1确认。\n')
    return selection

def paired_bootstrap(records,method_a,method_b,field='joint',draws=20000,seed=2026100802):
    # Each world retains every source/operation/seed before equal-source weighting.
    cells={}
    for r in records:
        if r['method'] not in (method_a,method_b):continue
        cells.setdefault((r['world_id'],r['method'],r['source']),[]).append(r[field])
    worlds=sorted({k[0] for k in cells});differences=[]
    for w in worlds:
        values={method:np.mean([np.mean(cells[(w,method,s)]) for s in ('natural','history')]) for method in (method_a,method_b)}
        differences.append(values[method_a]-values[method_b])
    if not differences:return dict(status='NOT_ESTIMABLE',n_worlds=0,estimate=None,CI95=None)
    x=np.asarray(differences);rng=np.random.default_rng(seed);means=[]
    for _ in range(draws//100):means.extend(x[rng.integers(0,len(x),size=(100,len(x)))].mean(1).tolist())
    # Exploratory centered-bootstrap p; not randomized assignment inference.
    estimate=float(x.mean());center=np.asarray(means)-estimate;p=float((1+np.sum(abs(center)>=abs(estimate)))/(len(center)+1))
    return dict(status='ESTIMATED',n_worlds=len(x),estimate=estimate,CI95=np.quantile(means,[.025,.975]).tolist(),paired_world_raw_differences=dict(zip(worlds,x.tolist())),bootstrap_draws=draws,p_value=p,p_interpretation='centered paired cluster bootstrap; fixed3 training seeds, not unlimited checkpoint population')

def holm(values):
    ordered=sorted(enumerate(values),key=lambda v:v[1]);out=[None]*len(values);running=0.
    for rank,(index,value) in enumerate(ordered):running=max(running,min(1.,value*(len(values)-rank)));out[index]=running
    return out

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--readout',action='store_true');a=p.parse_args()
    if a.readout:print(json.dumps(readout(),ensure_ascii=False))
