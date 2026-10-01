"""CPU score verification, paired shared-world uncertainty and complete delivery."""
import math, statistics
import numpy as np
from common_g15 import *

def wilson(k,n):
    if not n:return None,None
    z=1.959963984540054;p=k/n;den=1+z*z/n;center=(p+z*z/(2*n))/den;half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return max(0,center-half),min(1,center+half)
def rate(k,n):return k/n if n else None
def pct(x):return 'NA' if x is None else f'{100*x:.2f}%'
def frac(k,n):return f'{k}/{n}' if n else 'NA (0)'
def table(headers,rows):return '\n'.join(['|'+'|'.join(headers)+'|','|'+'|'.join(['---']*len(headers))+'|']+['|'+'|'.join(map(str,row))+'|' for row in rows])
def grouped(rows,keys):
    result=collections.defaultdict(list)
    for r in rows:result[tuple(r[k] for k in keys)].append(r)
    return result
def paired_counts(a,b):
    a=np.asarray(a,bool);b=np.asarray(b,bool)
    return dict(both=int((a&b).sum()),natural_only=int((a&~b).sum()),edited_only=int((~a&b).sum()),neither=int((~a&~b).sum()))
def paired_boot(a,b,mask,draws):
    diff=np.asarray(a,float)-np.asarray(b,float);mask=np.asarray(mask,bool);n=int(mask.sum())
    if not n:return None,np.full(len(draws),np.nan)
    den=mask[draws].sum(1);num=(diff[draws]*mask[draws]).sum(1)
    samples=np.divide(num,den,out=np.full(len(draws),np.nan),where=den>0)
    return float(diff[mask].mean()),samples
def interval(samples):
    good=np.asarray(samples)[np.isfinite(samples)]
    return tuple(map(float,np.quantile(good,[.025,.975]))) if len(good) else (None,None)

def load_confirmation(complete,worlds):
    paths=sorted((ROOT/'outputs').glob('*.jsonl'));rows=[]
    for path in paths:rows+=read(path)
    if not paths and (ROOT/'per_example.jsonl.gz').exists():rows=read(ROOT/'per_example.jsonl.gz')
    rows=[r for r in rows if r['seed'] in complete]
    checkpointmap=json.loads((ROOT/'checkpoints_manifest.json').read_text())['models']
    finalmap={(s,m):checkpointmap[str(s)]['P']['sha256'] if m=='P' else json.loads((ROOT/f'training/{m}_s{s}.json').read_text())['final_sha256'] for s in complete for m in ['P']+CFG['methods']}
    for r in rows:
        w=worlds[r['world_id']]
        offset=r['offset']-1 if r['kind']=='atomic' else -2 if r['kind']=='old' else 0 if r['kind']=='self_first' else -1
        perspective=r.get('perspective','first');o=observation(r['output'],r['normal_end'],w,offset,perspective)
        assert all(o[k]==r[k] for k in ['joint','exact','score','error_type']), (r['kind'],r['world_id'])
        if 'current' in r:
            cur=observation(r['current']['output'],r['current']['normal_end'],w,-1 if r['kind']=='old' else 0)
            assert cur['joint']==r['current']['joint'] and cur['exact']==r['current']['exact']
            if 'full' in r:assert r['full']==full_success(cur,o)
        r.update(world=w,expected_frame=frame(w,offset,perspective),checkpoint_sha256=finalmap[r['seed'],r['method']])
        if r.get('source') in ['P','G','U']:r['producer_checkpoint_sha256']=checkpointmap[str(r['seed'])][r['source']]['sha256']
        elif r.get('source')=='Q':r['producer_checkpoint_sha256']=r['checkpoint_sha256']
    assert len(rows)==len(complete)*67840
    write(ROOT/'per_example.jsonl.gz',rows)
    dump(ROOT/'per_example_manifest.json',dict(rows=len(rows),gzip_sha256=digest(ROOT/'per_example.jsonl.gz'),complete_free_text_and_scoring=True,history_or_smoke_not_pooled=True,unpack='gzip -dc per_example.jsonl.gz > per_example.jsonl'))
    return rows

def analyze(complete,rows,worlds):
    cells=[];fixed=[];olds=[];selfs=[];reset=[];pairs=[];core=[];errors=[];dates=[];arrays={};masks={};atom_arrays={};points=[]
    plans={sp:[w['record_id'] for w in read(ROOT/f'data/{sp}_worlds.jsonl') if w['record_status']=='recorded_plan'] for sp in ['iid','template_ood']}
    atomids={sp:{status:[w['record_id'] for w in read(ROOT/f'data/{sp}_worlds.jsonl') if w['record_status']==status] for status in ['recorded_plan','reported_cancelled','reported_completed']} for sp in plans}
    for (seed,method,split),rs in sorted(grouped(rows,['seed','method','split']).items()):
        assert len(rs)==8480;ids=plans[split];N=160;groups=grouped(rs,['kind']);ar=groups['atomic',];cellrates=[]
        for (status,d,p),samples in sorted(grouped(ar,['status','offset','perspective']).items()):
            assert len(samples)==N;k=sum(r['joint'] for r in samples);exact=sum(r['exact'] for r in samples);lo,hi=wilson(k,N);elo,ehi=wilson(exact,N)
            cells.append(dict(seed=seed,method=method,split=split,status=status,offset=d,perspective=p,k=k,N=N,rate=k/N,exact_k=exact,exact_rate=exact/N,wilson_lo=lo,wilson_hi=hi,exact_wilson_lo=elo,exact_wilson_hi=ehi))
            cellrates.append(k/N)
        assert len(cellrates)==40;macro=statistics.mean(cellrates);worst=min(cellrates)
        for status,aids in atomids[split].items():
            by=collections.defaultdict(list)
            for r in ar:
                if r['status']==status:by[r['world_id']].append(r['joint'])
            count=8 if status=='reported_completed' else 16
            assert all(len(by[rid])==count for rid in aids)
            atom_arrays[seed,method,split,status]=np.array([statistics.mean(by[rid]) for rid in aids])
        fr=groups['fixed',];lookup={(r['source'],r['world_id']):r for r in fr};assert len(lookup)==640
        C=np.array([lookup['U',rid]['matched'] for rid in ids]);masks[seed,method,split,'fixed']=C;n=int(C.sum());source_counts={}
        for source in ['E','P','G','U']:
            sample=[lookup[source,rid] for rid in ids];a=np.array([r['joint'] for r in sample]);arrays[seed,method,split,source]=a
            assert all(r['matched']==bool(c) for r,c in zip(sample,C));k=int(a[C].sum());exact=sum(r['exact'] for r in sample if r['matched']);raw=int(a.sum());full=sum(r['full'] for r in sample)
            z=dict(seed=seed,method=method,split=split,source=source,k=k,n=n,rate=rate(k,n),raw_next_k=raw,N=N,raw_rate=raw/N,raw_current_and_next_k=full,raw_current_and_next_rate=full/N,exact_k=exact,raw_exact_k=sum(r['exact'] for r in sample),gate_and_next_k=k,gate_and_next_rate=k/N,exploratory=n<40)
            for label,kk,nn in [('conditional',k,n),('raw',raw,N),('exact',exact,n),('gate',k,N),('raw_full',full,N)]:z[label+'_wilson_lo'],z[label+'_wilson_hi']=wilson(kk,nn)
            fixed.append(z);source_counts[source]=k
            if source!='E':
                pc=paired_counts(arrays[seed,method,split,'E'][C],a[C]);pr=dict(seed=seed,method=method,split=split,source=source,n=n,**pc)
                for key_,v in pc.items():pr[key_+'_rate']=rate(v,n);pr[key_+'_wilson_lo'],pr[key_+'_wilson_hi']=wilson(v,n)
                assert sum(pc.values())==n;pairs.append(pr)
        all4=np.logical_and.reduce([arrays[seed,method,split,s] for s in ['E','P','G','U']]);all3edit=np.logical_and.reduce([arrays[seed,method,split,s] for s in ['P','G','U']])
        oldby=collections.defaultdict(dict)
        for r in groups['old',]:oldby[r['world_id']][r['source']]=r
        OC=np.array([oldby[rid]['H0']['matched'] for rid in ids]);oldall=np.array([all(oldby[rid][s]['joint'] for s in ['H0','H1','H2']) for rid in ids]);masks[seed,method,split,'old']=OC;arrays[seed,method,split,'old_all3']=oldall;on=int(OC.sum());ok=int(oldall[OC].sum());oldrates=[]
        for source in ['H0','H1','H2']:
            k=sum(oldby[rid][source]['joint'] for rid,c in zip(ids,OC) if c);oldrates.append(rate(k,on));lo,hi=wilson(k,on)
            olds.append(dict(seed=seed,method=method,split=split,source=source,k=k,n=on,N=N,rate=rate(k,on),wilson_lo=lo,wilson_hi=hi,gate_and_next_k=k,gate_and_next_N=N,raw_next_k=sum(oldby[rid][source]['joint'] for rid in ids)))
        lo,hi=wilson(ok,on);olds.append(dict(seed=seed,method=method,split=split,source='all3',k=ok,n=on,N=N,rate=rate(ok,on),wilson_lo=lo,wilson_hi=hi,gate_and_next_k=ok,gate_and_next_N=N))
        own={r['world_id']:r for r in groups['self_second',]};first={r['world_id']:r for r in groups['self_first',]};sf=np.array([own[rid]['full'] for rid in ids]);arrays[seed,method,split,'self_full']=sf
        sk=int(sf.sum());firstk=sum(first[rid]['joint'] for rid in ids);endk=sum(own[rid]['joint'] for rid in ids)
        z=dict(seed=seed,method=method,split=split,N=N,first_k=firstk,endpoint2_k=endk,full2_k=sk,first_exact_k=sum(first[rid]['exact'] for rid in ids),endpoint2_exact_k=sum(own[rid]['exact'] for rid in ids),full2_exact_k=sum(own[rid]['full_exact'] for rid in ids),first_failure1_k=sum(own[rid]['first_failure']==1 for rid in ids),first_failure2_k=sum(own[rid]['first_failure']==2 for rid in ids),no_failure_k=sk)
        for label in ['first','endpoint2','full2','first_exact','endpoint2_exact','full2_exact']:
            z[label+'_rate']=z[label+'_k']/N;z[label+'_wilson_lo'],z[label+'_wilson_hi']=wilson(z[label+'_k'],N)
        selfs.append(z)
        for (kind,source),sample in grouped(groups['reset_fixed',]+groups['reset_self',],['kind','source']).items():
            k=sum(r['joint'] for r in sample);full=sum(r['full'] for r in sample);ck=sum(r['joint'] for r in sample if r['matched']);lo,hi=wilson(k,N)
            reset.append(dict(seed=seed,method=method,split=split,kind=kind,source=source,next_k=k,full_k=full,N=N,conditional_k=ck,n=n,rate=k/N,wilson_lo=lo,wilson_hi=hi,conditional_rate=rate(ck,n),correct_current_equal_natural_k=sum(r['reset_equals_natural'] for r in sample),duplicate_controls_not_independent=True))
        oldrate=rate(ok,on);preserved=macro>=.98 and worst>=.90 and oldrate is not None and oldrate>=.90
        core.append(dict(method=method,seed=seed,split=split,atomic_macro=macro,atomic_min_cell=worst,old_all3_k=ok,old_n=on,old_all3=oldrate,old_min_source=min(oldrates) if on else None,P_k=source_counts['P'],U_k=source_counts['U'],G_k=source_counts['G'],natural_today_k=source_counts['E'],n=n,N=N,all_fixed4_k=int(all4[C].sum()),all_edited3_k=int(all3edit[C].sum()),first_k=firstk,endpoint2_k=endk,full2_k=sk,capability_working_pass=preserved,self_working_pass=sk/N>=.90,exploratory=n<40))
        for name,value in [('atomic_macro',macro),('old_all3',oldrate),('U',rate(source_counts['U'],n)),('P_source',rate(source_counts['P'],n)),('G_source',rate(source_counts['G'],n)),('self_full',sk/N)]:points.append(dict(seed=seed,method=method,split=split,metric=name,value=value))
        for (kind,source),sample in grouped([r for r in rs if r['kind']!='atomic'],['kind','source']).items():
            counts=collections.Counter(r['error_type'] for r in sample)
            errors.append(dict(seed=seed,method=method,split=split,kind=kind,source=source,N=len(sample),**{label:counts[label] for label in ['success','format_only','date_error','fact_error','date_and_fact_error','parse_unresolved','perspective_error','length_limit']}))
            for (pred,delta),v in grouped([r for r in sample if r['predicted_relative_date'] is not None],['predicted_relative_date','relative_date_delta_days']).items():dates.append(dict(seed=seed,method=method,split=split,kind=kind,source=source,predicted_relative_date=pred,delta_days=delta,k=len(v),reliably_parsed_N=sum(r['predicted_relative_date'] is not None for r in sample),raw_N=len(sample)))
    return dict(cells=cells,fixed=fixed,olds=olds,selfs=selfs,reset=reset,pairs=pairs,core=core,errors=errors,dates=dates,arrays=arrays,masks=masks,atom_arrays=atom_arrays,points=points,plans=plans)

def contrasts(complete,z):
    records=[];boots=collections.defaultdict(list);rng=np.random.default_rng(sub_seed('bootstrap'))
    draws={sp:{status:rng.integers(0,160,size=(2000,160)) for status in ['recorded_plan','reported_cancelled','reported_completed']} for sp in ['iid','template_ood']}
    for seed in complete:
        for split in draws:
            for a,b in [('F','N'),('O','N'),('O','F'),('F','P'),('O','P'),('N','P')]:
                for metric in ['U','P_source','G_source','self_full','atomic_macro','old_all3']:
                    if metric=='atomic_macro':
                        delta=0.;samples=np.zeros(2000);n='40 cells, 160 worlds/status'
                        for status,weight in [('recorded_plan',.4),('reported_cancelled',.4),('reported_completed',.2)]:
                            diff=z['atom_arrays'][seed,a,split,status]-z['atom_arrays'][seed,b,split,status]
                            delta+=weight*float(diff.mean());samples+=weight*diff[draws[split][status]].mean(1)
                    else:
                        key_='P' if metric=='P_source' else 'G' if metric=='G_source' else metric
                        mask=np.ones(160,bool) if metric=='self_full' else z['masks'][seed,a,split,'old' if metric=='old_all3' else 'fixed']
                        if metric!='self_full':assert np.array_equal(mask,z['masks'][seed,b,split,'old' if metric=='old_all3' else 'fixed'])
                        delta,samples=paired_boot(z['arrays'][seed,a,split,key_],z['arrays'][seed,b,split,key_],mask,draws[split]['recorded_plan']);n=int(mask.sum())
                    lo,hi=interval(samples)
                    row=dict(seed=seed,split=split,contrast=a+'-'+b,metric=metric,n=n,delta_pp=100*delta if delta is not None else None,ci_lo_pp=100*lo if lo is not None else None,ci_hi_pp=100*hi if hi is not None else None,bootstrap_replicates=2000,empty_draws=int((~np.isfinite(samples)).sum()),empty_handling='NA empty cohort; omit and count empty draw, never replace denominator',degenerate=lo==hi and lo is not None,fixed_training_models_world_uncertainty_only=True)
                    records.append(row);boots[split,a+'-'+b,metric].append((seed,delta,samples,n))
    for (split,contrast,metric),bs in boots.items():
        bs=[r for r in bs if r[1] is not None]
        if not bs:continue
        pts=[r[1] for r in bs];samples=np.array([r[2] for r in bs]);valid=np.isfinite(samples).all(0);lo,hi=interval(samples[:,valid].mean(0))
        records.append(dict(seed='mean',split=split,contrast=contrast,metric=metric,n=json.dumps({r[0]:r[3] for r in bs}),delta_pp=100*statistics.mean(pts),seed_SD_pp=100*statistics.stdev(pts) if len(pts)>1 else None,contributing_seeds=len(pts),ci_lo_pp=100*lo if lo is not None else None,ci_hi_pp=100*hi if hi is not None else None,bootstrap_replicates=2000,empty_draws=int((~valid).sum()),empty_handling='all contributing seed cohorts nonempty per shared draw, otherwise omitted',fixed_training_models_world_uncertainty_only=True))
    return records

def learning_and_training(complete,worlds):
    curves=[];learning=[];steps=[];samples=[];training=[]
    for seed in complete:
        group_tokens=[]
        for method in CFG['methods']:
            meta=json.loads((ROOT/f'training/{method}_s{seed}.json').read_text());assert meta['counts']['instances']==6400 and meta['updates']==200
            logs=read(ROOT/f'training/{method}_s{seed}_steps.jsonl.gz');assert len(logs)==200
            group_tokens.append([r['tokens'] for r in logs]);assert meta['initial_hash']==json.loads((ROOT/f'training/N_s{seed}.json').read_text())['initial_hash']
            if method=='O':assert len({r['D_producer_hash'] for r in logs})==200
            if method=='F':assert len({r['D_producer_hash'] for r in logs})==1
            for r in logs:
                steps.append(dict(seed=seed,method=method,step=r['step'],loss=r['loss'],**{k+'_loss':v for k,v in r['block_losses'].items()},**{k+'_tokens':v for k,v in r['tokens'].items()},first_wrong=r['first_wrong'],D_trajectory_targets=r['D_trajectory_targets'],D_producer_hash=r['D_producer_hash']))
                for o in r['current_records']:
                    w=worlds[o['world_id']];obs=observation(o['output'],o['normal_end'],w,0);assert obs['score']==o['score']
                    samples.append(dict(seed=seed,method=method,step=r['step'],**o,world=w))
            for curve in meta['curves']:curves.append({k:json.dumps(v) if isinstance(v,dict) else v for k,v in curve.items()})
            training.append(dict(seed=seed,method=method,instances=6400,**{k+'_tokens':v for k,v in meta['counts']['tokens'].items()},first_joint_wrong=meta['counts']['first_current_joint_wrong'],first_exact_wrong=meta['counts']['first_current_exact_wrong'],D_trajectory_targets=meta['counts']['D_trajectory_targets'],D_trajectory_fraction=meta['counts']['D_trajectory_targets']/1600,D_current_exact_wrong=meta['counts']['D_current_exact_wrong'],training_seconds=meta['training_seconds'],peak_cuda_bytes=meta['peak_cuda_bytes'],final_sha256=meta['final_sha256']))
    for path in sorted((ROOT/'learning').glob('*.jsonl')):learning+=read(path)
    if not learning and (ROOT/'learning_per_example.jsonl.gz').exists():learning=read(ROOT/'learning_per_example.jsonl.gz')
    for r in learning:
        assert r['split'] in ['train','dev'] and r.get('source')!='U'
        w=worlds[r['world_id']];off=r['offset']-1 if r['kind']=='atomic' else -2 if r['kind']=='old' else 0 if r['kind']=='seen_A' else -1
        o=observation(r['output'],r['normal_end'],w,off,r.get('perspective','first'));assert o['score']==r['score']
    assert len(learning)==len(complete)*24000
    # Compare block token budgets across N/F/O at every update, not just totals.
    for seed in complete:
        tokenlogs=[read(ROOT/f'training/{m}_s{seed}_steps.jsonl.gz') for m in CFG['methods']]
        assert all([r['tokens'] for r in logs]==[r['tokens'] for r in tokenlogs[0]] for logs in tokenlogs)
    csvwrite(ROOT/'learning_curves.csv',curves);csvwrite(ROOT/'optimizer_steps.csv',steps);csvwrite(ROOT/'training_budget.csv',training)
    write(ROOT/'learning_per_example.jsonl.gz',learning);write(ROOT/'training_samples.jsonl.gz',samples)
    return training

def cases(complete,rows,z):
    by=grouped([r for r in rows if r['kind']!='atomic'],['seed','split','world_id']);ids=json.loads((ROOT/'data/case_ids.json').read_text());selected=[];categories=[]
    for seed in complete:
        for split,rids in ids[str(seed)].items():
            for rid in rids:selected.append(dict(selection='pre-inference hash fixed',seed=seed,split=split,world_id=rid,rows=by[seed,split,rid]))
    for method in CFG['methods']:
        for split in ['iid','template_ood']:
            for category,kind,source in [('self_failure','self_second','Q'),('heldout_failure','fixed','U'),('old_maintenance_failure','old','H2')]:
                candidates=[r for r in rows if r['method']==method and r['split']==split and r['kind']==kind and r['source']==source and (not r['full'] if kind=='self_second' else r['matched'] and not r['joint'])]
                ranked=sorted(candidates,key=lambda r:hashlib.sha256(f'g15/failure/{r["seed"]}/{r["world_id"]}'.encode()).hexdigest())
                categories.append(dict(method=method,split=split,category=category,count=len(candidates),absent=not candidates,selected_seed=ranked[0]['seed'] if ranked else None,selected_world_id=ranked[0]['world_id'] if ranked else None,post_result_descriptive_only=True))
                if ranked:
                    r=ranked[0];selected.append(dict(selection=category+' first deterministic hash after failure classification',seed=r['seed'],split=split,world_id=r['world_id'],rows=[x for x in by[r['seed'],split,r['world_id']] if x['method']==method]))
    write(ROOT/'cases.jsonl.gz',selected);csvwrite(ROOT/'case_categories.csv',categories);out=['# G15 actual cases','', 'First12 worlds were fixed before inference, two per seed/split; supplementary failure examples use deterministic hash ordering within openly reported post-result categories. They do not affect training, cohorts, estimates or model choice. Absent categories remain absent.','']
    for case in selected:
        out += [f'## {case["selection"]} / seed{case["seed"]} / {case["split"]} / {case["world_id"]}','']
        for r in case['rows']:
            out += [f'{r["method"]} {r["kind"]} {r["source"]}: joint={r["joint"]}; exact={r["exact"]}; full={r.get("full","NA")}; C={r.get("matched","NA")}; error={r["error_type"]}; date_delta={r["relative_date_delta_days"]}',f'Current: {r.get("current",{}).get("output","natural tomorrow for self first")}',f'Output: {r["output"]}',f'Gold: {r["gold"]}',f'Parsed: {json.dumps(r["parsed_facts"],ensure_ascii=False)}','']
    (ROOT/'CASES.md').write_text('\n'.join(out).rstrip()+'\n');return len(selected)

def report(complete,z,differences,means,training):
    def summaries(method,split,metric):
        row=next((r for r in means if r['method']==method and r['split']==split and r['metric']==metric),None)
        return f'{pct(row["mean"])} ± {pct(row["sample_SD"])}' if row else 'NA'
    def gain(contrast,split,metric):
        r=next((r for r in differences if r['seed']=='mean' and r['contrast']==contrast and r['split']==split and r['metric']==metric),None)
        return f'{r["delta_pp"]:.2f}pp [world CI {r["ci_lo_pp"]:.2f},{r["ci_hi_pp"]:.2f}]' if r else 'NA'
    out=['# G15 自身状态监督与留出来源迁移','',f'完成seed={complete}，未完成seed={[s for s in CFG["seeds"] if s not in complete]}。每个完成seed的N/F/O均训练固定200步；主模型只用final200。','']
    for method in CFG['methods']:
        iid=[r for r in z['core'] if r['method']==method and r['split']=='iid']
        out += [f'1. {method}能力维持：IID原子macro {summaries(method,"iid","atomic_macro")}；旧yesterday all3 {summaries(method,"iid","old_all3")}。工作标准通过seed={[r["seed"] for r in iid if r["capability_working_pass"]]}，未通过={[r["seed"] for r in iid if not r["capability_working_pass"]]}；逐cell最低值和实际分母见主表。',f'2. {method}自身两步full：IID {summaries(method,"iid","self_full")}，OOD {summaries(method,"template_ood","self_full")}；IID达到90% seed={[r["seed"] for r in iid if r["self_working_pass"]]}。O的该路径已监督；新世界成功不是新长度泛化。',f'3. {method}留出U=精确F2 final200 today：IID {summaries(method,"iid","U")}；OOD {summaries(method,"template_ood","U")}。相对初始化P的IID改变量 {gain(method+"-P","iid","U")}；相对N的改变量 {gain(method+"-N","iid","U") if method!="N" else "自然控制自身NA"}。只有正向且维持通过才能支持有限留出来源迁移。','']
    out += [f'4. O对F的实际优势：IID自身full {gain("O-F","iid","self_full")}；留出U {gain("O-F","iid","U")}；OOD自身full {gain("O-F","template_ood","self_full")}；留出U {gain("O-F","template_ood","U")}。以这些配对差与逐seed方向判断在线刷新是否有额外作用，不预设必要性。','', '## 核心表：最终固定步模型','', '主来源E/P/G/U的共同C只取决于冻结当前全文/EOS/事实与P/G/U源mask，完全独立于更新后Q的当前输出及所有next输出。旧all3有独立的G13 yesterday匹配分母。自身分母始终原始160。','',table(['组','seed','split','自然macro','min-cell','旧all3','固定P','留出F2/U','旧G','自身step1','step2 endpoint','step2 full','today C/N'],[[r['method'],r['seed'],r['split'],pct(r['atomic_macro']),pct(r['atomic_min_cell']),frac(r['old_all3_k'],r['old_n']),frac(r['P_k'],r['n']),frac(r['U_k'],r['n']),frac(r['G_k'],r['n']),frac(r['first_k'],160),frac(r['endpoint2_k'],160),frac(r['full2_k'],160),frac(r['n'],160)] for r in z['core']]),'', '## 优先配对差：世界bootstrap与seed差异','', '2000次共享世界抽样，IID/OOD分开；跨条件、来源、训练seed共享同一世界draw。原子按status抽样整个世界的所有cell，权重16/40、16/40、8/40。区间仅为固定训练模型的世界抽样不确定性，不是所有训练随机性，不把同一世界×3当480个独立训练。空cohort NA，空draw计数省略。Wilson区间见原子逐cell/来源/自身/旧能力表，全零全一并不表示总体没有不确定性。','',table(['contrast','seed','split','metric','n','delta pp','seed SD pp','CI95 pp','empty draws'],[[r['contrast'],r['seed'],r['split'],r['metric'],r['n'],r['delta_pp'],r.get('seed_SD_pp','NA'),f'[{r["ci_lo_pp"]},{r["ci_hi_pp"]}]',r['empty_draws']] for r in differences if r['contrast'] in ['F-N','O-N','O-F'] or r['metric']=='U']),'', '## 训练监督与当前错误状态','',table(['method','seed','instances','A tokens','B tokens','C tokens','D tokens','T first joint wrong /1600','T first exact wrong /1600','D trajectory targets /1600'],[[r['method'],r['seed'],r['instances'],r['A_tokens'],r['B_tokens'],r['C_tokens'],r['D_tokens'],r['first_joint_wrong'],r['first_exact_wrong'],r['D_trajectory_targets']] for r in training]),'', 'O错误当前状态的D loss是轨迹目标监督，不称正确today续步监督。N/F也逐步记录当前T first自由输出，但它们的D实际输入仍分别是自然E与冻结P；不能把其T first错误等同于D来源错误。training_samples.jsonl.gz/optimizer_steps.csv保留真实当前输出、事实解析、梯度来源/hash、每步loss与token。所有组共同schedule、目标token数逐步一致。','', '## 能力与数据边界','', '完整40-cell自然结果在atomic_by_cell.csv，today→yesterday和tomorrow→today按status/perspective分别列出；不以宏平均隐藏某cell失败。旧H0/H1/H2/min/all3在old_source_results.csv，原始分母和gate-and-next亦保留。固定today条件及原始160下一步/full、exact、Wilson在fixed_source_results.csv；自然vs各编辑来源的四种配对计数在natural_source_pairs.csv，全部固定来源同时成功在core_results.csv。解析未决与确认日期/事实错误分开在error_counts.csv；可靠日期偏差在relative_date_errors.csv。','', 'G13旧yesterday维护和G-today恢复不是新未监督能力。P-source对F受监督，对O是初始/历史自身来源。U的精确final200表示不用于训练、dev、模型选择、蒸馏或对齐；U/P有共同祖先和自然语义训练，留出仅指本轮修复来源。模板OOD沿已有词汇与8–11模板，不等同开放自然语言。','', '自然mask未覆盖或替换编辑mask。共同C包含自然正确重构门槛，但自然mask不相等不会剔除编辑来源比较。每来源覆盖/失败原因及mask见cohort_results.csv与cache state manifest。自身first正确集合不改变固定C。重编码只用真实自由输出，first错则full错；正确相同文本控制是重复，不是新独立样本。reset_results.csv单列，不计为纯latent结果。','', '## 曲线、案例、运行及复现','', 'learning_curves.csv及learning_per_example.jsonl.gz有0/50/100/150/200 train/dev诊断，U与G-today均未进入dev；固定200最终模型，不选best。初始化与独立optimizer、detach/第一阶段梯度、冻结decoder可微、缓存不可变、真实输出reset、U隔离、full指标及保存/RNG恢复的CPU和GPU测试均有记录。完整确认per_example.jsonl.gz逐记录重新评分。CASES.md包含事前固定12世界及公开规则的失败案例；无该失败类别时明确absent。','', '独立G15 worktree保留用户原改动；基础BART、旧模型与旧结果只读。大FP32 caches/optimizer恢复保留local/，data/cache manifests有精确路径/SHA，只有小editor final上传。数据主seed20261001用g15命名子流，新2880事实世界含train1536，主IID/OOD各160 plan；历史去重只复用G14已列源并补G13/G14worlds，可访问范围和SHA列于data/manifest.json，没有全部历史无泄漏声明。','']
    if (ROOT/'budget.json').exists():out+=['allocation预算：'+json.dumps(json.loads((ROOT/'budget.json').read_text()),ensure_ascii=False),'']
    if (ROOT/'slurm_jobs.csv').exists():
        jobs=list(csv.DictReader((ROOT/'slurm_jobs.csv').open()));out += [table(['JobID','rawID','state','exit','GPU hours'],[[r[k] for k in ['job_id','raw_job_id','state','exit_code','gpu_hours']] for r in jobs]),'']
    deviations=json.loads((ROOT/'engineering_deviations.json').read_text()) if (ROOT/'engineering_deviations.json').exists() else []
    out += ['偏离/失败：'+json.dumps(deviations,ensure_ascii=False)+'. 未完成seed='+str([s for s in CFG['seeds'] if s not in complete])+'. 没有按结果追加训练、换模型或四/五步评估。', '', '解释只约束本设置：自身修复与留出迁移是不同终点；固定/当前来源都能迁移则不坚持在线刷新必要；维护失败不能称完成目标。训练集受监督任务仍差时先记录优化/预算/兼容性未决，不证明不可组合或不可能。不自动执行后续扩展。']
    (ROOT/'REPORT.md').write_text('\n'.join(out).rstrip()+'\n')

def main():
    verify_lock();complete=[s for s in CFG['seeds'] if (ROOT/f'seed_s{s}_complete.json').exists()];worlds={w['record_id']:w for w in read(ROOT/'data/worlds.jsonl')}
    for seed in complete:
        audit=json.loads((ROOT/f'seed_s{seed}_complete.json').read_text());assert audit['passed'] and audit['frozen_before']==audit['frozen_after'] and audit['U_frozen_before']==audit['U_frozen_after']
    rows=load_confirmation(complete,worlds);z=analyze(complete,rows,worlds);ds=contrasts(complete,z);means=[]
    for (method,split,metric),rs in grouped(z['points'],['method','split','metric']).items():
        values=[r['value'] for r in rs if r['value'] is not None]
        means.append(dict(method=method,split=split,metric=metric,contributing_seeds=len(values),mean=statistics.mean(values) if values else None,sample_SD=statistics.stdev(values) if len(values)>1 else None,per_seed=json.dumps({r['seed']:r['value'] for r in rs})))
    for filename,values in [('atomic_by_cell.csv',z['cells']),('fixed_source_results.csv',z['fixed']),('old_source_results.csv',z['olds']),('self_two_step_results.csv',z['selfs']),('reset_results.csv',z['reset']),('natural_source_pairs.csv',z['pairs']),('core_results.csv',z['core']),('error_counts.csv',z['errors']),('relative_date_errors.csv',z['dates']),('paired_differences.csv',ds),('seed_mean_SD.csv',means)]:csvwrite(ROOT/filename,values)
    cohorts=[]
    for seed in complete:
        for split in ['iid','template_ood']:
            meta=json.loads((ROOT/f'data/confirm_{split}_s{seed}.json').read_text());states=read(ROOT/meta['state_metadata']);gates=meta['gates'];n=sum(g['fixed_gate']['matched'] for g in gates)
            for source in ['E','P','G','U']:
                sample=[r for r in states if r['source']==source];k=sum(r['current']['exact'] and r['current']['joint'] and r['current']['normal_end'] for r in sample);lo,hi=wilson(k,160)
                cohorts.append(dict(seed=seed,split=split,source=source,current_correct_k=k,N=160,current_wilson_lo=lo,current_wilson_hi=hi,C=n,C_wilson_lo=wilson(n,160)[0],C_wilson_hi=wilson(n,160)[1],gate_failures=json.dumps(dict(collections.Counter(f for g in gates for f in g['fixed_gate']['failures']))),natural_mask_equal_k=sum(g['natural_mask_equal'] for g in gates),producer_masks_equal=all(g['producer_masks_equal'] for g in gates),exploratory=n<40))
    csvwrite(ROOT/'cohort_results.csv',cohorts)
    tr=learning_and_training(complete,worlds);case_n=cases(complete,rows,z);report(complete,z,ds,means,tr)
    dump(ROOT/'result_audit.json',dict(complete_seeds=complete,missing_seeds=[s for s in CFG['seeds'] if s not in complete],confirmation_rows=len(rows),all_scores_recomputed=True,U_final_only=True,all_group_token_schedules_equal=True,all_groups_6400_instances=True,O_producer_refreshed_every_update=True,F_frozen_producer_constant=True,bootstrap_shared_worlds=True,case_records=case_n,original_world_denominator=160,primary_checkpoint='fixed final200',max_own_semantic_edits=2))
    print('G15 aggregated',len(rows),'confirmation rows; complete',complete,flush=True)

if __name__=='__main__':main()
