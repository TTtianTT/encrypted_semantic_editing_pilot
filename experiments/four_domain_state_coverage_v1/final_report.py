"""Add corrected spatial/structural/probe evidence and concrete answers to reports."""
import csv,statistics
from collections import defaultdict
from common import *
from report import table,pct
from scientific_answers import research_answers,readcsv

def main():
    confirmation=ROOT.parent/'space_relation_confirmation_v1'
    main_status=readcsv(ROOT,'completion_status.csv');space_status=readcsv(confirmation,'completion_status.csv');identity=readcsv(ROOT,'identity_probe_status.csv');language=readcsv(ROOT,'language_structure_status.csv')
    position=readcsv(ROOT,'position_foils_status.csv')
    done=len(main_status)==32 and len(space_status)==6 and len(identity)==30 and len(language)==8 and len(position)==8 and all(r['status'] not in ('running_or_not_started','technical_failure') for r in main_status+space_status+identity+language+position)
    report=(ROOT/'RESULTS.md').read_text()
    if not done:report=report.replace('全部计划任务已结束。','原主数组已结束；补充确认/结构/probe仍未全部完成。')
    header=('全部预定计算和工件核验已结束；准入失败与未执行结构单列。' if done else '仍在运行或存在缺失任务；本文件是当前工件快照，不能当作全部完成。')
    report=report.replace('## 七个研究问题：以已完成证据回答', '## 七个研究问题：以已完成证据回答')
    start=report.index('## 七个研究问题：以已完成证据回答');end=report.index('## 执行与工件',start)
    report=report[:start]+'## 七个研究问题：以已完成证据回答\n\n'+'\n\n'.join(f'{i}. {s}' for i,s in enumerate(research_answers(),1))+'\n\n'+report[end:]
    # Existing original-study tables remain intact, but absolute-facing state
    # holdout is clearly distinguished from the corrected relative-state study.
    report=report.replace('|space|','|space（原朝向划分）|')
    prefix=f'本轮整体状态：**{header}**\n\n空间原协议按绝对朝向分层，不能据此声称留出了相对关系状态；它的行为/退化工件全部保留。主状态泛化问题使用独立预注册的关系确认版，语义与更正时间见POSTFORMAL_SEMANTIC_AUDIT.md。确认版重新初始化原子编辑器，训练文本集合相同但抽样行序改变，原版与确认版的差异不能只归因于补训覆盖。\n\n'
    report=report.replace('# 四领域连续表示编辑：结果', '# 四领域连续表示编辑：结果\n\n'+prefix,1)
    appendix=['## 空间关系状态确认：独立结果','', '状态0front/1right/2back/3left；plus物理朝向顺时针90度，关系状态减1。S只补训front，M补训front/back，right与left仅自然原子训练见过，未补训其编辑态续步。原世界坐标、人物、split和自然原子文本对集合不变。']
    gates=readcsv(confirmation,'admission.csv');by=defaultdict(dict)
    for r in gates:by[(r['model'],r['seed'])][r['kind']]=r
    gt=[dict(模型=m,seed=s,重构=pct(v['reconstruction']['rate']),原子=pct(v['atomic']['rate']),gold续步=pct(v['gold_next']['rate']),准入=v['atomic']['passed']) for (m,s),v in sorted(by.items())]
    appendix+=['',table(['模型','seed','重构','原子','gold续步','准入'],gt)]
    mm=[dict(模型=r['model'],seed=r['seed'],划分=r['holdout_split'],世界=r['worlds'],S=f"{r['S_k']}/{r['n']}",M=f"{r['M_k']}/{r['n']}",M减S=f"{float(r['M_minus_S'])*100:+.2f}pp") for r in readcsv(confirmation,'M_vs_S.csv') if r['source']=='U' and r['template']=='0' and r['cohort']=='fixed_fulltext_mask']
    appendix+=['',table(['模型','seed','划分','世界','S','M','M减S'],mm),'', '完整逐seed/group CSV与mean_and_range保存在space_relation_confirmation_v1。来源/状态/表达交叉保存在主目录transfer_quad.csv；字面全文与标准化全文匹配分别保存在literal_fulltext*及same_text_source_disagreement.csv。cross_backbone_fixed_worlds给共同内容世界/当前全文集合以及各backbone自己的覆盖；跨backbone token mask不能相同，限制另存JSON。']
    appendix+=['','## 语言结构能力与连续路径：后核心控制','', 'LINGUISTIC_CONTROLS_PLAN在此阶段拟合/解码前冻结，但在部分原始BART测试结果之后新增，不能冒充最初预注册。没有新训练或test调参。先做未编辑dev/test重构与三个P的dev原子/gold-next；同一固定门槛通过的结构才运行所有现存N/S/M的1–5步三路径，失败结构单列。此阶段没有新的复杂结构来源矩阵。']
    ls=readcsv(ROOT,'language_structure_gates.csv');lt=[]
    for r in ls:lt.append(dict(模型=r['model'],领域=r['domain'],seed=r['seed'],结构=r['template'],状态=r['status'],重构=pct(r.get('reconstruction_rate')),原子=pct(r.get('atomic_rate')),gold续步=pct(r.get('gold_next_rate'))))
    appendix+=['',table(['模型','领域','seed','结构','状态','重构','原子','gold续步'],lt),'', '逐例控制及轨迹在ADDITIONAL_PREDICTION_ARCHIVES；逐seed/结构/条件/路径/步骤的计数在language_structure_by_seed.csv。未解析、语法与终止失败不自动等同于已证实语义错误。']
    appendix+=['','semantic_components_by_seed单独给身份/对象绑定、绝对日期/方向、固定观察者、非目标评价和引语锚点/原话的约束。原冻结评分的scope=target∧preserved，是联合任务结果，不能单凭它判定锚点选择错误。新增scope_constraints_satisfied排除目标状态/说话语境端点正确性；语法破碎、未解析和未结束输出标为未知，另报覆盖、已解析条件率及全候选严格率。解析的身份/引语等槽位失败才作为对应语义错误案例；这项事后分析不影响准入或选择。']
    appendix+=['','独立负例审计发现原空间解析器的first-viewpoint回退可以把B的关系用于A，并且B视角和marker描述未校验物体身份：168个构造的错误A关系/B物体/marker物体负例均被原实现接受。独立SPACE_SCOPE_GUARD_CHECK拒绝全部168例，并通过1344个正确文本。构造负例与模型实际预测分别报告。原正式评分和门槛不改写；spatial_scoring_adjudication逐工件保留原通过数、实际确认假阳性数及保守修正数，不能把这些假阳性用作范围成功证据。位置诊断在GPU评估之前增加独立A视角和非目标物体检查，旧锁/代码和修订时间保存在protocol_revisions和POSITION_*REVISION。该修订不增加输入、训练或重新选checkpoint。']
    appendix+=['','独立校验的初版也曾把12条正确的I see the ticket that is to my left等同物体关系从句列为假阳性候选；逐例复核撤销了这项错误标记，原模型评分在这些样本上正确。POSITION_PARAPHRASE_GUARD_REVISION保存旧候选审计与旧锁，另通过224条关系从句正例。新校验将陌生表达标为unknown，只将已识别的明确矛盾列为确认假阳性；independent_guard_unresolved_k另报覆盖，不能把未知当作语义错误。诊断GPU评估尚未开始时已冻结修订，正式原始评分不变。']
    qa=read(ROOT/'QUANTITY_SCORING_AUDIT.json') if (ROOT/'QUANTITY_SCORING_AUDIT.json').exists() else {}
    appendix+=['',f"另一独立负例审计确认：情感原评分只读第一个copies数量，56条正确数量后追加不同数量的构造负例会被接受；未知主体评价/新物体颜色的112条对照已被原实现拒绝。实际预测的数量冲突成功数为{qa.get('actual_output_false_positives','尚待审计')}，已判当前正确但数量冲突的来源数为{qa.get('current_qualification_false_positives','尚待审计')}，详见quantity_scoring_adjudication。原分数不改写；尚未运行的位置诊断在GPU前增加所有未引述明确数量的一致性检查，允许同数重复、正常空白及引语作用范围。见POSITION_QUANTITY_AMENDMENT/REVISION。构造反例不是模型实际错误数。"]
    appendix+=['','## 续步输出审阅和身份probe','', '主phenomenon表的完整任务失败包含未解析输出；current_correct_next_failure.csv另给可解析语义不匹配、未解析、仅语法和仅终止计数。固定首个test世界×三个seed×三种轨迹的18个BART时间/人称案例由Codex助手逐一审阅：当前和gold-reencode下一步均正确，latent下一步输出重复/破碎或丢失必要关系，不是合理释义。仅据此证明这些案例的失败存在；不把全部未解析输出标成语义错误，不作独立人工标注或因果机制结论。见CONTINUATION_AGENT_REVIEW及continuation_review_set。']
    ip=readcsv(ROOT,'identity_probe_metrics.csv');ipgroups=defaultdict(list)
    for r in ip:
        if r['test_source']=='U':ipgroups[(r['study'],r['model'],r['domain'],r['variable'])].append(float(r['accuracy']))
    pt=[dict(实验=st,模型=m,领域=d,变量=v,seed数=len(x),留出U均值=pct(statistics.mean(x)),范围=f'[{pct(min(x))},{pct(max(x))}]') for (st,m,d,v),x in sorted(ipgroups.items())]
    appendix+=['',table(['实验','模型','领域','变量','seed数','留出U均值','范围'],pt),'','命名身份probe只从冻结P train表示拟合，跨P/Q/U test读取；current-correct-next-failed子集准确率另见identity_probe_on_failures。时间core锚点归属是常量，未拟合归属分类器；没有quote/external-anchor对照probe或子空间干预。可读出不等于编辑器使用。']
    appendix+=['','T5_CONTINUATION_AGENT_REVIEW另保存固定首个test世界的12例：时间三个seed、原朝向空间seed42，各三种轨迹。Codex逐一阅读当前、latent下一步与gold重编码对照，确认日期/关系错误、固定事实损失或破碎重复。空间例不是更正关系确认版的证据；保存这些例时部分正式评估尚未结束。此记录同样不是独立人工总体标注。']
    appendix+=['','T5_SPACE_CONTINUATION_AGENT_REVIEW将同一固定空间世界space_0120的审阅覆盖到42/43/44三个seed、三种轨迹，共九例，包含前述seed42三例。全部当前与gold重编码下一步正确，latent下一步缺失身份/关系/事实、错误方向或损坏重复。它支持原空间任务的行为存在性，不能作为关系状态留出的确认版结果。一个世界的多种轨迹和训练seed不能当作九个独立世界。']
    appendix+=['','T5_EMOTION_S42_CONTINUATION_AGENT_REVIEW记录首次情感结果：96条当前正确且gold续步正确的第二步，95条严格失败、1条成功，64条已解析槽位不匹配。固定emotion_0120三条路径中，正向保留negative且丢失其他内容，反向/逆操作从positive到negative而非neutral；后两例非目标评价和事实保持，明确是目标评价越级。首次单seed证据独立保存，不能冒充全部训练随机性；唯一成功反例保存在emotion_s42_continuation_counterexamples。后续分项三seed表仍是主要结果。']
    appendix+=['','ADMISSION_AGENT_REVIEW按领域×三个seed×固定三类评分失败取18个dev未编辑重构案例。其空间输出丢失颜色谓词、引入coffee事实或把key改成light；情感输出有损坏的dislits及重复破碎分句。单复数ticket/tickets案例未裁定为语义错误，保留为有限单数对象解析器的拒绝及指称不确定性。冻结准入是完整受控任务门槛，不是无限释义的语义等价判定；自动错误类别/槽位不等于独立人工证实的语义错误。三个seed的冻结encoder重构重复不能视为三次独立生成证据。']
    appendix+=['','## 位置与同措辞锚点补充诊断','', 'POSITION_FOILS_PLAN在部分正式test结果之后、这批GPU评估之前冻结。没有训练、重新选checkpoint或根据test调参。同世界的两种顺序共享gold转换；emotion额外把同主体的非目标对象放在前面，空间固定观察者在前，人称历史引语在前，时间引语和外部表达使用相同事件/相对日期句式。时间历史日期E−3与固定引语一致。原引语只作为原话记录，未假定为事实，原结果仍保留。']
    appendix+=['','情感补充variants2/3显式记录Narrator=Focus，外部第一人称I与参与者C历史引语中的I可以使用相同评价措辞；仅外部目标评价改变。引语分别在末尾/开头。该语法未训练，抽象等级转换已有自然原子训练；2/3单独配对，不与多对象0/1当作相同完整世界状态混合。独立评分适配器只绑定语法合法的未引述I，不修改回灌文本，也不修正I likes等语法错误。新增夹具在该诊断GPU评估之前冻结，7504项情感CPU正负例检查通过；详见POSITION_NARRATOR_AMENDMENT及修订哈希。']
    pg=[dict(模型=r['model'],领域=r['domain'],seed=r['seed'],顺序=r['variant'],状态=r['status'],重构=pct(r.get('reconstruction_rate')),原子=pct(r.get('atomic_rate')),gold续步=pct(r.get('gold_next_rate'))) for r in readcsv(ROOT,'position_foils_gates.csv')]
    appendix+=['',table(['模型','领域','seed','顺序','状态','重构','原子','gold续步'],pg),'', '全部可用角色的test原子预测，即使诊断未准入，仍在position_foils_by_seed与压缩逐例工件中；连续路径仅在同一P的该顺序dev门槛通过时执行。position_order_pairs以同世界/状态/操作配对给顺序差异；两个顺序同时正确才证明这些具体夹具的范围保持。仅靠原目标位于首句的挑战分数不能排除位置捷径。']
    appendix+=['','## 语言学解释限制','', '见LINGUISTIC_LIMITATIONS.md。core三人循环使用显式姓名，无人称信息丢失；第三代词挑战使用人工姓名/代词约定，没有独立性别属性测试。反身附加事件规定A保留A自己的key；主对象也是key时需要不同实例解释，原文本未命名实例，不能据此声称验证了唯一物体实例所有权。固定launch日期由E−2导出；C是叙述锚点，事件状态独立给定。更复杂图结构、复数/集合、平移、间接引语及随机子空间干预未执行，保留为限制。']
    appendix+=['','## 执行顺序偏差','', '工程阶段检查了全部八个模型/领域，但最初正式数组把每个组合的600步准入与其补训/行为串在一起，未先完成全组合的最终原子准入。每个组合的早期probe在该组合行为结束后运行，当时其他组合尚未完成；后续命名身份probe统一排在行为阶段之后。这些顺序偏差保留，不冒充最初的全局阶段顺序。剩余未启动孩子16–23改为先运行原预算P600/dev准入的2650，再由零GPU2651释放其原补训任务，复用同一P/dev工件，不新增训练更新。固定科学代码/数据/选择规则与阈值未改。见REMAINING_ATOMIC_PREFLIGHT与submission ledger。']
    report+='\n\n'+'\n\n'.join(appendix)+'\n';(ROOT/'RESULTS.md').write_text(report)
    errors=(ROOT/'ERROR_ANALYSIS.md').read_text();errors+='\n\n连续生成未解析与已解析的语义错误分开。固定18例的助手审阅记录是存在性案例证据，不是对全部未解析预测的独立标注。原空间朝向状态划分有解释限制；关系确认独立运行，旧结果不被改写。语言结构重构/原子准入失败先归入该结构基本能力限制，不进入组合失败平均。\n';(ROOT/'ERROR_ANALYSIS.md').write_text(errors)
    (confirmation/'RESULTS.md').write_text('# 空间关系状态确认结果\n\n'+header+'\n\n'+'\n\n'.join(appendix[:9])+'\n\n完整综合报告位于../four_domain_state_coverage_v1/RESULTS.md，逐seed原始CSV/预测/checkpoint在本目录。\n')
    (confirmation/'ERROR_ANALYSIS.md').write_text('# 空间关系状态错误分析\n\n见本目录failure_cases.jsonl、error_counts.csv、capability_regressions.csv及综合ERROR_ANALYSIS。原朝向划分未作为关系状态留出证据；确认版未准入组合不归入组合失败平均。\n')
    with (ROOT/'ERROR_ANALYSIS.md').open('a') as f:f.write('\nrepair_regression_witnesses.jsonl按同一冻结receiver checkpoint联合保存固定来源修复和旧自然原子损失。来源表示/当前全文、操作及gold在前后相同；选择每个合格checkpoint的字典序首例，保留全部seed和条件。repair_regression_joint_counts给完整数量，行为未完成的快照标为partial。未解析损失仍是受控任务失败，不自动作无限释义语义错误。\n')
    with (ROOT/'ERROR_ANALYSIS.md').open('a') as f:f.write('\nREPAIR_REGRESSION_AGENT_REVIEW逐一审阅初次生成的六个BART人称联合案例（涵盖三个seed）。固定来源修复后正确，旧自然输出出现施事/受事/所有者绑定替换或事件缺失；这些不是合理释义。它们均对应同一receiver checkpoint，证明在这些具体设置里修复和旧语义能力退化可以同时出现。后续新增自动案例不继承人工助手标签。\n')
    print('Combined report written; every phase terminal=',done)

if __name__=='__main__':main()
