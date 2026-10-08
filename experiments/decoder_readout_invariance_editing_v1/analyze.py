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
    controls=[]
    for r in rows(folder/'source_prefix_controls.jsonl'):
        for condition in ('zero','resample'):
            p=r[condition];score=p.get('score',{})
            controls.append(dict(world_id=r['world_id'],split=r['split'],side=r['side'],prefix_fraction=r['prefix_fraction'],condition=condition,status=p.get('status','COMPLETED'),target=score.get('target'),content=score.get('preserved'),joint=score.get('success'),EOS=p.get('ended'),zeroing_OOD=condition=='zero'))
    csv_write(ROOT/'results/source_prefix_controls.csv',controls)
    matched=[]
    for pair in sorted({r['source_pair'] for r in cs}):
        target=next(r['preservation'] for r in cs if r['split']=='validation' and r['source_pair']==pair and r['direction']=='real' and r['alpha']==1)
        for kind in ('isotropic','shared_rank4'):
            options=[r for r in cs if r['split']=='validation' and r['source_pair']==pair and r['direction']==kind and 0<=r['alpha']<=1]
            chosen=min(options,key=lambda r:(abs(r['preservation']-target),-r['alpha']))
            matched.append(dict(source_pair=pair,direction=kind,alpha=chosen['alpha'],validation_real_preservation=target,validation_random_preservation=chosen['preservation'],validation_random_numerator=chosen['preserved_numerator'],validation_random_denominator=chosen['preserved_denominator'],status='DEGENERATE_ZERO_AMPLITUDE' if chosen['alpha']==0 else 'LOCKED',selection='closest validation aggregate retention among fixed nonnegative grid<=1; tie larger amplitude; no per-test rejection'))
    dump(ROOT/'configs/RANDOM_PRESERVATION_LOCK.json',dict(locked=matched,source_sha=sha(folder/'perturbation_curves.jsonl'),independent_test_accessed=0))
    qualification=[r for p in sorted(folder.glob('*_qualification.jsonl')) for r in rows(p)]
    bridge=[r for p in sorted(folder.glob('*_bridge.jsonl')) for r in rows(p)]
    qsummary=[]
    for group in ('train','validation','replay'):
        for pair in sorted({r['source_pair'] for r in qualification}):
            rs=[r for r in qualification if r['split']==group and r['source_pair']==pair];ok=[r for r in rs if r['eligible']]
            if rs:qsummary.append(dict(split=group,source_pair=pair,scanned_worlds=len(rs),qualified_worlds=len(ok),mean_delta_norm=float(np.mean([r['delta_norm'] for r in ok])) if ok else None,exclusions={reason:sum(reason in r['reasons'] for r in rs) for reason in sorted({reason for r in rs for reason in r['reasons']})}))
    csv_write(ROOT/'results/panel_A_qualification.csv',qsummary)
    bsummary=[]
    for group in ('discovery','validation','replay'):
        for pair in sorted({r['source_pair'] for r in bridge}):
            for op in ('plus','minus'):
                rs=[r for r in bridge if r['split']==group and r['source_pair']==pair and r['operation']==op]
                if rs:bsummary.append(dict(split=group,source_pair=pair,operation=op,panel_A_denominator=len(rs),panel_B_numerator=sum(r['panel_B'] for r in rs),a_next_joint=sum(r['a_next']['score']['success'] for r in rs),b_next_joint=sum(r['b_next']['score']['success'] for r in rs)))
    csv_write(ROOT/'results/next_edit_bridge.csv',bsummary)
    endpoint=[r for r in cs if r['alpha']==1 and r['split']=='validation']
    numerical=dict(readout=summary,panel_A=qsummary,panel_B=bsummary,validation_alpha1=endpoint,matched_random_lock=matched)
    dump(ROOT/'results/S1_NUMERICAL_AUDIT.json',numerical)
    coarse={}
    for r in conditions:
        if r['split']=='discovery' and r['condition']=='VALUE_ZERO_OOD':coarse.setdefault(r['module'],[]).append(r['content_margin_shift'])
    ranked=sorted(coarse,key=lambda name:(np.mean(coarse[name]),name));assert ranked
    rng=random.Random(81001);candidate=ranked[0];randomsite=rng.choice([n for n in sorted(coarse) if n!=candidate])
    selection=dict(candidate=candidate,head=0,random_site=randomsite,ranked_discovery_mean_margin={n:float(np.mean(coarse[n])) for n in ranked},choice='most negative content-margin change under discovery value zeroing; independently validate normal color resampling; fixed head0 supplementary',random_seed=81001,max_candidates=1,validation_gate=dict(min_worlds=20,content_damage_min=.1,content_damage_gte_target_damage=True,mean_content_margin_shift_max=-.2),test_accessed=0)
    dump(ROOT/'configs/S2_CANDIDATES.json',selection)
    text(ROOT/'S1_READOUT_REPORT.md','# Discovery/validation readout results\n\n'+json.dumps(numerical,ensure_ascii=False,indent=2)+'\n\n配对只要求当前正确、exact native tokens/raw text、shape/mask及非底噪差异；不以next fork筛选。旧PCA replay单列。当前共同文本不等于概率/内部等价。曲线保留完整非单调网格，未二分搜索。独立test仍封存。32 validation worlds为探索性分析，不能越过独立确认至少40-world门槛。\n\nSDPA native projection self-patch误差0；eager候选backend对齐失败另报，未用于此run。SDPA不物化attention probs；AV/W_O及residual/norm实际hook值与观测传播保存。推断注意力pattern仅作后续诊断，不能声称是materialized fused-kernel内部张量。matched-current-preservation随机幅度仅由validation锁定，若alpha=0须称退化零扰动对照，不能解释为同范数随机方向保护能力。未称完整S1确认。\n')
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
