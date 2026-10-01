"""CPU-only paired world inference, complete outputs, fixed cases and report."""
import collections, math, statistics
import numpy as np
from common_g14 import *

def wilson(k,n):
    if not n:return (None,None)
    z=1.959963984540054;p=k/n;den=1+z*z/n;c=(p+z*z/(2*n))/den;h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den;return c-h,c+h
def ratio(k,n):return k/n if n else None
def pct(p):return 'NA' if p is None else f'{100*p:.2f}%'
def fraction(k,n):return f'{k}/{n} ({pct(ratio(k,n))})' if n else 'NA (0)'
def table(headers,rows):return '\n'.join(['|'+'|'.join(headers)+'|','|'+'|'.join(['---']*len(headers))+'|']+['|'+'|'.join(map(str,r))+'|' for r in rows])
def group(rows,keys):
    z=collections.defaultdict(list)
    for r in rows:z[tuple(r[k] for k in keys)].append(r)
    return z
def shared_bootstrap(a,b,mask,draws):
    a=np.asarray(a,float);b=np.asarray(b,float);mask=np.asarray(mask,bool);n=int(mask.sum())
    if not n:return dict(n=0,delta=None,ci=(None,None),samples=np.full(len(draws),np.nan),empty_draws=len(draws))
    m=mask[draws];den=m.sum(1);num=((a-b)[draws]*m).sum(1);samples=np.divide(num,den,out=np.full(len(draws),np.nan),where=den>0);valid=samples[np.isfinite(samples)]
    ci=tuple(np.quantile(valid,[.025,.975])) if len(valid) else (None,None)
    return dict(n=n,delta=float((a-b)[mask].mean()),ci=ci,samples=samples,empty_draws=int((den==0).sum()))
def pair_counts(a,b):
    a=np.asarray(a,bool);b=np.asarray(b,bool)
    return dict(both_success=int((a&b).sum()),old_only=int((a&~b).sum()),new_only=int((~a&b).sum()),both_fail=int((~a&~b).sum()))

def main():
    verify_lock();complete=[s for s in CFG['seeds'] if (ROOT/f'seed_s{s}_complete.json').exists()];missing=[s for s in CFG['seeds'] if s not in complete]
    for s in complete:
        z=json.loads((ROOT/f'seed_s{s}_complete.json').read_text());assert z['passed'] and z['zero_training'] and z['frozen_before']==z['frozen_after'] and z['rows']==6400
        assert json.loads((ROOT/f'history_reproduction_s{s}.json').read_text())['passed']
    rows=[]
    for p in sorted((ROOT/'outputs').glob('confirm_*.jsonl')):rows+=read(p)
    if (ROOT/'per_example.jsonl.gz').exists():
        keys={(r['seed'],r['R_method'],r['split']) for r in rows}
        with gzip.open(ROOT/'per_example.jsonl.gz','rt',encoding='utf-8') as f:
            for line in f:
                r=json.loads(line)
                if (r['seed'],r['R_method'],r['split']) not in keys:rows.append(r)
    worlds={w['record_id']:w for w in read(ROOT/'data/worlds.jsonl')}
    for r in rows:
        w=worlds[r['world_id']];cur=observe_text(r['current_output'],r['current_normal_end'],w,0);nxt=observe_text(r['next_output'],r['next_normal_end'],w,-1)
        assert cur['joint']==r['current_joint'] and cur['exact']==r['current_exact']
        assert nxt['score']==r['next_score'] and nxt['exact']==r['next_exact'] and nxt['joint']==r['next_joint'] and nxt['error_type']==r['error_type']
        assert r['two_step_joint']==(cur['joint'] and nxt['joint']) and r['two_step_exact']==(cur['exact'] and nxt['exact'])
        assert r['input_unchanged']
        r.update(world=w,expected_current_frame=frame(w,0),expected_next_frame=frame(w,-1))
    write(ROOT/'per_example.jsonl',rows)
    with gzip.open(ROOT/'per_example.jsonl.gz','wt',encoding='utf-8',compresslevel=6) as f:
        for r in rows:f.write(json.dumps(r,ensure_ascii=False)+'\n')
    dump(ROOT/'per_example_manifest.json',dict(rows=len(rows),plain_local_path=str(ROOT/'per_example.jsonl'),plain_sha256=digest(ROOT/'per_example.jsonl'),gzip_artifact='per_example.jsonl.gz',gzip_sha256=digest(ROOT/'per_example.jsonl.gz'),history_excluded=True,unpack='gzip -dc per_example.jsonl.gz > per_example.jsonl'))
    datasets=group(rows,['seed','R_method','split']);metrics=[];current_results=[];errors=[];relative=[];matrices=[];source_pairs=[];patterns=[];interfaces=[];arrays={};cohorts={};point_records=[]
    for (s,method,split),rs in sorted(datasets.items()):
        assert len(rs)==1600,(s,method,split,len(rs));ids=[w['record_id'] for w in read(ROOT/f'data/{split}_worlds.jsonl')]
        by={(r['mode'],r['producer'],r['receiver'],r['world_id']):r for r in rs};assert len(by)==1600
        C=np.array([by['latent','G','G',rid]['matched'] for rid in ids]);cohorts[s,method,split]=C
        for r in rs:assert r['matched']==bool(C[ids.index(r['world_id'])])
        n=int(C.sum());N=len(ids);matrix=dict(seed=s,R_method=method,split=split,n=n,N=N,exploratory=n<40)
        for (mode,P,Q),cell in sorted(group(rs,['mode','producer','receiver']).items()):
            cell=sorted(cell,key=lambda r:ids.index(r['world_id']));A=np.array([r['next_joint'] for r in cell]);arrays[s,method,split,mode,P,Q]=A
            k=int(A[C].sum());lo,hi=wilson(k,n);raw=int(A.sum());rawtwo=sum(r['two_step_joint'] for r in cell);rawexact=sum(r['next_exact'] for r in cell)
            z=dict(seed=s,R_method=method,split=split,mode=mode,producer=P,receiver=Q,matched_k=k,matched_n=n,matched_rate=ratio(k,n),matched_wilson_lo=lo,matched_wilson_hi=hi,matched_exact_k=sum(r['next_exact'] for r in cell if r['matched']),gate_and_next_k=k,gate_and_next_N=N,gate_and_next_rate=k/N,raw_next_k=raw,raw_N=N,raw_next_rate=raw/N,raw_two_step_k=rawtwo,raw_two_step_rate=rawtwo/N,raw_next_exact_k=rawexact,raw_two_step_exact_k=sum(r['two_step_exact'] for r in cell),exploratory=n<40)
            z['raw_next_wilson_lo'],z['raw_next_wilson_hi']=wilson(raw,N);z['raw_two_wilson_lo'],z['raw_two_wilson_hi']=wilson(rawtwo,N);z['gate_wilson_lo'],z['gate_wilson_hi']=wilson(k,N)
            z['matched_exact_wilson_lo'],z['matched_exact_wilson_hi']=wilson(z['matched_exact_k'],n);z['raw_next_exact_wilson_lo'],z['raw_next_exact_wilson_hi']=wilson(rawexact,N);z['raw_two_exact_wilson_lo'],z['raw_two_exact_wilson_hi']=wilson(z['raw_two_step_exact_k'],N)
            subset=C&np.array([r['natural_current_exact'] and r['natural_mask_equal'] for r in cell]);sn=int(subset.sum());sk=int(A[subset].sum());z.update(natural_correct_equal_mask_subset_n=sn,natural_correct_equal_mask_subset_k=sk,natural_correct_equal_mask_subset_rate=ratio(sk,sn));z['subset_wilson_lo'],z['subset_wilson_hi']=wilson(sk,sn)
            metrics.append(z);point_records.append(dict(seed=s,R_method=method,split=split,metric=f'{mode}_{P}{Q}_conditional',value=z['matched_rate']));point_records.append(dict(seed=s,R_method=method,split=split,metric=f'{mode}_{P}{Q}_raw_reconstruction_and_next' if mode=='natural' else f'{mode}_{P}{Q}_raw_two',value=z['raw_two_step_rate']))
            if mode=='latent':matrix[P+Q]=fraction(k,n);matrix[P+Q+'_raw_full']=fraction(rawtwo,N);matrix[P+Q+'_gate']=fraction(k,N)
            for matched_only in [False,True]:
                sub=[r for r in cell if r['matched'] or not matched_only];counts=collections.Counter(r['error_type'] for r in sub)
                errors.append(dict(seed=s,R_method=method,split=split,mode=mode,producer=P,receiver=Q,matched_only=matched_only,n=len(sub),**{label:counts[label] for label in ['success','format_only','date_error','fact_error','date_and_fact_error','parse_unresolved','perspective_error','length_limit']}))
                for (pred,delta),v in group([r for r in sub if r['predicted_relative_date'] is not None],['predicted_relative_date','relative_date_delta_days']).items():relative.append(dict(seed=s,R_method=method,split=split,mode=mode,producer=P,receiver=Q,matched_only=matched_only,predicted_relative_date=pred,delta_days=delta,k=len(v),all_N=len(sub),reliably_parsed_N=sum(r['predicted_relative_date'] is not None for r in sub)))
        for P,mode in [('G','latent'),('R','latent'),('E','natural')]:
            cell=[by[mode,P,'G',rid] for rid in ids];k=sum(r['current_joint'] for r in cell);exact=sum(r['current_exact'] for r in cell)
            lo,hi=wilson(k,N);elo,ehi=wilson(exact,N)
            current_results.append(dict(seed=s,R_method=method,split=split,producer=P,N=N,joint_k=k,joint_rate=k/N,joint_wilson_lo=lo,joint_wilson_hi=hi,exact_k=exact,exact_wilson_lo=elo,exact_wilson_hi=ehi,current_error_counts=json.dumps(dict(collections.Counter(r['current_error_type'] for r in cell))),match_n=n,coverage_rate=n/N,coverage_wilson_lo=wilson(n,N)[0],coverage_wilson_hi=wilson(n,N)[1],match_failures=json.dumps(dict(collections.Counter(x for r in cell for x in r['match_failures'])))))
            if P in ['G','R']:matrix['first_'+P]=fraction(k,N)
        for Q in ['G','R']:
            a=arrays[s,method,split,'latent','G',Q][C];b=arrays[s,method,split,'latent','R',Q][C];pc=pair_counts(a,b)
            z=dict(seed=s,R_method=method,split=split,receiver=Q,n=n,**pc,source_delta_pp=100*(float(a.mean()-b.mean())) if n else None)
            for label,k in pc.items():z[label+'_rate']=ratio(k,n);z[label+'_wilson_lo'],z[label+'_wilson_hi']=wilson(k,n)
            assert sum(pc.values())==n;source_pairs.append(z)
            for label,k in pc.items():point_records.append(dict(seed=s,R_method=method,split=split,metric=f'paired_Q{Q}_{label}',value=ratio(k,n)))
        gg=arrays[s,method,split,'latent','G','G'];rr=arrays[s,method,split,'latent','R','R'];gr=arrays[s,method,split,'latent','G','R'];rg=arrays[s,method,split,'latent','R','G'];target=C&gg&~rr
        for gr_ok,rg_ok,label in [(False,True,'receiver-update failure on both tested edited sources'),(True,False,'new producer state incompatible with both tested recipients'),(False,False,'either endpoint change breaks old success'),(True,True,'specific producer/receiver pairing incompatibility')]:
            k=int((target&(gr==gr_ok)&(rg==rg_ok)).sum());den=int(target.sum());lo,hi=wilson(k,den);patterns.append(dict(seed=s,R_method=method,split=split,descriptive_subset='C and GG correct and RR wrong; never a gate',subset_n=den,GR=gr_ok,RG=rg_ok,k=k,rate=ratio(k,den),wilson_lo=lo,wilson_hi=hi,description=label,absent=den==0 or k==0))
        reset=[by['reencode',P,'G',rid] for rid in ids for P in ['G','R']];assert all(r['reset_equals_natural'] for r in reset if r['matched'])
        for P in ['G','R']:
            for Q in ['G','R']:
                for rid,c in zip(ids,C):
                    if c:assert by['reencode',P,Q,rid]['next_output']==by['natural','E',Q,rid]['next_output']
        eq=sum(by['natural','E','G',rid]['natural_mask_equal'] for rid in ids);natural_exact=sum(by['natural','E','G',rid]['natural_current_exact'] for rid in ids)
        interfaces.append(dict(natural_mask_equal_wilson_lo=wilson(eq,N)[0],natural_mask_equal_wilson_hi=wilson(eq,N)[1],seed=s,R_method=method,split=split,N=N,natural_current_exact_k=natural_exact,natural_mask_equal_k=eq,C=n,matched_reset_equal_natural_instances=sum(r['reset_equals_natural'] for r in reset if r['matched']),matched_reset_instances=2*n,mask_mismatch_drops_from_main_C=0))
        matrices.append(matrix)
    # Same raw-world bootstrap draw is shared across all fixed models in each split.
    rng=np.random.default_rng(CFG['bootstrap_seed']);draws={sp:rng.integers(0,160,size=(CFG['bootstrap_replicates'],160)) for sp in CFG['world_counts']};contrasts=[];boot_store={};intersection=[]
    def add(kind,method,split,s,label,a,b,mask):
        z=shared_bootstrap(a,b,mask,draws[split]);lo,hi=z['ci'];r=dict(kind=kind,R_method=method,split=split,seed=s,contrast=label,n=z['n'],delta_pp=100*z['delta'] if z['delta'] is not None else None,ci_lo_pp=100*lo if lo is not None else None,ci_hi_pp=100*hi if hi is not None else None,bootstrap_replicates=2000,empty_draws=z['empty_draws'],empty_handling='empty cohort NA; empty resample omitted, never substitute denominator',uncertainty='paired shared world sampling, fixed models',exploratory=z['n']<40,degenerate=(lo==hi and lo is not None));contrasts.append(r)
        boot_store.setdefault((kind,method,split,label),[]).append((s,r,z['samples']))
    for s,method,split in datasets:
        C=cohorts[s,method,split]
        for Q in ['G','R']:add('source',method,split,s,'fixed_Q_'+Q,arrays[s,method,split,'latent','G',Q],arrays[s,method,split,'latent','R',Q],C)
        for P in ['G','R']:add('receiver',method,split,s,'fixed_P_'+P,arrays[s,method,split,'latent',P,'G'],arrays[s,method,split,'latent',P,'R'],C)
    for s in CFG['seeds']:
        for split in CFG['world_counts']:
            if (s,'F3',split) not in datasets or (s,'F2',split) not in datasets:continue
            mask=cohorts[s,'F3',split]&cohorts[s,'F2',split];n=int(mask.sum());equal=np.ones(160,bool)
            for P in ['G','R']:
                for Q in ['G','R']:
                    a=arrays[s,'F3',split,'latent',P,Q];b=arrays[s,'F2',split,'latent',P,Q];equal&=a==b
                    add('F3-F2','F3-F2',split,s,P+Q,a,b,mask)
                    intersection.append(dict(F3_wilson_lo=wilson(int(a[mask].sum()),n)[0],F3_wilson_hi=wilson(int(a[mask].sum()),n)[1],F2_wilson_lo=wilson(int(b[mask].sum()),n)[0],F2_wilson_hi=wilson(int(b[mask].sum()),n)[1],seed=s,split=split,cell=P+Q,intersection_n=n,F3_k=int(a[mask].sum()),F2_k=int(b[mask].sum()),F3_rate=ratio(int(a[mask].sum()),n),F2_rate=ratio(int(b[mask].sum()),n),F3_C=int(cohorts[s,'F3',split].sum()),F2_C=int(cohorts[s,'F2',split].sum())))
            intersection.append(dict(F3_wilson_lo=wilson(int(equal[mask].sum()),n)[0],F3_wilson_hi=wilson(int(equal[mask].sum()),n)[1],seed=s,split=split,cell='all four correctness patterns identical',intersection_n=n,F3_k=int(equal[mask].sum()),F3_rate=ratio(int(equal[mask].sum()),n)))
    for (kind,method,split,label),entries in boot_store.items():
        entries=[e for e in entries if e[1]['delta_pp'] is not None]
        if not entries:continue
        points=[e[1]['delta_pp'] for e in entries];samples=np.array([e[2] for e in entries]);ok=np.isfinite(samples).all(0);bt=samples[:,ok].mean(0);lo,hi=np.quantile(bt,[.025,.975]) if len(bt) else (None,None)
        contrasts.append(dict(kind=kind,R_method=method,split=split,seed='mean',contrast=label,n=json.dumps({e[0]:e[1]['n'] for e in entries}),delta_pp=statistics.mean(points),seed_sd_pp=statistics.stdev(points) if len(points)>1 else None,seeds=len(entries),ci_lo_pp=100*lo if lo is not None else None,ci_hi_pp=100*hi if hi is not None else None,bootstrap_replicates=2000,empty_draws=int((~ok).sum()),empty_handling='mean draw requires every contributing fixed-seed cohort nonempty; otherwise omitted',uncertainty='shared world draws across fixed seeds; training randomness separately summarized',degenerate=(lo==hi and lo is not None)))
    means=[]
    for (method,split,metric),cell in group(point_records,['R_method','split','metric']).items():
        vals=[r['value'] for r in cell if r['value'] is not None];means.append(dict(R_method=method,split=split,metric=metric,seeds=len(vals),mean=statistics.mean(vals) if vals else None,sample_sd=statistics.stdev(vals) if len(vals)>1 else None,per_seed=json.dumps({r['seed']:r['value'] for r in cell})))
    for name,data in [('per_seed_results.csv',metrics),('cross_matrices.csv',matrices),('current_results.csv',current_results),('source_paired_counts.csv',source_pairs),('contrast_results.csv',contrasts),('F2_F3_common_cohort.csv',intersection),('seed_mean_sd.csv',means),('descriptive_patterns.csv',patterns),('interface_checks.csv',interfaces),('error_counts.csv',errors),('relative_date_errors.csv',relative)]:csvwrite(ROOT/name,data)
    case_ids=json.loads((ROOT/'data/case_ids.json').read_text());cases=[];lines=['# G14 fixed cases','', 'Two F3 cases per seed/split chosen by pre-inference hash over all160 worlds, without outcome selection. Unmatched cases remain unmatched; no invented categories.','']
    for s in complete:
        for split,ids in case_ids[str(s)].items():
            for rid in ids:
                selected=[r for r in rows if r['seed']==s and r['R_method']=='F3' and r['split']==split and r['world_id']==rid];assert len(selected)==10
                cases.append(dict(seed=s,split=split,world_id=rid,rows=selected));lines += [f'## seed{s} / {split} / {rid}','',f'Current gold: {selected[0]["current_gold"]}',f'Next gold: {selected[0]["next_gold"]}',f'Matched: {selected[0]["matched"]}; failures: {selected[0]["match_failures"]}','']
                for r in selected:lines += [f'{r["mode"]} {r["producer"]}→{r["receiver"]}: current={r["current_output"]}',f'Next: {r["next_output"]}',f'joint={r["next_joint"]}; exact={r["next_exact"]}; error={r["error_type"]}; relative delta={r["relative_date_delta_days"]}; length={r["input_length"]}; mask={r["mask_hash"]}; parsed={json.dumps(r["parsed_facts"],ensure_ascii=False)}','']
    write(ROOT/'cases.jsonl',cases);(ROOT/'CASES.md').write_text('\n'.join(lines).rstrip()+'\n')
    dump(ROOT/'result_audit.json',dict(completed_seeds=complete,missing_seeds=missing,confirmation_rows=len(rows),all_scores_recomputed=True,history_not_pooled=True,cases=len(cases),zero_training=True,strict_current_only_gate=True,all_raw_denominators_160=True,matched_reset_equals_natural=True,bootstrap_shared_world_draws=True,bootstrap_empty_handling_explicit=True))
    report(matrices,metrics,source_pairs,contrasts,means,interfaces,patterns,intersection,complete,missing)
    print('G14 aggregated',len(rows),'confirmation rows; complete',complete,flush=True)

def report(matrices,metrics,pairs,contrasts,means,interfaces,patterns,intersection,complete,missing):
    def mean_cell(method,split,P,Q,mode='latent'):
        vals=[r['matched_rate'] for r in metrics if r['R_method']==method and r['split']==split and r['mode']==mode and r['producer']==P and r['receiver']==Q and r['matched_rate'] is not None]
        return statistics.mean(vals) if vals else None
    answer=[]
    for split in CFG['world_counts']:
        deltas=[r for r in contrasts if r['kind']=='source' and r['R_method']=='F3' and r['split']==split and r['seed']=='mean']
        answer.append(f"1. {split}，同正确today/同mask的F3来源差："+'；'.join(f"{r['contrast']}={r['delta_pp']:.2f}pp，world bootstrap95%CI[{r['ci_lo_pp']:.2f},{r['ci_hi_pp']:.2f}]" for r in deltas)+"。正确互换还需看两来源同时成功，零差不等于正确互换。")
        answer.append(f"2. {split}，F3的G→R条件续步均值={pct(mean_cell('F3',split,'G','R'))}，R→G={pct(mean_cell('F3',split,'R','G'))}；G→G={pct(mean_cell('F3',split,'G','G'))}，R→R={pct(mean_cell('F3',split,'R','R'))}。具体逐世界分层见下表，不唯一归因内部机制。")
        answer.append(f"3. {split}，F2对应GG/GR/RG/RR均值="+'/'.join(pct(mean_cell('F2',split,P,Q)) for P,Q in [('G','G'),('G','R'),('R','G'),('R','R')])+"；F2/F3直接差异只用同seed共同C，详见共同cohort和配对差表。")
        answer.append(f"4. {split}，F3自然today输入G/R接收均值={pct(mean_cell('F3',split,'E','G','natural'))}/{pct(mean_cell('F3',split,'E','R','natural'))}；真实输出重编码G→R/R→R={pct(mean_cell('F3',split,'G','R','reencode'))}/{pct(mean_cell('F3',split,'R','R','reencode'))}。C上重编码token/mask/encoder memory与自然输入逐元素一致；自然mask差异和全160世界技能另列，不用于筛除主C。")
    out=['# G14 同一today状态的生产者—接收者交叉诊断','',f'完成seed={complete}；未完成seed={missing}。零新增训练，固定T0/F3 final200/F2 final200，最长两次编辑。','']+answer+['','## 主交叉矩阵','', '每格联合成功k/C；匹配n/原始160。F3主对象、F2预设自然态继续训练对照。所有C由第一步正确全文/EOS/事实及G/R mask一致性决定，未使用任何下一步结果。','',table(['R','seed','split','n/N','G→G','G→R','R→G','R→R'],[[r['R_method'],r['seed'],r['split'],f"{r['n']}/{r['N']}",r['GG'],r['GR'],r['RG'],r['RR']] for r in sorted(matrices,key=lambda r:(CFG['R_methods'].index(r['R_method']),r['seed'],r['split']))]),'', '## 固定接收者：逐世界配对四类','',table(['R','seed','split','Q','C','两源都对','仅旧源对','仅新源对','两源都错','来源差pp'],[[r['R_method'],r['seed'],r['split'],r['receiver'],r['n'],r['both_success'],r['old_only'],r['new_only'],r['both_fail'],r['source_delta_pp']] for r in pairs]),'', '## 原始分母：第一步及两步完整轨迹','', '此处不要求全文严格进入C；两步成功为first_joint AND next_joint。gate-and-next /160另表，不等同全部世界两步准确率。','',table(['R','seed','split','first G','first R','GG full','GR full','RG full','RR full'],[[r['R_method'],r['seed'],r['split'],r['first_G'],r['first_R'],r['GG_raw_full'],r['GR_raw_full'],r['RG_raw_full'],r['RR_raw_full']] for r in matrices]),'', '## gate-and-next /原始160','',table(['R','seed','split','GG','GR','RG','RR'],[[r['R_method'],r['seed'],r['split'],r['GG_gate'],r['GR_gate'],r['RG_gate'],r['RR_gate']] for r in matrices]),'', '## 自然与真实输出重编码控制','',table(['R','seed','split','mode','P→Q','next k/C','raw next/160','raw two-step/160'],[[r['R_method'],r['seed'],r['split'],r['mode'],r['producer']+'→'+r['receiver'],fraction(r['matched_k'],r['matched_n']),fraction(r['raw_next_k'],r['raw_N']),fraction(r['raw_two_step_k'],r['raw_N']) if r['mode']=='reencode' else 'natural单步控制'] for r in metrics if r['mode']!='latent']),'',table(['R','seed','split','自然重构exact/160','自然mask==源mask/160','C','C上reset==natural实例'],[[r['R_method'],r['seed'],r['split'],f"{r['natural_current_exact_k']}/160",f"{r['natural_mask_equal_k']}/160",r['C'],fraction(r['matched_reset_equal_natural_instances'],r['matched_reset_instances'])] for r in interfaces]),'', '自然完整接口对照保留自身mask，未做跨来源mask覆盖。自然模式的raw_reconstruction_and_next指重构加一次编辑，不是两次语义编辑轨迹。自然重构正确且mask相同的C子集附在per_seed_results.csv，不能替代主C。相同文本控制输出不能作为额外独立样本。','', '## 三seed均值与sample SD','',table(['R','split','metric','seed N','mean','SD'],[[r['R_method'],r['split'],r['metric'],r['seeds'],pct(r['mean']),pct(r['sample_sd'])] for r in means]),'', '## 配对差与固定模型世界bootstrap','', '来源差为A_GQ−A_RQ；接收者差为A_PG−A_PR。2000次同世界配对抽样，跨seed/方法共享原始世界draw再限制到事前C；空cohort NA、空抽样显式计数并省略，无分母替换。CI只反映固定模型的世界抽样不确定性；三个seed不能覆盖全部训练随机性，也不是480次独立训练。每比例Wilson95在per_seed_results/current_results/source_paired_counts.csv；全零/全一的退化bootstrap不是总体无不确定性证明。','',table(['kind','R','split','seed','contrast','n','delta pp','seed SD pp (mean rows)','CI95 pp','empty draws'],[[r['kind'],r['R_method'],r['split'],r['seed'],r['contrast'],r['n'],r['delta_pp'],r.get('seed_sd_pp','NA'),f"[{r['ci_lo_pp']},{r['ci_hi_pp']}]",r['empty_draws']] for r in contrasts]),'', '## F2/F3共同匹配集合','',table(['seed','split','cell','intersection n','F3 k','F2 k'],[[r['seed'],r['split'],r['cell'],r['intersection_n'],r.get('F3_k'),r.get('F2_k','NA')] for r in intersection]),'', '## GG正确且RR错误世界的描述性定位','', '这个分层使用第二步结果，仅描述，绝不是匹配门槛。没有该类世界则n=0/NA；不存在类别显式absent。','',table(['R','seed','split','subset n','GR','RG','k','描述'],[[r['R_method'],r['seed'],r['split'],r['subset_n'],r['GR'],r['RG'],r['k'],r['description']] for r in patterns]),'', '改变生产者或接收者的实际行为差异只约束这两个已测试固定接收者。即使新状态两边都失败，也不证明语义丢失、对所有可能接收者不可用或latent编辑不可能。模板OOD共享既有词汇，不等同开放自然语言。没有按结果调整的高/低阈值，没有新训练、第三步或长链扩展。','', '## 工程复现、数据、资源和工件','', '历史复现每seed每split16世界：3模型×2步×32=192次逐文本/评分/EOS/有效长度核对；三个seed共576次。它们只用于工程复现，不加入320新世界确认统计。seed42 smoke仅历史世界；正式seed先复现再确认。完整历史清单和比对在data/history_batches.json、data/history_expected.jsonl、history_reproduction_s*.json。','', '新IID160/OOD160，三seed及F2/F3共用；数据主seed20261001，完整事实身份/全部合法日期人称render及可访问历史manifest去重范围、SHA、实际命名叶子RNG见data/manifest.json。检查点来自G13实际映射并核验全部旧artifact manifest SHA；从未选择best或回退。','', '未通过当前匹配的世界仍有完整输出/评分；没有补样本。每条包含current/next原文、gold、joint/exact、可靠解析事实/日期偏差、错误类型、mask/IDs/memory hashes、实际mask和有效长度。error_counts.csv分开未决/明确日期错/非日期事实错/二者皆错/格式差异；relative_date_errors.csv只统计可解析日期，不将所有失败称为推进过头。','', '12个事前hash案例见CASES.md/cases.jsonl，不按错误或成功选择。完整逐例记录per_example.jsonl.gz，解压得所需plain文件；精确本地路径/hash见per_example_manifest.json。大型完整FP32状态缓存留local/，data/confirm_s*_states.json记录实际路径/sha；不上传模型、重复旧checkpoint或latent。冻结前后、缓存保存重放、输入不变、当前门槛独立、零optimizer/backward在smoke_test.json和seed_s*_complete.json。','', '所有GPU经sbatch+srun，单卡smoke结束后一个array0–2%2；索引显式映射seed，内部顺序，无CUDA_VISIBLE_DEVICES覆盖。分区B300q/default account/QOS/exclude node01沿G13核验环境，官方语法参考：[job arrays](https://slurm.schedmd.com/job_array.html)、[sbatch](https://slurm.schedmd.com/sbatch.html)、[srun](https://slurm.schedmd.com/srun.html)。请求walltime仅据smoke吞吐量确定，科学规模不变。','']
    if (ROOT/'budget.json').exists():out+=['实际/请求allocation预算：'+json.dumps(json.loads((ROOT/'budget.json').read_text()),ensure_ascii=False),'']
    if (ROOT/'slurm_jobs.csv').exists():
        jobs=list(csv.DictReader((ROOT/'slurm_jobs.csv').open()));out+=[table(['JobID','raw ID','state','exit','start','end','GPU hours'],[[r[k] for k in ['job_id','raw_job_id','state','exit_code','start','end','gpu_hours']] for r in jobs]),'']
    deviations=json.loads((ROOT/'engineering_deviations.json').read_text()) if (ROOT/'engineering_deviations.json').exists() else []
    out+=['偏离/失败记录：'+json.dumps(deviations,ensure_ascii=False)+'。未完成seed='+str(missing)+'。没有因结果不好重试或追加科学实验。']
    (ROOT/'REPORT.md').write_text('\n'.join(out).rstrip()+'\n')

if __name__=='__main__':main()
