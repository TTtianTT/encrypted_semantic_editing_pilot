"""CPU report from audited full records after the human mask review."""
from .common import *


def percent(value):return f'{100*value:.4f}%'


def write_report():
    atomic_audit=read(ROOT/'results/SELECTED_VALIDATION_NUMERICAL_AUDIT.json')
    trajectory_path=ROOT/'results/SELECTED_TRAJECTORY_NUMERICAL_AUDIT.json'
    trajectory=read(trajectory_path) if trajectory_path.exists() else None
    resources=read(ROOT/'results/resource_ledger.json')
    review=read(ROOT/'configs/KEEP_MASK_REVIEW_LOCK.json')
    predicted=read(ROOT/'results/PREDICTED_CORE_EXPOSURE_AUDIT.json') if (ROOT/'results/PREDICTED_CORE_EXPOSURE_AUDIT.json').exists() else {}
    additional=predicted.get('additional_test_cores',[])
    closure_path=ROOT/'configs/FINAL_EXPOSURE_LOCK.json'
    closure=read(closure_path) if closure_path.exists() else None
    exposure_description=(f"完整保守审计已确认原test共{closure['known_exposed_count']}/128个core暴露，{closure['not_known_exposed_count']}/128暂未发现暴露；后者只是审计分类，不是已授权终点。历史原始输出审计覆盖{closure['historical_refs']}个冻结ref、{closure['historical_files']}个SHA去重文件、{closure['historical_string_fields']}个字符串字段，解析错误{len(closure['parse_errors'])}。完整union ID、原文、文件/branch/blob SHA、prior train/validation匹配及审计范围见FINAL_EXPOSURE_LOCK与压缩历史审计。" if closure else '完整跨分支原始输出审计仍在运行，暂不提出缩减test分母。')
    assert review['reviewed_by_human']
    methods=atomic_audit['methods'];atomic_table=[]
    for seed in (42,43,44):
        for method in methods:
            r=next(x for x in atomic_audit['atomic'] if x['seed']==seed and x['method']==method and x['grouping']=='source' and x['source']=='all_50_50')
            atomic_table.append(f"| {method} | {seed} | {r['joint_numerator']}/1536 | {r['target_numerator']}/1536 | {r['content_numerator']}/1536 | {r['mean_update_norm']:.4f} |")
    comparisons=[]
    for r in atomic_audit['comparisons']:
        comparisons.append(f"| {r['a']} − {r['b']} | {100*r['estimate']:.4f} | [{100*r['CI95'][0]:.4f}, {100*r['CI95'][1]:.4f}] | {r.get('Holm_adjusted_p','探索性附加比较')} |")
    old=(ROOT/'reports/DELIVERY_BEFORE_MASK_REVIEW_20261008.md').read_text()
    mechanism=old.split('## Q1：')[1].split('## Q2：')[0]
    mechanism='## Q1：'+mechanism
    if trajectory:
        chains=[]
        for seed in (42,43,44):
            for method in methods:
                nums=[next(r['complete_numerator'] for r in trajectory['trajectories'] if r['seed']==seed and r['method']==method and r['length']==length) for length in (1,2,3,5)]
                chains.append('| '+method+' | '+str(seed)+' | '+' | '.join(f'{n}/256' for n in nums)+' |')
        long_section='''## 原子与长期能力

64 validation worlds，每world两个固定操作顺序及两个方向。全部从自然起点出发，后续只使用各方法自己的latent输出，不重置gold state。完整轨迹要求每个步骤正确，不能以最后一步替代整链成功。Original/Plain旧轨迹和checkpoint/hash匹配后复用，原allocation已经计费。

| 方法 | seed | 1步 | 2步 | 3步 | 5步 |
| --- | --- | --- | --- | --- | --- |
'''+ '\n'.join(chains)+'''

逐步target/content/parse/EOS、顺序/逆方向、20,000次paired world-cluster差值和原始world differences见SELECTED_TRAJECTORY_NUMERICAL_AUDIT与CSV。每seed每长度256条相关轨迹对应64独立core world；另给“同world四条轨迹全部成功”的Wilson区间，避免0/100% bootstrap退化被解读为确定总体效果。三seed只代表已锁定checkpoint。单操作提升不能写成长期编辑解决，validation上的长链差异也不能写成独立test证据。

两步Mechanism-guided的seed42/43/44分别为0/124/7，Output-only为0/19/55，Random-site为0/66/54，分母各256。机制方法优势集中在seed43的forward方向（两种顺序64/64和60/64）；该seed inverse方向均0/64，seed44则低于两种强对照。三seed固定checkpoint均值差：vsOutput-only +7.421875百分点，world-cluster CI95 [5.859375,8.984375]；vsRandom-site +1.432292百分点，CI95 [0.130208,2.734375]。这些区间没有反映新训练seed总体的不确定性，不能从均值写成seed稳定收益。所有方法所有seed的三步和五步均0/256；“同world四条两步轨迹全部成功”也均0/64，Wilson95上界约5.6624%。

补充posthoc范数诊断复播19,200个已锁定latent步骤，首world共300次stored预测复核全部一致，算法/checkpoint不变。第二步机制平均update norm随seed为8.2915/8.9968/9.1566，Output-only为10.0234/11.5681/10.6247，Random-site为8.4981/8.4287/8.6517；幅度不同且成功差值随seed变号。预锁norm bins及完整有效token范数已报告，这些分层是描述性证据，不是随机化的等范数算法因果对照。
'''
    else:long_section='## 原子与长期能力\n\n选定三种新方法的纯latent1/2/3/5步评测尚未进入终态，数字NA。旧Original/Plain结果见审批前报告；不能从新单操作结果推断长链。\n'
    report=f'''# Decoder readout invariance editing v1：实际结果与限制

2026-10-08，Asia/Singapore；分支experiment/decoder-readout-invariance-editing-v1。用户确认“16例抽查通过”后，已完成具体KL/readout正则GPU梯度与8world过拟合验收，以及BART rank16四方法三个seed正式训练和全量validation单操作评测。此确认只解除I_keep人工抽查门槛，未授权变更独立test。

**完整研究计划仍未完成：独立S4为BLOCKED_TEST_INTEGRITY，正式test评测0。** 全部本轮方法比较是validation探索性证据。此前源颜色对照派生core漏检，提前编码了固定IID test的5/128 core；另经全量输出文本核验，T5Gemma下一操作输出还出现{len(additional)}个额外test core：{', '.join(additional) or '暂无'}。正式test评测0不等于所有core未暴露。已保存暴露ID/原文/出处、原split SHA与门禁修复；不补搜，不静默改分母。原123提案因额外输出暴露已撤回，不能按旧提案批准解封；任何新终点都需要另行锁定和显式决定。见DATA_EXPOSURE_CORRECTION、PREDICTED_CORE_EXPOSURE_AUDIT和S4_AMENDMENT_PROPOSAL。

{exposure_description}

历史输出还出现13个train core及1个validation core（drie_6aee5bf620ba0936），原先只查含domain字段的world元数据不足以识别这些输出暴露。保留原192/64划分及已训练checkpoint，逐core登记先前暴露，不将它们改称本轮全新独立样本；现有validation结果均为探索性。实际可访问输出的完整原文与SHA保留，未访问文件、未记录会话或不符合解析文法的表达仍不能保证无暴露。

## 完成范围

| 阶段 | 实际执行 | 仍缺失 |
| --- | --- | --- |
| 审计/CPU | 原分支HEAD、1321文件SHA、21分支元数据及完整可访问输出审计、固定train192/val64/test128/reserved128；真实人工16例通过 | 原test已知暴露{'12' if closure else '至少8'}/128；原128独立终点已破坏；OOD为UNAVAILABLE |
| S0 | BART FP32与原版T5Gemma BF16；memory注入、native无干预一致、mask/EOS/KV、H梯度、冻结参数、8world smoke通过 | 可选eager对齐失败已保留，不采用 |
| S1 BART | train32/val32/旧replay8，共288严格pair、概率/有限路径/随机/源前缀/传播/真实generation scores | 独立机制确认及完整多token语义候选log-prob未完成 |
| S2 BART | 全层discovery、固定L5/L0整层与head0双向K/V、native SDPA诊断、在线Q替换 | 无完整/唯一稀疏电路；未独立确认，top2/frozen-norm扩展未运行 |
| S3 BART | Plain/Output-only/Mechanism-guided/Random-site，seed42/43/44，192train/64val，400updates；keep/mech网格锁定 | validation不等于独立test；历史错误当前状态实际无覆盖 |
| validation长链 | {'四方法及Original全量1/2/3/5步已完成' if trajectory else '选定新方法运行待结束'} | 独立IID链与真实OOD未执行 |
| S4 | CPU暴露审计和阻塞报告 | BLOCKED_TEST_INTEGRITY；没有隐式修改分母 |
| T5Gemma | 原google/t5gemma-2b-2b-ul2-it BF16，S0及train16/val16一般SAME_TEXT小规模分析 | 每split16world，独立确认不可估计；新方法强对照未运行 |
| S5预调节 | 未运行 | NOT_RUN_PREREQUISITES；S0–S4主结果未完成，不是GPU配额耗尽 |

{mechanism}
## Q2：无donor编辑及强对照

64 validation core worlds，每world12合法操作×自然/history两来源，扫描不以方法成功或当前正确筛样本；每来源768条，预定50/50加权。本批所有当前来源都正确，错误历史状态0/1536，不能声称已验证这类恢复。历史源11/12前驱为future_plus，1/12为past_minus，其方向覆盖局限保留。操作plus使相对日期减一天，minus加一天；历史P代号没有改成person。

| 方法 | seed | 联合成功 | 目标正确 | 非目标内容保持 | 平均有效update norm |
| --- | --- | --- | --- | --- | --- |
{chr(10).join(atomic_table)}

主编辑器只接收H、mask、请求操作，一次latent forward输出新memory；测试/validation推理不使用donor、目标全文、重新编码、decoder反传、逐样本优化或拒绝搜索。训练gold只用于loss，teacher分支stop-grad，student保留H→decoder梯度，backbone/history运行前后SHA相同。PCA/source resampling/在线query中的donor与额外decoder forward仅为机制诊断，不算无donor算法能力。

全部新方法rank16、50688参数、matched init/minibatch序列、400updates、effective batch16/microbatch2、AdamW lr0.001/weight_decay0/clip1、共同size权重0.001。seed42 Output-only按锁定的两个keep权重选择0.1，机制权重0.1由内容不低于Output-only−2pp之后联合成功选择；Random-site跟随相同0.1权重与固定非候选L0，未择其最差结果。未选m1.0的Random-site实际1535/1536，也完整保留，不能隐藏它。主export统一update400，update200辅助，不因长链或test重选。

Plain已完成的同预算训练、checkpoint及全量预测SHA匹配后复用，没有重复训练或重复GPU计费。每update Plain8 student forward/8 backward；其他方法额外8 teacher forward。更新数与参数相同不代表GPU时间相同：逐方法训练walltime、前反向次数、参数、单编辑forward时延、native decode时延分别在selected_training_costs和selected_inference_benchmark；总实际GPU-hours按allocation账本。扰动norm可能不同，训练前锁定范数bins完整报告，包括空bin的NA，不能把更小改动说成机制特异性。

## 机制增量比较的统计边界

20,000次paired core-world bootstrap，保留同world的全部来源/操作/固定三seed；下列百分点差值与区间均探索性validation，seed42同时用于选择，不能称确认性显著收益。主比较族两项Holm校正；其它比较仅探索性。每seedraw differences、分子/分母和world-level Wilson在完整JSON/CSV。

| 比较 | 差值（百分点） | CI95（百分点） | Holm p（validation探索性） |
| --- | --- | --- | --- |
{chr(10).join(comparisons)}

vsPlain提升不证明机制有额外价值；只有vsOutput-only和vsRandom-site才对应增量及组件特异性。负差值、区间含0、目标/内容下降和所有失败均保留。KL/readout正则可能保护混含目标的层输出，S2已经观察到这种反证。选定checkpoint的事实不替代独立确认。

单操作主终点没有发现机制增量：三seed合并Mechanism-guided4579/4608（99.3707%），Output-only4580/4608（99.3924%），Random-site4579/4608（99.3707%），Plain4608/4608（100%）。Mechanism−Output −0.021701百分点，CI95 [−0.238715,0.173611]；Mechanism−Random约0，CI95 [−0.130208,0.108507]。相比Original各seed768/1536，四种新方法保留明显原子改善；相对Plain，加入正则出现少量目标/内容失败，不能描述成原子能力完全无损。

{long_section}
## 原版T5Gemma

使用原google/t5gemma-2b-2b-ul2-it BF16，未替换模型。train16/16和validation16/16 world各获得一个严格E_future_plus:E_past_minus pair；不是主动构造搜索，不要求下一操作分叉。最大有效memory差值norm444.5026245，768 token-pair，最大JS3.7178426e−5。旧next-fork资格不适用于当前面板A。

下一步native token输出分叉train32/32、validation31/32；正确性XOR0/64，两边下一步都失败。分叉与更好分别报告，不重复计正确性。独立40world确认门槛未达到，正式test扫描0，因此目前独立机制复现不可估计；不能说一般同文本pair不存在。无本模型可核验PCA来源，没有移植BART hidden basis。T5Gemma后续S2/新编辑器三seed强对照和模型迁移均未完成。

## 资源、终态发布与复现

最新账本：{len(resources['allocations'])}个allocation，总{resources['GPU_hours']:.6f} GPU-hours，峰值{resources['peak_concurrent_GPUs']}GPU；全部终态={resources['all_terminal']}。预算40 GPU-hours，失败/重试计入，allocation计费不重复.batch/.extern/srun steps。最后实时队列以results/FINAL_QUEUE_AUDIT为准，不能以旧STATUS猜当前作业。

FINAL_QUEUE_AUDIT区分受控作业与用户其他项目作业：本实验remaining_controlled_jobs为空；外部srf-response作业3053使用一GPU、不在本调度器登记表中，未取消，其启动19:51:16晚于本实验最后allocation结束19:46:05，未与最后两GPU核验批次重叠。外部作业不计入本轮GPU-hours，不宣称用户账户全部队列为空。

所有神经工作经唯一submit_stage→sbatch→srun，从不可变snapshot执行；没有登录节点神经工作或覆盖CUDA_VISIBLE_DEVICES。全项目外部锁/登记/squeue/sacct门禁最多两GPU，一个stage结束后才启动新array。所有新worktree、tmp/cache、环境尝试、checkpoint、日志、大产物和外部ledger在/dataset1/zailong/；原工作区/未提交历史未改。每terminal run全量记录独立核验、数字报告、commit/push/remote SHA核验，失败也发布。最后commit及远端回执在外部.decoder-readout-control-v1/final_receipt.json，避免commit内写自身SHA。

完整压缩逐样本记录、训练日志、排除原因和小editor checkpoint在reports；大缓存/activation路径、bytes、SHA在各ARTIFACTS，backbone不提交。root results保存全量聚合、paired raw differences与边界区间。CPU复算：main_results --summarize、trajectory_results、cpu_audit；图形重建figures/rebuild.py，图与依赖SHA在FIGURE_INDEX/PLOT_DEPENDENCIES。新图06/07/08展示所有方法、三seed纯latent链与实际训练成本/norm；旧03/04保留历史Plain参考，不混称最新主结果。

仍未完成：原128独立S4及S1/S2确认、真实模板OOD（不存在）、T5Gemma后续强对照、S5预调节器。测试终点修订需要显式决定，16例掩码批准不包含该决定；没有静默改成123或补样本。审批前报告保留在reports/DELIVERY_BEFORE_MASK_REVIEW_20261008.md，所有旧失败/负结果不覆盖。
'''
    text(ROOT/'FINAL_REPORT.md',report)
    text(ROOT/'STATUS.md',f"# 当前执行状态\n\nBART四方法三seed训练与完整validation单操作已完成，用户16例mask验收及GPU正则验收通过。长链：{'全部终态，已全量重算' if trajectory else '运行待终态'}。最新资源{resources['GPU_hours']:.6f}GPU-hours，峰值{resources['peak_concurrent_GPUs']}。\n\n独立S4仍BLOCKED_TEST_INTEGRITY，正式test评测0；未授权改终点。T5Gemma仅S0/小规模探索，扩展未完成。完整数字和局限见FINAL_REPORT.md；审批前交付已归档。\n")
    text(ROOT/'INTERPRETATION.md','当前相同native文本主要支持离散argmax容忍，不支持分布/内部状态相同。原生L5整层K/V替换和在线Q干预支持局部query-memory配合；固定head0阴性、Q-only亦恢复、正常颜色resampling同时损坏目标均限制完整/专属电路claim。四种新方法只有validation结果，必须按vsOutput-only/vsRandom-site的paired world差值和区间判断探索性增量，不能以vsPlain或选择分数宣称确认性机制收益。长链要求每步成功，单操作不能替代。原128独立test不可维持，保持阻塞与暴露记录，不改分母。\n')
    text(ROOT/'PUBLICATION_NOTES.md','本轮可发表材料是native encoder-memory读出与局部因果干预、全量匹配训练的validation正/负结果，以及明确的数据完整性错误。不得声称独立机制编辑确认、全局语义零空间、唯一完整电路、错误历史状态恢复或长期编辑解决。正式test评测0；已知编码、生成及历史输出core暴露合并见FINAL_EXPOSURE_LOCK，123提案已撤回，无已授权修订终点。本轮现有validation不改名独立test。单操作机制方法未超过Output-only/Random-site；两步均值优势随seed/方向变号，三/五步均0。完整原始预测、失败、成本、三seed和norm差异公开，旧终态报告不覆盖。\n')
    text(ROOT/'CLAIMS.md','| Claim | Evidence/status | Limit |\n| --- | --- | --- |\n| Large memory changes retain current native text | BART discovery/validation/replay | Probabilities change; finite paths nonmonotonic; no global nullspace |\n| Local query/memory interaction affects current readout | Exact whole-layer L5 K/V and online-Q interventions | Fixed head0 negative; Q-only also restores; mixed target/content; no unique circuit |\n| Small editors act without donor at inference | Four matched rank16 methods, three seeds, full validation | Training gold is supervision; no independent test confirmation |\n| Mechanism incremental atomic editing benefit | No observed gain over Output-only or Random-site | Exploratory selected validation; not confirmatory |\n| Two-step gain | Fixed-seed aggregate validation difference | Concentrated in seed43 forward; seed44 negative; magnitude confounded |\n| Long-term stability | Three/five-step complete trajectories all 0/256 per method/seed | Long-term stability not established |\n| T5Gemma natural same-text pairs exist in small panel | 16train+16validation worlds, no next-fork filtering | Independent40-world confirmation not executed |\n| Full registered128 independent endpoint | BLOCKED_TEST_INTEGRITY | Encoder/output/history core exposures audited; previous123 proposal withdrawn; no silent replacement |\n')
    print(dict(report=str(ROOT/'FINAL_REPORT.md'),trajectories_ready=bool(trajectory),test='BLOCKED_TEST_INTEGRITY'))


if __name__=='__main__':write_report()
