"""Reviewable report from checked outputs; no outcome is presumed."""
from mutil import *
import subprocess,datetime,re
def pct(x):return 'NA' if x is None else f'{100*x:.2f}%'
def rate(r):return pct(r['rate'])+f" ({r['k']}/{r['n']}; "+', '.join(pct(v) for v in r['ci95'])+')'
def table(head,rs):return '| '+' | '.join(head)+' |\n| '+' | '.join(['---']*len(head))+' |\n'+''.join('| '+' | '.join(str(v) for v in r)+' |\n' for r in rs)+'\n'
def main():
 verify();rr=read(ROOT/'results/confirmation_summary.json');sel=read(ROOT/'selection.json');checks=read(ROOT/'checks.json');jobmap=read(ROOT/'jobs.json');ledger=[];ids=','.join(jobmap)
 raw=subprocess.check_output(['sacct','-X','-j',ids,'--format=JobIDRaw,State,Start,End,ElapsedRaw,AllocTRES','--parsable2','--noheader'],text=True);events=[]
 for line in raw.splitlines():
  jid,state,start,end,elapsed,tres=line.split('|')[:6]
  if jid not in jobmap or jid==os.environ['SLURM_JOB_ID']:continue
  source=ROOT/f'logs/{jid}.out';log=None
  if source.exists():
   log=f'results/slurm_logs/{jid}.log';out=ROOT/log;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(source.read_bytes())
  m=re.search(r'gres/gpu=(\d+)',tres);g=int(m.group(1)) if m else 0;ledger.append(dict(job_id=jid,phase=jobmap[jid],state=state,start=start,end=end,elapsed_seconds=int(elapsed),gpus=g,log=log))
  if g and start!='Unknown':events.append((start,g))
  if g and end!='Unknown':events.append((end,-g))
 active=peak=0
 for ts,delta in sorted(events,key=lambda a:(a[0],a[1])):active+=delta;peak=max(peak,active)
 assert peak<=2;gpu_secs=sum(j['gpus']*j['elapsed_seconds'] for j in ledger);dump('run_ledger.json',dict(jobs=ledger,peak_gpus=peak,gpu_allocation_seconds=gpu_secs,postprocessing_job_id=os.environ['SLURM_JOB_ID'],resource_policy='Every compute phase sbatch allocation + srun step; global2 across projects; inspect user queue before GPU submission'))
 title='# 优化器重画、人称可达性与无对齐基线\n\n';text=title+f"所有训练与预测已完成并检查。新确认记录 **{checks['expected_confirmation_records']}** 条；全项目 GPU 实测峰值 **{peak}**，分配时间 **{gpu_secs/3600:.3f} GPU 小时**。新实验按 [protocol.json](protocol.json) 执行，权重选择只使用 dev，确认集不反向参与选择。\n\n"
 text+='## 优化器与主张表\n\n[绝对 CE 对照图](results/optimizer_absolute_ce.svg)、[规范 CE 差值图](results/optimizer_canonical_gap.svg)由原有固定面板重画，没有新预测。横轴给出 nats/target-token，虚线为规范编码 CE，标签为 AdamW1e-3 更新数。每个点为实测检查点；连线并非精确损失匹配的模型。Token MSE 为 world bootstrap95%，R5 为 world Wilson95%。\n\n'
 gaps=read(ROOT/'results/canonical_ce_gap.json');a=[r for r in gaps if r['variant']=='adam_1e3' and r['checkpoint'] in (0,100)];text+=table(['seed','更新','CE(编辑)−CE(规范)，nats/token','配对 world95% CI'],[[r['seed'],r['checkpoint'],f"{r['edited_minus_canonical_ce_mean']:.7g}",str(r['ci95_world_bootstrap'])] for r in a]);text+='负值是相同目标在规范编码之外具有更低 CE 的直接证据，不能把规范编码视为当前 CE 最优点；收益的绝对值很小。写入几何表和区间见 [write_geometry.json](results/write_geometry.json)：历史 CE 写入相对规范方向几乎正交，IID 范数比3.31–3.40，OOD3.69–3.80。此处比较的是理想写入大小，不是整个源状态大小。\n\n'
 text+='## 人称域：先 dev 选择，再新 worlds 确认\n\n闭式 ridge-RRR 在原96训练 worlds 的模板0、1↔2转换上拟合，训练更新为0。80新 dev worlds 与160新确认 worlds 及此前人称80确认 worlds 按 people/object/color/quantity 完整核心互斥。各操作与各 rank 按 dev token MSE 选 ridge，全部选到0.001。秩按 dev双向R5、全部合法单步、对齐MSE、较小rank依次排序。\n\n'
 text+=table(['rank','dev双向R5均值','dev全部单步','dev对齐MSE'],[[r,pct(v['R5']),pct(v['single']),f"{v['aligned_token_mse']:.6g}"] for r,v in sel['person']['dev'].items()]);text+=f"主分析选定 rank **{sel['person']['selected_rank']}**。以下四秩确认曲线均是预定诊断，不再按确认表现另选秩。\n\n"
 text+=table(['rank/条件','模板','全部合法单步均值','mask相等单步','对齐token MSE','正向R1 / R2 / R3 / R4 / R5','正向R5 95% CI','反向R5'],[[r['label'],r['template'],pct(r['single']['mean']),pct(r['aligned_single']['mean']) if r['aligned_single'] else 'NA',f"{r['token_mse']['mean']:.6g}" if r['token_mse'] else 'NA',' / '.join(pct(r['paths']['person_forward'][f'R{k}']['rate']) for k in range(1,6)),rate(r['paths']['person_forward']['R5']),rate(r['paths']['person_reverse']['R5'])] for r in rr if r['domain']=='person']);text+='模板3在此域没有 mask相等转换，单步地板与长度变化边界必须单列。不能将 MSE下降或某个rank单步失败单独解读为规范写法不存在；需要同时看解码准入、残差、双向链和 dev选择。RRR为确定性拟合，不能当作三个独立seed。\n\n'
 text+='## 时间域：覆盖匹配的无对齐对照\n\n四组均冻结同一 BART、rank16、随机初始化3 seeds42–44；训练全部12合法转换，template0、96worlds、600次更新、batch8/micro2、AdamW1e-3。CE_all 是覆盖与预算匹配的对照，不能把仅对齐C1当作其同数据基线。Floor 逐例计算 max(CE−CE_canonical,0) 后取均值；规范CE全程stop-gradient、提前缓存；它无需token对齐，也与经典反向梯度 flooding不同。\n\n'
 text+='Emb2Emb 风格控制采用非饱和 logistic adversarial loss，pool判别器和 DeepSets式 token-set(mean+max)敏感性，各扫描λ=0.01/0.1/1。每次editor更新配一次D更新，D lr1e-4，train-only固定归一化。真实样本来自原train规范序列，按编辑source的有效长度匹配，判别器看不到 padding/长度输入；长度变化时约束的是该 source长度可访问的边缘规范分布，而非目标配对表示。它无需token对齐，但不是原Emb2Emb的句向量/cosine任务目标复现。[原论文](https://aclanthology.org/2020.emnlp-main.491/)是方法来源。\n\n'
 text+=table(['判别器/λ','dev四路径R5均值（三seed）','dev全部单步均值','选中'],[[n,pct(v['mean_R5']),pct(v['mean_single']),'是' if n in sel['time']['selected_groups'] else '否'] for n,v in sel['time']['dev'].items()]);text+='dev为历史80中的固定前32worlds，明确属于暴露过的探索面板；选择后在完全新的160 time cores上一次性评测模板0和3。模型选择不使用OOD或确认输出。确认cores排除了历史五个明确文件（含上一轮160确认）。\n\n'
 for t in (0,3):
  text+=f'### 模板{t}\n\n';tr=[r for r in rr if r['domain']=='time' and r['template']==t]
  text+=table(['条件/seed','全部单步','非目标保持','mask相等单步','mask变化单步','token MSE','对齐+1 R1 / R2 / R3 / R4 / R5','对齐+1 R5 95% CI','原交替R5','原重排R5'],[[r['label'],pct(r['single']['mean']),pct(r['preserved']['mean']),pct(r['aligned_single']['mean']) if r['aligned_single'] else 'NA',pct(r['mask_changing_single']['mean']) if r['mask_changing_single'] else 'NA',f"{r['token_mse']['mean']:.6g}" if r['token_mse'] else 'NA',' / '.join(pct(r['paths']['aligned_from_plus_one'][f'R{k}']['rate']) for k in range(1,6)),rate(r['paths']['aligned_from_plus_one']['R5']),rate(r['paths']['original_alternating']['R5']),rate(r['paths']['original_reordered']['R5'])] for r in tr])
 text+='反向对齐链、全部world bootstrap区间和三seed S坐标残差均见 [confirmation_summary.json](results/confirmation_summary.json)。不能只报四路径平均来混淆对齐失败与长度变化失败。重编码是gold规范参照，不是使用错误学生输出的开放域解码重编码算法。\n\n'
 text+='### 判别器有效性与训练成本\n\n';ds=read(ROOT/'results/discriminator_summary.json');text+=table(['条件','seed','held-out dev real/fake AUROC','分类正确率','real概率','fake概率'],[[r['group'],r['seed'],f"{r['AUROC_real_vs_fake']:.4f}",pct(r['accuracy']['mean']),f"{r['real_probability']['mean']:.4f}",f"{r['fake_probability']['mean']:.4f}"] for r in ds]);text+='这些读数检查训练后的判别器能否区分规范与编辑分布。AUROC接近随机仍可能来自弱判别器或对抗博弈，不证明完整状态在流形上。即使两种实现都失败，也不能排除更强判别器、不同条件化、权重或预算。\n\n'
 costs=[]
 for n in sel['time']['selected_groups']:
  for s in SEEDS:
   a=read(ROOT/f'results/train_{n}_s{s}_complete.json');costs.append([n,s,a['updates'],a['discriminator_updates'],f"{a['seconds']:.2f}",a['job_id']])
 text+=table(['条件','seed','editor更新','D更新','训练wall秒','job'],costs);text+='选择网格共24个编辑器、14,400次editor更新，backbone更新0；单纯匹配更新数不等于训练计算成本相同。编码器缓存和规范CE提取单列为3342。新轮未重新测开放域推理成本，沿用上轮实测成本参照并保持计算节省不作为卖点。\n\n'
 text+='## 统一主张与边界\n\n';text+=table(['主张','证据','边界'],[
 ['解码等价不等于续步等价','上一轮新world修补/注入、time/person C1','受控数据与固定接口'],
 ['低维残差可当前隐蔽、续步致败','训练拟合S、独立world、pre/post KL','B为主；读取分量效应依赖seed/template'],
 ['time对齐rank16存在可组合写法','RRR、C2/C3、五seed确认','有限视界，不推及所有域'],
 ['规范编码不是当前输出CE最优点','同目标配对NLL更低，绝对差与worldCI','有限面板，非全局最优证明'],
 ['CE写入几乎不沿规范方向','cos(w,d)、范数比、负平行系数','历史编辑器/对齐转换，非形式化攻击'],
 ['CE可奖励非规范写入，AdamW下破坏组合','C4、SGD/小lr对照','并非所有优化器必然漂移'],
 ['规范锚定能修复time对齐','C3五seed R5与结构OOD','闭包有限、注入鲁棒性未解决'],
 ['person可达性必须先dev诊断','本轮rank/ridge曲线与新确认','L2失败不能证明任何线性编辑都不行'],
 ['流形约束与规范置信下限是无对齐检验','本轮覆盖匹配对照、3seed、dev选择','有限实现/网格；真实流形成员资格未证明'],
 ['轨迹监督与状态锚定有不同经验视界','既有exp5/C5与C3/RRR闭包','有限权重/训练预算，非理论上限']]);
 text+='## 论文初稿与 decoder-only\n\n[论文LaTeX初稿](../../paper/main.tex)已写出现象、机制、成因、修复和边界，并从本轮检查输出生成补充结果表。作者和venue未指定。服务器没有pdflatex，未声称已编译论文PDF；图有独立PDF/SVG/PNG。\n\ndecoder-only的“上次方案”在当前上下文与仓库中未找到模型、层和读取/写入接口；已在任务开始时请求补充。该复现尚未运行，按用户允许的future work方式写进稿件，不虚构准入或C1/C3/C4结果。其余优先项不依赖该信息。\n\n'
 text+='## 运行、异常与复现\n\n';text+=table(['job','阶段','GPU','秒','状态','日志'],[[j['job_id'],j['phase'],j['gpus'],j['elapsed_seconds'],j['state'],f"[{j['job_id']}]({j['log']})" if j['log'] else '未启动，无日志'] for j in ledger]);text+='所有计算由sbatch分配、srun执行；GPU提交前检查用户全局队列。两条串行依赖链确保此轮最多2×1GPU，没有绕过Slurm的后台训练。0 GPU后处理同样通过Slurm。\n\n3353–3356曾误用预估作业号作为依赖，在启动前取消（0分配秒）；3357–3360使用实际返回ID重新提交，未增加GPU并发。该提交错误不影响权重或预测。\n\n';text+='[完整审计](checks.json)、[开发选择与预测SHA](selection.json)、[确定性gzip证据](results/evidence.json)、[协议](protocol.json)、[账本](run_ledger.json)。权重/编码缓存保留本地，其指纹保存于每任务完成记录；原始预测、解析状态与评分均归档。图的CPU第二次重跑只改善标签可读性，没有重新训练或新增预测。\n'
 (ROOT/'REPORT.md').write_text(text)
 (ROOT/'README.md').write_text('# Manifold controls and person reachability\n\nRead [REPORT.md](REPORT.md), [protocol.json](protocol.json), and [selection.json](selection.json). All compute uses sbatch + srun; global GPU cap2. Main manuscript: [paper/main.tex](../../paper/main.tex).\n')
 # Automatically populate manuscript figures/tables without inventing outcomes.
 latex=['\\paragraph{Development-selected follow-up.}',f"The person diagnostic selects rank {sel['person']['selected_rank']} on 80 fresh development worlds, then evaluates all four predeclared ranks on 160 separate worlds. The temporal controls use three seeds, 96 training worlds, 32 historical development worlds, and 160 new confirmation cores.",'\\begin{center}\\begin{tabular}{llrr}\\toprule','Domain & Condition & Single (\\%) & Forward aligned $R_5$ (\\%) \\\\ \\midrule']
 for r in rr:
  if r['template']!=0:continue
  path='person_forward' if r['domain']=='person' else 'aligned_from_plus_one';name=r['label'].replace('_','\\_');latex.append(f"{r['domain']} & {name} & {100*r['single']['mean']:.2f} & {100*r['paths'][path]['R5']['rate']:.2f} \\\\")
 latex+=['\\bottomrule\\end{tabular}\\end{center}','The table gives every seed separately; single success averages all legal transitions, including unsupported length changes. Full forward/reverse trajectories, structural-template floors, and world confidence intervals are in the accompanying checked report. Selected adversarial weights and held-out discriminator diagnostics remain finite implementation tests rather than proof of manifold membership.']
 (ROOT.parents[1]/'paper/followup_results.tex').write_text('\n'.join(latex)+'\n')
 for filename in ['REPORT.md','README.md','CLAIMS.md']:
  for target in re.findall(r'\]\(([^)]+)\)',(ROOT/filename).read_text()):
   if not target.startswith('https:'):assert (ROOT/target).exists(),target
 dump('results/report_complete.json',dict(job_id=os.environ['SLURM_JOB_ID'],gpus=0,protocol_sha256=sha(ROOT/'protocol.json'),checks_sha256=sha(ROOT/'checks.json'),tex_compiled=False))
 manifest={str(path.relative_to(ROOT)):sha(path) for path in sorted(ROOT.rglob('*')) if path.is_file() and not set(path.relative_to(ROOT).parts)&{'logs','local','shards','__pycache__'} and path.name!='manifest.json'};dump('manifest.json',manifest)
 print('report complete',len(manifest),'files',flush=True)
if __name__=='__main__':main()
