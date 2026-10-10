"""Standalone report and exportable rank curves; no inference or new fits."""
from shared import *

def table(headers,records):
    return '| '+' | '.join(headers)+' |\n| '+' | '.join(['---']*len(headers))+' |\n'+''.join('| '+' | '.join(map(str,r))+' |\n' for r in records)+'\n'
def readcsv(name):return list(csv.DictReader((ROOT/name).open()))
def pct(x):return 'NA' if x in (None,'','None') else f'{100*float(x):.2f}%'
def ci(x):
    if x in (None,'','None'):return 'NA'
    vals=json.loads(x) if isinstance(x,str) else x
    return '['+', '.join(pct(v) for v in vals)+']'

def main():
    p=verify();single=readcsv('results/single_summary.csv');chains=readcsv('results/chain_summary.csv');res=readcsv('results/residual_summary.csv')
    controls=readcsv('results/matched_control_summary.csv');cal=readcsv('results/probe_calibration_summary.csv');probes=readcsv('results/probe_state_summary.csv')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axs=plt.subplots(2,2,figsize=(11,8),sharex=True)
    for ti,t in enumerate((0,3)):
        for condition in p['fit_conditions']:
            ss=[next(r for r in single if r['condition']==condition and int(r['rank'])==rank and int(r['template'])==t and r['cohort']=='mask_aligned' and r['metric']=='success') for rank in p['ranks']]
            cc=[next(r for r in chains if r['condition']==condition and int(r['rank'])==rank and int(r['template'])==t and r['sequence']=='primary' and r['step']=='5') for rank in p['ranks']]
            axs[0,ti].plot(p['ranks'],[float(r['mean'])*100 for r in ss],marker='o',label=condition)
            axs[1,ti].plot(p['ranks'],[float(r['rate'])*100 for r in cc],marker='o',label=condition)
        axs[0,ti].set_title(f'Template {t}');axs[0,ti].set_ylabel('Aligned one-step success (%)');axs[1,ti].set_ylabel('Complete R5 success (%)')
        for ax in axs[:,ti]:ax.set_xscale('log',base=2);ax.set_ylim(-3,103);ax.set_xticks(p['ranks'],p['ranks']);ax.grid(alpha=.25);ax.legend()
        axs[1,ti].set_xlabel('Rank')
    fig.tight_layout();fig.savefig(ROOT/'results/rank_curves.png',dpi=170);fig.savefig(ROOT/'results/rank_curves.svg');plt.close(fig)
    body='# 规范写入可达性与残差语义：闭式分析\n\n'
    body+='本轮只执行实验 A、B。冻结 BART encoder、decoder 与三个 CE rank-16 编辑器，神经网络参数更新次数为 0；没有启动实验 C，也没有增加编辑器 seed。RRR 与时间探针均为规范编码上的闭式拟合。\n\n'
    body+='## 设计与解释边界\n\n'
    body+='沿用 96 个拟合 worlds 和 80 个历史分析留出 worlds，内容组合不重叠。留出 worlds 在之前已评估，不能声称新独立确认。只拟合模板 0 的条件中，模板 3 是结构 OOD；模板 0、3 都参与拟合的条件中，模板 3 仅是留出 world 泛化。\n\n'
    body+='每个合法相邻状态转换先检查 attention mask 相同，仅对相同者拟合 token 级共享仿射写入。截距不受惩罚。RRR 精确求解 mean-token 平方误差加 ridge 的秩约束目标：对增广设计的白化交叉协方差做 SVD 截断。它是该正则化目标的闭式最优解，不是所有数据分布、所有目标下的能力上界。三个 ridge 系数只用 80/16 的拟合 world 内部分割选择，然后在全部 96 个拟合 worlds 上重拟合。没有用评测输出选模型。\n\n'
    body+='[锁定协议](protocol.json)；[ridge 选择记录](results/ridge_selection.csv)；[mask 对齐覆盖](results/alignment_coverage.csv)。链同时测两个既有操作顺序，均从状态 0 开始。重编码保留同一 CE 操作，只在续步前编码上一步实际输出；不是把 gold 文本喂给编辑器。\n\n'
    body+='## 秩、单步保护和完整轨迹\n\n'
    body+='![秩与单步／R5](results/rank_curves.png)\n\n'
    body+=table(['模型','模板','对齐单步成功','非目标保持','R1','R2','R3','R4','R5','R5 95% CI'],[
        [model,t,
         pct(next(r['mean'] for r in single if r['model']==model and r['template']==str(t) and r['cohort']=='mask_aligned' and r['metric']=='success')),
         pct(next(r['mean'] for r in single if r['model']==model and r['template']==str(t) and r['cohort']=='mask_aligned' and r['metric']=='preserved')),
         *[pct(next(r['rate'] for r in chains if r['model']==model and r['template']==str(t) and r['sequence']=='primary' and r['step']==str(k))) for k in range(1,6)],
         ci(next(r['ci95'] for r in chains if r['model']==model and r['template']==str(t) and r['sequence']=='primary' and r['step']=='5'))]
        for model in dict.fromkeys(r['model'] for r in chains) for t in (0,3)])
    body+='单步表覆盖所有 mask 对齐的合法相邻转换，链 R1 只从状态 0 出发，两者不能直接混用。单步置信区间按 world 对重复转换取平均后 bootstrap；每个链格的 80 个 world 用 Wilson 区间。条件续步仅在此前整个前缀成功的 worlds 上计算，无合格前缀时为 NA。确定性 RRR 只有一个解，不复制成三个 seed。\n\n'
    body+='[全部单步与保护率](results/single_summary.csv)；[完整轨迹、条件续步与终点率](results/chain_summary.csv)；[逐 world 输出](results/evaluation.jsonl)。后一个文件中保留全部实际文本。\n\n'
    body+='## 理想写入残差有没有下降\n\n'
    body+=table(['模型','模板','操作','token MSE','S42 坐标 MSE','S43 坐标 MSE','S44 坐标 MSE'],[
        [model,t,op,*[f'{float(next(r[field] for r in res if r["model"]==model and r["template"]==str(t) and r["operation"]==op and r["basis_seed"]==str(s))):.6g}' for field,s in [('token_mse',42),('S_mse',42),('S_mse',43),('S_mse',44)]]]
        for model in dict.fromkeys(r['model'] for r in res) for t in (0,3) for op in ('plus','minus')])
    body+='这里只对 attention mask 对齐的 source/target 报潜空间 MSE；不对齐的转换依然生成和评估语义，但潜空间残差标为 NA。MSE 是每个有效 token／坐标的平均，再等权平均 world 与转换。S 是上一轮只在拟合 worlds 上得到的三个 PCA4 基。L2 下降与解码成功是两个指标；全秩失败只能说明这个拟合设计及 L2 目标不足，不能严格证明规范变化在总体上不可线性表示。\n\n'
    body+='[残差表](results/residual_summary.csv)。\n\n'
    body+='## 幅度匹配位移：方向与整体脆弱性\n\n'
    body+='使用上一轮 1→0 的历史匹配对。先在编辑状态上计算实际 ridge 位移，随机全空间位移与随机 4 维位移逐 world 匹配其 masked-token Frobenius 范数。把相同实际位移及同范数随机位移分别施加到编辑状态和对应规范状态上；不再使用范数远小的 random_ridge 作为这项对照。随机方向重复四次，区间按 world 聚类。\n\n'
    body+=table(['seed','状态','位移','范数','当前逐字保持','当前成功','下一步成功','当前保持 CI'],[[r['seed'],r['context'],r['condition'],f'{float(r["mean_norm"]):.4f}',pct(r['current_exact']),pct(r['current_success']),pct(r['next_success']),ci(r['current_exact_ci95'])] for r in controls])
    body+='参考状态接受的是编辑状态计算出的同一位移，因此这项表检验相同扰动在两种状态上的不对称；不是另算一个较小的规范状态位移。下一步使用同 seed 的 plus 编辑器。\n\n[匹配对照表](results/matched_control_summary.csv)；[逐样本对照](results/matched_controls.jsonl)。\n\n'
    body+='## 时间探针先校准，再解释\n\n'
    body+='只用模板 0 的规范编码、七个时间状态拟合七分类 ridge 探针。分别报告 full、S 与 S 正交补上各自拟合的探针，并分解同一 full 探针的 target-minus-source margin。S 探针准确率不足时，不能把其输出标签解释成可靠的状态载体。\n\n'
    body+=table(['seed','模板','分量','规范状态准确率','world bootstrap CI'],[[r['seed'],r['template'],r['component'],pct(r['mean']),ci(r['ci95'])] for r in cal])
    body+=table(['seed','状态','full→目标','S→目标','S→源','正交补→目标','正交补→源','共享 S margin','共享正交补 margin'],[[r['seed'],r['context'],pct(r['full_target_rate']),pct(r['S_target_rate']),pct(r['S_source_rate']),pct(r['complement_target_rate']),pct(r['complement_source_rate']),f'{float(r["shared_S_contribution"]):.5f}',f'{float(r["shared_complement_contribution"]):.5f}'] for r in probes])
    body+='这里的源状态固定为 +1，目标为 0。margin 为目标 logit 减源 logit，正数支持目标；两个共享分量贡献加独立列出的 bias 等于 full margin。它们是相关性诊断，不是探针本身的因果证据。\n\n[校准表](results/probe_calibration_summary.csv)；[状态与置信区间](results/probe_state_summary.csv)；[逐样本 margin](results/probe_states.jsonl)。\n\n'
    body+='## 续步失败的内容\n\n'
    fs=readcsv('results/failure_summary.csv');chosen=[r for r in fs if r['panel']=='historical_v2' and r['model']=='none' and r['template'] in ('0','3') and r['sequence']=='primary' and r['step']=='2']
    body+=table(['seed','模板','第二步类别','数目','失败中的占比'],[[r['seed'],r['template'],r['category'],r['count'],pct(r['fraction_of_failures'])] for r in chosen])
    body+='分类优先级：不可解析／语法不合规／未正常结束 → 非目标事实损坏 → 编辑未执行 → 其他错误状态。另存 target、preserved、parseable 等重叠标签，避免优先级掩盖共同失败。错误状态标记多走一步、历史状态或其他状态；仅凭文本无法辨认“复制旧状态”的来源。受控时间模板没有出现人物槽，非目标项主要是物体、颜色、数量、status，模板 3 还包括绝对日期，不能泛化成自然文本人物保持结论。\n\n'
    body+='上一轮模板 2 的输出也单独分类，但其单步地板效应不用于组合机制结论。OOD 随机马氏距离高于 S 的现象也不能直接证明是另一机制：不同预测器性能只构成机制异质性的线索。\n\n[全部错误类别](results/failure_summary.csv)；[逐条标签](results/failure_categories.jsonl)。\n\n'
    body+='## 下一步决策与机制措辞\n\n'
    iid16=next(r for r in chains if r['model']=='RRR_iid_only_r16' and r['template']=='0' and r['sequence']=='primary' and r['step']=='5')
    iidfull=next(r for r in chains if r['model']=='RRR_iid_only_r768' and r['template']=='0' and r['sequence']=='primary' and r['step']=='5')
    if float(iid16['rate'])>=.95:
        body+='RRR-16 在所测 IID 主轨迹上达到较高 R5，规范拟合目标下已存在可组合写法。这支持先研究目标欠约束，而无需先提高 rank。仍须核对另一顺序、单步非目标保护与模板 3，不能从一个顺序推出任意链长可达。\n\n'
    elif float(iidfull['rate'])>=.95:
        body+='RRR-16 未恢复 IID 主轨迹，而更高秩达到较高 R5。秩曲线支持“在本闭式规范拟合方案中，长链要求比当前 rank-16 更高的能力”；临界秩只能据表确定，不能把该实验当成全部 rank-16 编辑器不可达的证明。\n\n'
    else:
        body+='包括全秩在内的闭式 RRR 没有恢复 IID 主轨迹。结合残差是否下降与失败类别，结论应限定为共享线性写入、当前数据覆盖与 L2 目标的边界，尚不能区分非线性必要性、有限样本估计与 decoder 方向加权不足。此时不建议直接增加 rank 或重试投影估计器。\n\n'
    body+='上一轮 S 正交补注入三个 seed 均致败，读取分量单独注入也有 34%–80% 致败；因此两类分量都能独立产生失败，正交补效应更强。读取分量属于编辑器读取空间，并不足以单独证明编辑器放大是唯一中介。CE 的多解和 seed42 离群同样是目标欠约束的线索，而不是已证明的成因。\n\n'
    body+='本轮不继续尝试新的无参考投影估计器，也不训练 C。若后续训练规范 L2 或续步等价目标，应检验 S 残差、S 注入敏感性和跨 seed 子空间是否共同改善；其中子空间角度还需结合残差能量及 eigengap，接近零残差时 PCA 方向本身可能不稳定。最终论文确认需另锁新 worlds 与 5 个 seed，当前三个历史 seed 不替代确认实验。实用价值以状态有效性及机制为主，不以节省重编码成本为主。\n\n'
    if (ROOT/'results/resources.json').exists():
        resource=read(ROOT/'results/resources.json');body+=f'实际 GPU 分配：{resource["total_gpu_allocation_seconds"]} 秒，峰值 1 张 GPU；CPU 闭式拟合不计作神经网络训练。\n\n'
    body+='[审计](results/audit.json)；[资源账本](results/resources.json)；[源码与产物哈希](results/artifact_manifest.json)；[复现说明](README.md)。\n'
    (ROOT/'REPORT.md').write_text(body)
    print('Report and rank curves written.')

if __name__=='__main__':main()
