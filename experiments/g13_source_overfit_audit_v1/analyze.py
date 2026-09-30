"""CPU-only aggregation, world-paired uncertainty, cases and reproducible report."""
import collections, gzip, math, statistics
import numpy as np
from common_g13 import *
REL={-4:'four days ago',-3:'three days ago',-2:'two days ago',-1:'yesterday',0:'today',1:'tomorrow',2:'in two days',3:'in three days',4:'in four days'}
def mean(xs): return float(np.mean(xs)) if len(xs) else None
def wilson(k,n):
    if not n: return [None,None]
    z=1.959963984540054; p=k/n; den=1+z*z/n; c=(p+z*z/(2*n))/den; h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return [c-h,c+h]
def proportion(xs):
    n=len(xs); k=int(sum(xs)); return dict(n=n,k=k,rate=k/n if n else None,wilson95=wilson(k,n))
def fmt(x): return 'NA' if x is None else f'{100*x:.2f}%'
def frac(xs): return f"{sum(xs)}/{len(xs)} ({fmt(mean(xs))})" if xs else 'NA (0)'
def table(headers,rows): return '\n'.join(['|'+'|'.join(headers)+'|','|'+'|'.join(['---']*len(headers))+'|']+['|'+'|'.join(map(str,r))+'|' for r in rows])
def grouping(rows,keys):
    out=collections.defaultdict(list)
    for r in rows: out[tuple(r[k] for k in keys)].append(r)
    return out
def fr_by_world(fr,matched=True):
    by=collections.defaultdict(dict)
    for r in fr:
        if matched and not r['matched']: continue
        by[r['record_id']][r['source']]=r
    return by
def error_type(r):
    s=r['score']
    if s['parse_unresolved']: return 'parse_unresolved'
    if s['parsed_date_error'] and s['parsed_nondate_error']: return 'date_and_fact_error'
    if s['parsed_date_error']: return 'date_error'
    if s['parsed_nondate_error']: return 'fact_error'
    if not s['perspective_ok']: return 'perspective_error'
    if not r['normal_end']: return 'length_limit'
    if s['joint_ok'] and not r['exact']: return 'format_only'
    return 'success'
def main():
    verify_lock(); complete=[s for s in CFG['seeds'] if (ROOT/f'seed_s{s}_complete.json').exists()]
    missing=[s for s in CFG['seeds'] if s not in complete]
    rows=[]
    for p in sorted((ROOT/'outputs').glob('*.jsonl')): rows+=read(p)
    if (ROOT/'per_example.jsonl.gz').exists():
        raw_keys={(r['method'],r['seed'],r['split'],r['checkpoint']) for r in rows}
        with gzip.open(ROOT/'per_example.jsonl.gz','rt',encoding='utf-8') as f:
            for l in f:
                if not l.strip(): continue
                r=json.loads(l)
                if (r['method'],r['seed'],r['split'],r['checkpoint']) not in raw_keys: rows.append(r)
    worlds={w['record_id']:w for w in read(ROOT/'data/worlds.jsonl')}
    failures={}
    for r in rows:
        r['error_type']=error_type(r)
        if r['kind']=='rollout' and r['first_failure']==r['step']:
            failures[r['method'],r['seed'],r['split'],r['checkpoint'],r['mode'],r['record_id']]=r['error_type']
    for r in rows:
        if r['kind']=='rollout': r['first_failure_type']=failures.get((r['method'],r['seed'],r['split'],r['checkpoint'],r['mode'],r['record_id'])) if r['first_failure'] is not None else None
    # Save exact raw texts, gold facts, parses, score, source and steps. Compressed copy is the Git artifact.
    with (ROOT/'per_example.jsonl').open('w') as f, gzip.open(ROOT/'per_example.jsonl.gz','wt',encoding='utf-8',compresslevel=6) as g:
        for r in rows:
            w=worlds[r['record_id']]; assert score(r['output'],r['frame'],w,r['normal_end'])==r['score']
            line=json.dumps(dict(r,world=w),ensure_ascii=False)+'\n'; f.write(line); g.write(line)
    dump(ROOT/'per_example_manifest.json',dict(path=str(ROOT/'per_example.jsonl'),sha256=digest(ROOT/'per_example.jsonl'),bytes=(ROOT/'per_example.jsonl').stat().st_size,rows=len(rows),git_artifact='per_example.jsonl.gz',gzip_sha256=digest(ROOT/'per_example.jsonl.gz'),unpack='gzip -dc per_example.jsonl.gz > per_example.jsonl',no_latents_uploaded=True))
    datasets=grouping(rows,['method','seed','split','checkpoint']); fixed=[]; atoms=[]; rolls=[]; core=[]; core_roll=[]; errors=[]; unmatched=[]; metrics={}; maps={}
    for s in complete:
        for method in ['T0']+CFG['methods']:
            for split in ['iid','template_ood']:
                assert len(datasets[method,s,split,'final'])==8480,(method,s,split,'missing final outputs')
    for (method,s,split,cp),rs in datasets.items():
        fr=[r for r in rs if r['kind']=='fixed']; ar=[r for r in rs if r['kind']=='atomic']; rr=[r for r in rs if r['kind']=='rollout']; by=fr_by_world(fr); n=len(by); N=len(fr)//3
        am=[]
        for (status,d,p),cell in grouping(ar,['status','offset','perspective']).items():
            z=proportion([r['score']['joint_ok'] for r in cell]); am.append(z['rate']); atoms.append(dict(method=method,seed=s,split=split,checkpoint=cp,status=status,offset=d,transition=REL[d]+' -> '+REL[d-1],perspective=p,k=z['k'],n=z['n'],rate=z['rate'],wilson_lo=z['wilson95'][0],wilson_hi=z['wilson95'][1],exact_k=sum(r['exact'] for r in cell),parse_unresolved=sum(r['score']['parse_unresolved'] for r in cell),date_errors=sum(r['score']['parsed_date_error'] for r in cell),fact_errors=sum(r['score']['parsed_nondate_error'] for r in cell),outside_T0_natural_support=(d==4)))
        macro=mean(am); metrics[method,s,split,cp]={}; mp={}
        metrics[method,s,split,cp]['atomic_macro']=macro
        # Each world contributes a cell-count-weighted mean. This reproduces the 40-cell macro.
        byatom=grouping(ar,['record_id'])
        mp['atomic_macro']={k[0]:mean([r['score']['joint_ok'] for r in cell])*len(cell)*3/40 for k,cell in byatom.items()}
        oldsupport=mean([a['rate'] for a in atoms if a['method']==method and a['seed']==s and a['split']==split and a['checkpoint']==cp and not a['outside_T0_natural_support']])
        metrics[method,s,split,cp]['atomic_T0_support']=oldsupport
        source_rates=[]; source_fracs=[]; source_k=[]
        for src in range(3):
            cell=[b[src] for b in by.values()]; successes=[r['score']['joint_ok'] for r in cell]; z=proportion(successes); source_rates.append(z['rate']); source_fracs.append(frac(successes)); source_k.append(z['k']); metrics[method,s,split,cp]['H'+str(src)]=z['rate']; mp['H'+str(src)]={rid:int(b[src]['score']['joint_ok']) for rid,b in by.items()}
            fixed.append(dict(method=method,seed=s,split=split,checkpoint=cp,source=src,k=z['k'],n=n,raw_N=N,rate=z['rate'],wilson_lo=z['wilson95'][0],wilson_hi=z['wilson95'][1],coverage=n/N,gate_and_next_k=z['k'],gate_and_next_rate=z['k']/N,exact_k=sum(r['exact'] for r in cell),parse_unresolved=sum(r['score']['parse_unresolved'] for r in cell),date_errors=sum(r['score']['parsed_date_error'] for r in cell),fact_errors=sum(r['score']['parsed_nondate_error'] for r in cell),format_only=sum(r['score']['joint_ok'] and not r['exact'] for r in cell),exploratory=n<40))
            non=[r for r in fr if r['source']==src and not r['matched']]; unmatched.append(dict(method=method,seed=s,split=split,checkpoint=cp,source=src,n=len(non),joint_k=sum(r['score']['joint_ok'] for r in non),exact_k=sum(r['exact'] for r in non),note='outside fixed same-text mechanism cohort'))
        joint=[all(b[k]['score']['joint_ok'] for k in range(3)) for b in by.values()]; all3=mean(joint); metrics[method,s,split,cp]['all3']=all3; mp['all3']={rid:int(all(b[k]['score']['joint_ok'] for k in range(3))) for rid,b in by.items()}
        minsrc=min(source_rates) if n else None; gap=source_rates[0]-source_rates[2] if n else None
        fixed.append(dict(method=method,seed=s,split=split,checkpoint=cp,source='all3',k=sum(joint),n=n,raw_N=N,rate=all3,wilson_lo=wilson(sum(joint),n)[0],wilson_hi=wilson(sum(joint),n)[1],coverage=n/N,gate_and_next_k=sum(joint),gate_and_next_rate=sum(joint)/N,exploratory=n<40,min_source=minsrc,H0_minus_H2_pp=100*gap if gap is not None else None))
        today=[r for r in ar if r['offset']==0 and r['status']=='recorded_plan' and r['perspective']=='first']
        core.append(dict(method=method,seed=s,split=split,checkpoint=cp,atomic_macro=macro,atomic_T0_support=oldsupport,today=frac([r['score']['joint_ok'] for r in today]),H0=source_fracs[0],H1=source_fracs[1],H2=source_fracs[2],min_source=minsrc,all3=frac(joint),matched=f'{n}/{N}',n=n,N=N,coverage_rate=n/N,**{'gate_H'+str(k):f'{source_k[k]}/{N} ({fmt(source_k[k]/N)})' for k in range(3)},gate_all3=f'{sum(joint)}/{N} ({fmt(sum(joint)/N)})'))
        rd={}
        for (mode,k),cell in grouping(rr,['mode','step']).items():
            ep=proportion([r['score']['joint_ok'] for r in cell]); tr=proportion([r['trajectory_ok'] for r in cell]); rd[mode,k]=cell
            metric=f'{mode}_full{k}'; metrics[method,s,split,cp][metric]=tr['rate']; mp[metric]={r['record_id']:int(r['trajectory_ok']) for r in cell}
            rolls.append(dict(method=method,seed=s,split=split,checkpoint=cp,mode=mode,step=k,n=ep['n'],endpoint_k=ep['k'],endpoint_rate=ep['rate'],endpoint_wilson_lo=ep['wilson95'][0],endpoint_wilson_hi=ep['wilson95'][1],trajectory_k=tr['k'],trajectory_rate=tr['rate'],trajectory_wilson_lo=tr['wilson95'][0],trajectory_wilson_hi=tr['wilson95'][1],first_failed_at_step=sum(r['first_failure']==k for r in cell),unresolved=sum(r['score']['parse_unresolved'] for r in cell),date_errors=sum(r['score']['parsed_date_error'] for r in cell),fact_errors=sum(r['score']['parsed_nondate_error'] for r in cell),natural_conversion_replayed=method in ['F1','F2','F3'],own_edited_source_directly_supervised=False,frozen_H2_analogue=(k==3 and method in ['F0','F1','F3']),source_note='only fixed G yesterday H1/H2 supervised; own updated R edited sources are not cached training inputs, including depth1 today'))
        if rd:
            core_roll.append(dict(method=method,seed=s,split=split,checkpoint=cp,step1=frac([r['score']['joint_ok'] for r in rd['latent',1]]),**{f'step{k}':frac([r['trajectory_ok'] for r in rd['latent',k]]) for k in range(2,6)},reencode5=frac([r['trajectory_ok'] for r in rd['reencode',5]])))
        maps[method,s,split,cp]=mp
        for (kind,),cell in grouping(rs,['kind']).items(): errors.append(dict(method=method,seed=s,split=split,checkpoint=cp,kind=kind,observations=len(cell),parse_unresolved=sum(r['score']['parse_unresolved'] for r in cell),confirmed_date_error=sum(r['score']['parsed_date_error'] for r in cell),confirmed_fact_error=sum(r['score']['parsed_nondate_error'] for r in cell),confirmed_perspective_error=sum(not r['score']['parse_unresolved'] and not r['score']['perspective_ok'] for r in cell),length_limit=sum(not r['normal_end'] for r in cell),semantic_success_format_diff=sum(r['score']['joint_ok'] and not r['exact'] for r in cell)))
    for filename,rs in [('fixed_source_results.csv',fixed),('atomic_by_transition.csv',atoms),('rollout_results.csv',rolls),('unmatched_results.csv',unmatched),('error_counts.csv',errors),('core_source_table.csv',core),('core_rollout_table.csv',core_roll)]: csvwrite(ROOT/filename,rs)
    failure_rows=[]
    finals=[r for r in rows if r['kind']=='rollout' and r['step']==5]
    for keys,cell in grouping(finals,['method','seed','split','checkpoint','mode']).items():
        counts=collections.Counter((r['first_failure'],r['first_failure_type']) for r in cell)
        failure_rows += [dict(zip(['method','seed','split','checkpoint','mode'],keys),first_failure=k[0],error_type=k[1] or 'no_failure',k=n,N=len(cell)) for k,n in counts.items()]
    csvwrite(ROOT/'first_failure_types.csv',failure_rows)
    # Paired contrasts per seed; identical immutable C across arms makes source pairings valid.
    contrasts=[]; rng=np.random.default_rng(CFG['bootstrap_seed']); B=CFG['bootstrap_replicates']
    pairs=[('F1','F0'),('F1','F2'),('F3','F1'),('F3','F2')]
    wanted=['atomic_macro','H0','H1','H2','all3','latent_full3','latent_full4','latent_full5','reencode_full5']
    for split in ['iid','template_ood']:
        all_ids={status:sorted(w['record_id'] for w in worlds.values() if w['split']==split and w['record_status']==status) for status in ['recorded_plan','reported_cancelled','reported_completed']}
        draws={st:rng.integers(0,len(ids),(B,len(ids))) for st,ids in all_ids.items()}
        for a,b in pairs:
            for metric in wanted:
                seed_deltas=[]; seed_boot=[]; seedNs={}
                for s in complete:
                    if (a,s,split,'final') not in maps or (b,s,split,'final') not in maps: continue
                    ma=maps[a,s,split,'final'].get(metric,{}); mb=maps[b,s,split,'final'].get(metric,{}); ids=sorted(set(ma)&set(mb)); seedNs[str(s)]=len(ids)
                    assert set(ma)==set(mb), 'Do not force pair different source cohorts'
                    if not ids: continue
                    delta=mean([ma[i]-mb[i] for i in ids]); boots=[]
                    statuses=list(all_ids) if metric=='atomic_macro' else ['recorded_plan']
                    for j in range(B):
                        vals=[]
                        for st in statuses:
                            vals += [ma[all_ids[st][k]]-mb[all_ids[st][k]] for k in draws[st][j] if all_ids[st][k] in ma]
                        boots.append(mean(vals))
                    bt=np.array([x for x in boots if x is not None]); lo,hi=np.quantile(bt,[.025,.975]); seed_deltas.append(delta); seed_boot.append(boots)
                    contrasts.append(dict(contrast=a+'-'+b,split=split,seed=s,metric=metric,n=len(ids),delta_pp=100*delta,ci_lo_pp=100*lo,ci_hi_pp=100*hi,replicates=B,uncertainty='paired world resampling; fixed training seed; status-stratified atomic sampling',degenerate=bool(lo==hi),binomial_intervals='see component proportions Wilson intervals'))
                if seed_deltas:
                    bt=np.nanmean(np.array([[np.nan if x is None else x for x in z] for z in seed_boot]),axis=0); lo,hi=np.quantile(bt,[.025,.975]); contrasts.append(dict(contrast=a+'-'+b,split=split,seed='mean',metric=metric,n=json.dumps(seedNs),delta_pp=100*mean(seed_deltas),seed_sd_pp=100*statistics.stdev(seed_deltas) if len(seed_deltas)>1 else None,ci_lo_pp=100*lo,ci_hi_pp=100*hi,replicates=B,uncertainty='same world draws shared across fixed seeds; training randomness summarized separately',degenerate=bool(lo==hi)))
    csvwrite(ROOT/'paired_contrasts.csv',contrasts)
    # Cross-seed common C sensitivity, with honest denominator and no pooled-seed trials.
    robustness=[]
    for split in ['iid','template_ood']:
        sets=[set(json.loads((ROOT/f'data/cohort_s{s}.json').read_text())['cohorts'][split]) for s in complete]; common=set.intersection(*sets) if sets else set()
        for method in ['T0']+CFG['methods']:
            for s in complete:
                mp=maps.get((method,s,split,'final'),{})
                for metric in ['H0','H1','H2','all3']:
                    v=[mp.get(metric,{})[i] for i in sorted(common) if i in mp.get(metric,{})]; z=proportion(v); robustness.append(dict(method=method,seed=s,split=split,metric=metric,common_n=len(common),k=z['k'],n=z['n'],rate=z['rate'],exploratory=len(common)<40))
    csvwrite(ROOT/'cross_seed_common_cohort.csv',robustness)
    # Seed means and SD for every core metric (no treating shared worlds as extra seeds).
    summaries=[]
    for method in ['T0']+CFG['methods']:
        for split in ['iid','template_ood']:
            for metric in ['atomic_macro','atomic_T0_support','H0','H1','H2','all3','latent_full1','latent_full2','latent_full3','latent_full4','latent_full5','reencode_full5']:
                vals=[metrics.get((method,s,split,'final'),{}).get(metric) for s in complete]; vals=[v for v in vals if v is not None]
                summaries.append(dict(method=method,split=split,metric=metric,seeds=len(vals),mean=mean(vals),sd=statistics.stdev(vals) if len(vals)>1 else None,seed_values=json.dumps(vals)))
    csvwrite(ROOT/'seed_mean_sd.csv',summaries)
    # Fixed-source train vs independent IID on equal one-step semantic targets; matched/all worlds distinguished.
    train_iid=[]; learning=[]; learning_atoms=[]; budget_rows=[]; learning_raw=[]
    for p in sorted((ROOT/'learning').glob('*.jsonl')): learning_raw+=read(p)
    if not learning_raw and (ROOT/'learning_per_example.jsonl.gz').exists():
        with gzip.open(ROOT/'learning_per_example.jsonl.gz','rt',encoding='utf-8') as f: learning_raw=[json.loads(l) for l in f if l.strip()]
    with gzip.open(ROOT/'learning_per_example.jsonl.gz','wt',encoding='utf-8',compresslevel=6) as g:
        for r in learning_raw:
            g.write(json.dumps(r,ensure_ascii=False)+'\n')
            if r['kind']=='atomic': learning_atoms.append(r)
    la=[]
    for (method,s,split,cp,status,d,p),cell in grouping(learning_atoms,['method','seed','split','checkpoint','status','offset','perspective']).items():
        z=proportion([r['score']['joint_ok'] for r in cell]); la.append(dict(method=method,seed=s,split=split,step=cp,status=status,offset=d,perspective=p,k=z['k'],n=z['n'],rate=z['rate']))
    csvwrite(ROOT/'learning_atomic_by_transition.csv',la)
    for s in complete:
        for method in CFG['methods']:
            meta=json.loads((ROOT/f'training/{method}_s{s}.json').read_text()); fullsources={'H'+k:v for k,v in meta['anchor_source_counts'].items()}; bgsource='H2' if method=='F0' else 'E_atomic'; fullsources[bgsource]=fullsources.get(bgsource,0)+3200
            budget_rows.append(dict(method=method,seed=s,steps=meta['updates'],supervised_instances=meta['counts']['instances'],anchor_tokens=meta['counts']['anchor_tokens'],background_tokens=meta['counts']['background_tokens'],total_tokens=meta['counts']['anchor_tokens']+meta['counts']['background_tokens'],anchor_source_counts=json.dumps(meta['anchor_source_counts']),background_source=bgsource,background_instances=3200,source_counts=json.dumps(fullsources),training_and_diagnostic_seconds=meta['training_and_diagnostic_seconds'],peak_cuda_bytes=meta['peak_cuda_bytes'],best_step=meta['best_step']))
            for x in meta['curve']:
                for src in range(3): learning.append(dict(method=method,seed=s,step=x['step'],split=x['split'],source=src,token_nll=x['token_nll'][str(src)],success=x['source'][str(src)],matched_n=x['matched_n'],raw_n=x['original_n'],atomic_macro=x['atomic_macro'],all3=x['all3']))
            tr=[r for r in learning_raw if r['method']==method and r['seed']==s and r['split']=='train' and r['checkpoint']=='200' and r['kind']=='fixed']; iid=[r for r in datasets[method,s,'iid','final'] if r['kind']=='fixed']
            for matched in [True,False]:
                for src in range(3):
                    a=[r for r in tr if r['source']==src and (r['matched'] or not matched)]; b=[r for r in iid if r['source']==src and (r['matched'] or not matched)]
                    la=sum(r['loss_sum'] for r in a)/sum(r['target_tokens'] for r in a) if a else None; lb=sum(r['loss_sum'] for r in b)/sum(r['target_tokens'] for r in b) if b else None
                    aa=mean([r['score']['joint_ok'] for r in a]); bb=mean([r['score']['joint_ok'] for r in b]); interval=[None,None]
                    if a and b:
                        va=np.array([r['score']['joint_ok'] for r in a],dtype=float); vb=np.array([r['score']['joint_ok'] for r in b],dtype=float)
                        bt=va[rng.integers(0,len(va),(B,len(va)))].mean(1)-vb[rng.integers(0,len(vb),(B,len(vb)))].mean(1); interval=(100*np.quantile(bt,[.025,.975])).tolist()
                    train_iid.append(dict(method=method,seed=s,source=src,matched_only=matched,seen_source=(src==2 if method in ['F0','F1'] else src==0 if method=='F2' else True),train_n=len(a),iid_n=len(b),train_k=sum(r['score']['joint_ok'] for r in a),iid_k=sum(r['score']['joint_ok'] for r in b),train_rate=aa,iid_rate=bb,gap_pp=100*(aa-bb) if aa is not None and bb is not None else None,gap_ci_lo_pp=interval[0],gap_ci_hi_pp=interval[1],gap_uncertainty='independent world bootstrap, train and IID are different worlds',train_wilson=json.dumps(wilson(sum(r['score']['joint_ok'] for r in a),len(a))),iid_wilson=json.dumps(wilson(sum(r['score']['joint_ok'] for r in b),len(b))),train_token_nll=la,iid_token_nll=lb))
    csvwrite(ROOT/'learning_curves.csv',learning); csvwrite(ROOT/'training_iid_comparison.csv',train_iid); csvwrite(ROOT/'training_budget.csv',budget_rows)
    # Historical source/task/length matched audit includes own free rollout separately from supervised A third input.
    oldrows=[]
    for s in complete:
        rs=read(ROOT/f'baseline/train_iid_s{s}.jsonl')
        for (method,split,task,kind,step,source),cell in grouping(rs,['method','split','task','kind','step','source']).items():
            oldrows.append(dict(method=method,seed=s,split=split,task=task,kind=kind,step=step,source=source,n=len(cell),joint_k=sum(r['score']['joint_ok'] for r in cell),joint_rate=mean([r['score']['joint_ok'] for r in cell]),trajectory_k=sum(r.get('trajectory_ok',False) for r in cell) if kind=='old_free' else None,token_nll=sum(r['loss_sum'] for r in cell)/sum(r['target_tokens'] for r in cell) if kind=='old_diagnostic' else None))
    csvwrite(ROOT/'baseline/train_iid_summary.csv',oldrows)
    # Deterministic category sampling, then deterministic fallback to at least24 actual cases.
    casepool=[]
    for (method,s,split,cp),rs in datasets.items():
        if cp!='final' or method=='T0': continue
        fr=fr_by_world([r for r in rs if r['kind']=='fixed']); rollout={r['record_id']:r for r in rs if r['kind']=='rollout' and r['mode']=='latent' and r['step']==5}
        third={r['record_id']:r for r in rs if r['kind']=='rollout' and r['mode']=='latent' and r['step']==3}
        for rid,b in fr.items():
            cats=[]; h0=b[0]['score']['joint_ok']; h2=b[2]['score']['joint_ok']
            if h0 and not h2: cats.append('natural_only')
            if h2 and not h0: cats.append('edited_only')
            if all(b[k]['score']['joint_ok'] for k in range(3)): cats.append('all3')
            if h2 and not third[rid]['trajectory_ok']: cats.append('fixed_success_rollout_failure')
            ident=f'{method}/{s}/{split}/{rid}'; rank=hashlib.sha256(f'{CFG["cases"]["seed"]}/{ident}'.encode()).hexdigest()
            casepool.append(dict(id=ident,rank=rank,categories=cats,method=method,seed=s,split=split,record_id=rid,current_text=b[0]['current_text'],sources=[b[k] for k in range(3)],first_failure=rollout[rid]['first_failure'],rollout_step5=rollout[rid],world=worlds[rid]))
    casepool.sort(key=lambda z:z['rank']); picked=[]; counts={}; used=set()
    for cat in CFG['cases']['categories']:
        sel=[r for r in casepool if cat in r['categories'] and r['id'] not in used][:6]; counts[cat]=len(sel)
        for r in sel: picked.append(dict(r,selected_category=cat)); used.add(r['id'])
    for r in casepool:
        if len(picked)>=24: break
        if r['id'] not in used: picked.append(dict(r,selected_category='deterministic_fallback')); used.add(r['id'])
    write(ROOT/'cases.jsonl',picked); dump(ROOT/'case_selection.json',dict(predeclared_categories=CFG['cases'],available={cat:sum(cat in x['categories'] for x in casepool) for cat in counts},selected=counts,actual_total=len(picked),no_fabrication=True))
    lines=['# Fixed diagnostic cases','', 'Category absence is explicit: '+json.dumps(counts)+'. Fallback cases do not claim an absent category. Unresolved parse is a conservative failure, not a confirmed fact error.','']
    for i,r in enumerate(picked,1):
        lines += [f'## {i}. {r["selected_category"]}: {r["id"]}', '', f'Current: {r["current_text"]}',f'Gold next: {r["sources"][0]["gold"]}', f'Own rollout first failure: {r["first_failure"]}', '']
        for o in r['sources']:
            lines += [f'H{o["source"]}: {o["output"]}',f'joint={o["score"]["joint_ok"]}; parsed={json.dumps(o["score"]["parsed"],ensure_ascii=False)}; unresolved={o["score"]["parse_unresolved"]}; date error={o["score"]["parsed_date_error"]}; other fact error={o["score"]["parsed_nondate_error"]}', '']
        lines += [f'Own step5: {r["rollout_step5"]["output"]}',f'Gold step5: {r["rollout_step5"]["gold"]}', '']
    (ROOT/'CASES.md').write_text('\n'.join(lines).rstrip()+'\n')
    # Decision criteria per seed, keeping support and source fit separate.
    decisions=[]
    for s in complete:
        m=metrics['F3',s,'iid','final']; t=metrics['T0',s,'iid','final']; drop=100*(t['atomic_macro']-m['atomic_macro']); source_ok=all(m[k] is not None and m[k]>=.95 for k in ['H0','H1','H2']); all3_ok=m['all3'] is not None and m['all3']>=.9
        minimum=min(a['rate'] for a in atoms if a['method']=='F3' and a['seed']==s and a['split']=='iid' and a['checkpoint']=='final')
        decisions.append(dict(seed=s,sources_95=source_ok,all3_90=all3_ok,atomic_drop_pp=drop,atomic_drop_le5=drop<=5,atomic_min_cell=minimum,working_repair=source_ok and all3_ok and drop<=5,own_step2=m['latent_full2'],own_step5=m['latent_full5']))
    dump(ROOT/'decision.json',decisions)
    report(core,core_roll,summaries,contrasts,train_iid,oldrows,decisions,complete,missing,budget_rows,learning)
    meta_checks=[json.loads((ROOT/f'training/{method}_s{s}.json').read_text()) for s in complete for method in CFG['methods']]
    frozen=all(m['G_unchanged'] and m['ED_unchanged'] and m['caches_unchanged'] for m in meta_checks)
    count_ok=all(x['supervised_instances']==6400 for x in budget_rows); replay_ok=all(len({x['background_tokens'] for x in budget_rows if x['seed']==s and x['method'] in ['F1','F2','F3']})==1 for s in complete); anchor_ok=all(len({x['anchor_tokens'] for x in budget_rows if x['seed']==s and x['method'] in ['F1','F2','F3']})==1 for s in complete)
    assert frozen and count_ok and replay_ok and anchor_ok
    dump(ROOT/'result_audit.json',dict(completed_seeds=complete,missing_seeds=missing,all_output_scores_recomputed=True,rows=len(rows),data_lock_valid=True,small_cases=len(picked),all_counts_6400=count_ok,replay_tokens_equal=replay_ok,anchor_tokens_equal=anchor_ok,frozen_checks_all=frozen,no_test_checkpoint_selection=True))
    print('aggregated',len(rows),'rows, complete',complete,flush=True)

def report(core,core_roll,summaries,contrasts,train_iid,oldrows,decisions,complete,missing,budget_rows,learning):
    primary=[r for r in core if r['checkpoint']=='final']; primary_roll=[r for r in core_roll if r['checkpoint']=='final']; success=sum(x['working_repair'] for x in decisions)
    evidence=[]
    f10=next((r for r in contrasts if r['seed']=='mean' and r['split']=='iid' and r['contrast']=='F1-F0' and r['metric']=='atomic_macro'),None)
    if f10 is not None:
        evidence.append(f"F1−F0 的 IID 原子宏平均差为 {f10['delta_pp']:.2f} pp（世界bootstrap95%CI {f10['ci_lo_pp']:.2f}…{f10['ci_hi_pp']:.2f}）")
    h2=next((r for r in contrasts if r['seed']=='mean' and r['split']=='iid' and r['contrast']=='F1-F0' and r['metric']=='H2'),None)
    if h2 is not None: evidence.append(f"固定H2差为 {h2['delta_pp']:.2f} pp")
    overfit=[]
    for r in train_iid:
        if not (r['matched_only'] and r['seen_source'] and r['gap_ci_lo_pp'] is not None and r['gap_ci_lo_pp']>0): continue
        cu={(v['split'],v['step']):v for v in learning if v['method']==r['method'] and v['seed']==r['seed'] and v['source']==r['source']}
        if cu['train',200]['token_nll']<cu['train',0]['token_nll'] and cu['dev',200]['token_nll']>cu['dev',0]['token_nll']: overfit.append(f"{r['method']}/s{r['seed']}/H{r['source']}")
    if complete:
        supported=[]
        if f10 and f10['ci_lo_pp']>0 and h2 and h2['delta_pp']>=0: supported.append('原子覆盖不足／监督预算分配')
        if success: supported.append(f'固定表示来源监督与适应不足（F3有{success}/{len(complete)}个seed达到工作修复门槛，显示这些具体来源可同时学会）')
        conclusion='目前结果更支持'+'、'.join(supported)+'。' if supported else '目前未满足预定修复证据门槛，当前实验尚不能完整区分来源适应、优化或监督兼容性问题。'
        conclusion+=('同时观察到符合预定普通过拟合证据组合的 '+', '.join(overfit)+'。' if overfit else '同来源训练/IID比较和学习曲线未形成普通样本过拟合作为主要解释的配套证据。')
        self5=[r['own_step5'] for r in decisions]
        conclusion+=f"F3自身第二步完整轨迹逐seed为 {[fmt(r['own_step2']) for r in decisions]}，第五步为 {[fmt(x) for x in self5]}；固定旧来源可处理仍不等于更新后自身表示链的闭包泛化。"
    else: conclusion='实验尚未完成，当前只能报告已有部分结果，不能作三seed结论。'
    # Report body below uses the locked final-step metrics, never selected confirmation performance.
    out=['# G13 编辑器过拟合与表示来源诊断','',f'**{conclusion}** '+ '；'.join(evidence)+f'。完成seed={complete}；未完成seed={missing}。四组各seed最终固定200步为主结果，best-dev只作次分析。', '', '表一：来源与能力保护（40-cell自然原子宏平均；today→yesterday为plan/first自然输入；来源值为成功n/C；匹配n/N以160主世界为分母）。','',table(['method','seed','split','原子宏平均','today→yesterday','H0','H1','H2','min-source','all3','匹配 n/N'],[[r['method'],r['seed'],r['split'],fmt(r['atomic_macro']),r['today'],r['H0'],r['H1'],r['H2'],fmt(r['min_source']),r['all3'],r['matched']] for r in primary]),'', '表二：自身自由rollout（所有160个plan测试世界，更新后的R自己的状态；重编码只用自身自由输出）。','',table(['method','seed','split','step1 endpoint','step2 full','step3 full','step4 full','step5 full','重编码 step5 full'],[[r[k] for k in ['method','seed','split','step1','step2','step3','step4','step5','reencode5']] for r in primary_roll]),'', 'F1/F2/F3回放覆盖全部五步自然转换，包括three days ago→four days ago；F0无回放。第二步输入是更新R产生的today编辑态，本轮没有直接监督该状态；第三步yesterday有固定G的H2对应但分布不同；第四/第五步涉及未训练的更深编辑态。语义覆盖、表示来源覆盖与深度外推分别判断。固定H2续步绝不计作自身第三步完整轨迹。IID/OOD保留共享受控词汇；模板8–11相对T0/G12/G13训练0–7持出，不能外推开放语言。合法自然offset+4在T0训练支持外，atomic_T0_support另报原有支持。','', '## 三seed均值和标准差','',table(['method','split','metric','seed N','mean','SD'],[[r['method'],r['split'],r['metric'],r['seeds'],fmt(r['mean']),fmt(r['sd'])] for r in summaries]),'', '## 配对组间差（百分点）','', '2000次world-level paired bootstrap，同seed同世界配对；原子按状态分层，跨seed使用共享世界抽样。CI只代表固定训练seed下世界抽样不确定性，训练随机性用seed SD另报。全零/全一退化bootstrap不是总体无不确定性证明；逐比例Wilson区间在三个结果CSV中（例如0/160的95%Wilson上界约2.34%）。共同来源集合随seed变化，cross_seed_common_cohort.csv报告交集稳健性；C<40探索性，空集合NA。','',table(['contrast','split','seed','metric','N','difference','CI95'],[[r['contrast'],r['split'],r['seed'],r['metric'],r['n'],f"{r['delta_pp']:.2f}",f"[{r['ci_lo_pp']:.2f}, {r['ci_hi_pp']:.2f}]"] for r in contrasts if r['metric'] in ['atomic_macro','H0','H2','all3','latent_full5']]),'', '## 同来源、同一步任务 train/IID','', '只列实际监督的来源，固定80个训练诊断世界与独立IID均使用相同匹配门槛；loss为有效目标token NLL。training_iid_comparison.csv另含全来源/全分母、训练与IID独立world bootstrap的gap CI以及各比例Wilson区间。自然原子开发监测固定每状态16世界，来源开发使用全部128主世界。原子train诊断是训练split世界，不保证每个转换tuple都出现在回放中；实际训练tuple由schedule明确给出。','',table(['method','seed','source','train n','IID n','train joint','IID joint','gap pp','train NLL','IID NLL'],[[r['method'],r['seed'],'H'+str(r['source']),r['train_n'],r['iid_n'],fmt(r['train_rate']),fmt(r['iid_rate']),f"{r['gap_pp']:.2f}" if r['gap_pp'] is not None else 'NA',f"{r['train_token_nll']:.5f}" if r['train_token_nll'] is not None else 'NA',f"{r['iid_token_nll']:.5f}" if r['iid_token_nll'] is not None else 'NA'] for r in train_iid if r['matched_only'] and r['seen_source']]),'']
    curves=[]
    out += ['## 匹配覆盖与续步的联合指标','', '以下分母是原始160世界，要求先通过固定G共同门槛再续步成功。它同时反映匹配覆盖与续步能力，不能替代普通自然单步准确率；未匹配世界另表unmatched_results.csv，逐例保持matched=false。','',table(['method','seed','split','coverage','gate+H0 / raw','gate+H1 / raw','gate+H2 / raw','gate+all3 / raw'],[[r['method'],r['seed'],r['split'],fmt(r['coverage_rate']),r['gate_H0'],r['gate_H1'],r['gate_H2'],r['gate_all3']] for r in primary]),'']
    for s in complete:
        for method in CFG['methods']:
            sources=[2] if method in ['F0','F1'] else [0] if method=='F2' else [0,1,2]
            for src in sources:
                lookup={(r['split'],r['step']):r for r in learning if r['method']==method and r['seed']==s and r['source']==src}; tr0=lookup['train',0]['token_nll']; tr1=lookup['train',200]['token_nll']; dv0=lookup['dev',0]['token_nll']; dv1=lookup['dev',200]['token_nll']; curves.append([method,s,'H'+str(src),f'{tr0:.5f}→{tr1:.5f}',f'{dv0:.5f}→{dv1:.5f}',str(tr1<tr0 and dv1>dv0)])
    out += ['同来源学习曲线：0/25/50/75/100%快照均已保存；这里只显示端点，完整曲线见learning_curves.csv。训练改进且开发恶化为事前过拟合证据之一，不能仅凭长链失败替代。','',table(['method','seed','source','train NLL 0→200','dev NLL 0→200','train改善且dev恶化'],curves),'', '## 不新增训练的旧模型审计','', 'Original按真正受监督的自然单步和二次编辑任务评估；G12 A/B三步均为受监督长度。A第三步canonical自然输入的teacher-forced/条件生成，与其自身自由第三步完整轨迹分别列出。80个真实训练世界按模板/极性分层，并与同记录状态/模板/极性/offset/人称/长度的独立IID配对；原始任务与配对身份见data/old_task_pairs_s*.json。六世界×前三步历史复现检查及所有旧G12链行重评分在baseline/，旧结果未改写。','',table(['method','seed','split','task','kind','step','source','joint n/N','free full n/N','NLL'],[[r['method'],r['seed'],r['split'],r['task'],r['kind'],r['step'],r['source'],f"{r['joint_k']}/{r['n']}",f"{r['trajectory_k']}/{r['n']}" if r['trajectory_k'] is not None else 'NA',f"{r['token_nll']:.5f}" if r['token_nll'] is not None else 'NA'] for r in oldrows]),'', '旧报告关键结论核实：G11主锚点文本匹配后下一步不同；G12 B第三步使用本组stopgrad(h2)，第三步修复但四/五步失败，且没有完整自然原子回放。后续T+推进观察参考日、事件绝对日期不变。旧日志缺少同固定诊断世界的历史验证曲线，不能声称历史训练改善且开发恶化。','', '## 能力保护与解释边界','',table(['seed','each source≥95%','all3≥90%','atomic drop pp','drop≤5pp','working repair','own step5'],[[r['seed'],r['sources_95'],r['all3_90'],f"{r['atomic_drop_pp']:.2f}",r['atomic_drop_le5'],r['working_repair'],fmt(r['own_step5'])] for r in decisions]),'', '上述阈值是本轮工作标准，不是统计非劣效性证明。逐转换和人称/状态结果全部公开，不能用宏平均掩盖某单元清零。F1−F0是等实例预算的监督分配对照，F0自然目标分布有意不同；它不能唯一归因旧G12退化。F1−F2和F3对照只改变相同锚点的表示来源。','', 'F3若同时学会H0/H1/H2并保护原子能力，可排除这些具体固定状态在本设置下必然不能共存于同rank16编辑器的说法。固定旧状态成功但自身rollout失败，支持更新后表示来源/轨迹外推未闭合；训练/IID都差则首先是优化、容量或监督兼容性未决，不能叫普通过拟合。若两套都改善，必须承认训练设计限制可解释此前失败，不坚持更强内在缺陷叙事。任何失败都不证明latent编辑不可能。','', '最小剩余问题限定为：对照固定源与自身源的已有逐例结果，并核对实际失败转换/解析类型；不追加on-policy或长链训练。可选H3/H4筛查未运行，只记未完成，不记0%。','', '## 预算、工件、验证与偏离','',table(['method','seed','steps','instances','anchor tokens','background tokens','GPU seconds incl diagnostics','best step'],[[r['method'],r['seed'],r['steps'],r['supervised_instances'],r['anchor_tokens'],r['background_tokens'],f"{r['training_and_diagnostic_seconds']:.2f}",r['best_step']] for r in budget_rows]),'', '所有组6400个有效监督实例（200×2×16），F1/F2/F3目标token序列逐项相同，F0不同token数如实记录；这个表不是allocation GPU-hour表。完整allocation资源表见slurm_jobs.csv和budget.json，stdout/stderr与提交命令均保存。单GPU smoke通过后仅主array0–2%2，每个seed顺序四组，全轮最多两张GPU。','', '十二项CPU单元测试（含实际rollout函数的CPU状态流与失败保持测试）、GPU梯度/缓存重放/保存复原/冻结参数检查、历史输出复现通过；每组训练后G/ED/cache哈希检查和其他独立算子的参数/生成监测不变。可恢复optimizer/RNG检查点在local/，仅小editor final/best权重与全部snapshot诊断上传。完整latent缓存和大型原始文本文件留现有本地工件目录；完整逐例文本/事实/解析以per_example.jsonl.gz上传，解压恢复per_example.jsonl，其精确本地路径/hash在per_example_manifest.json。','', '预训练范围扩展：额外的cancelled/completed原子世界使总训练世界1536，主锚点仍512、dev128、确认各160。保留真实生成器模板/极性联合支持。初次CPU准备配额错误、提前启动CPU测试均在任何GPU/新结果之前修正，记录pre_gpu_engineering_log.json；未改学习率/步数/组定义，未据测试追分。不可访问历史manifest范围明确未核验。','', 'best-dev所有H0/H1/H2与自然原子开发源参与选择，不能称这些来源完全未参与模型选择；每次同分取更早。','', '## Best-dev次表','',table(['method','seed','split','atomic macro','H0','H1','H2','all3','n/N'],[[r['method'],r['seed'],r['split'],fmt(r['atomic_macro']),r['H0'],r['H1'],r['H2'],r['all3'],r['matched']] for r in core if r['checkpoint']=='best']), '', '关键案例见CASES.md（确定性类别抽样、不存在的类别显式标明），完整三来源/输出/预期事实/解析/首次失败在cases.jsonl；未决、明确日期错、非日期事实错及纯格式差异分别计数于error_counts.csv。']
    if (ROOT/'budget.json').exists(): out += ['', '实际Slurm预算：'+json.dumps(json.loads((ROOT/'budget.json').read_text()),ensure_ascii=False)]
    if (ROOT/'engineering_retry_1.json').exists():
        z=json.loads((ROOT/'engineering_retry_1.json').read_text()); jobs=list(csv.DictReader((ROOT/'slurm_jobs.csv').open()))
        out += ['', '正式首轮array '+z['failed_array']+'在任何G13训练前因prepare模块同名导入遮蔽失败，使用显式文件路径导入修复后重试。科学配置、数据、schedule、学习率和200步预算未变；重试每seed walltime改为6000秒，使包含失败申请在内的累计请求为11.3333 GPU小时。不是因结果不佳重试。详见engineering_retry_1.json。', '', table(['JobID','allocation raw ID','state','GPUs','elapsed seconds','GPU hours'],[[r['job_id'],r.get('raw_job_id',r['job_id']),r['state'],r['gpu_count'],r['elapsed_seconds'],f"{float(r['gpu_hours']):.5f}"] for r in jobs])]
    out += ['', '数据RNG精确复建2880世界通过；实际使用20260930派生的status/split/round独立子流，data_rng_provenance.json记录实际调用的子流名称和种子。数据manifest中的上层namespace哈希不是实际叶子生成器seed，侧表明确区分，未改变任何锁定世界。']
    if (ROOT/'historical_refs_overlap_audit.json').exists():
        z=json.loads((ROOT/'historical_refs_overlap_audit.json').read_text()); out += ['', f"补充历史分支manifest审计：{len(z['additional_unique_manifest_blobs'])}个额外Git blob，核查{z['additional_unique_facts']}个事实身份，重合{len(z['collisions'])}，读取错误{len(z['errors'])}。这项只读补查在数据锁定后、训练运行中完成，明确属于审计时间偏离；没有替换世界、调整训练或选择checkpoint。初始训练前审计范围仍按data/manifest.json列出，补查见historical_refs_overlap_audit.json；不可访问历史仍不能声称已全覆盖。"]
    (ROOT/'REPORT.md').write_text('\n'.join(out)+'\n')
if __name__=='__main__': main()
