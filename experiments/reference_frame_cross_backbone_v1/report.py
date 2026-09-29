import csv
from common import *
def main():
 budget=json.loads((ROOT/'budget.json').read_text());summary=list(csv.DictReader((ROOT/'evaluation/summary.csv').open())) if (ROOT/'evaluation/summary.csv').exists() else [];facts=list(csv.DictReader((ROOT/'evaluation/fact_summary.csv').open())) if (ROOT/'evaluation/fact_summary.csv').exists() else []
 def find(model,g,split,path,mode='latent_chain'):return next((r for r in summary if (r['model'],r['group'],r['split'],r['path'],r['mode'])==(model,g,split,path,mode)),None)
 def fmt(model,g,split,path,metric='trajectory_joint',mode='latent_chain'):
  r=find(model,g,split,path,mode)
  if not r:return '未训练/未评估'
  n=r['endpoint_successes' if metric=='endpoint_joint' else 'trajectory_successes'];return f"{n}/{r['N_outputs']} ({float(r[metric])*100:.2f}%)"
 admissions={m:json.loads((ROOT/f'calibration/{m}/admission.json').read_text()) if (ROOT/f'calibration/{m}/admission.json').exists() else {'status':'not_run','passed':False} for m in MODELS}
 completed=[m for m in MODELS if (ROOT/f'evaluation/{m}_complete.json').exists()]
 lines=['# 跨骨干参考系编辑预实验：实际结果','下表G1/G3依次列出；两步/三步指T_plus²/T_plus³的纯表示全轨迹，原子为六视图按世界内平均。预检不通过的模型没有训练结果，不能填成编辑准确率0。','|模型/层|准入|G1/G3原子|G1/G3两步全轨迹|G1/G3三步全轨迹|时间→人称 G1/G3|人称→时间 G1/G3|已解析非日期错/未决|GPU秒|','|---|---|---|---|---|---|---|---|---:|']
 for model in MODELS+(['BART'] if find('BART','G1','test_iid','atomic_all') else []):
  a=admissions.get(model,{'status':'复用参照，64/64存档复现'});secs=sum(j.get('gpu_seconds',0) for j in budget['jobs'] if j['model']==model)
  if model!='BART' and model not in completed:lines += [f"|{model}|{a['status']}|—|—|—|—|—|见重构分层，非编辑结果|{secs}|"];continue
  for split,label in [('test_iid','IID'),('test_template_ood','OOD')]:
   cells=[' / '.join(fmt(model,g,split,p,'endpoint_joint' if p=='atomic_all' else 'trajectory_joint') for g in ['G1','G3']) for p in ['atomic_all','plus_plus','plus3','plus_person','person_plus']]
   fs=[r for r in facts if r['model']==model and r['split']==split];damage='；'.join(f"{r['group']} {r['nondate_error_N']}错/{r['unresolved_N']}未决/{r['N']}输出" for r in fs)
   lines+=['|'+model+'/'+label+'|'+a['status']+'|'+'|'.join(cells)+'|'+damage+'|'+str(secs)+'|']
 lines += ['\n## 直接回答本批问题']
 findings=ROOT/'FINDINGS.md'
 lines += [findings.read_text() if findings.exists() else '完整结果仍在运行；此文件不是最终结论。']
 lines += ['## 固定A/B准入结果','原句分母920合法视图；目标阶段分母5880，保留同世界重复出现的相关性。相同文本只生成一次并按预定角色/出现回填评分，两类分母不视为独立样本。优先最大化两类joint较低值、再总体值、平局A。','|模型|包装|原句joint n/N|目标joint n/N|逐字一致/6800|正常结束/6800|未决/6800|是否选中|','|---|---|---:|---:|---:|---:|---:|---|']
 for model,a in admissions.items():
  for r in a.get('summaries',[]):
   rates=r['rates'];lines += [f"|{model}|{r['wrapper']}|{round(rates['source']*920)}/920 ({rates['source']*100:.2f}%)|{round(rates['target']*5880)}/5880 ({rates['target']*100:.2f}%)|{r['exact']}|{r['normal_end']}|{r['unresolved']}|{r['wrapper']==a['selected_wrapper']}|"]
  if not a.get('summaries'):lines += [f"|{model}|—|{a['status']}|—|—|—|—|—|"]
 lines += ['FLAN-T5-large的B包装原句898/920、目标5762/5880，均未达到精确的98%门槛，不按四舍五入后的98.0%放行。22条未确认原句中，描述性字符串核对发现9条只缺记录日期后的句点，另13条仅输出作者/记录日期、遗漏正文。前9条说明严格parser存在格式局限，不能都称为事实损坏；主分数与门槛保持冻结，未据此补训练。细节见calibration/flan-t5-large/punctuation_diagnostic.json和review/MODEL_REVIEW.md。', 'T5Gemma IT B包装原始逐字一致为0/6800，去除首尾空白后为6800/6800；输出保留了额外换行。原始字符串没有被覆盖，语义评分沿用旧解析逻辑，重编码按官方chat模板统一处理正文。']
 lines += ['\n各包装×角色×计划/完成/取消的全部n/N及字段判定见calibration/<模型>/admission.json、A_scored.jsonl、B_scored.jsonl。实际渲染输入、特殊token、EOS及长度见*_unique_outputs.jsonl。不因未决修改parser、删样本或补第三种指令。未决不等于逐条确认语义错误；便利模型复核只能说明所读例子。',
 '## 接口、精度、配置与初始化','模型权重在/dataset1/zailong/models/reference-frame-cross-backbone/，revision、tokenizer revision、文件hash、下载耗时见models/*.json；基础权重不上传。既有环境未升级，软件版本见environment.json，模块源码hash和实际加载类见*_interface.json。',
 '|模型|实际类|d|每算子参数/四算子总数|输入上限/生成上限|dtype/attention|包装|','|---|---|---:|---|---|---|---|']
 for model in MODELS+['BART']:
  p=ROOT/f'models/{model}_interface.json'
  if not p.exists():continue
  c=json.loads(p.read_text());lines += [f"|{model}|{c['model_class']}|{c.get('encoder_output_dimension','—')}|{c.get('parameters_per_operator','—')}/{c.get('total_editor_parameters','—')}|{c['source_length']}/{c['max_new_tokens']}|{c['dtype']}/{c['attention']}|{admissions.get(model,{}).get('selected_wrapper','A' if model=='BART' else '—')}|"]
 lines += ['\n编辑位置为encoder最后表示、decoder cross-attention投影之前；维度实测而非硬编码。全部非padding token编辑，包括包装/特殊token。四个独立rank16参数为33d与132d。G1/G3同骨干初始权重共享，但跨骨干不载BART编辑器。',
 'T5Gemma2首次加载受嵌套dtype影响，encoder曾为bf16，尚未生成A/B结果就因与float32编辑器不兼容而失败。显式model.float()恢复既定float32协议，重试完整预检；失败日志和55 GPU秒保留。未改变旧环境或评分。FLAN checkpoint的shared/lm_head权重不一致警告由Transformers处理为保留两者，没有擅自强制权重绑定。',
 'API预检含右移labels对齐、显式/隐式teacher forcing logits一致、零编辑/直通生成一致、确定性、H与编辑器有限非零梯度、第二步CE能回传H1、骨干无梯度、样本骨干权重未变、padding不变。低秩V初始零梯度可正常，未要求每个因子首步非零。',
 '训练若通过准入：AdamW .001/weight_decay0、float32、clip1、600更新、有效batch16、microbatch4，各完整有效batch权重分母先算再累积；每100原子dev token NLL选best，平局早者。G3链样本阶段均值各0.5，外权为终点有效token数。不同骨干不跨tokenizer比较NLL，不称等FLOPs。未进入训练的模型没有伪造训练曲线或best checkpoint。',
 '## 共同确认集：全部核心路径','新seed2026092904，与v1/v2/v3完整事实键去重。80IID/80模板OOD，词汇共享，模板奇偶与否定相关的旧局限保留。minus3仅53个合法世界，其余每链80；27个completed在模型输出前标N/A。原子每世界六视图，先世界内平均；主率保留未决/重构失败/未结束。',
 '|模型|层|路径|方式|G1终点|G3终点|G1全轨迹|G3全轨迹|','|---|---|---|---|---|---|---|---|']
 for model in ['BART']+completed:
  for split,label in [('test_iid','IID'),('test_template_ood','OOD')]:
   for path in list(ATOMIC)+list(CHAINS):
    for mode in ['latent_chain']+(['decode_reencode'] if path in CHAINS else []):
     if not find(model,'G1',split,path,mode):continue
     cells=[fmt(model,g,split,path,metric,mode) for metric in ['endpoint_joint','trajectory_joint'] for g in ['G1','G3']];lines+=['|'+model+'|'+label+'|'+path+'|'+mode+'|'+'|'.join(cells)+'|']
 lines += ['\n逐步frame/date/person和每个非日期字段、遗漏/重复文本诊断见per_step.csv；按T_plus源offset/person/status/polarity分层见T_plus_strata.csv。解析字段错误见fact_errors.csv，完整固定分母及解析子集分母见fact_summary.csv。未决不能被“已解析子集零错误”掩盖。正确目标重构是oracle诊断而非数学上界；规则只读源文本及框架。无编辑循环1/2/3次、每阶段target和原句重构见各模型controls.jsonl，缓存只复用完全相同实际文本，不用gold替换模型输出。',
 '主表事实错误/未决统计的是1866个路径方式终点输出，每个世界有多条相关路径，不是1866个独立世界；日期错误另列，全部中间阶段字段见per_step.csv。未解析输出不进入“已解析字段错误”计数，不能据零已解析非日期错误宣称全部事实保持。',
 '## 训练与对照实测','|模型|组|更新/选中步|监督token|算子样本调用|decoder前向批次|训练含dev秒|峰值显存字节|','|---|---|---|---:|---:|---:|---:|---:|']
 for model in completed:
  for g in ['G1','G3']:
   c=json.loads((ROOT/f'checkpoints/{model}/{g}/complete.json').read_text());v=list(c['counts'].values());lines += [f"|{model}|{g}|{c['step']}/{c['beststep']}|{sum(r['supervision_tokens'] for r in v)}|{sum(r['operator_calls'] for r in v)}|{sum(r['decoder_forward_calls'] for r in v)}|{c['wall_seconds']:.2f}|{c['peak_cuda_bytes']}|"]
 lines += ['这里的前向批次按实际microbatch调用统计；算子调用按样本次数统计。训练秒不含全部GPU加载/调度时间，资源账本则计完整分配秒。两训练作业可能并发，不据这一次运行的耗时差作端到端性能结论。training_counts.csv逐算子列出更新、token与时间；dev_curves.csv保存全部六次完整原子dev检查。',
 '|模型|层|对照|全轨迹 n/N|未决阶段数|','|---|---|---|---:|---:|']
 import collections
 control=collections.defaultdict(lambda:[0,0,0])
 for r in csv.DictReader((ROOT/'evaluation/control_summary.csv').open()):
  v=control[r['model'],r['split'],r['kind']];v[0]+=int(r['N']);v[1]+=int(r['trajectory_N']);v[2]+=int(r['unresolved_stage_N'])
 for (model,split,kind),v in control.items():lines += [f"|{model}|{split}|{kind}|{v[1]}/{v[0]}|{v[2]}|"]
 rules=read('outputs/text_rule.jsonl');lines += [f"Text-rule全轨迹{sum(r['trajectory_joint'] for r in rules)}/{len(rules)}。这是固定受控语法内基线，不构成神经方法的性能优势。重构缓存只节省重复诊断生成，不以缓存后的总时间冒充每次部署重构成本。timing_summary.csv分别报告encode、edit、实际decode和纯链诊断decode；BART batch4、新IT正式batch16，不能直接据其计时归因骨干速度。",'## 配对差值','|模型|层|路径|指标|G3−G1百分点 [记录bootstrap 95%区间]|','|---|---|---|---|---:|']
 for r in json.loads((ROOT/'evaluation/paired_statistics.json').read_text())['results']:
  if r['comparison']=='G3-G1' and r.get('mode')=='latent_chain' and r['metric']=='trajectory_joint' and r['path'] in ['T_plus','plus_plus','plus3','plus_person','person_plus']:
   lines += [f"|{r['model']}|{r['split']}|{r['path']}|{r['metric']}|{100*r['delta']:+.2f} [{100*r['ci95'][0]:+.2f}, {100*r['ci95'][1]:+.2f}]|"]
 lines += [
 '## 统计与证据边界','2000次配对world bootstrap，同层所有模型/路径/视图共用重采样索引。paired_statistics.json含每模型G3−G1、latent−reencode；只有存在新骨干完成结果时才有跨骨干−BART差值。单seed区间只涵盖记录抽样，不涵盖训练随机性；探索性多比较不作确认性显著发现。',
 '本轮测量、对照支持的解释、机制猜测分开：重编码优于纯链仅支持继续使用编辑表示存在问题，不能证明离开流形；更大/指令模型的差异同时涉及tokenizer/包装/训练前提，不能唯一归因规模或架构。没有decoder-only实验。',
 '## 资源与完成状态',f"实际累计{budget['total_gpu_seconds']} GPU分配秒（{budget['total_gpu_seconds']/3600:.4f}小时），预检{budget['preflight_gpu_seconds']}秒，上限分别14400/3600。用户途中将并发上限放宽为2，见PROTOCOL_AMENDMENT_01；每作业单GPU、sbatch+srun，父/step最大ElapsedRaw不重复计费，排队另列。基础下载无GPU，分别记录耗时。",
 '完成/准入不通过/接口失败/预算跳过分别见每模型admission及预算记录，不混入准确率。没有自动扩大模型、prompt、rank、训练步数或seed。已获准的模型下载完成；未训练模型是准入规则限制，不冒称进行了G1/G3。',
 '## 审查与复现','预先20确认世界的匿名完整轨迹见review/blind_trajectories.csv，映射review/private_mapping.json独立保存。最多20配对便利案例见[review/CASES.md](review/CASES.md)，模型复核另存；human_label为空，尚无真人审核。',
 '复现见README.md与commands.log。协议、原世界哈希、评分器锁、模型/初始化/接口配置均保存。v1/v2/v3只读核验；独立分支本地提交，远端只同步独立分支，不覆盖main。原模型权重、环境、凭据和latest优化器恢复状态不上传。']
 (ROOT/'REPORT.md').write_text(''.join(('\n' if i and line.startswith('|') and lines[i-1].startswith('|') else '\n\n' if i else '')+line for i,line in enumerate(lines))+'\n');print('report written')
if __name__=='__main__':main()
