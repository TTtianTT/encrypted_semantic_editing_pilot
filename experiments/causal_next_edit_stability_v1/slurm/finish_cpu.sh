#!/usr/bin/env bash
set -euo pipefail
: "${SLURM_JOB_ID:?CPU aggregation must use Slurm}"
: "${SLURM_STEP_ID:?CPU aggregation must use srun}"
python - <<'PY'
import os,sys
from collections import defaultdict,Counter
from experiments.causal_next_edit_stability_v1.common import ROOT,SOURCE,read,rows,dump,jsonl
from experiments.causal_next_edit_stability_v1.aggregate import collapse,equal_seed_mean,write_csv,mdtable
from experiments.causal_next_edit_stability_v1.metrics import clustered_difference
import numpy as np
sys.path.insert(0,str(SOURCE))
from semantics import gold
assert read(ROOT/'configs/aggregate_cpu.json')['gpus']==0
assert read(ROOT/'results/descriptive_analysis_lock.json')['test_intervention_results_read_when_locked'] is False
rs=[];operators=[];confidence=[]
for model in ('bart','t5gemma'):
    for seed in (42,43,44):
        path=ROOT/f'local/test_{model}/{model}_s{seed}/results.jsonl'
        if path.exists():rs.extend(rows(path));operators.extend(rows(path.parent/'operator.jsonl'))
        pairfile=ROOT/f'local/scan_{model}/{model}_s{seed}/pairs.jsonl'
        if pairfile.exists():
            groups=defaultdict(list)
            for r in rows(pairfile):groups[(r['split'],r['original_split'],r['donor_source'],r['operation'])].append(r)
            for (split,old,source,op),xs in groups.items():
                delta=[abs(r['good_current']['token_mean_nll']-r['bad_current']['token_mean_nll']) for r in xs]
                matched=sum(r['confidence_matched_nll'] for r in xs)
                confidence.append(dict(model=model,editor_seed=seed,split=split,original_split=old,source=source,operation=op,n_pairs=len(xs),n_worlds=len({r['world_id'] for r in xs}),NLL_matched=matched,NLL_discarded=len(xs)-matched,NLL_discard_fraction=1-matched/len(xs),mean_abs_NLL_difference=float(np.mean(delta)),max_abs_NLL_difference=max(delta),good_mean_entropy=float(np.mean([r['good_current']['mean_entropy'] for r in xs])),bad_mean_entropy=float(np.mean([r['bad_current']['mean_entropy'] for r in xs])),margin_threshold='NA; preregistered NLL-only subset'))
cs=collapse(rs);byseed=[];chains=[]
for key in sorted({(r['model'],r['editor_seed'],r['method_name']) for r in cs if r['sequence_name']=='primary'}):
    model,seed,method=key;xs=[r for r in cs if (r['model'],r['editor_seed'],r['method_name'],r['sequence_name'])==(*key,'primary')]
    entry=dict(model=model,editor_seed=seed,method=method,n_worlds=len(xs))
    entry.update({k:equal_seed_mean(xs,k) for k in ('C0','exact_preservation','R1','patch_norm','relative_patch_norm','other_operation_success')})
    entry['C1']=sum(r['step_successes'][0] for r in xs)/len(xs);byseed.append(entry)
for key in sorted({(r['model'],r['editor_seed'],r['sequence_name'],r['method_name']) for r in cs if r['R5'] is not None}):
    model,seed,seq,method=key;xs=[r for r in cs if (r['model'],r['editor_seed'],r['sequence_name'],r['method_name'])==key]
    entry=dict(model=model,editor_seed=seed,sequence=seq,method=method,n_worlds=len(xs))
    entry.update({k:equal_seed_mean(xs,k) for k in ('C0','exact_preservation','R1','R3','R5')})
    entry['step_endpoints']=[sum(r['step_successes'][i] for r in xs)/len(xs) for i in range(5)]
    entry['first_failure_distribution']=dict(sum((Counter(r['first_failure_distribution']) for r in xs),Counter()));chains.append(entry)
for name,xs in [('table_B_by_seed',byseed),('table_C_by_seed',chains),('confidence_audit',confidence)]:
    write_csv(ROOT/f'results/{name}.csv',xs);dump(ROOT/f'results/{name}.json',xs)
longstats=[]
for model in ('bart','t5gemma'):
    methods=read(ROOT/f'results/{model}_method_lock.json').get('methods',[])
    if not methods:continue
    method=methods[0]['name']
    for seq in ('primary','reordered'):
        for endpoint in ('R3','R5'):
            xs=[dict(r,R1=r[endpoint],sequence_name='primary') for r in rs if r['model']==model and r['sequence_name']==seq and r[endpoint] is not None]
            stats=clustered_difference(xs,method,[f'random_{method}_{s}' for s in range(61001,61009)])
            stats.pop('p_raw',None)
            longstats.append(dict(model=model,sequence=seq,endpoint=endpoint,method=method,interpretation='secondary exploratory world-cluster CI; no additional confirmatory p-value',**stats))
dump(ROOT/'results/secondary_rollout_statistics.json',longstats)
relations=[]
for phase in ('discovery','test'):
    for seed in (42,43,44):
        base=ROOT/f'local/{phase}_bart/bart_s{seed}';p=base/'operator.jsonl'
        if not p.exists():continue
        outcome={r['world_id']:r['R1'] for r in rows(base/'results.jsonl') if r['sequence_name']=='primary' and r['method_name']==read(ROOT/'results/bart_method_lock.json')['methods'][0]['name']}
        for metric in read(ROOT/'results/descriptive_analysis_lock.json')['operator_relation_metrics']:
            xs=[r for r in rows(p) if r['world_id'] in outcome]
            a=np.array([r[metric] for r in xs]);b=np.array([outcome[r['world_id']] for r in xs],dtype=float)
            estimable=len(xs)>2 and np.std(a)>1e-12 and np.std(b)>1e-12
            relations.append(dict(phase=phase,editor_seed=seed,metric=metric,n_worlds=len(xs),Pearson_R1=float(np.corrcoef(a,b)[0,1]) if estimable else None,status='descriptive correlation; not causation' if estimable else 'NA; constant outcome or predictor'))
dump(ROOT/'results/operator_relations.json',relations)
pathfile=ROOT/'local/decoder_bart/bart_s42/paths.jsonl'
if pathfile.exists():
    registry={r['pair_id']:r for r in rows(ROOT/'local/scan_bart/bart_s42/pairs.jsonl')}
    normalized=[]
    for r in rows(pathfile):
        pair=registry[r['pair_id']]
        meta={k:v for k,v in pair.items() if k not in ('world','state_path','donor_next','recipient_next')}
        meta.update(r);meta.update(job_id=read(pathfile.parent/'complete.json')['result']['resources']['job_id'],C0=None,exact_preservation=None,R1=None,R3=None,R5=None,step_successes=None,first_failure=None,operation_sequence=[pair['operation']],gold_states=[gold(pair['world'],pair['gold_next_state'],pair['template'])],target_score=r['R'],walltime=read(pathfile.parent/'complete.json')['result']['resources']['wall_seconds'],failure_reason='NA; this auxiliary record measures teacher-forced score, not freely generated joint success',intervention_spec='B/R full-module mediator block/insert/off-path/reverse plus separately labelled rank4 readout refinement; fixed gold prefix',alpha=1,effective_rank=None,patched_positions=[r['prefix_position']],patch_norm=r['R_mediator_shift_norm'],patch_norm_interpretation='full R-minus-B mediator change at the selected decoder query position; not upstream patch norm')
        normalized.append(meta)
    jsonl(ROOT/'results/decoder_path_sample_records.jsonl',normalized)
examples=rows(ROOT/'results/examples.jsonl');method=read(ROOT/'results/bart_method_lock.json')['methods'][0]['name']
secondary=read(ROOT/'results/bart_method_lock.json')['methods'][1]['name']
for tag,predicate in [('locked_secondary_no_recovery',lambda r:r['method_name']==secondary and not r['R1']),('matched_random_current_damage',lambda r:r['method_name'].startswith('random_'+method+'_') and not r['C0']),('donor_long_chain_failure',lambda r:r['method_name']=='good' and r['R5'] is False)]:
    xs=sorted((r for r in rs if r['sequence_name']=='primary' and predicate(r)),key=lambda r:(r['world_id'],r['editor_seed'],r['method_name']))
    if xs:examples.append(dict(example_type=tag,**xs[0]))
jsonl(ROOT/'results/examples.jsonl',examples)
summary=read(ROOT/'results/summary.json');B=read(ROOT/'results/table_B_methods.json');C=read(ROOT/'results/table_C_rollouts.json');D=read(ROOT/'results/table_D_paths.json')
main=next(r for r in B if r['model']=='bart' and r['method']==method);reverse=next(r for r in B if r['model']=='bart' and r['method']=='reverse_'+method)
text='\n\n## 十项验收回答与解释边界\n\n'
text+='1. BART每个seed固定扫描256个world，N→E与R→E的plus/minus均有256个合格world，E→E为0；primary每world仅取固定优先级的一对N→E。独立测试每seed仅取80个新world，三seed共用相同world簇，不计作240个独立world。T5Gemma每seed同样扫描256个world，严格规则下合格配对为0；其下一步修补指标为NA。原始分母和逐项排除计数见表A，不能将配对内恢复率称为候选池整体成功率提升。\n\n'
text+='2. 两模型16-world S0全部通过；无干预当前/下一步greedy IDs与原路径相等，no-op/self/alpha0 logits max/mean差0，encoder调用0，full donor复现donor一步，hook退出移除，padding不参与统计，诊断关闭KV cache。正式每world再复核资格与full-donor轨迹。未使用TransformerLens转换。\n\n'
text+=f'3. 锁定{method}的独立C0={main["C0"]:.2%}，当前exact={main["exact_preservation"]:.2%}，R1={main["R1"]:.2%}；相对8-seed同维同有效位置同Frobenius范数随机均值差={main["random_difference"]:.4f}，95%CI={main["random_difference_ci95"]}。同一对donor-minus-bad的共享4维方向逐memory token投影，不是4个token，也不是已命名语义特征。第二个锁定方法保留于表B及by-seed表，未按test效果更换方法。\n\n'
text+=f'4. 在Good上反向去除同一候选成分后，C0={reverse["C0"]:.2%}，R1={reverse["R1"]:.2%}。只有保持当前位置而损伤下一步的部分支持操作相关兼容性解释；token-span反向对照在discovery造成当前语义破坏，不能用作特异机制证据。随机控制的C0/C1均另报，不能隐去其一般损伤。\n\n'
text+='5. 真实编辑器是逐token仿射残差：T(h)=h+U(Vh)+b，有效位置mask后转回原dtype。差分用Delta+Delta VᵀUᵀ预测；FP32误差与BF16输出舍入误差分开列于operator表。Bias改变绝对状态，绝对读取/写入投影与bias对齐另存，不能由差分抵消宣称bias无用。关系诊断先于结果锁定定义；结果无变化时相关系数为NA，而不是零因果效应。\n\n'
text+='6. 路径诊断只在32个discovery world的固定gold共同前缀测第一语义分叉token margin。R的mediator来自修补Bad后的运行。最后一层cross-attention输出阻断/回填呈对应score变化；最后一层residual紧邻logits，完整替换的强作用本身不能识别独特语义路径。off-path维数和位置相同，但实际扰动范数不同，控制不足以证明唯一特异性。未执行decoder activation patch自由生成，因而这里报告teacher-forced读出效应/candidate causal mechanism，不宣称已证明输出恢复或完整causal circuit。\n\n'
text+='7. 所有长链只在t=0干预一次，后续不补donor、不重编码。以下完整R3/R5及Good上限与随机控制同时展示；各步endpoint、首次失败及错误分解另表，不能用末步偶然正确替代全链正确。\n\n'
text+=mdtable([r for r in C if r['method'] in ('bad','good','full',method,'random_'+method+'_8seed_mean')],['sequence','method','R1','R3','R5','step_endpoints'])+'\n'
improved=any(r['method']==method and (r['R3']>0 or r['R5']>0) for r in C)
text+=('在所测序列观察到完整多步改善，可使用observed multi-step recoverability improvement，范围限于这些序列与IID新world。' if improved else '没有观察到完整R3/R5改善；结论仅为operation-specific one-step compatibility repair，不称长期稳定修复。')+'\n\n'
text+='8. 三个可用编辑器seed均分开报告，等权seed均值不是训练随机性总体区间。N与一次R在全部256world×3seed的good/bad/mask逐元素相同；primary仅运行N，不将R视为独立机制复现。置信度NLL≤0.1 nat的保留数/弃样比例见confidence_audit，主test子集保留数见表E；多token完整候选margin阈值未被套用。T5Gemma工具等价性通过，但原始文本尾部空格/换行使N/R→E排除，不能作为科学反例。模板0为IID；没有模板OOD、跨领域或更丰富历史的确认。\n\n'
text+='9. SAE在test解封前已标SKIPPED：T5Gemma没有合格配对，双模型discovery/validation前置条件未满足；没有SAE训练或追加字典搜索。Backbone和原编辑器始终冻结。\n\n'
text+='10. 已执行S0/S1双模型三seed扫描，BART discovery/validation、discovery decoder路径、三seed锁定独立轨迹；T5Gemma无合格pair的S2–S4为NOT ESTIMABLE，SAE/额外领域为SKIPPED。Slurm拒绝增加运行中任务时限而允许pending子任务增加，真实返回码与子任务时限见ledger。若发生TIMEOUT，失败allocation与同配置缺失world恢复均累计GPU-hours；无需重做已完成world。总GPU-hours、峰值并发、全部终态以最终sacct刷新表为准；所有GPU通过唯一sbatch入口和srun。\n\n'
text+='主比较经验bootstrap在全一/全零样本上可能退化为零宽区间，这不表示总体无不确定性。仅3个固定编辑器seed、有限语法world及有特权good donor，不能推出通用语义feature、唯一circuit或无donor部署修复。\n\n'
text+='逐seed主方法表：\n\n'+mdtable([r for r in byseed if r['method'] in (method,'random_'+method+'_8seed_mean','reverse_'+method,'good')],['editor_seed','method','n_worlds','C0','C1','R1','exact_preservation'])+'\n'
text+='次要探索性长链差值的10,000次world-cluster CI：\n\n'+mdtable(longstats,['sequence','endpoint','n_worlds','estimate','ci95'])+'\n'
path=ROOT/'CAUSAL_NEXT_EDIT_STABILITY_V1_REPORT.md';path.write_text(path.read_text()+text)
dump(ROOT/'results/descriptive_completion.json',dict(passed=True,job_id=os.environ['SLURM_JOB_ID'],independent_raw_records=len(rs),new_interventions=False,extra_training=False,tables=['table_B_by_seed','table_C_by_seed','confidence_audit','operator_relations','secondary_rollout_statistics'],interpretation='descriptive analyses specified before test results were read'))
print(dict(descriptive_tables_complete=True,records=len(rs)))
PY
