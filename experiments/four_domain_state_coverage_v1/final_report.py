"""Add corrected spatial/structural/probe evidence and concrete answers to reports."""
import csv,statistics
from collections import defaultdict
from common import *
from report import table,pct
from scientific_answers import research_answers,readcsv

def main():
    confirmation=ROOT.parent/'space_relation_confirmation_v1'
    main_status=readcsv(ROOT,'completion_status.csv');space_status=readcsv(confirmation,'completion_status.csv');identity=readcsv(ROOT,'identity_probe_status.csv');language=readcsv(ROOT,'language_structure_status.csv')
    done=len(main_status)==32 and len(space_status)==6 and len(identity)==30 and len(language)==8 and all(r['status'] not in ('running_or_not_started','technical_failure') for r in main_status+space_status+identity+language)
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
    appendix+=['','## 续步输出审阅和身份probe','', '主phenomenon表的完整任务失败包含未解析输出；current_correct_next_failure.csv另给可解析语义不匹配、未解析、仅语法和仅终止计数。固定首个test世界×三个seed×三种轨迹的18个BART时间/人称案例由Codex助手逐一审阅：当前和gold-reencode下一步均正确，latent下一步输出重复/破碎或丢失必要关系，不是合理释义。仅据此证明这些案例的失败存在；不把全部未解析输出标成语义错误，不作独立人工标注或因果机制结论。见CONTINUATION_AGENT_REVIEW及continuation_review_set。']
    ip=readcsv(ROOT,'identity_probe_metrics.csv');ipgroups=defaultdict(list)
    for r in ip:
        if r['test_source']=='U':ipgroups[(r['study'],r['model'],r['domain'],r['variable'])].append(float(r['accuracy']))
    pt=[dict(实验=st,模型=m,领域=d,变量=v,seed数=len(x),留出U均值=pct(statistics.mean(x)),范围=f'[{pct(min(x))},{pct(max(x))}]') for (st,m,d,v),x in sorted(ipgroups.items())]
    appendix+=['',table(['实验','模型','领域','变量','seed数','留出U均值','范围'],pt),'','命名身份probe只从冻结P train表示拟合，跨P/Q/U test读取；current-correct-next-failed子集准确率另见identity_probe_on_failures。时间core锚点归属是常量，未拟合归属分类器；没有quote/external-anchor对照probe或子空间干预。可读出不等于编辑器使用。']
    report+='\n\n'+'\n\n'.join(appendix)+'\n';(ROOT/'RESULTS.md').write_text(report)
    errors=(ROOT/'ERROR_ANALYSIS.md').read_text();errors+='\n\n连续生成未解析与已解析的语义错误分开。固定18例的助手审阅记录是存在性案例证据，不是对全部未解析预测的独立标注。原空间朝向状态划分有解释限制；关系确认独立运行，旧结果不被改写。语言结构重构/原子准入失败先归入该结构基本能力限制，不进入组合失败平均。\n';(ROOT/'ERROR_ANALYSIS.md').write_text(errors)
    (confirmation/'RESULTS.md').write_text('# 空间关系状态确认结果\n\n'+header+'\n\n'+'\n\n'.join(appendix[:9])+'\n\n完整综合报告位于../four_domain_state_coverage_v1/RESULTS.md，逐seed原始CSV/预测/checkpoint在本目录。\n')
    (confirmation/'ERROR_ANALYSIS.md').write_text('# 空间关系状态错误分析\n\n见本目录failure_cases.jsonl、error_counts.csv、capability_regressions.csv及综合ERROR_ANALYSIS。原朝向划分未作为关系状态留出证据；确认版未准入组合不归入组合失败平均。\n')
    print('Combined report written; every phase terminal=',done)

if __name__=='__main__':main()
