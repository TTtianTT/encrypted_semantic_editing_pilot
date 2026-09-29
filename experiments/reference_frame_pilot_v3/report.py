import csv
from common import *
def main():
 rows=list(csv.DictReader((ROOT/'evaluation/summary.csv').open()));facts=list(csv.DictReader((ROOT/'evaluation/fact_diagnostics.csv').open()));ck=json.loads((ROOT/'checkpoints/G3/complete.json').read_text());budget=json.loads((ROOT/'budget.json').read_text());gate=json.loads((ROOT/'evaluation/next_round_gate.json').read_text());paired=json.loads((ROOT/'evaluation/paired_statistics.json').read_text())['results']
 def cell(dataset,split,g,p,m='trajectory_joint',mode='latent_chain'):
  return float(next(r for r in rows if (r['dataset'],r['split'],r['group'],r['path'],r['mode'])==(dataset,split,g,p,mode))[m])
 pct=lambda v:f'{100*v:.2f}%'
 lines=['# G3：逐步监督最小验证', '“G3是否让同一个小时间算子在每次调用时都正确转换参考系，同时保持事实？”',
 '实测：新IID确认集G3单步和T_plus²完整轨迹均100%，G2分别为52.5%和56.25%；但人称→时间92.5%，较G1的98.75%下降6.25个百分点，超过预定5个百分点容限。OOD两步全轨迹80%，未训练三步全轨迹仅IID13.75%/OOD5%。只能支持已训练两步的局部修复。',
 '回答：'+('新IID确认集达到预注册的单步、两步全轨迹和跨操作保持门槛，支持下一轮多seed及等监督预算复核；这还不是任意长度可组合或总体可靠性的证明。' if gate['all_passed'] else '新IID确认集未同时达到预注册的全部门槛；本批停止，不自动扩大训练或修改损失。'),
 f"实际只新增G3 seed42一次600更新；G1/G2权重及旧输出复用。best={ck['beststep']}步，原子dev token NLL={ck['best_dev_token_nll']:.8f}。所有结果按固定合法世界分母。旧诊断集与新确认集分开。尚无真人审核：结构化自动检查 + 模型复核。",
 '## 核心配对结果（纯表示链）']
 for dataset,title in [('confirmation','新确认集'),('diagnostic','既有诊断集（影响过本轮设计）')]:
  lines += ['\n### '+title,'|层|指标|G1|G2|G3|','|---|---|---:|---:|---:|']
  for split,label in [('test_iid','IID'),('test_template_ood','OOD')]:
   for path,metric,name in [('T_plus','endpoint_joint','T_plus单步'),('plus_plus','first_joint','T_plus²第一步'),('plus_plus','endpoint_joint','T_plus²终点'),('plus_plus','trajectory_joint','T_plus²全轨迹'),('plus3','endpoint_joint','T_plus³终点'),('plus3','trajectory_joint','T_plus³全轨迹'),('plus_person','trajectory_joint','时间→人称全轨迹'),('person_plus','trajectory_joint','人称→时间全轨迹'),('other_atomic','endpoint_joint','其他原子')]:
    lines += ['|'+label+'|'+name+'|'+'|'.join(pct(cell(dataset,split,g,path,metric)) for g in ['G1','G2','G3'])+'|']
 lines += ['\n### 六条原子分别报告（新确认集）','|层|路径|G1|G2|G3|','|---|---|---:|---:|---:|']
 for split,label in [('test_iid','IID'),('test_template_ood','OOD')]:
  for path in ATOMIC:lines+=['|'+label+'|'+path+'|'+'|'.join(pct(cell('confirmation',split,g,path,'endpoint_joint')) for g in ['G1','G2','G3'])+'|']
 lines += ['\n### 重编码链对照（新确认集）','|层|路径|G1终点/轨迹|G2终点/轨迹|G3终点/轨迹|','|---|---|---:|---:|---:|']
 for split,label in [('test_iid','IID'),('test_template_ood','OOD')]:
  for path in ['plus_plus','plus3','plus_person','person_plus']:lines+=['|'+label+'|'+path+'|'+'|'.join(pct(cell('confirmation',split,g,path,'endpoint_joint','decode_reencode'))+'/'+pct(cell('confirmation',split,g,path,'trajectory_joint','decode_reencode')) for g in ['G1','G2','G3'])+'|']
 controls=json.loads((ROOT/'evaluation/final_integrity.json').read_text())['controls']
 lines += ['\n对照完整分母与通过数：`'+json.dumps(controls,ensure_ascii=False)+'`。目标重构是oracle可表达性诊断，不是数学上界；规则只读取输入与frame。']
 lines+=['\n完整六原子路径（包括T_plus_first/third、T_minus_first/third及两人称）、两种执行方式及全部反向/往返/三步路径见evaluation/summary.csv。每步事实/未决/正常结束见steps.csv，T_plus源offset、人称和状态见T_plus_stratified.csv。主率保留未决和未正常结束；trajectory_joint逐例取所有阶段交集。',
 '## 未训练链与解释边界','|新集层|纯表示路径|G1全轨迹|G2全轨迹|G3全轨迹|','|---|---|---:|---:|---:|']
 for split,label in [('test_iid','IID'),('test_template_ood','OOD')]:
  for path in ['minus_minus','plus_minus','minus_plus','person_return','minus3']:
   lines+=['|'+label+'|'+path+'|'+'|'.join(pct(cell('confirmation',split,g,path)) for g in ['G1','G2','G3'])+'|']
 lines+=['\n两步源offset±2、三步±1；时间中间输入在G1合法源覆盖内，人称按其实际±2源范围标注。每路径通常80世界，minus3为53：27个completed因所有参考日不得早于记录日而在模型输出前预定不适用。无按失败筛样本。仅训练T_plus²的两个阶段，未训练其他序列；若三步仍差，只支持有限已训练长度。反向算子的原子监督不变，其两步失败不能叫遗忘。',
 '本轮测量支持的结论只限表中能力。辅助诊断识别了G2提前输出终点日期的模式；它不证明容量必然受限。G3同时加入第一步目标、降低原终点损失的相对权重，并增加解码计算；不能唯一归因于中间监督，也不称严格等FLOPs。没有做隐藏空间距离分析，更不据此声称离开流形。',
 '## 事实保持与不确定输出','以下计数以每组该层全部最终输出为分母，跨路径相关，不当独立样本。全阶段另在fact_diagnostics.csv；可解析子集事实错误不能替代全分母保持率。',
 '|集合|层|组|输出N|可解析N|非日期事实错|日期错|未决|未结束|','|---|---|---|---:|---:|---:|---:|---:|---:|']
 for r in facts:
  if r['scope']=='endpoint':lines+=['|'+'|'.join(r[k] for k in ['dataset','split','group','N','parsed_N','nondate_error_N','date_error_N','unresolved_N','not_ended_N'])+'|']
 errors=list(csv.DictReader((ROOT/'evaluation/parsed_nondate_errors.csv').open())) if (ROOT/'evaluation/parsed_nondate_errors.csv').exists() else []
 counts={}
 for r in errors:
  key=r['dataset']+'/'+r['group']+'/'+r['field'];counts[key]=counts.get(key,0)+1
 lines+=['\n逐阶段已解析非日期错误字段计数：`'+json.dumps(counts,ensure_ascii=False)+'`。角色、数量、动作、状态/否定/归属等逐例列于parsed_nondate_errors.csv；未决不自动标注为已确认语义错误。',
 '## 日期错误模式与旧证据核对','G2旧IID T_plus²首步41/80、终点80/80、全轨迹41/80；旧OOD首步42/80、终点75/80、全轨迹40/80，由逐例交集计算。v2_test_iid_0002与0001的原始轨迹保存在v2_example_audit.jsonl，未修改旧输出。',
 '新IID的G2首步日期45/80正确、25/80提前到两步目标、10/80仍停原日期；G3为80/80正确。新OOD的G3首步74/80正确、5/80停原日期、1/80提前。错误不全是提前到终点。',
 '第一步错日期比较规范化相对offset：把解析输出日期减去该第一步frame.view_date，再比较源、第一步和第二步gold的相对offset。绝不把各gold在自身frame下还原的相同绝对事件日拿来区分阶段。分类完整清单/计数见first_date_classes.csv与first_date_class_counts.csv。',
 '## 训练与必要实现验证',
 '真实混合batch含6普通+10链样本，在初始权重和只读G2权重分别校验0/1损失与原G2、活动编辑器梯度一致（float32容差内）。正式0.5/0.5两阶段梯度非零且有限，BART参数无梯度、eval确定、padding不变、源mask与目标一致。校验权重未用于G3初始化，正式从initial.pt重开。',
 '|操作|更新|样本|实际监督token|G2终点权重token|算子样本调用|解码batch调用|训练秒|','|---|---:|---:|---:|---:|---:|---:|---:|']
 for op,c in ck['counts'].items():lines+=['|'+op+'|'+'|'.join(str(c[k]) for k in ['optimizer_updates','samples','supervision_tokens','endpoint_weight_tokens','operator_sample_calls','decoder_batch_calls'])+f"|{c['seconds']:.3f}|"]
 lines += [f"\n总监督token={sum(c['supervision_tokens'] for c in ck['counts'].values())}，G2终点权重token={sum(c['endpoint_weight_tokens'] for c in ck['counts'].values())}；1600替换位置与G2逐项一致。训练峰值CUDA分配={ck['peak_cuda_bytes']} bytes，训练/开发观察阶段墙时={ck['wall_seconds']:.2f}s。普通样本采用数学等价token归一化，浮点求和造成未改监督算子权重最大约4.5e-6差异，审计已记录，不称字节完全相同。",
 '六次检查点按完整原子dev token NLL选择；观察轨迹不是选模指标。完整学习过程见checkpoints/G3/complete.json与evaluation/dev/。初始、模型、数据、配置、训练代码和checkpoint hash均保存。',
 'G3新确认集最终输出中IID未决302/1866、OOD309/1866；OOD两条已解析非日期损坏均为数量变化（往返链7→4与2→3），不可称全路径事实零损坏。具体模型复核见review/model_review.md。',
 '## 配对统计及下一轮决定','2000次按世界配对bootstrap，IID/OOD及两个集合分别处理，同世界所有路径/视图用同一组重采样索引；仅seed42，区间不包含训练随机性。以下为新确认集G3−G2百分点差（95%记录抽样区间）。','|层|指标|差值pp|95%区间pp|','|---|---|---:|---:|']
 for r in paired:
  if r['dataset']=='confirmation' and r['comparison']=='G3-G2' and r['mode']=='latent_chain' and (r['path'],r['metric']) in [('T_plus','endpoint_joint'),('plus_plus','trajectory_joint'),('plus3','trajectory_joint'),('plus_person','trajectory_joint'),('person_plus','trajectory_joint')]:
   lines += [f"|{r['split']}|{r['path']}/{r['metric']}|{r['delta']*100:.2f}|[{r['ci95'][0]*100:.2f}, {r['ci95'][1]*100:.2f}]|"]
 lines+=['\n新IID工程门槛逐项：`'+json.dumps(gate['checks'],ensure_ascii=False)+'`。'+('全部满足，值得下一轮补seed与等监督预算对照；先不扩大自然文本或宣称通用组合。' if gate['all_passed'] else '未全部满足，本批到此停止，不自动调系数或追加训练。')+' OOD和事实/未决必须与门槛一起判断；已训练长度与未训练长度分别报告。',
 '## 资源、交付与复现',f"累计{budget['total_gpu_allocation_seconds']} GPU分配秒（{budget['gpu_hours']:.4f}小时），上限3600；父/step不重复累计，队列单列，始终至多1张GPU。1735/1736为Slurm step启动失败，没有模型输出，合计3秒也计入预算；随后避开故障节点重试相同评估。训练只运行一次。",
 '执行命令见commands.log，Slurm原始记账见logs/sacct.txt，预算见budget.json。encode/edit/decode及纯链中间诊断解码时间逐例保存；未宣称端到端加速。',
 '新确认集预选20世界的匿名全轨迹见review/blind_trajectories.csv，方法/路径映射独立保存。配对解释案例见[review/CASES.md](review/CASES.md)，对应JSONL可复核；没有某类案例就明确写没有观察到。便利抽样不能估计准确率，模型复核不是人工真值。',
 '本批未运行多seed、等监督预算额外训练、三步训练、反向训练、自然文本、其他模型、rank/系数搜索或加密；它们不在授权范围。v1/v2保持原样，Git仅提交v3目录；原BART与环境不上传，latest优化器状态仅本地保存。']
 (ROOT/'REPORT.md').write_text(''.join(('\n' if i and line.startswith('|') and lines[i-1].startswith('|') else '\n\n' if i else '')+line for i,line in enumerate(lines))+'\n')
 print('report written')
if __name__=='__main__':main()
