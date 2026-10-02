"""CPU paired world analysis. All cohorts locked before receiver outputs."""
import itertools,statistics
import numpy as np
from common_g17 import *
def plain_row(r):return {k:v.item() if isinstance(v,np.generic) else v for k,v in r.items()}

def paired_boot(delta,mask,draw):
    n=int(mask.sum())
    if not n:return dict(delta_pp=None,ci_low_pp=None,ci_high_pp=None,empty_draws=len(draw)),np.full(len(draw),np.nan)
    denominators=mask[draw].sum(1);numerators=(delta[draw]*mask[draw]).sum(1);boot=np.divide(numerators,denominators,out=np.full(len(draw),np.nan),where=denominators>0)*100
    good=boot[np.isfinite(boot)];ci=np.quantile(good,[.025,.975]) if len(good) else [None,None]
    return dict(delta_pp=float(delta[mask].mean()*100),ci_low_pp=float(ci[0]) if ci[0] is not None else None,ci_high_pp=float(ci[1]) if ci[1] is not None else None,empty_draws=int((denominators==0).sum())),boot

def main():
    verify_lock();worlds=read(ROOT/'data/worlds.jsonl');byid={w['record_id']:w for w in worlds};rows=[]
    for s in CFG['seeds']:
        done=json.loads((ROOT/f'seed_s{s}_complete.json').read_text());assert done['passed'] and json.loads((ROOT/f'frozen_s{s}.json').read_text())['passed']
        for p,h in done['output_sha256'].items():assert digest(ROOT/p)==h;rows+=read(ROOT/p)
    assert len(rows)==130560
    # Independently rescore every current / next / self output; no old result rewritten.
    for r in rows:
        d=r['anchor'] if r['kind'] in ['current','self_first'] else r['anchor']-1
        o=observation(r['output'],r['normal_end'],byid[r['world_id']],d)
        assert all(o[k]==r[k] for k in ['gold','score','joint','exact','error_type','parsed_facts']),r['world_id']
    write(ROOT/'per_example.jsonl.gz',rows)
    lookup={(r['seed'],r['split'],r['anchor'],r['kind'],r['producer'],r['receiver'],r['world_id']):r for r in rows};assert len(lookup)==len(rows)
    def get(s,sp,a,kind,p,q):return [lookup[s,sp,a,kind,p,q,w['record_id']] for w in worlds if w['split']==sp]
    def vec(rs,k='joint'):return np.array([r[k] for r in rs],dtype=bool)
    cohorts={};coverage=[];natural=[];source=[];selfrows=[];maskrows=[];pairs=[];interchange=[];errors=[];dates=[];resets=[];means=[]
    draws={sp:np.random.default_rng(sub_seed('analysis/shared_world/'+sp)).integers(0,160,(2000,160)) for sp in CFG['splits']}
    def measured(rs,mask=None):
        selected=rs if mask is None else [r for r,b in zip(rs,mask) if b]
        return dict(**proportion(sum(r['joint'] for r in selected),len(selected)),exact_k=sum(r['exact'] for r in selected),EOS_k=sum(r['normal_end'] for r in selected))
    for s,sp,a in itertools.product(CFG['seeds'],CFG['splits'],CFG['anchors']):
        ns=get(s,sp,a,'current','E','');coverage.append(dict(seed=s,split=sp,anchor=a,producer='E',**measured(ns),current_C_n=None,current_C_N=160,natural_mask_equal_k=sum(r['natural_mask_equal'] for r in ns)))
        for p in CFG['producers']:
            rs=get(s,sp,a,'current',p,'');m=vec(rs,'matched');cohorts[s,sp,a,p]=m
            coverage.append(dict(seed=s,split=sp,anchor=a,producer=p,**measured(rs),current_C_n=int(m.sum()),current_C_N=160,natural_mask_equal_k=sum(r['natural_mask_equal'] for r in rs),current_gate_failures=json.dumps(dict(collections.Counter(r['error_type'] for r in rs if not r['matched'])))))
            for q in CFG['receivers']:
                hand=get(s,sp,a,'handoff',p,q);assert np.array_equal(vec(hand,'matched'),m)
                source.append(dict(seed=s,split=sp,anchor=a,producer=p,receiver=q,scope='conditional_C',**measured(hand,m),C=int(m.sum()),N=160,gate_and_next_k=sum(r['gate_and_next'] for r in hand),raw_full2_k=sum(r['full2'] for r in hand),raw_full2_N=160,raw_next_k=sum(r['joint'] for r in hand)))
                reset=get(s,sp,a,'reset',p,q);resets.append(dict(seed=s,split=sp,anchor=a,producer=p,receiver=q,scope='raw160',**measured(reset),full2_k=sum(r['full2'] for r in reset),conditional_k=sum(r['joint'] for r,b in zip(reset,m) if b),C=int(m.sum()),duplicate_natural_k=sum(r['duplicate_natural_control'] for r in reset),reset_correct_on_C_equal_to_natural=True))
                eq=np.array([r['natural_mask_equal'] for r in hand]);fn_nat=vec(get(s,sp,a,'natural','E','F')) & vec(get(s,sp,a,'natural','E','N'))
                maskrows.append(dict(seed=s,split=sp,anchor=a,producer=p,receiver=q,raw_N=160,equal_mask_k=int(eq.sum()),C=int(m.sum()),strict_C_n=int((m&eq).sum()),strict_joint_k=int((vec(hand)&m&eq).sum()),strict_not_substitute_for_main=True,F_N_natural_both_good_on_C=int((m&fn_nat).sum()),joint_in_descriptive_natural_good_C=int((m&fn_nat&vec(hand)).sum())))
                n=vec(get(s,sp,a,'natural','E',q));v=vec(hand);mc=m&eq
                for scope,mk in [('C',m),('C_equal_mask',mc)]:
                    c=paired_counts(n[mk],v[mk]);interchange.append(dict(seed=s,split=sp,anchor=a,receiver=q,sources='E-'+p,scope=scope,n=int(mk.sum()),**c,all_success_k=c['both'],both_wrong_same_text_k=sum(not r['joint'] and not nr['joint'] and r['output']==nr['output'] for r,nr,b in zip(hand,get(s,sp,a,'natural','E',q),mk) if b)))
        for q in CFG['natural_receivers']:
            rs=get(s,sp,a,'natural','E',q);natural.append(dict(seed=s,split=sp,anchor=a,receiver=q,scope='raw160',**measured(rs)))
            one=get(s,sp,a,'self_first',q,q);two=get(s,sp,a,'self_second',q,q)
            for r1,r2 in zip(one,two):assert r2['full2']==full_success(r1,r2)
            selfrows.append(dict(seed=s,split=sp,anchor=a,receiver=q,**proportion(sum(r['full2'] for r in two),160),first_k=sum(r['joint'] for r in one),first_exact_k=sum(r['exact'] for r in one),endpoint_k=sum(r['joint'] for r in two),endpoint_exact_k=sum(r['exact'] for r in two),first_failure1=sum(r['first_failure']==1 for r in two),first_failure2=sum(r['first_failure']==2 for r in two)))
        for p1,p2 in itertools.combinations(CFG['producers'],2):
            m=cohorts[s,sp,a,p1]&cohorts[s,sp,a,p2];v1=vec(get(s,sp,a,'handoff',p1,'F'));v2=vec(get(s,sp,a,'handoff',p2,'F'));c=paired_counts(v1[m],v2[m])
            rs1=get(s,sp,a,'handoff',p1,'F');rs2=get(s,sp,a,'handoff',p2,'F')
            interchange.append(dict(seed=s,split=sp,anchor=a,receiver='F',sources=p1+'-'+p2,scope='pair_C_intersection',n=int(m.sum()),**c,all_success_k=c['both'],both_wrong_same_text_k=sum(not r['joint'] and not t['joint'] and r['output']==t['output'] for r,t,b in zip(rs1,rs2,m) if b)))
        mt=cohorts[s,sp,a,'P']&cohorts[s,sp,a,'U']&cohorts[s,sp,a,'G'];allv=np.logical_and.reduce([vec(get(s,sp,a,'handoff',p,'F')) for p in CFG['producers']])
        interchange.append(dict(seed=s,split=sp,anchor=a,receiver='F',sources='P-U-G',scope='triple_C_intersection',n=int(mt.sum()),all_success_k=int((allv&mt).sum()),**{f'Wilson_{k}':v for k,v in zip(['low','high'],wilson(int((allv&mt).sum()),int(mt.sum())))}))
    boot_store={};mean_pairs=[]
    for sp,a,p,(left,right),metric in itertools.product(CFG['splits'],CFG['anchors'],CFG['producers'],[('F','N'),('F','P'),('N','P')],['conditional_joint','raw_full2','gate_and_next']):
        seed_entries=[];boots=[]
        for s in CFG['seeds']:
            lr=get(s,sp,a,'handoff',p,left);rr=get(s,sp,a,'handoff',p,right);m=cohorts[s,sp,a,p] if metric=='conditional_joint' else np.ones(160,dtype=bool);key_='joint' if metric=='conditional_joint' else 'full2' if metric=='raw_full2' else 'gate_and_next'
            v1=vec(lr,key_);v2=vec(rr,key_);stats,b=paired_boot(v1.astype(float)-v2.astype(float),m,draws[sp]);cnt=paired_counts(v1[m],v2[m]);entry=dict(seed=s,split=sp,anchor=a,producer=p,contrast=left+'-'+right,metric=metric,n=int(m.sum()),**cnt,**stats,exploratory=int(m.sum())<40,bootstrap_replicates=2000)
            pairs.append(entry);seed_entries.append(entry);boots.append(b)
        vals=[r['delta_pp'] for r in seed_entries if r['delta_pp'] is not None];all_present=len(vals)==3;bm=np.mean(np.stack(boots),axis=0) if all_present else np.full(2000,np.nan);valid_b=bm[np.isfinite(bm)];ci=np.quantile(valid_b,[.025,.975]) if len(valid_b) else [None,None]
        mean_pairs.append(dict(seed='mean',split=sp,anchor=a,producer=p,contrast=left+'-'+right,metric=metric,delta_pp=statistics.mean(vals) if all_present else None,seed_sample_SD_pp=statistics.stdev(vals) if all_present else None,ci_low_pp=float(ci[0]) if ci[0] is not None else None,ci_high_pp=float(ci[1]) if ci[1] is not None else None,empty_draws=2000-len(valid_b),contributing_seeds=len(vals),per_seed_n=json.dumps([r['n'] for r in seed_entries]),bootstrap_replicates=2000))
    pairs=[plain_row(r) for r in pairs+mean_pairs]
    for name,rs in [('current_coverage',coverage),('natural_controls',natural),('source_state_results',source),('paired_repair_gains',pairs),('interchangeability',interchange),('self_rollout',selfrows),('mask_controls',maskrows),('reset_controls',resets)]:csvwrite(ROOT/(name+'.csv'),rs)
    for kind,rs in [('source',source),('natural',natural),('self',selfrows)]:
        keys=sorted({(r['split'],r['anchor'],r.get('producer',''),r['receiver']) for r in rs})
        for sp,a,p,q in keys:
            sub=[r for r in rs if (r['split'],r['anchor'],r.get('producer',''),r['receiver'])==(sp,a,p,q)];vs=[r['rate'] for r in sub if r['rate'] is not None]
            means.append(dict(kind=kind,split=sp,anchor=a,producer=p,receiver=q,mean=statistics.mean(vs) if len(vs)==3 else None,sample_SD=statistics.stdev(vs) if len(vs)==3 else None,contributing_seeds=len(vs),per_seed=json.dumps([dict(seed=r['seed'],k=r['k'],n=r['n']) for r in sub])))
    csvwrite(ROOT/'seed_mean_SD.csv',means)
    for key_,group in itertools.groupby(sorted(rows,key=lambda r:(r['seed'],r['split'],r['anchor'],r['kind'],r['producer'],r['receiver'])),key=lambda r:(r['seed'],r['split'],r['anchor'],r['kind'],r['producer'],r['receiver'])):
        group=list(group);counter=collections.Counter(r['error_type'] for r in group);errors.append(dict(zip(['seed','split','anchor','kind','producer','receiver'],key_))|dict(n=len(group),**counter))
    csvwrite(ROOT/'error_types.csv',errors)
    for r in rows:
        if r['predicted_relative_date'] is not None and not r['joint']:dates.append({k:r[k] for k in ['seed','split','world_id','anchor','kind','producer','receiver','predicted_relative_date','relative_date_delta_days','error_type']})
    csvwrite(ROOT/'parsed_date_errors.csv',dates)
    selection=json.loads((ROOT/'data/case_ids.json').read_text());case_rows=[r for r in rows if r['world_id'] in selection[str(r['seed'])][r['split']]];assert len(case_rows)==12*4*34
    write(ROOT/'case_records.jsonl.gz',case_rows);case_md=['# G17 twelve pre-hash-selected worlds\n\nChosen before inference; all anchors and receivers, including failure/nonmatch. No error-selected main cases.\n']
    for s in CFG['seeds']:
        for sp in CFG['splits']:
            for wid in selection[str(s)][sp]:
                case_md.append(f'\n## seed{s} {sp} {wid}\n')
                for a in CFG['anchors']:
                    case_md.append(f'\nCurrent anchor {a}; gold next: {render(byid[wid],frame(byid[wid],a-1))}\n')
                    for p in CFG['producers']:
                        c=lookup[s,sp,a,'current',p,'',wid];case_md.append(f'\nProducer {p}, C={c["matched"]}, current={c["output"]}\n')
                        for q in CFG['receivers']:
                            r=lookup[s,sp,a,'handoff',p,q,wid];case_md.append(f'\n- {p}→{q}: joint={r["joint"]}; exact={r["exact"]}; EOS={r["normal_end"]}; {r["error_type"]}; output: {r["output"]}\n')
    (ROOT/'CASES.md').write_text(''.join(case_md))
    failure_rows=[];failure_md=['# Post-hoc descriptive failures\n\nFirst2 by predetermined SHA order in each observed error class among F handoffs. These do not affect any cohort/primary. Empty classes stated.\n']
    for err in ['date_error','fact_error','date_and_fact_error','parse_unresolved','perspective_error','length_limit']:
        rs=sorted([r for r in rows if r['kind']=='handoff' and r['receiver']=='F' and r['error_type']==err],key=lambda r:hashlib.sha256(f'g17/failure/{r["seed"]}/{r["world_id"]}/{r["anchor"]}/{r["producer"]}'.encode()).hexdigest())[:2]
        failure_rows+=rs;failure_md.append(f'\n## {err}: {len(rs)} displayed\n')
        if not rs:failure_md.append('No observed cases.\n')
        for r in rs:failure_md.append(f'\nseed{r["seed"]} {r["split"]} {r["world_id"]}, a={r["anchor"]}, {r["producer"]}→F, C={r["matched"]}\n\nCurrent: {r["current_output"]}\n\nGold: {r["gold"]}\n\nOutput: {r["output"]}\n')
    write(ROOT/'failure_cases.jsonl.gz',failure_rows);(ROOT/'FAILURE_CASES.md').write_text(''.join(failure_md))
    primary=[r for r in pairs if r['split']=='iid' and r['anchor']==2 and r['producer']=='U' and r['contrast']=='F-N' and r['metric']=='conditional_joint'];dump(ROOT/'primary_result.json',dict(rows=primary,stable_positive=all(r['n']>=40 and r['delta_pp'] is not None and r['delta_pp']>0 for r in primary if r['seed']!='mean') and primary[-1]['ci_low_pp'] is not None and primary[-1]['ci_low_pp']>0,naturals=[r for r in natural if r['split']=='iid' and r['anchor']==2 and r['receiver'] in ['F','N']],zero_training=True))
    make_report(source,natural,selfrows,primary,pairs)
    dump(ROOT/'analysis_audit.json',dict(passed=True,all_records_CPU_rescored=len(rows),complete_main_cases=12,case_records=len(case_rows),zero_training=True,bootstrap_replicates=2000,shared_world_draws_all_anchors_sources_receivers_seeds=True,scientific_lock_sha256=digest(ROOT/'scientific_lock.json'),empty_bootstrap_draws_reported=True))
    print('G17 analysis complete',primary,flush=True)

def make_report(source,natural,selfrows,primary,pairs):
    si={(r['seed'],r['split'],r['anchor'],r['producer'],r['receiver']):r for r in source};ni={(r['seed'],r['split'],r['anchor'],r['receiver']):r for r in natural};ri={(r['seed'],r['split'],r['anchor'],r['receiver']):r for r in selfrows}
    mean=primary[-1];txt=['# G17 跨语义状态 × 表示来源迁移边界\n\n零训练，全部冻结；唯一主检验 IID,+2,U，固定同一输入比较F−N。\n\n']
    for s in CFG['seeds']:
        f=si[s,'iid',2,'U','F'];n=si[s,'iid',2,'U','N'];p=si[s,'iid',2,'U','P'];d=next(r for r in primary if r['seed']==s)
        txt.append(f'seed{s}: F={f["k"]}/{f["n"]}, N={n["k"]}/{n["n"]}, P={p["k"]}/{p["n"]}; Δ={d["delta_pp"]}pp, CI=[{d["ci_low_pp"]},{d["ci_high_pp"]}], C/160={f["C"]}/160; 自然F={ni[s,"iid",2,"F"]["k"]}/160,N={ni[s,"iid",2,"N"]["k"]}/160。\n\n')
    txt.append(f'固定三seed平均差={mean["delta_pp"]}pp，sample SD={mean["seed_sample_SD_pp"]}pp，95% paired-world CI=[{mean["ci_low_pp"]},{mean["ci_high_pp"]}]。这些是固定旧训练模型的共享世界抽样区间，不包括全训练随机性；其他单元CI为描述性，不是同时置信区间。\n\n')
    txt.append('真实历史标签：+2为已审计谱系未直接监督的编辑态续步；today/P对F直接修复、today/U/G有相关祖先暴露；yesterday/G为维护输入；−2修复未见但G10祖先两步暴露。自然规则已监督，精确来源与相关状态暴露分开，未知历史不等于未见。详情SUPERVISION_AUDIT及完整覆盖CSV。\n\n')
    txt.append('表一：每格F k/C；N k/C；F−N百分点。C按锚点/生产者独立，所有未匹配保留；小于40探索性，空C为NA。\n\n|seed|split|当前锚点|P生产|U生产|G生产|\n|---|---|---|---|---|---|\n')
    for sp in CFG['splits']:
        for s in CFG['seeds']:
            for a in CFG['anchors']:
                cells=[]
                for p in CFG['producers']:
                    f=si[s,sp,a,p,'F'];n=si[s,sp,a,p,'N'];delta=(f['rate']-n['rate'])*100 if f['rate'] is not None else None
                    cells.append(f'F {f["k"]}/{f["n"]}; N {n["k"]}/{n["n"]}; Δ{delta:.2f}pp; C {f["C"]}/160' if delta is not None else 'NA; C0/160')
                txt.append(f'|{s}|{sp}|{a}|'+ '|'.join(cells)+'|\n')
    txt.append('\n表二：每格自然 k/160；自身step1/endpoint/full2成功数（各分母160），完整运行无重编码。\n\n|seed|split|锚点|P|N|F|G历史参照|\n|---|---|---|---|---|---|---|\n')
    for sp in CFG['splits']:
        for s in CFG['seeds']:
            for a in CFG['anchors']:
                cells=[]
                for q in ['P','N','F','G']:
                    n=ni[s,sp,a,q];r=ri[s,sp,a,q];cells.append(f'自然{n["k"]}/160; 自身{r["first_k"]}/{r["endpoint_k"]}/{r["k"]}')
                txt.append(f'|{s}|{sp}|{a}|'+ '|'.join(cells)+'|\n')
    txt.append('\n完整P接收、F−P/N−P、raw full2/gate-and-next、exact/EOS/日期/事实/解析类别、Wilson区间、source pair/triple交集与都对/仅一对/都错、相等mask严格子集和真实重编码都在对应CSV和完整逐例工件。两条相同错误输出不算成功互换。\n\n')
    txt.append('范围：320个新事实世界，四锚点为相关变体；每seed/split仍160主世界，不把1280锚点变体或480跨seed记录当独立训练。模板OOD只支持已有词汇模板8–11，不是开放语言泛化。未重验其余状态/人称或完整40cell，未追加任何训练/三步以上自运行/候选比较。\n\n资源账本在budget.json/slurm_jobs.csv；工程验收在CPU/GPU冻结及smoke/analysis审计。低分不是重试理由，旧目录和参数只读。\n')
    (ROOT/'REPORT.md').write_text(''.join(txt))
if __name__=='__main__':main()
