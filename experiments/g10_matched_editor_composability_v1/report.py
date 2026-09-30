"""Render the final G10 report from the locked tables and audit."""
import csv,json
from g10_common import *
def tab(rows,cols):
 head='|'+'|'.join(cols)+'|\n|'+'|'.join(['---']*len(cols))+'|\n'
 return head+''.join('|'+'|'.join(str(r.get(c,'')) for c in cols)+'|\n' for r in rows)
def pct(v):return 'N/A' if v is None or v=='' else f'{100*float(v):.1f}%'
def main():
 cmp=list(csv.DictReader((ROOT/'evaluation/per_editor_composition.csv').open()));frag=list(csv.DictReader((ROOT/'evaluation/fragility_summary.csv').open()));assoc=json.loads((ROOT/'evaluation/association.json').read_text()) if (ROOT/'evaluation/association.json').exists() else list(csv.DictReader((ROOT/'evaluation/association.csv').open()))
 gates={}
 for x in csv.DictReader((ROOT/'evaluation/matching_gate.csv').open()):gates.setdefault(x['editor'],{})[x['split']]=f"{x['joint_success']}/{x['N']}"
 iid=[x for x in cmp if x['split']=='composition_iid']; ood={x['editor']:x for x in cmp if x['split']=='composition_template_ood'}
 main_rows=[]
 for x in iid:
  y=ood[x['editor']]
  main_rows.append(dict(editor=x['editor'],gate_pass=x['gate_pass'],dev_iid=gates.get(x['editor'],{}).get('match_iid',''),dev_ood=gates.get(x['editor'],{}).get('match_template_ood',''),
    iid_step1=pct(x['step1_rate']),ood_step1=pct(y['step1_rate']),iid_steps3to5=pct(x['steps3to5_endpoint_mean']),ood_steps3to5=pct(y['steps3to5_endpoint_mean']),
    iid_step3=pct(x['step3_rate']),iid_step4=pct(x['step4_rate']),iid_step5=pct(x['step5_rate']),iid_full5=pct(x['trajectory_through_5_rate']),ood_full5=pct(y['trajectory_through_5_rate']),
    iid_unresolved=x['unresolved'],ood_unresolved=y['unresolved'],iid_nondate_errors=x['confirmed_nondate_errors'],ood_nondate_errors=y['confirmed_nondate_errors']))
 assoc_rows=assoc if isinstance(assoc,list) else []
 primary=next((x for x in assoc_rows if x['split']=='combined' and x['outcome']=='steps3to5_endpoint_mean'),None)
 rho='not estimated' if primary is None else f"Spearman rho={float(primary['spearman_rho']):.3f}, descriptive p={float(primary['nominal_two_sided_p']):.3f} (n={primary['n_editors']})"
 rho_ci=json.loads((ROOT/'evaluation/association_world_bootstrap.json').read_text())[0]['ci95']
 lines=['# G10: Matched Editor Composability','', '**结果：本轮没有发现 decoder-directional fragility 能稳定预测长期组合成功。** 八个通过单步 dev gate 的编辑器在新 IID 上单步均为100%，但 3–5 步平均 endpoint success 仅0–19.6%，五步完整轨迹均为0%；合并 IID/OOD 的 fragility 相关为 '+rho+f"；按世界 bootstrap 的区间为 {rho_ci}，且不包含训练随机性。方向脆弱性不支持作为本样本中的可靠预测量。",'', '实验只重复独立T+算子。rank8_seed43因dev IID为75/80（93.75%）未达到预先规定的匹配门槛，仍报告单步确认集结果，不纳入匹配相关分析。Joint-rank16历史结果只说明联合任务可学，不能说明独立算子已经可组合。','', '## 候选匹配与单步、长程结果','', '开发匹配世界用于预先固定保留集合；确认集是另一批全新世界。3–5 endpoint是第3、4、5步成功率的平均；完整轨迹通过率要求从第一步至该步每一步全部joint成功。各比率分母均为每层80个固定世界。','',tab(main_rows,['editor','gate_pass','dev_iid','dev_ood','iid_step1','ood_step1','iid_steps3to5','ood_steps3to5','iid_step3','iid_step4','iid_step5','iid_full5','ood_full5','iid_unresolved','ood_unresolved','iid_nondate_errors','ood_nondate_errors']), '各步原始判定及输出见evaluation/per_step_raw.csv和outputs目录；被dev gate排除者没有长链分数。','', '## Fragility与重复稳定性','', '主fragility为step1的G8 editor-forward content/structure failure area，减去两种orthogonal random control area均值。在alpha 0..2上对粗网格梯形积分；不是首次失败半径。负值表示编辑方向比随机方向更少破坏内容/结构。','',tab([{**x,**{k:f"{float(x[k]):.4f}" for k in ['editor_forward_content_failure_area','radial_orthogonal_random_content_failure_area','editor_orthogonal_random_content_failure_area','excess_forward_failure_area']}} for x in frag if x['split']=='composition_iid' and x['step']=='1'],['editor','N','editor_forward_content_failure_area','radial_orthogonal_random_content_failure_area','editor_orthogonal_random_content_failure_area','excess_forward_failure_area']), 'combined editor-level Spearman ρ为正但弱，方向与“越脆弱、越不稳定”的预测相反；n=8，不能据此确认反向关系。IID-only ρ=0.268（p=.520），OOD-only ρ=0.399（p=.328）。这些小样本描述值不支持有预测关联。','', '五方向、step1–4、逐alpha输出、next gold corridor、fact/structure和两轮半径细化见evaluation/success_vs_alpha.csv与basin/scan_*.jsonl；图见evaluation/success_vs_alpha.svg。','', '## 表示漂移、residual dynamics与失败模式','', '逐步pooled/token drift、residual norm、相邻residual cosine及语义评分见evaluation/per_step_raw.csv。大部分失败从第三步开始；未决计入固定分母但不称为已确认语义错误。当前结果显示rank16_seed42、rank8_seed42和rank32_seed44的IID步骤3–5 endpoint均值相对较高，但五步轨迹仍全部失败，不能称稳定。便利案例见review/stable_unstable_trajectories.json；未做真人审核。','', '## Joint-rank16 历史任务对照','', '既有T5Gemma IT Joint-rank16 seed42在独立参考系联合任务集IID与template-OOD均80/80 endpoint joint，且无未决/非日期错误。该结果支持一次性联合转换可学习；它不属于本轮匹配面板，也不能证明独立T+算子可重复组合。记录锚点为[`529fb6b`](https://github.com/TTtianTT/encrypted_semantic_editing_pilot/commit/529fb6b)。','', '## 训练、资源与结论边界','', '九个候选均从新初始化训练200更新，使用同一个G3 T+来源日程、3200训练样本及固定1600个两阶段替换出现。rank8/16/32单算子参数量分别为13,056 / 25,344 / 49,920；监督token数、算子耗时和峰值显存见training/rank*.json及checkpoint元数据。GPU累计分配4,399秒（1.22 GPU小时，包含失败尝试），最大并发2张；分项见budget.json。本轮未跑正则变体或T5Gemma。','', '这些结果直接测量的是冻结BART-base、受控模板、T+最多五次、seed42/43/44下的关联。它们不证明方向脆弱性无预测价值，也不证明rank或seed无关；编辑器样本最多8个，且每个seed单次训练。没有真人审核，不可泛化到自然文本或其他骨干。','', '## 复现与文件','', '协议与命令见PROTOCOL.md、README.md、commands.log。世界、代码、模型、训练、dev gate、测试输出与方向扫描均有hash；运行`.venv/bin/python experiments/g10_matched_editor_composability_v1/audit.py`可复核数据和产物。基础模型保持只读。']
 geo=list(csv.DictReader((ROOT/'evaluation/geometry_summary.csv').open())); retained={x['editor'] for x in cmp if x['gate_pass']=='True'}; geo_rows=[]
 for split in ['composition_iid','composition_template_ood']:
  for step in range(1,6):
   vals=[x for x in geo if x['editor'] in retained and x['split']==split and int(x['step'])==step]
   if vals:geo_rows.append(dict(split=split,step=step,editors=len(vals),**{k:f"{sum(float(x[k]) for x in vals if x.get(k,'')!='')/sum(x.get(k,'')!='' for x in vals):.4f}" for k in ['pooled_l2','token_l2','residual_norm','residual_previous_cosine'] if any(x.get(k,'')!='' for x in vals)}))
 i=lines.index('## 表示漂移、residual dynamics与失败模式');lines[i:i]=['## 表示漂移与残差动态','', '下表按通过匹配门槛的编辑器先求 editor-level 均值，再跨编辑器平均；保留集合与每编辑器每步数据见evaluation/geometry_summary.csv。step1的相邻residual cosine为空，因为没有前一步残差。', '', tab(geo_rows,['split','step','editors','pooled_l2','token_l2','residual_norm','residual_previous_cosine']), '这些是诊断量，与结构化联合成功率分开解释。逐条输出与完整编辑器层记录在evaluation/per_step_raw.csv。', '']
 (ROOT/'REPORT.md').write_text('\n'.join(lines)+'\n');print('REPORT.md written')
if __name__=='__main__':main()
