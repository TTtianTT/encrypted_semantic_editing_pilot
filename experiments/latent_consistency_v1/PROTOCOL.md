# 补充实验 v1（训练前登记，2026-09-27）

用户要求：相同模型、数据和预算下加入目标编码一致性，检查连续组合；补上Shift收敛。原测试已看过，本轮是事后、固定配置的重复测试分析，不是新封存确认集；不据结果调lambda或换划分。原结果不覆盖、不自动push。

## B配对消融

同原B冻结BART revision、rank64、数据文件/hash、600更新、batch8、AdamW1e-3/weight_decay0、梯度clip1、seed42、greedy/max_new_tokens100。测试100个相同未见源组，future+passive组合仍不进入训练/开发选择。单seed是最小机制验证，不称稳定可复现。

两组各一对共4次训练，均从相同初始化重新训练：
1. 独立基本操作CE：lambda0对lambda0.1。
2. 原已见组合监督CE：0.5 primitive CE+0.5 present/passive组合CE，lambda0对lambda0.1；一致性亦按0.5/0.5加权。
每一对复用完全相同随机样本日程、更新数、模型初始化、参数量；两臂都计算目标encoder及一致性项（对照乘0），使新增目标编码计算机会相同。组2本来有额外组合监督，不与组1宣称等信息比较。

损失：L=原CE+lambda*L_cons。目标 E(y) 为同一冻结encoder的stop-gradient输出。token memory源/目标长度不同：对目标有效token（包括BOS/EOS）按归一化位置线性插值到源有效长度（align_corners=True）；不纳入任何padding，不对未知测试参考优化。L_cons=逐样本 mean((T(E(x))-aligned(E(y)))^2)/(mean(aligned(E(y))^2)+1e-8)，再平均batch。lambda固定0.1，无网格搜索/结果后修改。此插值不是词对齐，不保证精确流形投影，负结果仅约束该具体一致性形式。

在primitive及已见组合上分别施加该一致性；不使用保留future/passive组合监督。600步最终checkpoint，不按测试/开发挑步数。生成路径仍passive→future，比较latent_once与decode_reencode；同时输出单步passive漂移。主比较：每组lambda0.1减lambda0的连续组合Joint_auto；分别报告属性、内容、有效性、chrF、精确参考匹配、单步内容保留。沿用原规则及其已知误判，不修正阈值以追逐提升。源组2000次paired bootstrap，100源分母不剔除失败。

诊断：开发集primitive/seen-combo一致性误差与CE、固定测试的离线目标编码误差（仅评分，绝不反馈编辑器）、T(E(x))和E(G(T(E(x))))的再编码残差。后者也需长度插值，不能冒充精确语义距离。核查padding、目标无梯度、编辑器一致性梯度存在、配对初始化/批日程相同。

## Shift收敛审计（与B消融分开）

恢复A seed42/43/44第1000步的真实editor和Adam状态；不重置动量。恢复同一numpy样本日程在1000步后的序列，同一5k训练/363开发、lr1e-3、batch≤16、优化器/冻结E/G不变。各继续到5000步，每200步记录全开发token NLL、训练损失、梯度范数和参数更新大小；保存optimizer/checkpoint，开发NLL选择best，固定训练上限不按测试延长。

两个连续1000步窗口（3000→4000、4000→5000）开发NLL相对改善都在[0,1%]时仅称“该审计窗口近平台”；仍明显下降则明确未证明收敛；恶化/震荡不视为数学收敛。不能由5000步上限证明最优。

三seed在所有配置冻结后统一生成：原1000步Shift、延长后开发best Shift、原1000步预算下选定低秩。5000步Shift对1000步低秩明确是额外计算预算诊断，不替换同预算主结论。仍以364源句为单位，先句内平均seed、2000次paired bootstrap。报告loss曲线、旧/新Shift差及低秩差距变化。不会因某个结果较好缩短/加长训练或重新选rank。

## 资源

一个sbatch/srun作业，1GPU/4CPU、最多1小时（程序55分钟安全截止），低于此前剩余11.76GPU小时；不运行新的B/C加密扩展。所有结果在本目录，原文件只增加指向本补充报告的说明。最终提供本地git commit，不push。
