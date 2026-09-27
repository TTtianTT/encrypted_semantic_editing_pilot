"""Render fixed supplemental measurements; does not train or select models."""
import json,statistics
from pathlib import Path
R=Path(__file__).resolve().parents[1];P=R/'experiments/latent_consistency_v1';O=P/'results'
def read(p):return json.load(open(p))
def main():
 b=read(O/'B_summary.json');bs=read(O/'B_paired_statistics.json');a=read(O/'A_summary.json');ast=read(O/'A_paired_statistics.json');fits=read(O/'B_frozen.json')['runs'];shifts=read(O/'Shift_frozen.json')['runs']
 lines=['# 一致性约束与 Shift 收敛补充实验','',
 '本轮已完成四组 B 配对训练（seed42）及 Shift 三 seed 从1000到5000步的延长训练、全部生成与源句配对统计。作业1619由 sbatch/srun 使用1张B300、4 CPU执行；未新增HE实验。原测试集已看过，本轮属于固定配置的事后分析，不是新的封存验证。尚未人工核验。','',
 '结论：目标编码一致性降低了所定义的表示误差，但对连续组合的任务成功率产生相反方向的结果；不支持“加入该约束普遍改善组合”的主张。Shift在5000步仍未达到预登记近平台标准，原结论必须限定为既定训练预算下的落后，不能宣称已收敛的固定方向存在性能上限。','',
 '## 固定协议与可比性','',
 '同一冻结BART-base（revision aadd2ab0ae0c8268c7c9693540e9904811f36177）、token memory 96×768、mask、原StylePTB划分、rank64与greedy解码。B每个配对训练臂均600更新、batch8、AdamW lr0.001、clip1、同初始化和采样日程。原基本操作CE或0.5基本操作CE+0.5已见组合CE保持不变；只加入λ=0.1的一致性，λ=0也计算同一目标编码与损失，使配对计算步骤一致。参数量每组297216，无新可训练参数。实际耗时有初始化/缓存等波动，不要求墙钟恰好相等。','',
 '一致性为停止梯度的E(目标句)有效token按归一化位置线性插值到源有效长度后，与编辑memory计算目标能量归一化MSE。padding不计入。它不是语义词对齐，尤其语态转换可能重排词序；结果仅适用于这个预先固定的最小实现。λ不搜索，所有B模型取600步最终权重。future+passive组合未用于训练或选参，seen-combo仅为present+passive。','',
 '目标只进入训练监督和生成完成后的离线残差评分，不进入生成、测试编辑或解码指令；共享E/G被冻结且梯度能回到编辑器。一致性梯度、padding及停止梯度检查见results/smoke.json；初始化和采样日程hash见results/B_frozen.json。文件hash见provenance.json。','',
 '## 连续组合结果','',
 '全部为同一100个未见源组。Joint_auto为future与passive同时达成、固定内容检查通过且输出有效；不剔除失败。下表单seed，不能称稳定可复现。','',
 '| 训练设置 | λ | 路径 | Joint_auto | 内容auto | future | passive | chrF | 精确参考 |','|---|---:|---|---:|---:|---:|---:|---:|---:|']
 for x in b:
  if x['path']=='single_passive':continue
  lines.append(f"| {x['context']} | {x['lambda']} | {x['path']} | {x['joint_n']}/100 | {x['content_auto']:.0%} | {x['future_auto']:.0%} | {x['passive_auto']:.0%} | {x['reference_chrf']:.2f} | {x['exact_reference']:.0%} |")
 lines+=['','λ=0.1减λ=0，2000次源组paired bootstrap的百分点差及95%区间（多个探索比较，未作多重校正）：','']
 for k,v in bs.items():
  x=v['Joint_auto'];c=v['content_auto'];lines.append(f"- {k}：Joint_auto {x['difference_pp']:+.2f}pp [{x['CI95_pp'][0]:.2f}, {x['CI95_pp'][1]:.2f}]；内容auto {c['difference_pp']:+.2f}pp。")
 lines+=['','单步passive与连续两步的内容auto差（单步减两步，正值为增加漂移）：','', '| 设置 | λ | 单步内容auto | 连续内容auto | 增加漂移 | 目标memory误差 | 再编码残差 |','|---|---:|---:|---:|---:|---:|---:|']
 for x in b:
  if x['path']!='latent_once':continue
  single=next(v for v in b if v['context']==x['context'] and v['lambda']==x['lambda'] and v['path']=='single_passive')
  lines.append(f"| {x['context']} | {x['lambda']} | {single['content_auto']:.0%} | {x['content_auto']:.0%} | {x['additional_content_drop_pp']:.1f}pp | {x['target_memory_error_offline']:.3f} | {x['reencode_memory_error_offline']:.3f} |")
 lines+=['','开发集 CE / 一致性误差：','', '| 设置 | 训练秒数 | future | present | passive | 已见组合 |','|---|---:|---:|---:|---:|---:|']
 for x in fits:lines.append('| '+x['name']+f" | {x['training_wall_s']:.2f} | "+' | '.join(f"{x['dev'][k]['CE']:.4f} / {x['dev'][k]['consistency']:.4f}" for k in ['future','present','passive','seen_combo'])+' |')
 lines+=['','误差变小不等于事实保留改善。已有组合监督时，一致性可与生成CE目标冲突；位置插值及固定权重也可能影响结果，本次消融不能区分这些解释。原内容自动规则对合法辅助词变化、NER与角色解析有误判，原B官方参考仅约52%通过内容检查；这些缺陷未在本轮调阈值掩盖。有效性规则只覆盖空输出、EOS、重复等，不能当成流畅性已验证。','',
 '## Shift 收敛检查','',
 '恢复原1000步checkpoint的Adam动量与连续采样日程，同样5k训练/363开发及lr、batch，三seed各继续到5000步；每200步开发NLL，按开发NLL选best，不按测试调整。预登记标准为3000→4000、4000→5000两个窗口相对下降均不超过1%；这也仅代表窗口近平台，不是最优性证明。','',
 '| seed | 1000步NLL | 3000步 | 4000步 | 5000步 | 两窗口相对下降 | best步 | 近平台 |','|---:|---:|---:|---:|---:|---|---:|---|']
 for x in shifts:
  c={v['step']:v['dev_token_loss'] for v in x['history']}
  lines.append(f"| {x['seed']} | {c[1000]:.6f} | {c[3000]:.6f} | {c[4000]:.6f} | {c[5000]:.6f} | "+' / '.join(f'{v:.2%}' for v in x['last_two_1000_step_relative_improvements'])+f" | {x['best_step']} | {x['near_plateau_by_preregistered_rule']} |")
 lines+=['','完整曲线及末次梯度、参数更新量见results/Shift_learning_curves.csv；未将“梯度非零”误作未收敛的唯一证据。','', '| 方法 | seed42 | seed43 | seed44 | 平均Joint_auto | seed标准差 | 平均内容auto |','|---|---:|---:|---:|---:|---:|---:|']
 for name in ['shift_1000','shift_extended','lowrank_1000_budget']:
  rr=[x for x in a if x['method']==name];lines.append('| '+name+' | '+' | '.join(f"{x['joint_n']}/364" for x in rr)+f" | {statistics.mean(x['Joint_auto'] for x in rr):.2%} | {statistics.stdev(x['Joint_auto'] for x in rr)*100:.2f}pp | {statistics.mean(x['content_auto'] for x in rr):.2%} |")
 lines+=['','先同一源句内平均三seed的配对差，再对364源句做2000次bootstrap：','']
 for k,v in ast.items():
  x=v['Joint_auto'];lines.append(f"- {k}：{x['difference_pp']:+.2f}pp，95%区间[{x['CI95_pp'][0]:.2f}, {x['CI95_pp'][1]:.2f}]；逐seed差="+', '.join(f'{v:+.2f}' for v in x['per_seed_difference_pp'])+'pp。')
 lines+=['','**低秩1000步与Shift5000步属于不等预算诊断**，不替换原同预算主表。区间主要反映固定训练结果下测试源句的不确定性，不覆盖评估器系统误差或广泛训练随机性。只报告预算内结果；5000步仍下降时不能排除进一步训练或不同优化设置缩小差距。','',
 '## 审计、样本与交付','',
 '同硬件重生成原A模型与重新训练λ=0的B对照，逐样本输出复现核对见results/original_replay_audit.json。各路径分母、源组唯一性见results/analysis_audit.json；错误仍计入分母。补充无编辑重构未重训，沿用原冻结模型的重构结果，不新增表示修复。原HE正确性结论保持历史范围，本轮没有重新加密新算子。','',
 '自动成功状态改变的前3个样本/方向见results/changed_examples.json，不是人工评判。盲审包human_review/blind.csv覆盖100源×8种组合输出，方法映射单独保存；尚未人工核验。所有逐样本JSONL包含来源、方法、seed、配置hash、参考、组件、错误及计时。','',
 '实际输出中，独立训练的 `Higher earnings helped some issues` 从只输出 `some issues` 改为 `some issues will be helped by Higher earnings`；已有组合监督的 `Then he unleashed his own unstoppable attack` 则从正确的被动句退化为 `Then he will be unleashed by him on his own unstoppable attack`。这些是可检查的自动变化案例，不代替系统盲审。所有补充路径生成失败为0、valid_auto为100%，但后一个例子说明该有效性规则不能保证语法和事件关系正确。','',
 'Slurm最终状态COMPLETED，390秒×1GPU=0.10833 GPU小时；包含此前阶段累计0.34528 GPU小时，低于12小时上限。CPU HE本轮未执行。实际日志与用量见logs/slurm-1619.out、budget.json及根目录budget.json。','',
 '## 决策','',
 '调整，暂不扩大组合实验或HE规模。本轮最多支持：“在固定StylePTB/BART协议的一次seed42消融中，位置插值式目标编码一致性降低表示残差，但对两种训练设置的连续组合Joint_auto影响相反；Shift在5000步仍呈开发损失下降，低秩优势只能按明确训练预算描述。”','',
 '下一步只做一个实验：在固定的四组B输出上完成100个源句的匿名人工配对审查，检验独立训练改善与已见组合退化是否对应真实属性/事实变化，再决定是否值得改进对齐方式。','']
 (P/'REPORT.md').write_text('\n'.join(lines))
if __name__=='__main__':main()
