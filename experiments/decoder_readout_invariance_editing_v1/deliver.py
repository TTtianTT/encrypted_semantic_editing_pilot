"""CPU-only report writer for the actual blocked delivery, not a completion claim."""
from .common import *
from .metrics import wilson


def run():
    ledger=read(ROOT/'results/resource_ledger.json')
    assert ledger['all_terminal'] and ledger['peak_concurrent_GPUs']<=2
    audit=read(ROOT/'results/VALIDATION_NUMERICAL_AUDIT.json')
    withdrawal=read(ROOT/'configs/TEST_EXPOSURE_WITHDRAWAL_LOCK.json')
    hours=ledger['GPU_hours'];n_alloc=len(ledger['allocations'])
    failed=sum(r['state']=='FAILED' for r in ledger['allocations'])
    assert n_alloc==16 and failed==3 and withdrawal['exposed_count']==5
    atomic_table=[];chain_table=[]
    for seed in (42,43,44):
        base={r['method']:r for r in audit['atomic'] if r['seed']==seed and r['grouping']=='source' and r['source']=='all_50_50'}
        for method in ('Original','Plain'):
            r=base[method]
            atomic_table.append(f"| {method} | {seed} | {r['joint_numerator']}/1536 | {r['target_numerator']}/1536 | {r['content_numerator']}/1536 | {r['mean_update_norm']:.4f} |")
            ts={r['length']:r for r in audit['trajectories'] if r['seed']==seed and r['method']==method}
            chain_table.append('| '+method+' | '+str(seed)+' | '+' | '.join(str(ts[length]['complete_numerator'])+'/256' for length in (1,2,3,5))+' |')
    main='\n'.join(atomic_table);chain='\n'.join(chain_table)
    report=f'''# Decoder readout invariance editing v1 — 实际执行与阻塞报告

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
| L5固定head0 AA / BA / AB / BB | 32 | 各64 | 各64/64 | 各64/64 | 未将整层作用定位到该head |
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
{main}

各seed Original自然来源768/768、history0/768；Plain两来源均768/768。新editor每操作25344参数、共50688，rank16，effective batch16/microbatch2，AdamW lr0.001、size权重0.001、wd0、clip1，400updates，200/400小checkpoint均保存SHA。原操作plus使相对日期减一天、minus加一天，未凭名称改方向。训练/validation来源不包含test core；backbone和历史editor运行前后SHA相同、无参数梯度。

Plain在推理时输入只有H/mask/op，一次latent forward；无donor、目标全文、重编码、decoder反传、逐样本优化或rejection sampling。训练gold用于CE，evaluator gold不提供给editor。PCA、source resampling和在线Q替换的donor只属于诊断。

20,000次paired world-cluster bootstrap保留world内来源/操作/三seed，Plain−Original联合差值+50个百分点，探索性CI[50,50]；该退化区间不是真实效果已知无误。固定64world上“全部合法操作/两来源均正确”的Plain为64/64，单seed Wilson95约[94.3376%,100%]；Original为0/64，约[0%,5.6624%]。三seed只描述固定checkpoint，不能推断无限checkpoint总体。Original是历史冻结参考，没有相同新训练预算；Plain norm更小也可能有影响，不能由该比较推断机制价值。完整范数/来源/方向/状态/当前正确分层在CSV。

Output-only、Mechanism-guided、Random-site均NA（未训练），其主比较族和Holm校正p均NA。keep/mech损失代码已写，但除S0通用H梯度外，这些具体正则尚未经过正式GPU训练验收；S4 worker入口是未接通的原型，不能声称完整接口已验收。

## Q3及长期能力

自然起点、两种固定操作顺序及其逆方向；每seed256轨迹=64world×4，每步使用该方法自己产生的memory。完整成功要求所有前缀步骤正确，后续不替换gold state、不解码重编码。

| 方法 | seed | 1步 | 2步 | 3步 | 5步 |
| --- | --- | --- | --- | --- | --- |
{chain}

所有seed、两方法的3/5步完整成功均0/256；以world要求四条方向轨迹全正确，长度2/3/5均0/64，Wilson95[0,5.6624%]。Plain两步平均较Original提升约2.0833个百分点，探索性paired世界bootstrap CI[1.171875,3.125]个百分点；长度1/3/5差值0，边界bootstrap退化另给world区间。单操作能力没有在这64world受损，但长期仍失败；不能叫长期编辑解决。正式IID/模板OOD结果分别NA/UNAVAILABLE；reserved128不是OOD。

## 原版T5Gemma可估计性

模型为`google/t5gemma-2b-2b-ul2-it`，BF16；未静默换T5Gemma2/Gemma/270M。固定train16/16、validation16/16world找到E_future_plus:E_past_minus严格pair，每world1对；有效memory差值最大范数444.5026245，共768token-pair、最大JS3.7178426e−5。没有构造搜索，也不要求next fork。

下一步token分叉train32/32、validation31/32；两端联合编辑正确率均0/64侧对照记录，正确性分叉0/64。二者都失败仍可输出不同。因每split仅16独立world且正式test未扫描，独立机制复现是未运行、不可估计；不能说一般A配对不存在。来源P未提供：没有可核验本模型锁定PCA，未迁移BART basis；旧资格JSON的泛化“SOURCE_UNAVAILABLE_CONTENT_PROVENANCE_GUARD”标签在这32行实际指P缺失，非模型失败。模型S2与新方法训练/强对照尚未做。

## 资源、失败、发布和复现

16个allocation，其中13 COMPLETED、3技术FAILED；总**{hours:.6f} GPU-hours**，峰值**{ledger['peak_concurrent_GPUs']}GPU**，全部allocation终态。失败也按allocation AllocTRES×Elapsed计费，不重复累计.batch/.extern/srun steps。剩余预算{40-hours:.6f} GPU-hours；未完成是数据与人工review阻塞，不是用完配额。最终实时队列证明在`results/FINAL_QUEUE_AUDIT.json`；没有遗留受控作业。

所有模型工作实际经唯一submit_stage→sbatch array→srun worker；不可变科学快照与代码/数据/checkpoint SHA在manifests。受控作业各1GPU，array%2，跨stage全局锁/登记/squeue/sacct门禁，没有覆盖CUDA_VISIBLE_DEVICES。所有新worktree、环境尝试、tmp/cache、训练checkpoint、activation大产物、日志和外部ledger都在`/dataset1/zailong/`。原工作区仍在原分支、tracked diff为空；没有覆盖已有结果或main历史。

每个GPU终态已各自collect→数字报告→commit→push→ls-remote核验，失败也交付；seed43首次收集索引竞态的补交回执见`COLLECTION_RECEIPT_CORRECTION.md`，修复串行收集/发布锁，旧commit保留。最终commit及远端核验回执置于worktree外`{CONTROL}/final_receipt.json`，避免要求commit包含自身SHA。

CPU重算：`python -m experiments.decoder_readout_invariance_editing_v1.finalize`；完整资格/预测/排除/失败轨迹在reports/*.jsonl.gz，root聚合与20k bootstrap/raw world differences在results。五幅科研图见figures/FIGURE_INDEX.json，隔离绘图版本锁在manifests/PLOT_DEPENDENCIES.json。大tensor/cache不提交Git，ARTIFACTS.json给完整路径、bytes、SHA；小editor checkpoints已提交。实际提交命令保存在各*_registration.json；已终态stage再次submit为拒绝重复，无需重跑。

图1有限大扰动与随机曲线；图2原生传播观测（不是不同量纲L2收缩）；图3Original/Plain目标—内容比较并标其余方法NA；图4三seed纯latent1/2/3/5步；图5双向K/V与在线Q因果诊断。前四类要求都有可用数据或明确缺项，绝不填入未运行的新方法效果。

后续需要真实人工keep位置核验，以及对被破坏的预注册test终点作显式修订决定。只有新的独立协议可以改变确认终点，不能在现有报告中静默重分池。主方法强对照、独立确认、T5Gemma后续和预调节扩展都保留未完成状态。
'''
    text(ROOT/'FINAL_REPORT.md',report)
    status=f'''# 实际状态（2026-10-08）

整体 BLOCKED，未完成完整S0–S4研究。S0两模型通过；BART S1/S2探索机制完成部分项目；Plain三seed400updates及Original/Plain64world validation单操作/纯latent轨迹完成；T5Gemma一般SAME_TEXT 32探索world完成。

S3其他三方法 BLOCKED_MASK_REVIEW；S4 BLOCKED_TEST_INTEGRITY（5/128派生core已编码；不换split/不补搜）；S5 NOT_RUN_PREREQUISITES。机制增量收益NA。模板OOD UNAVAILABLE。

总{hours:.6f} GPU-hours、16 allocation（3失败），峰值2GPU，全部终态、实时队列无遗留任务。最终16CPU检查通过。所有新文件和临时/缓存/环境/产物位于 /dataset1/zailong/。详见FINAL_REPORT.md及各run稳定报告；推送SHA核验回执在外部ledger。
'''
    text(ROOT/'STATUS.md',status)
    text(ROOT/'INTERPRETATION.md','''# 解释与反证

大幅状态改变仍可留在相同离散argmax输出区域，概率不等价；有限路径出现中间失配/重入，否定全局线性nullspace或凸盆地解释。BART L5的K/V成对替换并不恢复，recipient实际前缀上的在线Q恢复可以恢复，支持上游query与memory配合。Q-only也有效；不能将QKV联合恢复称唯一必要完整电路。

正常颜色value替换证明局部内容依赖，同时伤害日期目标，说明正则可能保护目标信息。未训练Mechanism-guided/Output-only/Random-site，所以没有机制带来增量算法价值的估计。Plain仅说明本validation历史来源单操作可以用同架构复训改善；三/五步仍0，长期失败未解决。

T5Gemma E→E一般同文本pair存在，下一步生成token不同却两端都不正确，说明读出不变、输出分叉和成功提升是三件不同的测量。独立确认被数据完整性阻塞；不能把探索性32world称跨模型确认。
''')
    text(ROOT/'CLAIMS.md','''# Claim边界

| Claim | 状态 | 支持/反证 |
| --- | --- | --- |
| 有结构大幅memory改变可保持当前native文本 | 探索支持 | BART288pair，T5Gemma32pair；无独立test |
| 同文本意味着分布或内部状态等价 | 不支持 | BART最大JS0.0124072；T5Gemma非零JS |
| 大幅不敏感形成全局nullspace/凸盆地 | 反证 | alpha0.5失配、0.75重入 |
| decoder不读memory | 不支持 | L5替换损坏日期/内容 |
| K/V自身成对补偿即可解释 | 不支持 | L5 BB仍0/64 |
| 局部query/memory配合 | 探索支持 | 在线KV_B0/32、Q_B与QKV_B32/32；非唯一电路 |
| L5是非目标内容专属电路 | 不支持 | 正常颜色V替换也伤害目标49/64 |
| 固定head0解释整层替换效应 | 不支持 | 四条件均64/64当前成功，未定位该head |
| 机制正则胜过输出/随机正则 | NA未运行 | 三方法缺checkpoint，主检验族未执行 |
| Plain改善这批历史源单操作 | validation支持 | 每seedhistory0/768→768/768，冻结历史参考不是update-matched新对照 |
| 长期编辑已稳定 | 反证 | 三/五步均0/256 |
| T5Gemma没有一般同文本pair | 反证 | E→E32/32探索world严格资格 |
| 固定128world仍是完全独立确认 | 失效 | 5个派生core提前编码；0正式test评测不等于0暴露 |
''')
    text(ROOT/'PUBLICATION_NOTES.md','''# 发布与复现注意事项

推荐描述：探索性的decoder读出保持与query/memory干预，外加Plain三seed单操作validation和失败的长期latent轨迹。本文尚不能作为mechanism-guided editor优于输出约束的确认研究。

任何摘要须同时披露5/128test core派生暴露、人工内容mask review未收到、强对照尚未运行、只有validation结果、真实模板OOD不存在。bootstrap退化不能写为无不确定性。每seed64world内1536操作和256轨迹不是1536或256独立world；三seed不是随机checkpoint总体。PCA/donor/Q诊断含额外信息与计算，Plain推理仅一次latent forward。

原生HF/PyTorch、affine editor/parser精确版本与文件SHA见INPUTS；外部解释框架仅借鉴思路。没有SAE/transcoder/backbone训练、没有完整ALTI+或circuit-tracer移植。CPU绘图依赖隔离安装，许可证元数据见PLOT_DEPENDENCIES。原仓库许可政策需继承，论文引用不授权第三方代码。

从terminal报告的压缩全量预测重算：finalize模块、CSV和VALIDATION_NUMERICAL_AUDIT；raw/processed生成与head记录连接world/module/sample ID。传播图标observational；精确native替换仅称intervention_supported本地效应。大型产物只保存manifest、hash和local存储路径，小editor checkpoint随终态commit提交。所有路径位于/dataset1/zailong/。

worker不能修改Git。CPU collect/publish共享锁，终态结果逐run推送，禁止force-push/main merge。每个run的源码由immutable snapshot执行，修正另立run版本，旧失败保留。不声称重试调度/完整S4 evaluator已通过验收；当前自动重复提交是拒绝，技术断点恢复仅实现于训练与逐world缓存。
''')
    text(ROOT/'reports/BRIDGE_DEFINITION_CORRECTION.md','''# NEXT_EDIT_FORK口径更正

最初worker的panel_B错误存储“下一步联合成功的XOR”。计划B只要求A之上下一步结果不同。旧不可变run及字段不覆盖；从完整生成token重新计算，追加native_token_fork和legacy_accuracy_fork两列。

BART discovery32world：256/256 token分叉，192/256正确性分叉；validation同256/256与192/256；replay8world为64/64与48/64。T5Gemma train16world为32/32与0/32，validation16world为31/32与0/32。两端都失败时仍可发生输出分叉，不能由correctness XOR=0推断输出相同。

该CPU更正不改变A资格、不重新选择pair、不访问新test、不做模型运行。表与逐对来源见next_edit_bridge_recomputed.csv/summary.csv和BRIDGE_DEFINITION_AUDIT.json。T5Gemma资格记录中P缺失被泛化写成SOURCE_UNAVAILABLE_CONTENT_PROVENANCE_GUARD；实质是没有可核验本模型PCA，不能迁移BART basis。没有因此删除E→E pair。
''')
    for stage,reason in [('S3','BLOCKED_MASK_REVIEW'),('S4','BLOCKED_TEST_INTEGRITY')]:
        folder=ROOT/f'reports/BLOCKED_{stage}_20261008'
        s=read(ROOT/f'results/{stage}_SUBMISSION_STATUS.json')
        dump(folder/'RUN_STATUS.json',s | dict(model='bart',seeds=[42,43,44],job_id=None,
            exit_code=None,completed_samples=0,remaining_samples=None if stage=='S3' else 128,
            GPU_hours=0,allocation='NOT_SUBMITTED_CPU_PREFLIGHT',status=reason))
        text(folder/'REPORT.md',f'''# {stage} 阻塞终态

状态 {reason}；没有提交GPU作业，GPU-hours0。模型BART、计划seeds42/43/44；实际新方法完成0，预测/成功率NA，不记0%。

{('用户计划§6.2要求I_keep准确性人工抽查；16固定train例已在KEEP_MASK_REVIEW.md，未收到人类核验，不能创建reviewed_by_human=True。Plain三个seed已完成，不依赖此mask。剩余Output-only/Mechanism-guided/Random-site每方法三个seed未执行。' if stage=='S3' else '原扫描分母128，派生颜色对照提前编码5个IIDtest core；正式test评测0，未暴露剩123。split/IDs/hash不变，不补搜、不以123静默代替独立确认。组件/超参/全部方法checkpoint尚未齐备，也不能解封test。')}

本轮累计{hours:.6f} GPU-hours、峰值2；不是预算耗尽。科学代码/锁与完整更正见FINAL_REPORT.md。没有伪造训练完成或独立确认结论。
''')
        text(folder/'INTERPRETATION.md','阻塞是执行/数据完整性条件，不是该方法科学成功率0；未运行项NA。已执行探索性结果独立保留，不做隐式test修订。\n')
        inputs=[ROOT/f'results/{stage}_SUBMISSION_STATUS.json',ROOT/'configs/SPLIT_LOCK.json',
            ROOT/('reports/KEEP_MASK_REVIEW.md' if stage=='S3' else 'configs/TEST_EXPOSURE_WITHDRAWAL_LOCK.json')]
        dump(folder/'ARTIFACTS.json',[dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size) for p in inputs])
    audit_path=ROOT/'AUDIT.md';s=audit_path.read_text()
    s+='\n## 最终实际审计更正\n\n初始划分无历史core交叉；但派生颜色donor最初无core门禁，5个test/2个reserved core被编码，独立终点BLOCKED，详细更正见FINAL_REPORT和DATA_EXPOSURE_CORRECTION。正式test评分0不等于神经暴露0。源数据512/splitSHA保留，不静默补池。\n\n实际shard：S0/T5资格1小时上限、PARITY15分钟、其他3小时；不是所有shard1小时。累计2.3925 GPU-hours、16allocation，三失败均保留，峰值2，全部终态。原环境未升级，CPU绘图另有prefix内隔离依赖；临时目录先前/tmp尝试已迁入local/environment_attempts，无本任务残留/tmp目录。最终CPU16项通过。所有大产物/执行快照/日志/缓存和外部ledger位于/dataset1/zailong/。\n'
    text(audit_path,s)
    for name in ('S1_READOUT_REPORT.md','S2_CAUSAL_REPORT.md'):
        p=ROOT/name;text(p,p.read_text()+'\n最终更正：正式独立test评测仍0，但5个IIDtest core已被派生颜色donor编码；不能再称全128未暴露。独立确认BLOCKED_TEST_INTEGRITY，见FINAL_REPORT和DATA_EXPOSURE_CORRECTION；桥接panel_B按实际next token不同重新计算，旧correctness XOR单列。\n')
    p=ROOT/'README.md';s=p.read_text()
    s+='\n本轮实际结果与阻塞见 [FINAL_REPORT](FINAL_REPORT.md)。S0两模型通过；BART机制为探索性局部query/memory配合；Plain三seed单操作validation1536/1536但三/五步0/256；T5Gemma32探索world一般严格pair存在。其他三训练方法NA，S4因5个test core派生暴露阻塞；没有完成完整计划。\n\nCPU重算：`python -m experiments.decoder_readout_invariance_editing_v1.finalize`。绘图：`PYTHONPATH=experiments/decoder_readout_invariance_editing_v1/local/analysis_deps python experiments/decoder_readout_invariance_editing_v1/figures/rebuild.py`；依赖只用于绘图、不升级原环境。重新prepare S3_SELECT/S4会输出可审计阻塞状态，不能用于绕开review或test完整性门禁。\n'
    text(p,s)
    print(dict(status='BLOCKED',GPU_hours=hours,allocations=n_alloc,failed=failed))


if __name__=='__main__':run()
