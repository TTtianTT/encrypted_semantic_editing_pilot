"""Reviewed report from complete tables, without selecting methods/checkpoints."""
from futils import *
def pct(x):return 'NA' if x is None else f'{100*x:.2f}%'
def rate(r):return f"{pct(r['rate'])} [{pct(r['ci95'][0])}, {pct(r['ci95'][1])}] ({r['k']}/{r['n']})" if r['n'] else 'NA (n=0)'
def mean_ci(r,digits=4):return f"{r['mean']:.{digits}g} [{r.get('ci95_world_bootstrap',r.get('ci95'))[0]:.{digits}g}, {r.get('ci95_world_bootstrap',r.get('ci95'))[1]:.{digits}g}]"
def table(cols,rs):return '\n'.join(['| '+' | '.join(cols)+' |','| '+' | '.join(['---']*len(cols))+' |']+['| '+' | '.join(map(str,r))+' |' for r in rs])+'\n'
def main():
 assert read(ROOT/'checks.json')['passed'];p=read(ROOT/'protocol.json');ledger=read(ROOT/'run_ledger.json');ss=read(ROOT/'results/fresh_single_summary.json');cs=read(ROOT/'results/fresh_chain_summary.json');cl=read(ROOT/'results/fresh_closure_summary.json');ms=read(ROOT/'results/fresh_mechanism_summary.json');vis=read(ROOT/'results/fresh_visibility.json');control=read(ROOT/'results/control_summary.json');geometry=read(ROOT/'results/write_geometry_summary.json');risk=read(ROOT/'results/continuation_risk_models.json');angles=read(ROOT/'results/fresh_cross_seed_angles.json');pca=read(ROOT/'results/fresh_pca.json')
 def crows(domain,g,seed,t,path,ck):return sorted([r for r in cs if r['domain']==domain and r['group']==g and r['seed']==seed and r['template']==t and r['path']==path and r['checkpoint']==ck],key=lambda r:r['step'])
 def singles(domain,g,seed,t,ck,scope):return next(r for r in ss if r['domain']==domain and r['group']==g and r['seed']==seed and r['template']==t and r['checkpoint']==ck and r['scope']==scope)
 text=f"""# 输出正确仍会失去续步：五 seed 锁定确认、优化器对照与有限闭包

本轮完成了写入几何、固定样本 CE/梯度分析、标量视界检验、12 组不超过 100 步的优化器对照、五 seed 新 worlds 确认，以及 BART 人称域复现。没有开启新的方法线。对齐时间域的 C3（CE+规范 L2）是锁定的主方法；长度变化和定向扰动鲁棒性继续作为边界。

五 seed 时间域主比较确认了规范锚定的五步效果；人称域未复现修复效果。这是同一 BART 的跨属性检验，尚不是跨模型复现。

时间域 C3 在五 seed、两模板、三种循环上均保持到 20 步；50 步成功率则依 seed 和路径从 0% 到 100% 不等。因此修复与任意长度闭包仍须分开，seed45 的长链退化不能被前三个探索 seed 的较好表现掩盖。

标题保留优化设置的限定。**CE 在非规范写法上有可优化的似然收益，但五步退化的程度依赖优化路径。**不能将本轮 AdamW 下的因果结果改写成“任何优化器优化 CE 都必然破坏组合性”，也不能把它全部归为零梯度平坦区里的随机漂移。

## 锁定、覆盖与统计单位

[确认协议](protocol.json)在首条新 world 预测前提交，锁定提交为 `946b5fa`，协议 SHA256 为 `{sha(ROOT/'protocol.json')}`。训练仍为原来的 96 worlds；160 个新时间 worlds 按固定随机种子生成，以 `(object,color,quantity,status)` 排除了协议指纹中的四份历史数据文件（共 {p['excluded_legacy_cores']} 个事实组合）。这是相对这些显式历史文件的新确认集，不声称扫描过仓库所有旧数据。历史 80 worlds 仅用于优化器和机制量的探索性分析。

确认 seed 为 42–46。C1/C3 的 42–44 使用已固定的原始最终 checkpoint；45–46 新训练，全部仍为 600 次更新。C4 的五 seed 从同一个平衡 RRR-16 写法重放到 50 步，42–44 在旧 10/25/50 检查点与原参数逐项一致。RRR 和重编码各是一个确定性参照，不能把同一映射重复计成五份独立模型证据。

对齐路径是早期事后选出的，本次已预先锁定。IID 为模板 0，结构 OOD 为模板 3。四条五步顺序全部评测，包含原交替、原重排，以及从 +1、−1 出发的两条对齐路径。原重排第二步涉及长度变化；对齐训练未覆盖这一转换，不能把其单步地板称为组合失败。每个 seed/path/template 的完整轨迹以 world 为统计单位，用 Wilson 95% 区间；跨转换均值按 world bootstrap，不将一个 world 的八种转换当成八个独立样本。

## 五 seed 主比较

下表为对齐 +1 路径。单步列是一个 world 内**训练覆盖的全部八个对齐转换都成功**的比例，强于平均转换成功率；R1–R5 是完整前缀成功率。模板 3 也评测同一转换图，不重新选择容易成功的转换。括号为 R5 的 world 分母，方括号为 95% 区间。其他三个顺序和所有检查点见[完整逐 seed 表](results/fresh_chain_summary.json)，[逐转换单步表](results/fresh_single_cells.json)同时给出语义成功、逐字相等和非目标保持。

"""
 rr=[]
 for g in ('C1','C3','RRR','reencode'):
  for seed in (SEEDS if g in ('C1','C3') else (0,)):
   for t in (0,3):
    ck=600 if g in ('C1','C3') else 0;z=crows('time',g,seed,t,'aligned_from_plus_one',ck);a=singles('time',g,seed,t,ck,'train_supported');rr.append([g,seed if seed else 'det.',t,rate(a['metrics']['success']['all_edges']),rate(a['metrics']['preserved']['all_edges']),'/'.join(pct(r['trajectory']['rate']) for r in z),rate(z[-1]['trajectory'])])
 text+=table(['条件','seed','模板','对齐单步：world 内全对','非目标保持：world 内全对','R1 / R2 / R3 / R4 / R5','R5 95% CI'],rr)
 text+='\n完整逐 seed 表同时提供以先前完整前缀成功为分母的 `conditional_continuation` 和 Wilson 区间；前缀已全部失败时条件续步率为 NA。\n'
 text+='\n[全部合法转换的目标与保护率](results/fresh_single_summary.json)保留长度变化地板；这些结果不支持“所有转换均已修复”的说法。模板 3 只是结构扩展，不等于开放域或全部 OOD。\n\n'
 text+='## C4：密集检查点下，视界是否分层退化\n\n![新 worlds 的五 seed、五个深度](results/fresh_C4_depths.svg)\n\n'
 rr=[]
 for seed in SEEDS:
  for t in (0,3):
   for ck in CKS:
    z=crows('time','C4',seed,t,'aligned_from_plus_one',ck);a=singles('time','C4',seed,t,ck,'train_supported');rr.append([seed,t,ck,' / '.join(pct(r['trajectory']['rate']) for r in z),rate(z[-1]['trajectory']),rate(z[0]['current_exact']),rate(a['metrics']['success']['all_edges'])])
 text+=table(['seed','模板','AdamW 更新','R1 / R2 / R3 / R4 / R5','R5 95% CI','首步逐字正确','对齐单步：world 内全对'],rr)
 text+='\n只连接已测的检查点，不推断其间每一次更新的精确崩溃时刻。首步正确与更深前缀退化可以同时发生；这组干预固定了初始化、数据和秩，但其优化器限定不可去掉。\n\n'
 text+='## 写入几何：相对规范写入的幅度与方向\n\n记 `w=T(Ex)-Ex`、`d=E(y)-E(x)`、`e=w-d`。下表由已有残差范数、规范范数和投影系数精确恢复 `||w||`，没有新训练或新解码。每个 world 先平均八种对齐转换，再 bootstrap worlds。\n\n'
 text+=table(['历史 seed','模板','cos(w,d)','||w||/||d||','<w,d>/||d||²'],[[r['seed'],r['template'],mean_ci(r['cos_write_ideal'],5),mean_ci(r['write_to_ideal_norm'],5),mean_ci(r['write_projection'],5)] for r in geometry])
 text+='\n历史 CE 写入范数约为规范写入的 3.3–3.8 倍，却几乎与规范方向正交，不能解释成“相对规范写入很小、方向任意”。这一比例不说明写入相对整个源表示的范数也大。这支持“decoder-directed 的写入捷径”这一解释。它不是关于 C4 **总写入**方向的断言：C4 初始已有 RRR 的规范分量，后续新增偏离主要正交，规范方向上的欠写甚至可以有所减小。\n\n与[对抗扰动的经典工作](https://arxiv.org/abs/1312.6199)和[shortcut learning](https://arxiv.org/abs/2004.07780)的联系是机制类比。本实验没有运行经典攻击的最小扰动、感知约束或攻击转移协议，因此不将这些编辑直接命名为已证明的对抗样本。\n\n'
 text+="""## CE 的可优化收益与优化器影响\n\n所有优化器对照从相同平衡 RRR 初始化出发，使用相同对齐 minibatches，三 seed，每组 100 次更新。纯 SGD 无 momentum，AdamW 无 weight decay；clip、batch 和目标相同。固定面板是历史 80 worlds×八种对齐转换，避免拿不同训练 minibatch 的 CE 比较。对齐单步 greedy 检查使用预定的前 16 worlds，R5 使用全部 80。此前 C2 的 L2 训练实际采用 **AdamW**；“SGD 能到达”的旧措辞泛指梯度训练，本轮纯 SGD 是独立控制。

![相同固定面板 CE 尺度上的残差与 R5](results/optimizer_matched_loss.svg)

"""
 rr=[]
 for r in control:
  if r['checkpoint']!=100:continue
  init=next(a for a in control if a['variant']==r['variant'] and a['seed']==r['seed'] and a['checkpoint']==0);rr.append([r['variant'],r['seed'],f"{init['nll']['mean']:.7g} → {r['nll']['mean']:.7g}",f"{100*(1-r['nll']['mean']/init['nll']['mean']):.3f}%",mean_ci(r['token_mse'],5),rate(r['R5'])])
 text+=table(['优化器 / lr','seed','固定 CE：初始→100 步','相对降幅','100 步 token MSE','100 步 R5'],rr)
 text+="""\nCE 下降在绝对量上仍很小（初始输出已经正确），不能只用相对百分比渲染为巨大语义收益。共同降幅对照只在实际达到的范围内插值，不外推。95% 降幅处，达到该降幅的对照 R5 为 100%；98% 降幅附近，原学习率 AdamW 的部分 seed 已退化，SGD 保持五步表现。插值是相邻检查点之间的描述，不能当成实测的中间模型或精确损失匹配的因果效应；[所有插值括号和未达到范围](results/matched_CE_reduction.json)公开保留。

各对照在降低 CE 时都可以增加非规范残差，因此“CE 严格无梯度，只是随机漂移”不成立。但未证明纯 SGD 在 100 步内会像原 AdamW 那样把 R5 压到 0。合适的结论是：**输出级目标允许、且可奖励偏离规范的写法；组合性的破坏取决于具体优化路径和优化程度。**

RRR 初始化处对编辑状态的 CE 梯度，下降方向 `−g` 与规范编辑方向的平均余弦几乎为零。旧 S 中的梯度能量仅为部分能量，而不是“全部梯度都在 S”；与现有 RRR 残差的下降方向余弦略负，也不支持每个瞬时 hidden 梯度都在增大 L2 的说法。hidden 梯度与受共享 rank-16 参数约束的实际更新方向须区分。

"""
 text+=table(['梯度指标','seed','均值、world bootstrap 95% CI'],[[r['metric'],r.get('seed','shared'),mean_ci(r,6)] for r in read(ROOT/'results/hidden_gradient_summary.json')])
 text+='\n[每个历史 C4 检查点、相同样本的 CE](results/historical_c4_fixed_likelihood.jsonl.gz)覆盖 0、10、25、50、100、200、400、600；新优化器对照只比较前 100 步。训练 batch loss 不用于上述判断。\n\n'
 text+=table(['历史 seed / IID','更新','固定 CE（world 均值 95% CI）','规范编码 CE','token MSE'],[[r['seed'],r['checkpoint'],mean_ci(r['nll'],6),mean_ci(r['canonical_nll'],6),mean_ci(r['token_mse'],6)] for r in read(ROOT/'results/historical_c4_likelihood_summary.json') if r['template']==0])
 text+='\n[模板 3 的相同面板与全部区间](results/historical_c4_likelihood_summary.json)。\n\n'
 text+="""## 残差—视界统一图：可排序，但不共享一个阈值\n\n历史档案共 308,640 条记录，其中 206,400 条属于 chain/dose/closure 的逐步记录。只取“进入下一步前”的残差，并要求当前完整前缀仍正确、两侧 mask 可对齐，得到 83,470 条有效续步记录；没有把失败后的残差当作原因。统计拟合按 world 的 SHA256 固定分为两半，训练各条件总权重相等，测试 worlds 不参与风险拟合；另做同时留出 world 和编辑器族的检验。全部仍是探索性历史数据，不借此声称最终独立确认。

![所有历史条件的续步风险](results/continuation_risk.svg)

"""
 text+=table(['模板','进入下一步的量','held-world 失败 AUROC','Brier','50% 概率拟合阈值'],[[r['template'],r['metric'],f"{r['test_auc_failure']:.4f}",f"{r['test_brier']:.4f}",f"{r['threshold_50']:.6g}"] for r in risk])
 text+="""\n高 AUROC 不等于统一机制定律：按条件的校准明显不同，token MSE 和 S 能量都没有把所有族压成同一条曲线。[逐条件校准](results/continuation_risk_models.json)、[同时留出 world 和编辑器族](results/continuation_leave_family_out.json)保留失败情况。

进一步固定“状态 0、下一操作 plus”，历史 seed42/IID 的 C1 在 MSE≈0.00476 时下一步 0/80，而 C4(100) 在更高 MSE≈0.00614 时为 80/80。S 上也存在反例：C1 的能量≈0.401、下一步全失败，C5 的能量更高≈0.547、下一步却为 80/80。这里比较的是不同编辑器族，因此结论是**跨族的全局标量阈值不足**，不是否定固定编辑器中的局部误差增长。还必须控制方向、状态/操作和未来编辑器。

![固定状态和操作后的幅度反例](results/matched_context_risk.svg)

在 mask 对齐域，真正的向量递推是 `e_next = e A_o + r_o`，其中 `r_o=T_o(E(y))-E(o(y))`。标量代理含每步 forcing：`ε_next≈ρ ε+ε₀`，不是只放大一次初始误差。解为 `ε_k≈ρ^k ε_init+ε₀(ρ^k−1)/(ρ−1)`；没有方向一致性、uniform decoder 裕度和放大界时，它不提供闭包保证。本轮另将已知循环谱半径作为 ρ 的标量代理，在训练半 worlds 的前 10 步拟合 forcing，作 held-world 诊断；谱半径不是诱导范数，且阈值拟合使用了训练半 worlds 的全部闭包记录，不能称为仅用 10 步监督预测任意长度。

"""
 text+=table(['模板','RRR 路径','代理预测首个失败步（封顶51）','held-world 观测均值（封顶51）','视界 MAE'],[[r['template'],r['path'],r['predicted_first_failure_capped51'],f"{r['observed_first_failure_mean_capped51']:.2f}",f"{r['horizon_MAE_capped51']:.2f}"] for r in read(ROOT/'results/scalar_horizon_test.json')])
 text+='\n[完整相位 forcing、谱值和外推误差](results/scalar_horizon_test.json)。这一近似能组织部分趋势，但不能代替方向干预，也没有建立全文共享的 τ。\n\n'
 text+="""## 新 worlds 的修补、注入与可见性\n\n机制使用预定前 80 个新时间 worlds；各 seed 的 S 只拟合 C1 训练 worlds 的 1→0 差分，在新 worlds 推理前冻结。历史匹配为 `T_plus(E(1))` 与 `E(0)`，下一操作仍是 plus。纳入条件预先规定：当前 edited/reference 都正确、canonical next 正确、edited next 失败。完整修补和完整注入是按构造的校准点；低维/分量干预与同范数随机方向才提供额外因果信息。

下表给出修补后“当前和下一步都正确”，以及注入后在当前**逐字正确**的样本中下一步失败。空分母必须记 NA，不能记成 0% 敏感性；[完整条件与当前保持率](results/fresh_mechanism_summary.json)同时报告宽语义成功和严格逐字保持。

"""
 rr=[]
 for seed in SEEDS:
  for t in (0,3):
   for component in ('full','S','S_R','S_perp','random_S_norm'):
    a=next(r for r in ms if r['seed']==seed and r['template']==t and r['kind']=='repair' and r['component']==component);b=next(r for r in ms if r['seed']==seed and r['template']==t and r['kind']=='inject' and r['component']==component);rr.append([seed,t,component,a['eligible'],rate(a['paired_success']),rate(b['current_exact_retention']),rate(b['next_failure_given_current_exact'])])
 text+=table(['seed','模板','分量','eligible','修补：当前+下一步','注入：当前逐字保持','注入：next fail | 当前逐字正确'],rr)
 text+='\n“当前不可见”限定为当前文本保持、teacher-forced 分布变化相对小，不是 decoder 输出分布严格相同或残差处在权重矩阵的精确 nullspace。S_R 和 S_perp 来自读取投影的正交拆分，它们分别并不一定仍处在原 S 中。\n\n'
 text+=table(['seed','模板','eligible','KL pre（S_perp）','KL post（S_perp）'],[[r['seed'],r['template'],r['eligible'],mean_ci(r['KL_pre_S_perp'],5) if r['eligible'] else 'NA',mean_ci(r['KL_post_S_perp'],5) if r['eligible'] else 'NA'] for r in vis])
 text+='\n**新确认更明确地支持读取空间外的路径 B。**五 seed、两模板各 80/80 符合纳入条件；只修补 S_perp 已全部救回，注入 S_perp 则在当前逐字正确 80/80 的同时使下一步全部失败。pre KL 约 0.00042–0.00405，post KL 约 0.797–3.096。读取分量单独修补全部失败；IID 下单独注入 S_R 不致败，模板 3 的 seed43/44 分别有 49/80、60/80 致败，其余为 0/80。因此路径 A 的独立作用依赖编辑器及模板，本次 C1 复现不支持把旧 P 编辑器的“两分量任一错都会失败”结构推广到所有 CE 编辑器。规范性缺陷的主要机制得到独立确认，读取分量的具体交互结构保留条件限定。\n'
 text+='\n[首次失败类别](results/fresh_first_failure_categories.json)按每条轨迹的第一次失败统计，不反复计后续坏状态。本轮确认用 C1 的训练拟合 S；它是同机制在对齐 CE 编辑器中的复现，不把新 S 与历史 P checkpoint 的旧 S 混为同一个固定子空间。过去 activation K/V 修补的 decoder 定位仍属于探索证据，未在此次重复整套逐层扫描。\n\n'
 rr=[]
 for domain in ('time','person'):
  for g in ('C1','C3','C4'):
   for t in (0,3):
    rows_=[r for r in read(ROOT/'results/fresh_aligned_first_failure_categories.json') if r['domain']==domain and r['group']==g and r['template']==t and r['checkpoint']==(50 if g=='C4' else 600)];counts={name:sum(r['categories'].get(name,0) for r in rows_) for name in ('unparseable','grammar','non_target','target_state','scope_or_end')};rr.append([domain,g,t,sum(r['failed_trajectories'] for r in rows_),*[counts[name] for name in counts]])
 text+=table(['域','条件','模板','首次失败总数','不可解析','语法','非目标破坏','目标状态错','作用域或 EOS'],rr)
 text+='\n新 C1 的 IID 首次失败以不可解析为主（2384/2400），但另有 15 次目标状态错和 1 次非目标破坏，不能沿用旧样本“全部不可解析”的绝对表述。C4 的结构 OOD 与人称域还出现明显的语法和非目标保持失败。\n'
 text+='\n该表排除时间域原重排的长度变化路径，按种子和路径汇总**失败轨迹次数**，不是独立 world 数，不能据此套 pooled 二项置信区间；逐 seed 计数保留在[细表](results/fresh_aligned_first_failure_categories.json)。人称模板 3 的计数仍包括其单步地板。\n\n'
 text+='## 方法本身的闭包边界\n\nC3 和 RRR 在预定前 80 个新 worlds 上每步评测到 50；下表逐 seed 报完整轨迹，三个循环都返回起点。\n\n'
 rr=[]
 for g in ('C3','RRR'):
  for seed in (SEEDS if g=='C3' else (0,)):
   for t in (0,3):
    for path in ('original_alternating','aligned_from_plus_one','aligned_from_minus_one'):
     z={r['step']:r for r in cl if r['group']==g and r['seed']==seed and r['template']==t and r['path']==path};rr.append([g,seed if seed else 'det.',t,path,rate(z[10]['trajectory']),rate(z[20]['trajectory']),rate(z[50]['trajectory'])])
 text+=table(['条件','seed','模板','循环','R10','R20','R50'],rr)
 text+="""\n[循环全空间谱半径](results/fresh_spectrum.json)与观测漂移一起报告；>1 说明存在不稳定方向，不证明每个起点都会激发它，也不是所有轨迹都会在同一步失败。五步成功与任意长度闭包仍是不同要求。

最终各组的 train-only 残差 PCA 同时报告绝对能量、centered 能量、top4 占比和第 4 eigengap。[能量表](results/fresh_pca.json)、[跨 seed 主角度](results/fresh_cross_seed_angles.json)包含五 seed 时间域和三 seed 人称域。尤其在规范残差很小、第四 eigengap 很弱时，角度可以不稳定；不能仅凭角度就宣称不同 seed 已收敛到同一个解。C4 共同初始化也会缩小角度，但并不保证组合性。

对齐 C3 修复的是残差的产生。既有探索性注入显示 C2/C3 仍对定向 S 残差敏感；本轮未重跑 C3 全套注入敏感性，因此这条鲁棒性边界仍引用[前一轮固定干预](../canonical_objective_v1/results/injection_summary.json)，不改称新确认的鲁棒性证据。

"""
 text+=table(['时间域 C3 seed','残差绝对能量','centered 能量','top4 占比','relative eigengap4'],[[r['seed'],f"{r['energy']:.6g}",f"{r['centered_energy']:.6g}",f"{r['top4_fraction']:.4f}",f"{r['relative_gap4']:.4f}"] for r in pca if r['domain']=='time' and r['group']=='C3'])
 text+='\n'+table(['时间域 C3 seed 对','4 个主角度（度）'],[[f"{r['seed_a']} / {r['seed_b']}",', '.join(f'{v:.2f}' for v in r['angles_degrees'])] for r in angles if r['domain']=='time' and r['group']=='C3'])
 text+="""

## 人称域：不将单步地板改名为组合失败

复现固定同一 BART、rank16，三个 seed，96 train worlds、80 新 worlds，仅跑 C1/C3/C4/RRR（以及确定性重编码参照）。模板 0 的 mask 对齐图只有 1↔2；经过状态 0 的转换改变长度，未纳入规范拟合。模板 3 先前没有通过该域的结构单步准入，仍测量并报告地板，不能用于支持组合结论。ridge=1e-4 和 C3 的归一化 L2 权重均从时间域继承，不搜索人称域测试集。

"""
 rr=[]
 for g in ('C1','C3','C4','RRR','reencode'):
  for seed in ((42,43,44) if g in ('C1','C3','C4') else (0,)):
   for t in (0,3):
    ck=50 if g=='C4' else 600 if g in ('C1','C3') else 0;z=crows('person',g,seed,t,'person_forward',ck);a=singles('person',g,seed,t,ck,'all_legal');b=singles('person',g,seed,t,ck,'train_supported');rr.append([g,seed if seed else 'det.',t,pct(a['metrics']['success']['mean']),rate(b['metrics']['success']['all_edges']),mean_ci(b['metrics']['token_mse'],5) if b['metrics']['token_mse'] else 'NA','/'.join(pct(r['trajectory']['rate']) for r in z),rate(z[-1]['trajectory'])])
 text+=table(['条件','seed','模板','全部合法单步均值','训练覆盖两转换：world 内全对','覆盖转换 token MSE','1↔2 路径 R1 / R2 / R3 / R4 / R5','R5 95% CI'],rr)
 text+="""\n**方法跨属性复现失败。**人称模板 0 上，C1 的训练覆盖两转换单步全部成功，第二步至第五步却全失败，因而现象已在第二个属性中复现。C3 的覆盖单步均值为 98.125%–99.375%，token MSE 从 C1 的约 0.023–0.025 降至约 0.0026，仍然第二步全失败：残差下降不足以保证修复。RRR 正向首步只有 23/80，模板 3 首步为 0/80，初始状态没有通过准入。因此该域 C4 不能支持“破坏已经可组合的解”。时间域规范锚定的修复效果没有推广到此次人称域设置；论文必须将方法有效性限定在时间对齐域。模板 3 的训练覆盖两转换连 source/target mask 都不相等（token MSE 为 NA），其单步地板单独报告。

[反向路径、全部单步与密集 C4 检查点](results/fresh_chain_summary.json)均保留，不能只挑这张表中的一种顺序。固定秩/继承超参下的负复现也不能直接证明规范写法不可能存在；本轮没有追加更高秩、新 λ 或 ridge 搜索。

## 论文主张与边界

| 主张 | 本轮对应证据 | 必须保留的边界 |
| --- | --- | --- |
| 解码正确不足以保障续步 | 新五 seed C1 链，匹配修补/注入 | 受控合成数据、指定编辑器族；宽语义与逐字指标分开 |
| 有低维、当前文本隐蔽的非规范残差 | train-only S 的新世界干预、pre/post KL | 逐分量、逐 seed 和当前保持分母判断；full 修补为构造控制 |
| 时间对齐域的 rank16 能写出可组合状态 | RRR、C3，新世界主比较；C2 为旧探索 | 有限已测视界；不推及长度变化和任意属性 |
| CE 可偏离规范解，AdamW 下损害组合性 | 同初始化 C4 新五 seed；固定 CE、SGD/小 lr 对照 | 优化路径及程度重要，不是所有优化器必然破坏的定理 |
| 规范锚定可修复对齐时间域 | C3、新 worlds、结构模板3 | 不保证任意长度，也不证明注入鲁棒性 |
| 误差幅度能排序风险，但没有共享全局阈值 | lagged 风险曲线、固定状态/操作反例 | 世界与编辑器族外推分别报告；还依赖方向和未来映射 |
| 轨迹覆盖和状态锚定有不同经验视界 | 既有实验5/C5 与本轮 C3/RRR 闭包 | 单一权重/预算，C5 同时改变数据和目标，不能宣称一般理论上限 |

长度变化不再开启新方法线。一步 KL/第三步监督的既有结果用于说明本设置的经验视界，不是对递归状态等价目标的普遍否定。论文贡献是机制与状态有效性评测，计算节省不作为主要实用价值论据。本轮未追加 Emb2Emb 式流形对抗基线；确认只比较预先选定的条件，不声称 C3 相对所有经典流形方法的最优性。

## 成本与交付

"""
 costs=read(ROOT/'results/compute_reference.json');rr=[]
 for mode in ('latent_C3','decode_symbolic_reencode'):
  vals=[r['seconds'] for r in costs if r['mode']==mode and not r['warmup']];rr.append([mode,f'{np.mean(vals):.4f}',f'[{min(vals):.4f}, {max(vals):.4f}]',f'{np.mean(vals)/80:.5f}'])
 text+='同步计时，预热后 3 次，batch16、80 worlds，五次状态更新+终局解码；不计共同的初始编码。重编码另外包括每步当前解码/解析与 encoder，受控 symbolic 操作读取已知 gold world/state，因此是成本参照与规范上界，不能当作开放域算法。与旧 0.078 秒/world 的单 world 设置不可直接横比。\n\n'+table(['模式','五步×80 worlds 平均秒','实测范围','秒 / world 五步'],rr)
 text+=f"\n本轮新增编辑器更新 **7,600** 次，backbone 更新 **0** 次。按用户运行中指令，资源上限调整为两张卡，实测峰值 **{ledger['peak_gpus']} 张 GPU**；所有计算通过 `sbatch` 分配、`srun` 执行，此前登录节点上的派生统计已在无 GPU 的 Slurm 任务中重跑。累计 **{ledger['allocation_seconds']} GPU 分配秒（{ledger['allocation_seconds']/3600:.4f} GPU 小时）**，未超锁定总预算。科学协议保持原始 SHA；[资源调整记录](resource_amendment.json)、[运行账本](run_ledger.json)、[审计](checks.json)、[checkpoint 指纹](checkpoint_index.json)、[预测档案与解压后 SHA](results/prediction_archives.json)。\n\n所有原始文本、EOS 与独立评分保留在确定性 gzip 档案；权重和 encoder 缓存留在本地。统计代码与 standalone SVG/PNG 一并上传，当前结果不再用于修改确认协议或另选一个测试表现更好的方法。\n"
 text+='\n'+table(['Slurm 作业','阶段','GPU','分配秒','状态'],[[j['job_id'],j['phase'],j['gpus'],j['elapsed_seconds'],j['state']] for j in ledger['jobs']])+f"\n统计、审计、归档与报告的 CPU 后处理作业：{ledger['postprocessing_job_id']}（0 GPU，`sbatch` + `srun`）。CPU 重跑的首次尝试 3326/3328 因派生脚本遗漏分组函数导入而失败；补齐导入后 3329/3330 成功。单步审查 3333 的新模块导入查找失败，CPU 驱动改用绝对脚本路径后重跑。这些失败均未影响任何 GPU 预测或模型权重，账本保留原退出码。全部配置、命令和日志路径见运行账本。\n"
 (ROOT/'REPORT.md').write_text(text)
if __name__=='__main__':main()
