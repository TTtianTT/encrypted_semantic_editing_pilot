# Decoder readout invariance editing v1 — 实际执行与阻塞报告

2026-10-08，Asia/Singapore。分支 `experiment/decoder-readout-invariance-editing-v1`。

**本轮没有完成完整研究计划。** 已实际执行两模型S0、BART探索性S1/S2、三个seed的Plain正式复训与validation纯latent轨迹、原版T5Gemma小规模重新资格核验。Output-only、Mechanism-guided、Random-site未训练；独立S4没有执行。机制增量算法收益为NA，不能写成正结果，也不能写成“机制无收益”的负结果。

## 完成范围和不可越过的阻塞

| 阶段 | 实际完成 | 边界/未完成 |
| --- | --- | --- |
| 审计/CPU | 初始远端HEAD、1321历史文件SHA、21分支暴露扫描、固定512world划分；最终16 CPU检查 | 派生donor core门禁最初遗漏，已补审计并如实记录泄漏 |
| S0 | BART FP32、原版T5Gemma BF16 native注入/梯度/8world过拟合通过 | 可选eager对齐失败；没有采用该路径 |
| S1 BART | train32、validation32、旧replay8；288严格pair，有限路径/随机对照/源与前缀/传播/raw-vs-processor额外验收 | 探索性；独立test确认、多token语义候选序列log-prob尚未完成 |
| S2 BART | 全层discovery筛选；L5/L0层与固定head0双向K/V；实际SDPA固定pattern诊断；在线Q补充 | 只支持局部机制；未进行独立test、top2联合/frozen-normalization诊断或完整电路枚举 |
| S3 | Plain rank16 seeds42/43/44，每seed192train、400updates；64validation无筛选C与纯latent轨迹 | keep/mech内容mask人工抽查未收到，其他三方法及超参选择未运行 |
| S4 | 仅CPU阻塞审计，正式test评测0 | `BLOCKED_TEST_INTEGRITY`；原定128world独立终点失效 |
| T5Gemma | S0；train16、validation16一般SAME_TEXT核验及逐token概率 | 每split仅16world；独立资格不可估计；S2/三个seed强对照/迁移评测未运行 |
| S5预调节器 | 未运行 | `NOT_RUN_PREREQUISITES`；主结果未完成，不能称预算耗尽 |

用户计划§6.2要求“`I_keep` 的准确性必须人工抽查”。16个固定train样本已整理在 [KEEP_MASK_REVIEW](reports/KEEP_MASK_REVIEW.md)，没有收到人类核验；`KEEP_MASK_REVIEW_LOCK.json`不存在，不能伪造。Plain只用CE+size，不使用此mask，因此能够完成。

我在初版源颜色对照中遗漏了派生core检查：S1/S2为正常颜色value resampling编码的core，碰到固定IID test中的5/128，以及reserved中的2个core。虽然正式test输出评测仍为0，已不能说全部128是未暴露的独立world。完整ID/证据见 [数据暴露更正](reports/DATA_EXPOSURE_CORRECTION.md)、`COUNTERFACTUAL_EXPOSURE_AUDIT.json` 和 `TEST_EXPOSURE_WITHDRAWAL_LOCK.json`。划分SHA和world IDs保留；不补搜，不把剩余123静默改成新主终点。新门禁在编码前拒绝test/reserved core。S3/S4阻塞终态分别发布，GPU-hours0。

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
| L5正常颜色V resampling | 32 | 64 | 0/64 | 0/64 | 内容损坏64/64，同时目标损坏49/64；组件混含目标信息 |
| 在线L5 KV_B | 16 | 32 | 0/32 | 32/32 | 保持recipient上游query时失败 |
| 在线L5 Q_B | 16 | 32 | 32/32 | 32/32 | donor query在recipient实际当前前缀在线重算 |
| 在线L5 QKV_B | 16 | 32 | 32/32 | 32/32 | 联合替换恢复；Q-only也恢复，所以不是唯一必要路径 |

正常颜色对照平均内容margin变化−3.4905072，符合预先validation内容依赖门槛，但目标损害76.5625%是保护该读出可能妨碍编辑的反证。没有声称内容专属head或完整唯一电路。query诊断使用donor及额外decoder forward；每一步只使用recipient实际前缀，没有注入完整gold未来激活。这个成本和信息条件不能包装为主方法推理。

原生projection self/no-op和在线self-query误差严格0，hook退出后清理。首次手算AV失败保留；新快照使用真实mask和native SDPA重放，局部AV误差0。手算AV误差最高2.71797e−5，从未注入。fused SDPA未物化attention probability；fixed-pattern只是被修改网络的prefix诊断，自由生成未运行项为NA。

桥接口径也做了更正：旧worker的`panel_B`实际存“下一步正确性XOR”，不符合计划B的“下一步结果不同”。从完整原始预测重新计算，BART validation生成token分叉256/256、正确性分叉192/256（32world×4pair×2操作）；T5Gemma分别31/32和0/32。旧记录不覆盖，正确新表在`next_edit_bridge_summary.csv`，更正见`BRIDGE_DEFINITION_CORRECTION.md`。仅输出分叉不证明某侧更好。

## Q2：实际编辑结果及强对照缺项

以下全部是64world **validation**，不是独立test。单操作每world12合法操作×2来源，分母1536；自然/history各768。历史来源为已核验冻结编辑器产生的规定一族状态，11/12前驱方向是future_plus、1/12为past_minus，覆盖不完整。本批当前错误状态实际为0/1536；规则并未按正确性过滤，但不能声称已验证错误历史源恢复。

| 方法 | seed | 联合成功 | 目标正确 | 非目标内容保持 | 平均有效扰动norm |
| --- | --- | --- | --- | --- | --- |
| Original | 42 | 768/1536 | 768/1536 | 770/1536 | 14.4767 |
| Plain | 42 | 1536/1536 | 1536/1536 | 1536/1536 | 12.2248 |
| Original | 43 | 768/1536 | 768/1536 | 768/1536 | 14.4662 |
| Plain | 43 | 1536/1536 | 1536/1536 | 1536/1536 | 14.2304 |
| Original | 44 | 768/1536 | 768/1536 | 769/1536 | 14.6004 |
| Plain | 44 | 1536/1536 | 1536/1536 | 1536/1536 | 14.1779 |

各seed Original自然来源768/768、history0/768；Plain两来源均768/768。新editor每操作25344参数、共50688，rank16，effective batch16/microbatch2，AdamW lr0.001、size权重0.001、wd0、clip1，400updates，200/400小checkpoint均保存SHA。原操作plus使相对日期减一天、minus加一天，未凭名称改方向。训练/validation来源不包含test core；backbone和历史editor运行前后SHA相同、无参数梯度。

Plain在推理时输入只有H/mask/op，一次latent forward；无donor、目标全文、重编码、decoder反传、逐样本优化或rejection sampling。训练gold用于CE，evaluator gold不提供给editor。PCA、source resampling和在线Q替换的donor只属于诊断。

20,000次paired world-cluster bootstrap保留world内来源/操作/三seed，Plain−Original联合差值+50个百分点，探索性CI[50,50]；该退化区间不是真实效果已知无误。固定64world上“全部合法操作/两来源均正确”的Plain为64/64，单seed Wilson95约[94.3376%,100%]；Original为0/64，约[0%,5.6624%]。三seed只描述固定checkpoint，不能推断无限checkpoint总体。Original是历史冻结参考，没有相同新训练预算；Plain norm更小也可能有影响，不能由该比较推断机制价值。完整范数/来源/方向/状态/当前正确分层在CSV。

Output-only、Mechanism-guided、Random-site均NA（未训练），其主比较族和Holm校正p均NA。keep/mech损失代码已写，但除S0通用H梯度外，这些具体正则尚未经过正式GPU训练验收；S4 worker入口是未接通的原型，不能声称完整接口已验收。

## Q3及长期能力

自然起点、两种固定操作顺序及其逆方向；每seed256轨迹=64world×4，每步使用该方法自己产生的memory。完整成功要求所有前缀步骤正确，后续不替换gold state、不解码重编码。

| 方法 | seed | 1步 | 2步 | 3步 | 5步 |
| --- | --- | --- | --- | --- | --- |
| Original | 42 | 256/256 | 0/256 | 0/256 | 0/256 |
| Plain | 42 | 256/256 | 9/256 | 0/256 | 0/256 |
| Original | 43 | 256/256 | 0/256 | 0/256 | 0/256 |
| Plain | 43 | 256/256 | 0/256 | 0/256 | 0/256 |
| Original | 44 | 256/256 | 0/256 | 0/256 | 0/256 |
| Plain | 44 | 256/256 | 7/256 | 0/256 | 0/256 |

所有seed、两方法的3/5步完整成功均0/256；以world要求四条方向轨迹全正确，长度2/3/5均0/64，Wilson95[0,5.6624%]。Plain两步平均较Original提升约2.0833个百分点，探索性paired世界bootstrap CI[1.171875,3.125]个百分点；长度1/3/5差值0，边界bootstrap退化另给world区间。单操作能力没有在这64world受损，但长期仍失败；不能叫长期编辑解决。正式IID/模板OOD结果分别NA/UNAVAILABLE；reserved128不是OOD。

## 原版T5Gemma可估计性

模型为`google/t5gemma-2b-2b-ul2-it`，BF16；未静默换T5Gemma2/Gemma/270M。固定train16/16、validation16/16world找到E_future_plus:E_past_minus严格pair，每world1对；有效memory差值最大范数444.5026245，共768token-pair、最大JS3.7178426e−5。没有构造搜索，也不要求next fork。

下一步token分叉train32/32、validation31/32；两端联合编辑正确率均0/64侧对照记录，正确性分叉0/64。二者都失败仍可输出不同。因每split仅16独立world且正式test未扫描，独立机制复现是未运行、不可估计；不能说一般A配对不存在。来源P未提供：没有可核验本模型锁定PCA，未迁移BART basis；旧资格JSON的泛化“SOURCE_UNAVAILABLE_CONTENT_PROVENANCE_GUARD”标签在这32行实际指P缺失，非模型失败。模型S2与新方法训练/强对照尚未做。

## 资源、失败、发布和复现

16个allocation，其中13 COMPLETED、3技术FAILED；总**2.392500 GPU-hours**，峰值**2GPU**，全部allocation终态。失败也按allocation AllocTRES×Elapsed计费，不重复累计.batch/.extern/srun steps。剩余预算37.607500 GPU-hours；未完成是数据与人工review阻塞，不是用完配额。最终实时队列证明在`results/FINAL_QUEUE_AUDIT.json`；没有遗留受控作业。

所有模型工作实际经唯一submit_stage→sbatch array→srun worker；不可变科学快照与代码/数据/checkpoint SHA在manifests。受控作业各1GPU，array%2，跨stage全局锁/登记/squeue/sacct门禁，没有覆盖CUDA_VISIBLE_DEVICES。所有新worktree、环境尝试、tmp/cache、训练checkpoint、activation大产物、日志和外部ledger都在`/dataset1/zailong/`。原工作区仍在原分支、tracked diff为空；没有覆盖已有结果或main历史。

每个GPU终态已各自collect→数字报告→commit→push→ls-remote核验，失败也交付；seed43首次收集索引竞态的补交回执见`COLLECTION_RECEIPT_CORRECTION.md`，修复串行收集/发布锁，旧commit保留。最终commit及远端核验回执置于worktree外`/dataset1/zailong/workspace/encrypted_semantic_editing_pilot/.decoder-readout-control-v1/final_receipt.json`，避免要求commit包含自身SHA。

CPU重算：`python -m experiments.decoder_readout_invariance_editing_v1.finalize`；完整资格/预测/排除/失败轨迹在reports/*.jsonl.gz，root聚合与20k bootstrap/raw world differences在results。五幅科研图见figures/FIGURE_INDEX.json，隔离绘图版本锁在manifests/PLOT_DEPENDENCIES.json。大tensor/cache不提交Git，ARTIFACTS.json给完整路径、bytes、SHA；小editor checkpoints已提交。实际提交命令保存在各*_registration.json；已终态stage再次submit为拒绝重复，无需重跑。

图1有限大扰动与随机曲线；图2原生传播观测（不是不同量纲L2收缩）；图3Original/Plain目标—内容比较并标其余方法NA；图4三seed纯latent1/2/3/5步；图5双向K/V与在线Q因果诊断。前四类要求都有可用数据或明确缺项，绝不填入未运行的新方法效果。

后续需要真实人工keep位置核验，以及对被破坏的预注册test终点作显式修订决定。只有新的独立协议可以改变确认终点，不能在现有报告中静默重分池。主方法强对照、独立确认、T5Gemma后续和预调节扩展都保留未完成状态。
