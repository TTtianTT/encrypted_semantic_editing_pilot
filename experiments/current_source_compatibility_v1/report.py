"""Chinese reports generated from all seeds, no outcome-dependent model selection."""
import csv,statistics,collections
from study import *
def csvrows(name):
    p=ROOT/name;return list(csv.DictReader(p.open())) if p.exists() else []
def table(keys,rs):return '\n'.join(['|'+'|'.join(keys)+'|','|'+'|'.join(['---']*len(keys))+'|']+['|'+'|'.join(str(r.get(k,'')) for k in keys)+'|' for r in rs])
def pct(v):return 'NA' if v in (None,'','None') else f'{float(v)*100:.2f}%'
def main():
    audit=read(ROOT/'ANALYSIS_AUDIT.json');summary=csvrows('summary_by_seed.csv');paired=csvrows('paired_contrasts.csv');loss=csvrows('old_capability_changes.csv');prefix=csvrows('prefix_quality.csv');resource=read(ROOT/'resource_usage.json')
    complete=audit['all_seeds_complete'];lines=['# 当前来源兼容性：实验结果','', '**全部预定条件与评估已完成。**' if complete else '**当前工件快照；尚未全部完成，不能视为最终结论。**','', '模型google/t5gemma-2b-2b-ul2-it，原子T0 seeds42/43/44，各600步已选checkpoint；骨干冻结，两个rank16操作头共152064参数。N/F/R从各seed同一T0出发，各200 optimizer updates，800自然replay+800续步。训练覆盖全部合法当前状态及操作头输出标签；R仅一次前缀、每20更新重建、detach，不筛除错误。主checkpoint固定200，100仅诊断。','', '沿用96/24/32世界划分；IID与模板OOD共享32个测试世界，是同世界不同表达，不能当64个独立世界。旧自然测试768行/seed原样保留；IID/OOD穷举两步各704序列，长链每种模板在32个世界上合计256条序列、每步1–5。实际独立世界仍为32。U循环下一seed的原子T0，是来源对照，不是第四次训练重复。']
    gates=[]
    for seed in (42,43,44):
      p=ROOT/f'runs/preflight/s{seed}/admission.json'
      if p.exists():
        g=read(p);gates.append(dict(seed=seed,重构=pct(g['reconstruction']['rate']),原子=pct(g['atomic']['rate']),gold续步=pct(g['gold_next']['rate']),通过=g['passed']))
    lines+=['','## 原始能力与准入','',table(['seed','重构','原子','gold续步','通过'],gates),'','准入针对原有核心dev。模板OOD是另外的表达留出测量，没有被当作通过核心准入即可保证的能力。其自然单步及gold-reencode对照单列，OOD失败同时可能包含表达识别不足。']
    atomrows=[dict(seed=r['seed'],条件=r['condition'],测试=r['test'],自然单步macro=pct(r['rate']),成功=f"{r['k']}/{r['denominator']}") for r in summary if r['update'] in ('0','200') and r['source']=='natural']
    lines+=['',table(['seed','条件','测试','自然单步macro','成功'],atomrows)]
    mainrows=[]
    for r in summary:
      if r['update'] not in ('0','200') or r['source']!='self' or r['cohort']!='all' or r['metric']!='full2':continue
      def find(metric):return next(x for x in summary if all(x[k]==r[k] for k in ('seed','condition','update','test','source','cohort')) and x['metric']==metric)
      first=find('first');cond=find('conditional_next');end=find('endpoint2')
      mainrows.append(dict(seed=r['seed'],条件=r['condition'],测试=r['test'],第一步=f"{first['k']}/{first['denominator']}",第二步endpoint=f"{end['k']}/{end['denominator']}",两步完整=f"{r['k']}/{r['denominator']}",条件续步=f"{cond['k']}/{cond['denominator']}"))
    lines+=['','## 自身运行：逐seed主结果','',table(['seed','条件','测试','第一步','第二步endpoint','两步完整','条件续步'],mainrows),'','条件分母因模型而变化，不用于单独排名；错误前缀恢复可以提高endpoint，full2仍失败。长度2穷举集与后面的五步路径初始分布不同。']
    aggregate=[dict(条件=r['condition'],测试=r['test'],来源=r['source'],指标=r['metric'],seeds=r['seeds'],均值=pct(r['mean']),最小=pct(r['minimum']),最大=pct(r['maximum'])) for r in csvrows('mean_and_range.csv') if r['update'] in ('0','200') and (r['source']=='self' and r['metric']=='full2' and r['cohort']=='all' or r['source']=='latent' and r['metric'] in ('full3_all','full4_all','full5_all') or r['source']=='natural')]
    lines+=['','## 均值与范围','',table(['条件','测试','来源','指标','seeds','均值','最小','最大'],aggregate),'','均值及范围保留训练seed层级；逐seed结果为主。条件成功率无有效分母时记NA，不补零。完整分项另见mean_and_range.csv、continuation_cells.csv、sequence_metrics.csv及quality_metrics.csv。']
    pairs=[dict(seed=r['seed'],对比=r['contrast'],测试=r['test'],来源=r['source'],指标=r['metric'],集合=r['cohort'],差值pp=f"{float(r['delta_pp']):+.2f}",世界CI=f"[{float(r['ci_low_pp']):+.2f},{float(r['ci_high_pp']):+.2f}]",世界=r['worlds']) for r in paired if r['update']=='200' and (r['metric']=='full2' and r['cohort']=='all' or r['source']=='latent' and r['metric'] in ('full3_all','full4_all','full5_all'))]
    lines+=['','## R−F、F−N：固定世界配对','',table(['seed','对比','测试','来源','指标','集合','差值pp','世界CI','世界'],pairs),'','2000次按世界聚类的paired bootstrap，共享世界及其所有序列；区间只描述固定训练模型的内容抽样，不含完整训练随机性。零差区间[0,0]不证明总体效应严格为零。']
    longrows=[dict(seed=r['seed'],条件=r['condition'],测试=r['test'],方法=r['source'],指标=r['metric'],成功=f"{r['k']}/{r['denominator']}") for r in summary if r['update'] in ('0','200') and r['source'] in ('latent','actual_reencode','gold_reencode') and r['metric'] in ('full2_all','full3_all','full4_all','full5_all')]
    lines+=['','## 长度迁移与重编码控制','',table(['seed','条件','测试','方法','指标','成功'],longrows),'','全部endpoint、条件分母、路径family、100步checkpoint和首次失败位置在CSV。纯latent只在第一步前编码；gold重编码使用正确当前文本，是能力控制；actual重编码回灌原始真实输出，无清洗或gold替换。二者分别报告。']
    retention=[]
    for r in summary:
      if r['update'] not in ('100','200') or r['test']!='iid' or r['source']!='natural':continue
      base=next(x for x in summary if x['seed']==r['seed'] and x['condition']=='T0' and x['test']=='iid' and x['source']=='natural')
      rr=[x for x in loss if all(x[k]==r[k] for k in ('seed','condition','update'))];delta=(float(r['rate'])-float(base['rate']))*100
      retention.append(dict(seed=r['seed'],条件=r['condition'],update=r['update'],macro=pct(r['rate']),相对T0pp=f'{delta:+.2f}',旧成功损失=sum(int(x['old_success_lost']) for x in rr),旧失败修复=sum(int(x['old_failure_repaired']) for x in rr),保留判据=delta>=-2))
    lines+=['','## 旧自然能力：平均值与逐例损失','',table(['seed','条件','update','macro','相对T0pp','旧成功损失','旧失败修复','保留判据'],retention),'','每个seed独立采用下降≤2pp工作判据；仍保留全部损失ID、状态及操作，不能只凭macro声称旧能力完好。']
    pr=[dict(seed=r['seed'],条件=r['condition'],刷新=r['refresh_update'],实际监督单位=r['n'],正确前缀=r['success'],已知相对状态错误=r['semantic_error'],内容缺失或改变=r['content_changed_or_lost'],评分未定=r['unresolved']) for r in prefix if r['sample_kind']=='actual_draws']
    lines+=['','## 训练来源质量及收益归属','',table(['seed','条件','刷新','实际监督单位','正确前缀','已知相对状态错误','内容缺失或改变','评分未定'],pr),'','错误类别可重叠，未解析/relative未知不算已证实语义错误。没有删除、替换、重新抽样或加权失败输入。prefix_quality另给唯一前缀与全池权重；实际监督表按对应20更新窗口的draws计数。正确前缀条件续步、失败前缀端点恢复、已知错误relative恢复与未定前缀恢复在summary分别列。后两类恢复不能解释为当前正确续步修复。repair_attribution.csv另将配对full2差值按双方前缀是否正确分解：endpoint差值=full2差值+失败前缀恢复差值；这些更新后分层是描述性分析，不能替换训练前固定诊断集或总体主指标。']
    diag=[dict(seed=r['seed'],条件=r['condition'],测试=r['test'],来源=r['source'],两步完整=f"{r['k']}/{r['denominator']}") for r in summary if r['update']=='200' and r['metric']=='full2' and r['cohort']=='fixed_diagnostic']
    lines+=['','## 补训前固定诊断集','',table(['seed','条件','测试','来源','两步完整'],diag),'','成员由T0第一步与T0 gold-current-reencode下一步同时成功确定，在正式训练前冻结。每个方法使用全部原始成员；更新后第一步变错计入自身full2失败。不会按更新后成功重新筛选。']
    def contrast(test,source,metric):
      rr=[r for r in paired if r['update']=='200' and r['contrast']=='R-F' and r['test']==test and r['source']==source and r['metric']==metric and r['cohort'] in ('all','long_paths')]
      vals=[float(r['delta_pp']) for r in sorted(rr,key=lambda r:int(r['seed']))]
      return ('尚未完成' if len(vals)!=3 else f'42/43/44={vals}pp，均值{statistics.mean(vals):+.2f}，范围[{min(vals):+.2f},{max(vals):+.2f}]，三个seed严格正向={all(v>0 for v in vals)}')
    answers=[
      'R是否优于F：IID自身full2 '+contrast('iid','self','full2')+'；固定T0 '+contrast('iid','fixed_T0','full2')+'；U '+contrast('iid','U','full2')+'。不能用条件成功率独立排名。',
      '长度迁移：IID纯latent full3 '+contrast('iid','latent','full3_all')+'；full4 '+contrast('iid','latent','full4_all')+'；full5 '+contrast('iid','latent','full5_all')+'。每一步完整率的绝对计数见表；端点恢复不等于完整长链。',
      '更新后的自身输出能力由第一步、full2、条件续步及固定诊断集共同判断，详见逐seed表。仅固定来源成功不代表自身成功；第一步失败不能被条件筛选隐藏。',
      '来源与表达迁移：模板OOD自身full2 '+contrast('ood','self','full2')+'；OOD U '+contrast('ood','U','full2')+'。U冻结且独立于该运行补训，仍只是三个原子编辑器间的来源对照。',
      '旧自然单步是否退化：按每个seed、条件的≤2pp规则及旧成功损失表判断，全部损失ID保留。平均分维持也可能掩盖不同样本的一失一得。',
      '收益归属：训练刷新表及测试前缀分项区分正确前缀续步与失败前缀端点恢复；已知错误relative、内容缺失及评分未定另列。恢复错误/未定前缀不支持当前正确续步被修复的解释。',
      'GPU开销：每个seed的源刷新pipeline及optimizer时间见RESOURCE_USAGE。刷新时间包含新编码、前缀调用、质量解码与缓存I/O，额外分配GPU时间如实记录；累计allocation包括技术失败和恢复。'
    ]
    lines+=['','## 七个研究问题','']+[f'{i}. {s}' for i,s in enumerate(answers,1)]+['','观察仅限于本模型、数据、rank16双头编辑器和200更新设置。即使R有帮助也不证明来源滞后是唯一失败机制。没有追加领域、probe、范围挑战或超参数搜索。','',f"累计{resource['gpu_hours']:.6f} allocation GPUh，本项目峰值{resource['peak_project_gpus']}，本轮开始后账号峰值{resource['peak_account_gpus_since_first_allocation']}。未完成列表见ANALYSIS_AUDIT。"]
    (ROOT/'RESULTS.md').write_text('\n\n'.join(lines)+'\n')
    (ROOT/'ERROR_ANALYSIS.md').write_text('# 错误分析\n\n逐例输出、解析槽位、target/preserved/ended及受控grammar均保留。未知表达不自动裁定语义错误，controlled grammar包含完整性，不是一般英文语法判断。\n\n训练来源：prefix_quality给每次刷新唯一前缀、全池加权及实际监督draws的质量，错误输入未删改。测试错误前缀端点恢复与正确前缀条件成功分开；只有full2/完整长链才要求所有前步均成功。repair_attribution.csv给配对差值分解；更新后共同正确前缀分层是描述性的，不用于重新筛选主结果。\n\n旧能力损失ID及状态/操作在old_capability_changes；首次失败分布在first_failure；固定诊断集不随方法重新筛选。ERROR_CASES、CASE_SELECTION与AGENT_READING记录固定选择及执行代理对原始文本的逐例阅读，不冒充独立人工标注。\n\n技术失败见ENGINEERING_EVENTS、failure.json和Slurm日志，不作为语义成功率0。初次smoke2739导入失败，2740恢复验证通过；首轮preflight归档复验混入dev及其他条件，限定原始P/test后恢复，已完成GPU预测不变。\n')
    costs=[]
    for seed in (42,43,44):
      for method in ('N','F','R'):
        p=ROOT/f'local/s{seed}/{method}'
        if not (p/'refreshes.json').exists():continue
        refresh=read(p/'refreshes.json');logs=rows(p/'training.jsonl')
        costs.append(dict(seed=seed,condition=method,updates=len(logs),refreshes=len(refresh),source_pipeline_seconds=sum(r['generation_seconds'] for r in refresh),optimizer_seconds=sum(r['optimizer_seconds'] for r in logs)))
    with (ROOT/'condition_compute.csv').open('w') as f:
      if costs:w=csv.DictWriter(f,fieldnames=list(costs[0]));w.writeheader();w.writerows(costs)
    extra=[]
    for seed in (42,43,44):
      rr={r['condition']:r for r in costs if r['seed']==seed}
      if set(rr)=={'N','F','R'}:extra.append(dict(seed=seed,R源pipeline秒=round(rr['R']['source_pipeline_seconds'],3),F源pipeline秒=round(rr['F']['source_pipeline_seconds'],3),额外R减F_GPUh=(rr['R']['source_pipeline_seconds']-rr['F']['source_pipeline_seconds'])/3600))
    (ROOT/'RESOURCE_USAGE.md').write_text('# 资源核验\n\n'+f"全部GPU计算经sbatch+srun，单任务1GPU；累计{resource['gpu_hours']:.6f} allocation GPUh，本项目峰值{resource['peak_project_gpus']}，账号本轮峰值{resource['peak_account_gpus_since_first_allocation']}。失败/重试计入，batch/step行不重复加总。\n\n"+table(['seed','R源pipeline秒','F源pipeline秒','额外R减F_GPUh'],extra)+'\n\n刷新pipeline按实际GPU分配下的壁钟时间记录，包括新编码、前缀计算、质量解码、缓存I/O；不是GPU内核利用率。optimizer时间在condition_compute.csv。全部其他模型加载、评估、队列后分配等待与CPU写盘开销包含在总allocation记账中，不归因于纯前缀计算。原始JobID、GPU请求、节点、开始结束、退出码和Elapsed在slurm_accounting.psv。\n')
    print('Reports written; complete=',complete)
if __name__=='__main__':main()
