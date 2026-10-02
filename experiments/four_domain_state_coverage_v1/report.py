"""Chinese report from per-seed observations; no model or selection changes."""
import csv,statistics
from collections import defaultdict,Counter
from common import *

def csvrows(name):
    p=ROOT/name
    return list(csv.DictReader(p.open())) if p.exists() and p.stat().st_size>1 else []

def pct(value):return 'NA' if value is None or value=='' else f'{float(value)*100:.2f}%'
def table(fields,records):
    return '\n'.join(['|'+'|'.join(fields)+'|','|'+'|'.join(['---']*len(fields))+'|']+['|'+'|'.join(str(r.get(f,'NA')) for f in fields)+'|' for r in records])

def main():
    statuses=csvrows('completion_status.csv');gates=csvrows('admission.csv');summaries=csvrows('summary_by_seed.csv');contrasts=csvrows('M_vs_S.csv');phenomena=csvrows('current_correct_next_failure.csv');regression=csvrows('capability_regressions.csv');errors=csvrows('error_counts.csv');counts=read(ROOT/'analysis_audit.json');budget=read(ROOT/'budget.json') if (ROOT/'budget.json').exists() else {}
    complete=sum(r['phase']=='formal' and r['status']=='completed' for r in statuses);failed=sum(r['phase']=='formal' and r['status']=='not_admitted' for r in statuses);sourcefail=sum(r['status']=='source_training_infeasible' for r in statuses);symbol=sum(r['phase']=='symbol' and r['status']=='symbol_diagnostic' for r in statuses)
    all_done=len(statuses)==32 and not any(r['status'] in ('running_or_not_started','technical_failure') for r in statuses)
    lines=['# 四领域连续表示编辑：结果', '', '**状态：'+('全部计划任务已结束。' if all_done else '仍在运行；以下是已写入工件的观察，不是全轮最终结论。')+'**',f'正式完成N/S/M组合{complete}/24；未通过准入{failed}/24；来源训练不可行{sourcefail}；符号对照完成{symbol}/8。独立重评分预测{counts["predictions_independently_rescored"]:,}条。每领域96/24/32个train/dev/test内容世界，各改写/轨迹共享世界划分。', '', '实际模型是冻结facebook/bart-base和google/t5gemma-2b-2b-ul2-it。仓库270M为预训练版、旧重构准入失败，不是已通过准入的270M IT；见AUDIT、model_manifest及EXPERIMENT_PLAN。结果不外推为所有语言模型性质。', '', '## 准入：逐模型、领域、seed', '', '门槛：重构≥95%，自然原子和gold-current-reencode续步macro≥85%、每state/sign cell≥75%。选择仅看600步原子训练期间完整dev NLL；N/S/M均final200。失败组合保留，未训练其N/S/M。']
    gatetable=[]
    bygate=defaultdict(dict)
    for r in gates:bygate[(r['model'],r['domain'],r['seed'],r['phase'])][r['kind']]=r
    for (m,d,s,p),rr in sorted(bygate.items()):gatetable.append(dict(模型=m,领域=d,seed=s,输入=p,重构=pct(rr['reconstruction']['rate']),原子=pct(rr['atomic']['rate']),最低原子cell=pct(rr['atomic']['min_cell']),gold续步=pct(rr['gold_next']['rate']),准入=rr['atomic']['passed']))
    lines+=['',table(['模型','领域','seed','输入','重构','原子','最低原子cell','gold续步','准入'],gatetable),'','## 当前正确但不能继续','','以下计数要求latent前一步语义正确、同世界的gold重编码下一步正确，但latent下一步失败。它比“终点错”更窄；不证明语义已丢失或任何纯latent编辑器不可能。重复路径/步骤不是独立世界。']
    phgroups=defaultdict(lambda:[0,0,set()])
    for r in phenomena:
        if r['condition']=='P' and r['template']=='0':
            cell=phgroups[(r['model'],r['domain'],r['seed'])];cell[0]+=int(r['latent_next_failed_k']);cell[1]+=int(r['current_correct_and_gold_next_correct_n']);cell[2].add(r['trajectory'])
    phrows=[dict(模型=m,领域=d,seed=s,失败=f'{v[0]}/{v[1]}',备注='合计路径步骤；独立世界32') for (m,d,s),v in sorted(phgroups.items())]
    lines+=['',table(['模型','领域','seed','失败','备注'],phrows),'','## M与S：留出当前状态 × 留出U来源','','主表只列template0、预先固定P/Q/U当前全文及mask共同匹配集；两符号方向合计，rows不是独立世界。配对cohort不用下一步结果筛选。各来源全候选/current-correct覆盖及排除原因另见paired_cohort_coverage和summary_by_seed。']
    mainrows=[];mean_groups=defaultdict(list)
    for r in contrasts:
        if r['template']=='0' and r['source']=='U' and r['cohort']=='fixed_fulltext_mask':
            n=int(r['n']);delta=float(r['M_minus_S']);mainrows.append(dict(模型=r['model'],领域=r['domain'],seed=r['seed'],留出划分=r['holdout_split'],世界=r['worlds'],S=f'{r["S_k"]}/{n}',M=f'{r["M_k"]}/{n}',M减S=f'{delta*100:+.2f}pp'));mean_groups[(r['model'],r['domain'],r['holdout_split'])].append((int(r['seed']),delta))
    lines+=['',table(['模型','领域','seed','留出划分','世界','S','M','M减S'],mainrows),'','三seed均值与范围（缺seed时明确n）：']
    means=[dict(模型=m,领域=d,留出划分=h,seed数=len(v),均值=f'{statistics.mean(x for s,x in v)*100:+.2f}pp',范围=f'[{min(x for s,x in v)*100:+.2f},{max(x for s,x in v)*100:+.2f}]pp') for (m,d,h),v in sorted(mean_groups.items())]
    lines+=['',table(['模型','领域','留出划分','seed数','均值','范围'],means),'','没有使用bootstrap区间；均值与范围展示训练seed差异，不把同一世界的多种表面表达当独立样本。来源迁移、当前状态迁移、表达迁移分别在source_matrix、template和state标签中报告；自然规则全训练，留出只指编辑态续步未补训。完全未训练的结构组合在challenge中单列，不能混成同一种留出。','','## 连续轨迹及恢复性','','CSV逐步列endpoint、条件续步、完整轨迹、保持/范围/可解析/受控语法。此表列template0的正向纯latent完整终点；空间四步整圈、人称三步循环另列。']
    tr=[]
    for r in summaries:
        if r.get('kind')!='trajectory' or r.get('template')!='0' or r.get('mode')!='latent' or r.get('trajectory')!='forward':continue
        d=r['domain'];step=int(r['step']);last=4 if d=='emotion' else 5
        if step!=last and not (d=='space' and step==4) and not (d=='person' and step==3):continue
        if r['condition'] not in ('P','N_h0','S_h0','M_h0'):continue
        tr.append(dict(模型=r['model'],领域=d,seed=r['seed'],条件=r['condition'],步=step,endpoint=f'{r["success_k"]}/{r["n"]}',完整=f'{r["full_k"]}/{r["n"]}',条件续步=pct(r.get('conditional_rate'))))
    lines+=['',table(['模型','领域','seed','条件','步','endpoint','完整','条件续步'],tr),'','## 锚点、作用范围及旧能力','','自然单步挑战与对应纯latent失败分开；template3/4/5及人称6是未训练结构，若单步不具备能力，不能归为组合失败。历史直接引语、固定绝对日期/坐标、未转身观察者、非目标评价、参与者/对象/所有者都独立计保持。合理受控释义被接受，未解析不判正确；不是开放语言评分器。']
    scopegroups=defaultdict(lambda:[0,0,0,0])
    for r in summaries:
        if r['kind']=='atomic' and int(r['template'])>=3:
            key=(r['model'],r['domain'],r['seed'],r['condition']);v=scopegroups[key];v[0]+=int(r['success_k']);v[1]+=int(r['n']);v[2]+=int(r['preserved_k']);v[3]+=int(r['scope_k'])
    sr=[dict(模型=m,领域=d,seed=s,条件=c,单步成功=f'{v[0]}/{v[1]}',非目标保持=f'{v[2]}/{v[1]}',范围正确=f'{v[3]}/{v[1]}') for (m,d,s,c),v in sorted(scopegroups.items()) if c in ('P','S_h0','M_h0')]
    lines+=['',table(['模型','领域','seed','条件','单步成功','非目标保持','范围正确'],sr),'','旧能力：以下只列自然core原子输入上P原本成功但补训后失败的计数；完整来源/表达/结构旧路径损伤另见capability_regressions.csv，改善不能抵消未报告的退化。']
    rg=[dict(模型=r['model'],领域=r['domain'],seed=r['seed'],条件=r['condition'],划分=r['holdout_split'],P成功=r['P_success_k'],损失=r['old_success_lost'],修复=r['old_failure_repaired'],分母=r['n']) for r in regression if r['shard']=='atomic_core']
    lines+=['',table(['模型','领域','seed','条件','划分','P成功','损失','修复','分母'],rg),'','## 机制分析的边界','','行为完成后的小型masked-mean线性probe以train世界拟合，跨P/Q/U新test世界读取当前状态、目标绑定槽、对象。角色槽不是完整参与者身份机制；core的锚点归属常量不能提供有意义分类证据。probe_on_next_failures列当前正确且续步失败的可读变量。可读出不等于编辑器使用；没有子空间替换或因果干预，不以距离/聚类给机制结论。','','## 七个研究问题：以已完成证据回答','','1. 出现现象的模型/领域以“当前正确但不能继续”逐seed表为准；未准入/技术失败组合不能给组合机制结论。','2. 多状态是否优于集中补训以M−S逐seed及两划分表为准，负值和方向分歧全部保留；不挑最好seed。','3. 来源、状态、表达形式分别比较同一固定P/Q/U输入、未补训H和template2；它们不是同一种泛化，完整交叉表在CSV。','4. 锚点/范围挑战显示实际能保持哪些静态事实和历史视点；挑战自然能力不足时只报告能力边界，不能归因latent路径。','5. 旧能力退化以逐seed损失/修复表和固定来源regression为准；任一路径修复不能代表整体能力保持。','6. 仅在两backbone都准入、相同领域和指标方向对应时比较一致性；不平均未准入与组合失败。','7. 下一步应优先用这里确实发生的配对失败，检验状态覆盖与来源兼容性/保护预算的相互作用；未准入领域先修复输入重构和原子能力。任何下一实验另冻结，不根据本轮test反复增加步数。','','## 执行与工件',f'累计实际GPU小时：{budget.get("actual_gpu_hours","NA")}；allocation账本峰值：{budget.get("max_concurrent_gpus","NA")}张。job IDs：{budget.get("job_ids",[])}。始终一任务一卡、一个项目全局最多两卡；符号数组依赖正式数组afterany，工程失败/重试也计入账本。', '', '科学锁、数据/模型/配置hash、SOURCE_LINEAGE_COMPLETE、逐例gzip预测及可恢复原始分片、checkpoint_index、来源cache manifests、完整日志索引共同构成证据。数据manifest的两个摘要行数仍保留修订前值；最终person6文件SHA正确，最终实际行数在data_delivery_audit中明确给出。无人类独立标签；评分范围是受控语义语法。']
    (ROOT/'RESULTS.md').write_text('\n\n'.join(lines)+'\n')
    counts_by=defaultdict(Counter)
    for r in errors:counts_by[(r['model'],r['domain'])][r['error']]+=int(r['n'])
    erows=[dict(模型=m,领域=d,类型=e,计数=n) for (m,d),v in sorted(counts_by.items()) for e,n in v.most_common()]
    errorlines=['# 错误审计','','所有错误按原始逐例输出保留。数量包含同世界的多个方向、来源、轨迹和步骤，不是独立样本数。受控规则未解析不会被算成功；语法标签不是通用语法判断。','',table(['模型','领域','类型','计数'],erows),'','案例按固定hash在每个模型/领域/错误类型中取前6，未按最好seed或最大差选取。failure_cases.jsonl保留源/当前/输出/gold与分项指标，可检查当前已错、当前正确续步错、参与者/所有者绑定、非目标改动和历史引语作用域等。时间目标错误不自动称为“锚点选择错误”，除非直接引语或明确固定锚点保持规则支持该归因。','','BART工程试跑的情感重构输出有重复/损坏词及句式变化，空间有对象名改写；评分器修复了合理协调/it指代，未接受客观事实丢失。T5Gemma原Return提示丢弃视角标签；统一Copy-exact dev接口复核通过后才冻结正式提示，工程原始结果保留。','','core单步准入、未训练expression/structure单步、固定来源续步和自身完整路径分开检查。不能用source自身正确率的筛选变化，伪装为同一固定cohort的改善。固定同全文/同mask/depth1交集与全候选覆盖均保留，空cohort为NA。','','修复与退化可以同时发生；capability_regressions.csv逐seed给P成功损失及P失败修复，不能只给净增量。机制probe的可读性不证明变量被使用，有限角色槽/常量锚点标签的限制已明示。']
    (ROOT/'ERROR_ANALYSIS.md').write_text('\n\n'.join(errorlines)+'\n');print('Reports written; final=',all_done)

if __name__=='__main__':main()
