# Decoder readout invariance editing v1：实际结果与限制

2026-10-08，Asia/Singapore；分支experiment/decoder-readout-invariance-editing-v1。用户确认“16例抽查通过”后，已完成具体KL/readout正则GPU梯度与8world过拟合验收，以及BART rank16四方法三个seed正式训练和全量validation单操作评测。此确认只解除I_keep人工抽查门槛，未授权变更独立test。

**完整研究计划仍未完成：独立S4为BLOCKED_TEST_INTEGRITY，正式test评测0。** 全部本轮方法比较是validation探索性证据。此前源颜色对照派生core漏检，提前编码了固定IID test的5/128 core；虽未做正式test评测，仍不能称原128全部未暴露。我已保存暴露ID/证据、原split SHA与门禁修复；不补搜、不将剩余123静默改成确认终点。完整记录见reports/DATA_EXPOSURE_CORRECTION.md和configs/TEST_EXPOSURE_WITHDRAWAL_LOCK.json。

## 完成范围

| 阶段 | 实际执行 | 仍缺失 |
| --- | --- | --- |
| 审计/CPU | 原分支HEAD、1321文件SHA、21分支暴露扫描、固定train192/val64/test128/reserved128；真实人工16例通过 | 原128独立终点已破坏；模板0–5均历史暴露，OOD为UNAVAILABLE |
| S0 | BART FP32与原版T5Gemma BF16；memory注入、native无干预一致、mask/EOS/KV、H梯度、冻结参数、8world smoke通过 | 可选eager对齐失败已保留，不采用 |
| S1 BART | train32/val32/旧replay8，共288严格pair、概率/有限路径/随机/源前缀/传播/真实generation scores | 独立机制确认及完整多token语义候选log-prob未完成 |
| S2 BART | 全层discovery、固定L5/L0整层与head0双向K/V、native SDPA诊断、在线Q替换 | 无完整/唯一稀疏电路；未独立确认，top2/frozen-norm扩展未运行 |
| S3 BART | Plain/Output-only/Mechanism-guided/Random-site，seed42/43/44，192train/64val，400updates；keep/mech网格锁定 | validation不等于独立test；历史错误当前状态实际无覆盖 |
| validation长链 | 选定新方法运行待结束 | 独立IID链与真实OOD未执行 |
| S4 | CPU暴露审计和阻塞报告 | BLOCKED_TEST_INTEGRITY；没有隐式修改分母 |
| T5Gemma | 原google/t5gemma-2b-2b-ul2-it BF16，S0及train16/val16一般SAME_TEXT小规模分析 | 每split16world，独立确认不可估计；新方法强对照未运行 |
| S5预调节 | 未运行 | NOT_RUN_PREREQUISITES；S0–S4主结果未完成，不是GPU配额耗尽 |

## Q1：为什么大幅改变还能读出同一句话

BART SAME_TEXT面板：train32/32world、validation32/32、旧replay8/8，每world4个不重复来源pair；合计288pair。资格不要求下一步分叉。EOS、有效mask/shape、原始文本和有效生成token全部核验；N=R去重，BOS/forced/EOS保留。P为旧锁定四维共享方向逐有效token修补，不是整个memory仅四自由度；没有学习新PCA或将80旧world重新称独立确认。

共同原生前缀下6912 token-pair记录，平均全词表JS约0.0003062501、最大0.0124072358。相同文本**不等于**相同概率/状态。validation平均有效memory差值范数：E_future_plus→N为14.6046024，→P为14.3956466（两者均非微小扰动；新池均值比例约98.57%，不能替换旧80world的96.3%报告）。固定8world子集alpha1，两种真实方向均8/8保留；同范数随机8方向为donor15/64、PCA17/64（isotropic和shared rank4此两项相同）。保留率匹配随机幅度仅由validation聚合选择alpha0.25，8个pair×随机类型均64/64；它的扰动更小，不是同范数保护证据。所有网格点原始结果保留。

反证：validation E_past_minus→N路径在alpha0/0.25为8/8、0.5为0/8、0.75/1/1.25又为8/8、1.5为0/8。两端相同不能证明整条线相同、凸盆地、全局nullspace或唯一不敏感半径。

8固定train/validation world的实际native generate额外审计：1536输出决策记录，其中64个forced BOS单列；其余1472个位置raw argmax、processor后argmax均与实际token一致（分歧0/1472），生成路径encoder再执行0次。9408实际head AV/W_O差异记录是观测证据，未测试边不称因果。所有机制forward使用cache=False；缓存兼容在S0另验收，没有跨memory复用旧cross-KV。

当前最可信的有限解释是：普通离散argmax对某些大幅有结构memory改变仍保持；其内部读出还依赖跨层query与memory的配合。该结论有直接反证约束，不能概括为decoder完全不读取memory。

## S2：局部因果干预及反证

层号零起点。候选L5是`model.decoder.layers.5.encoder_attn`，真实whole-layer W_O后、residual前组合读出；随机对照L0由固定seed81001从非候选选取。同world两个recipient方向是相关记录，不是64个独立world。

| validation干预 | 独立world | 侧记录 | joint | 内容保持 | 解释 |
| --- | --- | --- | --- | --- | --- |
| L5 AA | 32 | 64 | 64/64 | 64/64 | 原生recipient |
| L5 BA / AB / BB | 32 | 各64 | 各0/64 | 各64/64 | 日期损坏；成对K/V本身不能恢复 |
| L0 AA / BA / AB / BB | 32 | 各64 | 各64/64 | 各64/64 | 同规模非候选比较 |
| L5固定head0 AA / BA / AB / BB | 32 | 各64 | 各64/64 | 各64/64 | 未将整层作用定位到该head |
| L5正常颜色V resampling | 32 | 64 | 0/64 | 0/64 | 内容损坏64/64，同时目标损坏49/64；组件混含目标信息 |
| 在线L5 KV_B | 16 | 32 | 0/32 | 32/32 | 保持recipient上游query时失败 |
| 在线L5 Q_B | 16 | 32 | 32/32 | 32/32 | donor query在recipient实际当前前缀在线重算 |
| 在线L5 QKV_B | 16 | 32 | 32/32 | 32/32 | 联合替换恢复；Q-only也恢复，所以不是唯一必要路径 |

正常颜色对照平均内容margin变化−3.4905072，符合预先validation内容依赖门槛，但目标损害76.5625%是保护该读出可能妨碍编辑的反证。没有声称内容专属head或完整唯一电路。query诊断使用donor及额外decoder forward；每一步只使用recipient实际前缀，没有注入完整gold未来激活。这个成本和信息条件不能包装为主方法推理。

原生projection self/no-op和在线self-query误差严格0，hook退出后清理。首次手算AV失败保留；新快照使用真实mask和native SDPA重放，局部AV误差0。手算AV误差最高2.71797e−5，从未注入。fused SDPA未物化attention probability；fixed-pattern只是被修改网络的prefix诊断，自由生成未运行项为NA。

桥接口径也做了更正：旧worker的`panel_B`实际存“下一步正确性XOR”，不符合计划B的“下一步结果不同”。从完整原始预测重新计算，BART validation生成token分叉256/256、正确性分叉192/256（32world×4pair×2操作）；T5Gemma分别31/32和0/32。旧记录不覆盖，正确新表在`next_edit_bridge_summary.csv`，更正见`BRIDGE_DEFINITION_CORRECTION.md`。仅输出分叉不证明某侧更好。


## Q2：无donor编辑及强对照

64 validation core worlds，每world12合法操作×自然/history两来源，扫描不以方法成功或当前正确筛样本；每来源768条，预定50/50加权。本批所有当前来源都正确，错误历史状态0/1536，不能声称已验证这类恢复。历史源11/12前驱为future_plus，1/12为past_minus，其方向覆盖局限保留。操作plus使相对日期减一天，minus加一天；历史P代号没有改成person。

| 方法 | seed | 联合成功 | 目标正确 | 非目标内容保持 | 平均有效update norm |
| --- | --- | --- | --- | --- | --- |
| Original | 42 | 768/1536 | 768/1536 | 770/1536 | 14.4767 |
| Plain | 42 | 1536/1536 | 1536/1536 | 1536/1536 | 12.2248 |
| Output-only | 42 | 1525/1536 | 1525/1536 | 1525/1536 | 11.3727 |
| Mechanism-guided | 42 | 1530/1536 | 1530/1536 | 1530/1536 | 9.7482 |
| Random-site | 42 | 1528/1536 | 1528/1536 | 1528/1536 | 10.1105 |
| Original | 43 | 768/1536 | 768/1536 | 768/1536 | 14.4662 |
| Plain | 43 | 1536/1536 | 1536/1536 | 1536/1536 | 14.2304 |
| Output-only | 43 | 1520/1536 | 1525/1536 | 1525/1536 | 12.5657 |
| Mechanism-guided | 43 | 1519/1536 | 1532/1536 | 1532/1536 | 10.0982 |
| Random-site | 43 | 1524/1536 | 1532/1536 | 1532/1536 | 9.8370 |
| Original | 44 | 768/1536 | 768/1536 | 769/1536 | 14.6004 |
| Plain | 44 | 1536/1536 | 1536/1536 | 1536/1536 | 14.1779 |
| Output-only | 44 | 1535/1536 | 1536/1536 | 1536/1536 | 12.6112 |
| Mechanism-guided | 44 | 1530/1536 | 1531/1536 | 1531/1536 | 10.7781 |
| Random-site | 44 | 1527/1536 | 1530/1536 | 1530/1536 | 10.2822 |

主编辑器只接收H、mask、请求操作，一次latent forward输出新memory；测试/validation推理不使用donor、目标全文、重新编码、decoder反传、逐样本优化或拒绝搜索。训练gold只用于loss，teacher分支stop-grad，student保留H→decoder梯度，backbone/history运行前后SHA相同。PCA/source resampling/在线query中的donor与额外decoder forward仅为机制诊断，不算无donor算法能力。

全部新方法rank16、50688参数、matched init/minibatch序列、400updates、effective batch16/microbatch2、AdamW lr0.001/weight_decay0/clip1、共同size权重0.001。seed42 Output-only按锁定的两个keep权重选择0.1，机制权重0.1由内容不低于Output-only−2pp之后联合成功选择；Random-site跟随相同0.1权重与固定非候选L0，未择其最差结果。未选m1.0的Random-site实际1535/1536，也完整保留，不能隐藏它。主export统一update400，update200辅助，不因长链或test重选。

Plain已完成的同预算训练、checkpoint及全量预测SHA匹配后复用，没有重复训练或重复GPU计费。每update Plain8 student forward/8 backward；其他方法额外8 teacher forward。更新数与参数相同不代表GPU时间相同：逐方法训练walltime、前反向次数、参数、单编辑forward时延、native decode时延分别在selected_training_costs和selected_inference_benchmark；总实际GPU-hours按allocation账本。扰动norm可能不同，训练前锁定范数bins完整报告，包括空bin的NA，不能把更小改动说成机制特异性。

## 机制增量比较的统计边界

20,000次paired core-world bootstrap，保留同world的全部来源/操作/固定三seed；下列百分点差值与区间均探索性validation，seed42同时用于选择，不能称确认性显著收益。主比较族两项Holm校正；其它比较仅探索性。每seedraw differences、分子/分母和world-level Wilson在完整JSON/CSV。

| 比较 | 差值（百分点） | CI95（百分点） | Holm p（validation探索性） |
| --- | --- | --- | --- |
| Mechanism-guided − Output-only | -0.0217 | [-0.2387, 0.1736] | 1.0 |
| Mechanism-guided − Random-site | 0.0000 | [-0.1302, 0.1085] | 1.0 |
| Output-only − Plain | -0.6076 | [-0.9332, -0.3255] | 探索性附加比较 |
| Random-site − Plain | -0.6293 | [-1.0417, -0.2604] | 探索性附加比较 |

vsPlain提升不证明机制有额外价值；只有vsOutput-only和vsRandom-site才对应增量及组件特异性。负差值、区间含0、目标/内容下降和所有失败均保留。KL/readout正则可能保护混含目标的层输出，S2已经观察到这种反证。选定checkpoint的事实不替代独立确认。

## 原子与长期能力

选定三种新方法的纯latent1/2/3/5步评测尚未进入终态，数字NA。旧Original/Plain结果见审批前报告；不能从新单操作结果推断长链。

## 原版T5Gemma

使用原google/t5gemma-2b-2b-ul2-it BF16，未替换模型。train16/16和validation16/16 world各获得一个严格E_future_plus:E_past_minus pair；不是主动构造搜索，不要求下一操作分叉。最大有效memory差值norm444.5026245，768 token-pair，最大JS3.7178426e−5。旧next-fork资格不适用于当前面板A。

下一步native token输出分叉train32/32、validation31/32；正确性XOR0/64，两边下一步都失败。分叉与更好分别报告，不重复计正确性。独立40world确认门槛未达到，正式test扫描0，因此目前独立机制复现不可估计；不能说一般同文本pair不存在。无本模型可核验PCA来源，没有移植BART hidden basis。T5Gemma后续S2/新编辑器三seed强对照和模型迁移均未完成。

## 资源、终态发布与复现

最新账本：20个allocation，总3.591667 GPU-hours，峰值2GPU；全部终态=True。预算40 GPU-hours，失败/重试计入，allocation计费不重复.batch/.extern/srun steps。最后实时队列以results/FINAL_QUEUE_AUDIT为准，不能以旧STATUS猜当前作业。

所有神经工作经唯一submit_stage→sbatch→srun，从不可变snapshot执行；没有登录节点神经工作或覆盖CUDA_VISIBLE_DEVICES。全项目外部锁/登记/squeue/sacct门禁最多两GPU，一个stage结束后才启动新array。所有新worktree、tmp/cache、环境尝试、checkpoint、日志、大产物和外部ledger在/dataset1/zailong/；原工作区/未提交历史未改。每terminal run全量记录独立核验、数字报告、commit/push/remote SHA核验，失败也发布。最后commit及远端回执在外部.decoder-readout-control-v1/final_receipt.json，避免commit内写自身SHA。

完整压缩逐样本记录、训练日志、排除原因和小editor checkpoint在reports；大缓存/activation路径、bytes、SHA在各ARTIFACTS，backbone不提交。root results保存全量聚合、paired raw differences与边界区间。CPU复算：main_results --summarize、trajectory_results、cpu_audit；图形重建figures/rebuild.py，图与依赖SHA在FIGURE_INDEX/PLOT_DEPENDENCIES。新图06/07/08展示所有方法、三seed纯latent链与实际训练成本/norm；旧03/04保留历史Plain参考，不混称最新主结果。

仍未完成：原128独立S4及S1/S2确认、真实模板OOD（不存在）、T5Gemma后续强对照、S5预调节器。测试终点修订需要显式决定，16例掩码批准不包含该决定；没有静默改成123或补样本。审批前报告保留在reports/DELIVERY_BEFORE_MASK_REVIEW_20261008.md，所有旧失败/负结果不覆盖。
