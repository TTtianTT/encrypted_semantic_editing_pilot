"""CPU-only aggregate tables, clustered statistics, provenance and final report."""
import argparse
import csv
import gzip
from collections import Counter,defaultdict
from .common import *
from .metrics import clustered_difference,holm

def write_csv(path,xs):
    xs=list(xs)
    keys=list(dict.fromkeys(k for r in xs for k in r))
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=keys);w.writeheader()
        for r in xs:w.writerow({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(dict,list)) else v for k,v in r.items()})

def display_method(name):
    return name.rsplit('_',1)[0]+'_8seed_mean' if name.startswith('random_') else name

def collapse(rs):
    groups=defaultdict(list)
    for r in rs:groups[(r['world_id'],r['editor_seed'],r['sequence_name'],display_method(r['method_name']))].append(r)
    out=[]
    for (world,seed,seq,method),xs in groups.items():
        x=dict(xs[0]);x['method_name']=method
        for key in ('C0','exact_preservation','R1','R3','R5','patch_norm','relative_patch_norm','other_operation_success'):
            vals=[r[key] for r in xs if r.get(key) is not None];x[key]=sum(vals)/len(vals) if vals else None
        x['step_successes']=[sum(r['step_successes'][i] for r in xs)/len(xs) for i in range(len(xs[0]['step_successes']))]
        x['first_failure_distribution']=dict(Counter(str(r['first_failure']) for r in xs))
        out.append(x)
    return out

def equal_seed_mean(xs,key):
    by=defaultdict(list)
    for r in xs:
        if r.get(key) is not None:by[r['editor_seed']].append(r[key])
    return sum(sum(v)/len(v) for v in by.values())/len(by) if by else None

def mdtable(xs,columns):
    if not xs:return 'NA — no executed results.\n'
    text='| '+' | '.join(columns)+' |\n| '+' | '.join('---' for _ in columns)+' |\n'
    for r in xs:
        def fmt(v):
            if v is None:return 'NA'
            if isinstance(v,float):return f'{v:.4f}'
            return str(v).replace('|','/')
        text+='| '+' | '.join(fmt(r.get(c)) for c in columns)+' |\n'
    return text

def aggregate():
    audit=read(ROOT/'run_manifest.json');tables={};paircounts=[];testrecords=[];operators=[];samples=[];modelstats=[];paths=[]
    allfiles=[]
    for model in ('bart','t5gemma'):
        for seed in (42,43,44):
            scan=ROOT/f'local/scan_{model}/{model}_s{seed}'
            if (scan/'pair_audit.jsonl').exists():
                gr=defaultdict(list)
                for r in rows(scan/'pair_audit.jsonl'):gr[(r['split'],r['original_split'],r['source'],r['operation'])].append(r)
                for (sp,old,source,op),rs in gr.items():
                    x=dict(model=model,editor_seed=seed,split=sp,original_split=old,source=source,operation=op,scanned_worlds=len(rs))
                    for key in ('candidate_history_combinations','current_double_correct','exact_current_text','next_step_fork','same_shape_mask','final_pair_worlds','current_not_both_correct','current_text_mismatch','not_good_bad_fork','shape_or_mask_mismatch'):x[key]=sum(r.get(key,0) for r in rs)
                    for key in ('current_double_correct','exact_current_text','next_step_fork','same_shape_mask'):x[key+'_worlds']=sum(r.get(key,0)>0 for r in rs)
                    paircounts.append(x)
            p=ROOT/f'local/test_{model}/{model}_s{seed}/results.jsonl'
            if p.exists():testrecords.extend(rows(p));operators.extend(rows(p.parent/'operator.jsonl'))
        p=ROOT/f'local/decoder_{model}/{model}_s42/paths.jsonl'
        if p.exists():paths.extend(rows(p))
    for p in sorted((ROOT/'local').rglob('*')):
        if p.is_file() and p.suffix not in ('.tmp',):allfiles.append(dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p)))
    dump(ROOT/'results/artifact_index.json',allfiles)
    cs=collapse(testrecords);b=[];c=[];e=[]
    for model in ('bart','t5gemma'):
        rs=[r for r in cs if r['model']==model and r['sequence_name']=='primary']
        for method in sorted({r['method_name'] for r in rs}):
            xs=[r for r in rs if r['method_name']==method]
            x=dict(model=model,method=method,n_worlds=len({r['world_id'] for r in xs}),n_seed_worlds=len(xs),editor_seeds=sorted({r['editor_seed'] for r in xs}))
            x.update({key:equal_seed_mean(xs,key) for key in ('C0','exact_preservation','R1','patch_norm','relative_patch_norm','other_operation_success')});b.append(x)
        for seq in ('primary','reordered'):
            for method in sorted({r['method_name'] for r in cs if r['model']==model and r['sequence_name']==seq and r.get('R5') is not None}):
                xs=[r for r in cs if r['model']==model and r['sequence_name']==seq and r['method_name']==method]
                x=dict(model=model,sequence=seq,method=method,n_worlds=len({r['world_id'] for r in xs}),n_seed_worlds=len(xs))
                x.update({key:equal_seed_mean(xs,key) for key in ('R1','R3','R5','C0','exact_preservation')})
                x['step_endpoints']=[sum(sum(r['step_successes'][i] for r in xs if r['editor_seed']==s)/sum(r['editor_seed']==s for r in xs) for s in sorted({r['editor_seed'] for r in xs}))/len({r['editor_seed'] for r in xs}) for i in range(5)]
                x['first_failure_distribution']=dict(sum((Counter(r['first_failure_distribution']) for r in xs),Counter()));c.append(x)
        lockpath=ROOT/f'results/{model}_method_lock.json'
        if not rs:modelstats.append(dict(model=model,method=None,n_worlds=0,n_seeds=0,estimate=None,ci95=None,p_raw=None,status='NOT_ESTIMABLE; no eligible independent-test intervention records'))
        if lockpath.exists() and rs:
            for mi,method_spec in enumerate(read(lockpath)['methods']):
                method=method_spec['name'];stats=clustered_difference([r for r in testrecords if r['model']==model],method,[f'random_{method}_{s}' for s in range(61001,61009)])
                if mi==0:modelstats.append(dict(model=model,method=method,**stats))
                for x in b:
                    if x['model']==model and x['method']==method:x.update(random_difference=stats['estimate'],random_difference_ci95=stats['ci95'],comparison_status='primary' if mi==0 else 'secondary exploratory')
        for seed in (42,43,44):
            for source in ('E→E','N→E','R→E'):
                for confidence in ('all','NLL_matched'):
                    xs=[r for r in rs if r['editor_seed']==seed and r['donor_source']==source and (confidence=='all' or r['confidence_matched_nll'])]
                    if lockpath.exists():xs=[r for r in xs if r['method_name']==read(lockpath)['methods'][0]['name']]
                    e.append(dict(model=model,editor_seed=seed,source=source,confidence_subset=confidence,n_worlds=len({r['world_id'] for r in xs}),C0=equal_seed_mean(xs,'C0'),R1=equal_seed_mean(xs,'R1'),R3=equal_seed_mean(xs,'R3'),R5=equal_seed_mean(xs,'R5'),status='executed' if xs else 'NA; no eligible primary-source records'))
    adjusted=holm([x['p_raw'] for x in modelstats])
    for x,p in zip(modelstats,adjusted):x['p_holm']=p
    d=[]
    for model,module in sorted({(r['model'],r['module']) for r in paths}):
        xs=[r for r in paths if r['model']==model and r['module']==module]
        x=dict(model=model,module=module,n_worlds=len(xs))
        for key in ('upstream_gain','blocked_gain_removed','offpath_gain_removed','inserted_gain','R_mediator_shift_norm','reverse_mediator_shift_norm'):x[key]=sum(r[key] for r in xs)/len(xs)
        d.append(x)
    for name,xs in [('table_A_pairs',paircounts),('table_B_methods',b),('table_C_rollouts',c),('table_D_paths',d),('table_E_subgroups',e),('operator_propagation',operators)]:
        write_csv(ROOT/f'results/{name}.csv',xs);dump(ROOT/f'results/{name}.json',xs);tables[name]=xs
    dump(ROOT/'results/primary_statistics.json',modelstats)
    for model in ('bart','t5gemma'):
        rs=[r for r in testrecords if r['model']==model and r['sequence_name']=='primary']
        lock=read(ROOT/f'results/{model}_method_lock.json') if (ROOT/f'results/{model}_method_lock.json').exists() else None
        if not lock or not lock.get('methods'):continue
        method=lock['methods'][0]['name']
        choices=[('recovery',lambda r:r['method_name']==method and r['R1']),('failure',lambda r:r['method_name']==method and (not r['R1'] or r.get('R5') is False)),('reverse_damage',lambda r:r['method_name']=='reverse_'+method and not r['R1'])]
        for tag,predicate in choices:
            candidates=sorted((r for r in rs if predicate(r)),key=lambda r:(r['world_id'],r['editor_seed']))
            if candidates:samples.append(dict(example_type=tag,**candidates[0]))
    jsonl(ROOT/'results/examples.jsonl',samples)
    ledger=read(ROOT/'results/job_ledger.json');sae=read(ROOT/'results/SAE_STATUS.json') if (ROOT/'results/SAE_STATUS.json').exists() else dict(status='MISSING')
    resources=[]
    for sub in ledger['submissions']:
        resources.append(dict(stage=sub['stage'],array_id=sub['job_id'],terminal=sub['terminal'],GPU_hours=sum(r['gpus']*r['elapsed_seconds']/3600 for r in sub['allocations']),states=dict(Counter(r['state'] for r in sub['allocations'])),indices=sub['indices']))
    write_csv(ROOT/'results/slurm_resources.csv',resources)
    smoke={}
    for model in ('bart','t5gemma'):
        p=ROOT/f'local/smoke_{model}/{model}_s42/complete.json'
        smoke[model]=read(p)['result'] if p.exists() else dict(passed=None,status='MISSING')
    dump(ROOT/'results/S0_ACCEPTANCE.json',smoke)
    operator_summary=[]
    for model in ('bart','t5gemma'):
        xs=[r for r in operators if r['model']==model]
        if xs:operator_summary.append(dict(model=model,n=len(xs),max_absolute_error=max(r['absolute_prediction_error_max'] for r in xs),max_relative_error=max(r['relative_prediction_error'] for r in xs),mean_read_fraction=sum(r['read_subspace_fraction'] for r in xs)/len(xs),mean_bias_norm=sum(r['bias_token_norm'] for r in xs)/len(xs)))
    text='# 当前同文本状态的后续编辑分叉：因果干预结果\n\n'
    text+='本实验固定时间领域、原已准入 P 编辑器、三 seed42/43/44。冻结模型为 facebook/bart-base FP32 与原版 google/t5gemma-2b-2b-ul2-it BF16。所有数值来自已执行产物；未执行项为 NA/MISSING。来源、操作与有限候选池限制保留，局部 donor-assisted 干预不构成无 donor 部署算法或唯一完整 causal circuit。\n\n'
    text+='协议与数据在独立 test 干预之前锁定。按 world 哈希划分、跨 seed 共同分组；96 个原训练 worlds 全排除，固定候选池256（旧 dev24、旧 test32、新200），不为凑数继续搜索。primary 为当前 state0 的 plus，每 world 一对，固定 E→E/N→E/R→E 优先级；本轮独立 test 只取新 worlds，少于40 world 时标探索性。模板0为 IID；机制 held-out 不称模板 OOD。旧测试只用于资格/发现，不能复称独立确认。\n\n'
    text+='S0（见 results/S0_ACCEPTANCE.json）：'+', '.join(f'{m} passed={v.get("passed")}, worlds={v.get("worlds","NA")}' for m,v in smoke.items())+'。无干预当前/下一步 token 与原路径一致；no-op/self/alpha0 logits 精确相等、encoder forward0、padding不参与patch、hook退出移除、use_cache=False。Full donor仅是正对照；每个正式 pair 又核验 full/good 下一步及轨迹相等。\n\n'
    text+='表 A 的完整分母和排除原因在 CSV/JSON（history组合计数与 world计数分列）。E→E 没有合格 donor 时不制造配对；N、R 标签分别保存，即便同文本 reencode 与 N 实际数值相同。\n\n'+mdtable(paircounts,['model','editor_seed','split','original_split','source','operation','scanned_worlds','current_double_correct','exact_current_text','next_step_fork','same_shape_mask','final_pair_worlds'])+'\n'
    text+='表 B（seed 等权均值；8随机 seed先在同world/编辑器seed内平均，随机方向不算独立样本）。R1=C0且一步joint正确；保留当前exact、范数和随机比较。\n\n'+mdtable(b,['model','method','n_worlds','n_seed_worlds','C0','exact_preservation','R1','random_difference','random_difference_ci95','patch_norm','relative_patch_norm'])+'\n'
    text+='主比较统计：10,000次共同world-cluster percentile bootstrap，保持该world全部seed/方法关联；双侧符号翻转的对称/可交换假设单列，不是随机分配试验精确p值。两个模型的辅助p值按Holm校正；R3/R5、置信度/来源为次要探索性。\n\n'+mdtable(modelstats,['model','method','n_worlds','n_seeds','estimate','ci95','p_raw','p_holm'])+'\n'
    text+='表 C：只在t=0修补一次，之后只传递latent，用原T和未干预D。Gold由world状态机预先给定，两条合法5步序列分别为plus/minus/plus/minus/plus及plus/plus/minus/minus/plus；完整R3/R5不以最终endpoint替代。Good真实长链上限保留。\n\n'+mdtable(c,['model','sequence','method','n_worlds','R1','R3','R5','step_endpoints','first_failure_distribution'])+'\n'
    text+='反向干预见表B reverse行及逐例current保持、一步损伤；它只能描述候选成分的相反行为，不把一般损伤视为特异性。其他操作保持若未单列执行为NA。\n\n'
    text+='仿射传播为 row delta + delta VᵀUᵀ；实际forward保留bias、mask和dtype casts。FP32数值误差与BF16舍入误差如下，bias绝对量级不从差分抵消推断无作用。\n\n'+mdtable(operator_summary,['model','n','max_absolute_error','max_relative_error','mean_read_fraction','mean_bias_norm'])+'\n'
    text+='表 D：固定相同gold前缀第一语义分叉token的连续margin。候选mediator来自对bad做上游修补的R路径。模块位置、粗筛、最多3模块、rank4共享discovery子空间、自patch验收及B/R/阻断/插入/off-path/reverse均在decoder文件。辅助结果仅支持readout效应和candidate路径证据，未执行自由生成decoder patch；不能称latent修复或唯一完整电路。未过validation gate则该项NA。\n\n'+mdtable(d,['model','module','n_worlds','upstream_gain','blocked_gain_removed','offpath_gain_removed','inserted_gain'])+'\n'
    text+='表 E：实际 seed/来源/NLL匹配子集（margin因多token候选不硬套阈值，NLL≤0.1 nat锁定）；缺来源为NA而非0恢复率。\n\n'+mdtable(e,['model','editor_seed','source','confidence_subset','n_worlds','C0','R1','R3','R5','status'])+'\n'
    text+=f'SAE：{sae["status"]}。{sae.get("reason","")} 核心test前决策；不重新训练backbone或原编辑器。空间/其他领域未扩展。\n\n'
    text+='实际Slurm资源：\n\n'+mdtable(resources,['stage','array_id','terminal','GPU_hours','states'])+'\n'
    text+=f'总 allocation GPU-hours={ledger["gpu_hours"]:.6f}，allocation起止事件重建最大并发={ledger["maximum_concurrent_gpus"]} GPU，上限40 GPU-hours/2 GPU。失败、smoke与重试均计费，不重复加.batch/step。残留未终态数组：{[s["job_id"] for s in ledger["submissions"] if not s["terminal"]]}。Peak显存见每任务complete.resources，模型、数据、checkpoint、日志与完整结果hash见artifact_index/run_manifest。\n\n'
    text+='结论标签按实际表现：上游仅恢复一步为 operation-specific one-step compatibility repair；一次上游patch若提升所测完整长链为 observed multi-step recoverability improvement，仅限所测序列/分布；decoder单独patch为 readout repair。阴性/区间重叠不证明相等。少量成功、失败与reverse反例按固定world排序抽取于examples.jsonl，不能代替聚合。\n'
    (ROOT/'CAUSAL_NEXT_EDIT_STABILITY_V1_REPORT.md').write_text(text)
    dump(ROOT/'results/summary.json',dict(statistics=modelstats,resources=resources,total_gpu_hours=ledger['gpu_hours'],maximum_concurrent_gpus=ledger['maximum_concurrent_gpus'],operator_summary=operator_summary,SAE=sae))
    summary=dict(statistics=modelstats,gpu_hours=ledger['gpu_hours'])
    print(json.dumps(summary,ensure_ascii=False));return summary

if __name__=='__main__':aggregate()
