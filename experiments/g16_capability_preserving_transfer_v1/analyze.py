"""G16 CPU full-score verification, four versions, immutable-selection comparisons."""
import statistics
import numpy as np
from common_g16 import *
from selection import qualify,check_selection_lock
stats=load_module('g16_readonly_g15_aggregation',G15/'analyze.py');stats.ROOT=ROOT;stats.CFG=CFG

def versions(seed):
    maps=json.loads((ROOT/'checkpoints_manifest.json').read_text())['models'][str(seed)]
    vs={'P':dict(step=0,sha256=maps['P']['sha256'])}
    for m in CFG['methods']:
        z=json.loads((ROOT/f'training/{m}_s{seed}.json').read_text());vs[m+'-final']=dict(step=200,sha256=z['final_sha256'])
    z=json.loads((ROOT/f'selection_s{seed}.json').read_text())
    if z['selected_step'] is not None:vs['F-guard']=dict(step=z['selected_step'],sha256=z['checkpoint_sha256'])
    return vs

def confirmation(complete,worlds):
    rows=[]
    for seed in complete:
        for method,v in versions(seed).items():
            for split in ['iid','template_ood']:
                path=ROOT/f'outputs/{method}_s{seed}_{split}.jsonl'
                if path.exists():rs=read(path)
                else:rs=[r for r in read(ROOT/f'per_example_s{seed}.jsonl.gz') if r['method']==method and r['split']==split]
                assert len(rs)==8480
                for r in rs:
                    w=worlds[r['world_id']];offset=r['offset']-1 if r['kind']=='atomic' else -2 if r['kind']=='old' else 0 if r['kind']=='self_first' else -1
                    o=observation(r['output'],r['normal_end'],w,offset,r.get('perspective','first'))
                    assert all(o[k]==r[k] for k in ['score','joint','exact','error_type'])
                    if 'current' in r:
                        cur=observation(r['current']['output'],r['current']['normal_end'],w,-1 if r['kind']=='old' else 0)
                        assert cur['joint']==r['current']['joint'] and cur['exact']==r['current']['exact']
                        if 'full' in r:assert r['full']==full_success(cur,o)
                    assert r['checkpoint_sha256']==v['sha256'] and r['actual_updates']==v['step']
                    r.update(world=w,expected_frame=frame(w,offset,r.get('perspective','first')))
                    if r.get('source') in ['P','G','U']:r['producer_checkpoint_sha256']=json.loads((ROOT/'checkpoints_manifest.json').read_text())['models'][str(seed)][r['source']]['sha256']
                rows+=rs
        write(ROOT/f'per_example_s{seed}.jsonl.gz',[r for r in rows if r['seed']==seed])
    return rows

def contrasts(complete,z):
    records=[];boot=collections.defaultdict(list);rng=np.random.default_rng(sub_seed('bootstrap'))
    draws={sp:{status:rng.integers(0,160,size=(2000,160)) for status in ['recorded_plan','reported_cancelled','reported_completed']} for sp in ['iid','template_ood']}
    for seed in complete:
        for split in draws:
            for a,b in [('F-final','N-final'),('F-guard','F-final'),('F-guard','N-final'),('F-guard','P'),('F-final','P')]:
                for metric in ['U','P_source','G_source','self_full','atomic_macro','old_all3']:
                    if a not in versions(seed) or b not in versions(seed):
                        records.append(dict(seed=seed,split=split,contrast=a+' minus '+b,metric=metric,n=0,delta_pp=None,ci_lo_pp=None,ci_hi_pp=None,missing='selection failed; no fallback',bootstrap_replicates=2000));continue
                    if metric=='atomic_macro':
                        delta=0.;samples=np.zeros(2000);n='40 cells;160 worlds/status'
                        for status,weight in [('recorded_plan',.4),('reported_cancelled',.4),('reported_completed',.2)]:
                            diff=z['atom_arrays'][seed,a,split,status]-z['atom_arrays'][seed,b,split,status];delta+=weight*float(diff.mean());samples+=weight*diff[draws[split][status]].mean(1)
                    else:
                        key_='P' if metric=='P_source' else 'G' if metric=='G_source' else metric
                        mask=np.ones(160,bool) if metric=='self_full' else z['masks'][seed,a,split,'old' if metric=='old_all3' else 'fixed']
                        if metric!='self_full':assert np.array_equal(mask,z['masks'][seed,b,split,'old' if metric=='old_all3' else 'fixed'])
                        delta,samples=stats.paired_boot(z['arrays'][seed,a,split,key_],z['arrays'][seed,b,split,key_],mask,draws[split]['recorded_plan']);n=int(mask.sum())
                    lo,hi=stats.interval(samples);name=a+' minus '+b
                    records.append(dict(seed=seed,split=split,contrast=name,metric=metric,n=n,delta_pp=100*delta if delta is not None else None,ci_lo_pp=100*lo if lo is not None else None,ci_hi_pp=100*hi if hi is not None else None,bootstrap_replicates=2000,empty_draws=int((~np.isfinite(samples)).sum()),fixed_models_world_uncertainty_only=True))
                    boot[split,name,metric].append((seed,delta,samples,n))
    for (split,name,metric),bs in boot.items():
        bs=[r for r in bs if r[1] is not None]
        if not bs:continue
        pts=[r[1] for r in bs];samples=np.array([r[2] for r in bs]);valid=np.isfinite(samples).all(0);lo,hi=stats.interval(samples[:,valid].mean(0))
        records.append(dict(seed='mean',split=split,contrast=name,metric=metric,n=json.dumps({r[0]:r[3] for r in bs}),delta_pp=100*statistics.mean(pts),seed_SD_pp=100*statistics.stdev(pts) if len(pts)>1 else None,contributing_seeds=len(pts),ci_lo_pp=100*lo if lo is not None else None,ci_hi_pp=100*hi if hi is not None else None,bootstrap_replicates=2000,empty_draws=int((~valid).sum()),fixed_models_world_uncertainty_only=True))
    return records

def learning(complete,worlds):
    curve=[];steps=[];budget=[];current=[];selection=[]
    for seed in complete:
        tokenlogs=[]
        for method in CFG['methods']:
            z=json.loads((ROOT/f'training/{method}_s{seed}.json').read_text());logs=read(ROOT/f'training/{method}_s{seed}_steps.jsonl.gz');assert len(logs)==200 and z['counts']['instances']==6400
            tokenlogs.append([r['tokens'] for r in logs]);curve += [{k:json.dumps(v) if isinstance(v,dict) else v for k,v in r.items()} for r in z['curves']]
            assert z['initial_hash']==json.loads((ROOT/f'training/N_s{seed}.json').read_text())['initial_hash']
            if method=='F':assert len({r['D_producer_hash'] for r in logs})==1
            for r in logs:
                steps.append(dict(seed=seed,method=method,step=r['step'],loss=r['loss'],**{k+'_CE':v for k,v in r['block_losses'].items()},**{k+'_tokens':v for k,v in r['tokens'].items()},first_wrong=r['first_wrong']))
                for o in r['current_records']:
                    w=worlds[o['world_id']];assert observation(o['output'],o['normal_end'],w,0)['score']==o['score'];current.append(dict(seed=seed,method=method,step=r['step'],**o))
            budget.append(dict(seed=seed,method=method,updates=200,instances=6400,**{k+'_tokens':v for k,v in z['counts']['tokens'].items()},first_joint_wrong=z['counts']['first_current_joint_wrong'],first_exact_wrong=z['counts']['first_current_exact_wrong'],D_input_wrong=z['counts']['D_trajectory_targets'],training_seconds=z['training_seconds'],final_sha256=z['final_sha256']))
        assert tokenlogs[0]==tokenlogs[1]
        for c in json.loads((ROOT/f'training/F_s{seed}_candidates.json').read_text()):
            q=qualify(c);selected=json.loads((ROOT/f'selection_s{seed}.json').read_text())['selected_step'];selection.append(dict(seed=seed,step=c['step'],qualified=q['qualified'],reasons=json.dumps(q['reasons']),macro=q.get('atomic_macro'),min_cell=q.get('min_cell'),old_k=c['old_k'],old_n=c['old_n'],A_k=c['A_k'],A_n=c['A_n'],D_k=c['D_k'],D_n=c['D_n'],selected_step=selected,selected=c['step']==selected,sha256=c['checkpoint_sha256']))
        rs=[]
        for path in sorted((ROOT/'learning').glob(f'*_s{seed}_*.jsonl')):rs+=read(path)
        if not rs:rs=read(ROOT/f'learning_per_example_s{seed}.jsonl.gz')
        assert len(rs)==111680
        for r in rs:
            w=worlds[r['world_id']];d=r['offset']-1 if r['kind']=='atomic' else -2 if r['kind']=='old' else 0 if r['kind']=='seen_A' else -1
            assert observation(r['output'],r['normal_end'],w,d,r.get('perspective','first'))['score']==r['score'];assert r.get('source')!='U'
        write(ROOT/f'learning_per_example_s{seed}.jsonl.gz',rs)
    csvwrite(ROOT/'learning_curves.csv',curve);csvwrite(ROOT/'optimizer_steps.csv',steps);csvwrite(ROOT/'training_budget.csv',budget);csvwrite(ROOT/'selection_table.csv',selection);write(ROOT/'training_current.jsonl.gz',current)
    return budget

def cases(rows):
    chosen=[];by=stats.grouped(rows,['seed','split','world_id']);fixed=json.loads((ROOT/'data/case_ids.json').read_text());cats=[]
    for seed,ss in fixed.items():
        for split,ids in ss.items():
            for rid in ids:chosen.append(dict(selection='pre-inference hash fixed',seed=int(seed),split=split,world_id=rid,rows=by[int(seed),split,rid]))
    for method in ['N-final','F-final','F-guard']:
        for split in ['iid','template_ood']:
            for category in ['atomic_failure','self_failure','U_failure','any_maintenance_source_failure']:
                rs=[r for r in rows if r['method']==method and r['split']==split and ((category=='atomic_failure' and r['kind']=='atomic' and not r['joint']) or (category=='self_failure' and r['kind']=='self_second' and not r['full']) or (category=='U_failure' and r['kind']=='fixed' and r['source']=='U' and r['matched'] and not r['joint']) or (category=='any_maintenance_source_failure' and r['kind']=='old' and r['matched'] and not r['joint']))]
                rs=sorted(rs,key=lambda r:hashlib.sha256(f'g16/failure/{r["seed"]}/{r["world_id"]}/{r.get("source")}/{r.get("offset")}/{r.get("perspective")}'.encode()).hexdigest());cats.append(dict(method=method,split=split,category=category,count=len(rs),absent=not rs,post_result_descriptive=True))
                if rs:
                    r=rs[0];chosen.append(dict(selection='post-result first hash '+category,seed=r['seed'],split=split,world_id=r['world_id'],rows=[r]))
    write(ROOT/'cases.jsonl.gz',chosen);csvwrite(ROOT/'case_categories.csv',cats)
    out=['# G16真实案例','', '前12世界推断前锁定，所有实际版本共用世界；其余是公开类别中的事后hash首例，空类保留。维护失败类别涵盖H0/H1/H2。','']
    for c in chosen:
        out += [f'## {c["selection"]} / seed{c["seed"]} / {c["split"]} / {c["world_id"]}','']
        for r in c['rows']:out += [f'{r["method"]} step{r["actual_updates"]} {r["kind"]} {r.get("source","natural atomic")}: joint={r["joint"]}; exact={r["exact"]}; full={r.get("full","NA")}; C={r.get("matched","NA")}; error={r["error_type"]}; first_failure={r.get("first_failure","NA")}; date_delta={r["relative_date_delta_days"]}',f'Current: {r.get("current",{}).get("output","see natural input frame/token IDs")}',f'Output: {r["output"]}',f'Gold: {r["gold"]}',f'Parsed facts: {json.dumps(r["parsed_facts"],ensure_ascii=False)}','']
    (ROOT/'CASES.md').write_text('\n'.join(out).rstrip()+'\n')

def report(complete,z,ds,means):
    core=z['core'];selected=[json.loads((ROOT/f'selection_s{s}.json').read_text()) for s in CFG['seeds'] if (ROOT/f'selection_s{s}.json').exists()]
    headers=['seed','split','版本','实际步','macro','min-cell','旧all3','固定P','U','旧G','self1','self2 endpoint','full2','C/N','完整工作目标','配对改善区间支持']
    tab=[[r['seed'],r['split'],r['method'],r['actual_updates'],stats.pct(r['atomic_macro']),stats.pct(r['atomic_min_cell']),stats.frac(r['old_all3_k'],r['old_n']),stats.frac(r['P_k'],r['n']),stats.frac(r['U_k'],r['n']),stats.frac(r['G_k'],r['n']),stats.frac(r['first_k'],160),stats.frac(r['endpoint2_k'],160),stats.frac(r['full2_k'],160),stats.frac(r['n'],160),r['goal_working_pass'],r['paired_U_support']] for r in core]
    for s in CFG['seeds']:
        if not any(r['seed']==s and r['method']=='F-guard' for r in core):
            for sp in ['iid','template_ood']:tab.append([s,sp,'F-guard','NA','NA','NA','NA','NA','NA','NA','NA','NA','NA','NA','False (missing selection)','False'])
    passed=[r['seed'] for r in core if r['method']=='F-guard' and r['split']=='iid' and r['goal_working_pass'] and r['paired_U_support']]
    out=['# G16 能力约束下的固定来源修复与留出迁移复验','', '1. 预设规则实际选择：'+json.dumps({r['seed']:r['selected_step'] for r in selected})+'；null表示无合格候选，不fallback。','2. 所选模型的逐seed能力/自身完整目标通过：'+str(passed)+' / 原始3seed；具体失败cell与工作目标逐项见表和atomic_by_cell.csv。','3. 不读取U的开发规则所选U结果、相对P/N的配对变化如下；U是G15已考察过的同一修复留出生产者在新世界的复验，不是全新模型家族发现。','4. 是否比同轨迹final200更好：按guard−final的原子/旧all3/U/self配对差及逐seed方向解释；训练仍全部执行200步，不声称节省训练时间或新算法优势。','',stats.table(headers,tab),'', '## 配对差与不确定性','',stats.table(['seed','split','contrast','metric','n','delta pp','CI95 pp','seed SD pp'],[[r['seed'],r['split'],r['contrast'],r['metric'],r['n'],r.get('delta_pp'),f'[{r.get("ci_lo_pp")},{r.get("ci_hi_pp")}]',r.get('seed_SD_pp','NA')] for r in ds]),'', '三个seed共享世界，2000次共享world paired bootstrap按split分开；原子按status分层抽整个世界，保留该世界全部cell、40cell等权。Wilson区间在逐cell/source/self/maintenance表；0/1退化bootstrap不表示总体无不确定性。CI只包括固定模型的世界抽样，不包括完整训练/选择随机性，也不是480独立训练。','', '## 数据、选择及工程边界','', '新g16 namespace，2880事实世界、训练1536/开发384；每split480确认世界中主路径只有160plan。history来源复用G15已审计清单并补G15世界，只有有SHA/可访问范围无重合声明。模板OOD8–11保留词汇，非开放语言。所有状态的自由文本、gold、解析和错误类型在逐seed完整archive，不将解析未决当确认事实错误。','', '候选25/50/75/100/125/150/175/200，step0不允许选；全部128 dev主世界、每status128世界的40cell监测。C/P入口独立固定，覆盖<64选择失败。只选最早合格且不可修改，全部NF训练完、全局选择锁后才加载U/推断新确认。N只有final200。F-D是固定P续步，不能当更新自身full2；自身两步不参与开发选择，也不称全新长度/概念。','', 'F-final−N-final是等200步训练来源对照；F-guard−F-final是同轨迹检查点比较；F-guard−N/P包含来源和选择两因素，不能唯一归因。guard=final同SHA复用推断、差0，不虚增证据；guard缺失记NA且完整目标分母仍3。','', '完整C只看冻结E/P/G/U当前全文、EOS/事实和P/G/U同mask。自然mask单列、不替换。自身分母raw160；重编码只用自由输出，不给gold，不作为纯latent结果或独立重复证据。旧yesterday H2固定构造/续步只是维护，非新自身三步链。','', 'CPU G15退化审计、选择器/RNG/梯度/状态流/恢复/统计单测、单卡smoke、冻结hash和缓存proof有记录。没有O、架构/优化设置搜索、probe或新长链。科学目标通过与所有实验完成分开。','']
    if (ROOT/'budget.json').exists():out+=['资源：'+json.dumps(json.loads((ROOT/'budget.json').read_text())),'']
    out+=['作业、失败/偏离见slurm_jobs.csv/engineering_deviations.json。Slurm语法仅依据[数组官方文档](https://slurm.schedmd.com/job_array.html)、[sbatch](https://slurm.schedmd.com/sbatch.html)、[srun](https://slurm.schedmd.com/srun.html)。','']
    (ROOT/'REPORT.md').write_text('\n'.join(out))

def main():
    verify_lock();check_selection_lock();complete=[s for s in CFG['seeds'] if (ROOT/f'seed_s{s}_confirm_complete.json').exists()]
    worlds={w['record_id']:w for w in read(ROOT/'data/worlds.jsonl')};rows=confirmation(complete,worlds);z=stats.analyze(complete,rows,worlds);ds=contrasts(complete,z);means=[]
    for r in z['core']:
        v=versions(r['seed'])[r['method']];r.update(actual_updates=v['step'],checkpoint_sha256=v['sha256'])
        support=[];positive=[]
        for b in ['N-final','P']:
            name=r['method']+' minus '+b;x=next((d for d in ds if d['seed']==r['seed'] and d['split']==r['split'] and d['contrast']==name and d['metric']=='U'),None)
            positive.append(x is not None and x.get('delta_pp') is not None and x['delta_pp']>0);support.append(x is not None and x.get('ci_lo_pp') is not None and x['ci_lo_pp']>0)
        r['paired_U_support']=all(support);r['goal_working_pass']=r['capability_working_pass'] and r['self_working_pass'] and r['n']>=40 and r['old_n']>=40 and r['U_k']/r['n']>=.9 and all(positive)
    for (method,split,metric),rs in stats.grouped(z['points'],['method','split','metric']).items():
        vs=[r['value'] for r in rs if r['value'] is not None];means.append(dict(method=method,split=split,metric=metric,contributing_seeds=len(vs),original_seed_denominator=3,mean=statistics.mean(vs) if vs else None,sample_SD=statistics.stdev(vs) if len(vs)>1 else None,per_seed=json.dumps({r['seed']:r['value'] for r in rs})))
    for filename,values in [('atomic_by_cell.csv',z['cells']),('maintenance_results.csv',z['olds']),('fixed_source_results.csv',z['fixed']),('self_rollout_results.csv',z['selfs']),('reset_results.csv',z['reset']),('natural_source_pairs.csv',z['pairs']),('core_results.csv',z['core']),('error_counts.csv',z['errors']),('relative_date_errors.csv',z['dates']),('paired_differences.csv',ds),('seed_mean_SD.csv',means)]:csvwrite(ROOT/filename,values)
    learning(complete,worlds);cases(rows);report(complete,z,ds,means)
    dump(ROOT/'result_audit.json',dict(complete_seeds=complete,missing_seeds=[s for s in CFG['seeds'] if s not in complete],confirmation_rows=len(rows),learning_rows=len(complete)*111680,all_scores_recomputed=True,all_NF_step_token_schedules_equal=True,U_after_global_lock=True,selection_records_immutable=True,all_training_runs200=True,all_group_instances6400=True,guard_missing_not_fallback=True,shared_world_bootstrap=True))
    print('G16 aggregated',complete,len(rows),'confirmation rows',flush=True)

if __name__=='__main__':main()
