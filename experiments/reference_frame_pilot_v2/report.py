import json,csv,collections,statistics
from common import *
def pc(x):return f'{float(x)*100:.2f}%'
def main():
 summaries=list(csv.DictReader((ROOT/'evaluation/summary.csv').open()));groups=json.loads((ROOT/'evaluation/test_complete.json').read_text())['groups'];budget=json.loads((ROOT/'budget.json').read_text());cgate=json.loads((ROOT/'evaluation/c_gate.json').read_text());analysis=json.loads((ROOT/'evaluation/analysis_complete.json').read_text());last=groups[-1]
 def find(g,st,p,m='latent_chain'):
  return next(x for x in summaries if x['group']==g and x['split']==st and x['path']==p and x['mode']==m)
 def rate(g,st,p,m='latent_chain'):return pc(find(g,st,p,m)['joint_ok'])
 text=f'''# 文本参考系转换 v2：覆盖与有限链监督

研究问题：在同一冻结BART上，补足有限链的合法时间输入覆盖，能否恢复事实保持的连续表示转换；若不能，25%时间样本的T_plus²终点监督能否修复并迁移？本轮实际执行 **{', '.join(groups)}，每组seed42、600更新**，另完成v1三seed的有限诊断A。没有新增Shift、多seed、自然长文或模型搜索。

**本轮测量：** IID原子joint从G0 {rate('G0','test_iid','atomic_all')} 到G1 {rate('G1','test_iid','atomic_all')}；T_plus²重编码从 {rate('G0','test_iid','plus_plus','decode_reencode')} 到 {rate('G1','test_iid','plus_plus','decode_reencode')}，G1纯表示仍为 {rate('G1','test_iid','plus_plus')}。'''
 if 'G2' in groups:text+=f" G2的IID T_plus²纯表示为 **{rate('G2','test_iid','plus_plus')}**，未训练T_minus²为 {rate('G2','test_iid','minus_minus')}、T_plus³为 {rate('G2','test_iid','plus3')}；原子为 {rate('G2','test_iid','atomic_all')}。\n"
 text+='\n**下一步决定：** 主线得到更明确的边界：覆盖修复能改善文本重编码链，但不足以恢复纯表示连续时间操作；指定两步监督能学会该链，却明显伤害单步及时间×人称组合。值得在后续小批多seed复核覆盖收益及这个取舍；暂停把当前25%混合配方作为通用组合方案扩展到自然文本。本批不再追加训练。所有结果为结构化自动检查 + 模型复核，尚无真人审核；不将单seed结果称为已成立的新方法。\n'
 text+='''
本轮对五个问题的直接回答：

1. G1相对G0减少了覆盖失败：IID T_plus²重编码75%→100%，OOD76.25%→93.75%；反向及三步重编码亦提高，但OOD原子98.33%→96.46%，并非所有指标同时改善。
2. 合法时间中间源已经覆盖，G1纯表示T_plus²、T_minus²、往返及三步仍为0%；相应IID重编码为97.5%–100%，差距仍然存在。
3. G2的训练过T_plus²纯表示达到IID100%/OOD93.75%；未训练T_plus³仅23.75%/25%，两个往返仅5%–10%，T_minus²及T_minus³仍0%。有有限迁移，远不足以称通用组合。
4. G2原子IID100%→83.33%、OOD96.46%→82.50%；IID时间→人称97.5%→50%，人称→时间97.5%→48.75%。三条已解析非日期错误均为G2数量变化，未决输出另计，不能忽视事实代价。
5. 支持继续有限机制研究，因为覆盖和链监督的影响已被匹配对照分开；不支持当前G2作为保持全部能力的修复方案。先复现这个收益—代价，停止按当前配方直接扩展。

## 1. 证据复核与预检

v1的已审阅提交6883cf0与本地v1子树一致，关键数字均从逐样本JSONL复算吻合，详见v1_evidence_audit.json。没有重跑v1训练或改写其数据/结果。

新数据480训练世界、80dev、160test（IID/OOD各80）、60calibration，与v1按完整事实键去重，全部视图依世界划分。13,395条gold/独立源文本规则检查通过；920个合法校准视图重构全部逐字相同，满足100%语义要求。BART hash及eval、无梯度、重复编码一致、编辑器梯度、padding和长度检查已保存。

新世界先满足日期合法性：completed的record_date=event_date，plan/cancelled的event_date=record_date+5；所有组一致。completed正offset源不合法；从[-1,+1]起始三次T_minus也无法满足所有view_date≥record_date。因此各测试层minus3只含53个合法plan/cancelled世界，其余路径80世界；27个completed是预定结构性不适用，不是根据输出剔除。合法性清单在模型输出前生成，统计与bootstrap保留这些固定分母。G0是匹配对照，不是v1原样复现。

v2在训练前更正过P算子的覆盖布尔元数据：P13/P31三组都保持[-2,+2]源覆盖，不能因时间算子扩到±3就把P13接收−3也标为已覆盖。源文本、目标、框架、操作哈希未变，校准输出继续有效；旧锁及更正证据保留calibration/metadata_lock_history和metadata_correction.json。没有改变测试评分规则或模型输出。

## 2. A：旧checkpoint的三路第二步输入

A1=T_plus(E(x))；A2=E(实际第一步文本)；A3=E(正确中间文本)。A3使用正确答案，仅是诊断对照。两条路径、三seed、每个80 IID记录均保留。第一步每次语义通过且actual_mid与gold_mid逐字相同，所以A3与A2输入相同，复用其确定性输出；A1/A2也复用v1存档，没有重复生成已有输出。

|第二步输入|全80 joint|覆盖内53 joint|覆盖外27 joint|
|---|---:|---:|---:|
|A1 编辑隐藏表示|0%|0%|0%|
|A2 实际文本重编码|66.25%|100%|0%|
|A3 正确中间文本重编码|66.25%|100%|0%|

以上在T_plus²和T_minus∘T_plus、三个seed中一致。每条80中47条原文本与gold_mid token长度不变、33条改变。T_plus²的A1两种长度组均0%，A2/A3等长组20/47、变长组33/33；等长本身不能解释纯链失败，也不等于位置语义已对齐。token ID与mask有效长度已逐例存储，A1保持原mask；没有比较未对齐逐位置表示距离。

每个有效token的第二步更新范数/输入范数仅描述性保存于diagnostic_a/outputs.jsonl，汇总于update_norm_summary.csv；没有依据该量改变训练、分析路径或损失。

## 3. 预注册门槛与训练核对

G1 dev时间原子joint={atomic}；四条时间两步重编码={reencode}；T_plus² latent={latent}。因此C分支运行状态为{run}，决定在新test生成前保存。
'''.format(atomic=pc(cgate['atomic_time_joint']),reencode=', '.join(k+' '+pc(v) for k,v in cgate['two_step_reencode'].items()),latent=pc(cgate['plus_plus_latent']),run=cgate['run_G2'])
 text+='\n|组|best step|dev token NLL|原子dev joint|监督token|输入token|有效算子样本调用|T_plus²替换次数|\n|---|---:|---:|---:|---:|---:|---:|---:|\n'
 for g in groups:
  md=json.loads((ROOT/f'checkpoints/{g}/complete.json').read_text());cc=md['counts'];text+=f"|{g}|{md['beststep']}|{md['best_dev_token_nll']:.6f}|{pc(md['dev_joint'])}|{sum(c['supervision_tokens'] for c in cc.values())}|{sum(c['input_tokens'] for c in cc.values())}|{sum(c['operator_sample_calls'] for c in cc.values())}|{md['replaced_occurrences']}|\n"
 text+='''
三组初始化tensor hash相同，来自checkpoints/initial.pt。每组9600样本，T+/T−各3200、人称各1600；相同六路径索引计划，P13/P31输入/目标/采样逐项相同。G1/G2还共用时间源文本。G2从G1的T_plus源offset[-2,+2]预定替换1600次，占全部时间样本25%及T_plus的50%；每样本仅终点CE，无第一步附加CE、不解码重编码、不沿G1续训。不同长度、额外算子调用使实际计算不严格相等。最终审计还确认三组P13/P31权重逐字节相同，G1/G2的T_minus权重相同；人称组合的退化不是偷偷改变人称训练分布造成的，T_minus²不改善也不应描述成T_minus发生遗忘。

## 4. 冻结测试主表

均为joint_ok，按固定世界分母。原子all/time/person分别每世界6/4/2视图，先在世界内平均；链每合法世界一个预定起始视图。所有组共用清单。完整日期、人称、非日期事实、解析及结束状态在evaluation/summary.csv；状态/偏移/每一步另表。

|测试层|路径|方式|世界N|'''+ '|'.join(groups)+'|\n|---|---|---|---:|'+ '|'.join(['---:']*len(groups))+'|\n'
 paths=['atomic_all','atomic_time','atomic_person',*CHAINS]
 for st in ['test_iid','test_template_ood']:
  for p in paths:
   for mode in (['latent_chain'] if p.startswith('atomic_') else ['latent_chain','decode_reencode']):
    rs=[find(g,st,p,mode) for g in groups];text+=f"|{st}|{p}|{mode}|{rs[0]['N_worlds']}|"+'|'.join(pc(r['joint_ok']) for r in rs)+'|\n'
 text+='\n## 5. 事实保持、未决与对照\n\n下表在每组全部主要神经输出上给出诊断计数，不能把不同路径当独立统计样本。非日期错误分母仅针对可解析输出，不能替代全分母事实保持率；主表分母始终包含未决。v1 collateral只包括frame正确时的内容错误，不包括date漂移，v2另列date_ok。\n\n|组|输出数|未决数|未正常结束|可解析数|已解析非日期事实错误|已解析日期错误|计划→完成规则命中|\n|---|---:|---:|---:|---:|---:|---:|---:|\n'
 for g in groups:
  rs=read(f'outputs/{g}.jsonl');text+=f"|{g}|{len(rs)}|{sum(r['score']['parse_unresolved'] for r in rs)}|{sum(not r['score']['normal_end'] for r in rs)}|{sum(not r['score']['parse_unresolved'] for r in rs)}|{sum(r['score']['parsed_nondate_error'] for r in rs)}|{sum(r['score']['parsed_date_error'] for r in rs)}|{sum(r['score']['plan_to_completed'] for r in rs)}|\n"
 text+='\n|对照|输出数|joint成功数|评分参照|\n|---|---:|---:|---|\n'
 for name,fn,note in [('Text-rule','text_rule','目标参考系，仅源文本+框架'),('Target reconstruction','target_reconstruction','正确目标参考系，oracle可重构性诊断'),('Reconstruction','reconstruction_controls','无编辑原参考系，多次编解码')]:
  rs=read(f'outputs/{fn}.jsonl');text+=f"|{name}|{len(rs)}|{sum(r['score']['joint_ok'] for r in rs)}|{note}|\n"
 text+='''
正确目标重构不是数学上界或部署能力。规则完美不意味着神经方法实用更好。未决输出需要语义审查；不能由已解析子集没有错便声称全部事实保持。模型复核见review/model_review.md，未决/已解析错误抽查是便利样本，不用于准确率校正。原自动评分保持不变。

## 6. 统计与解释边界

IID核心配对差值（百分点，记录bootstrap95%区间）：G1−G0的T_plus²重编码 +25.00 [16.25,33.78]；G2−G1原子 −16.67 [−20.42,−12.92]，时间→人称纯链 −47.50 [−58.75,−37.50]，T_plus³纯链 +23.75 [15.00,33.75]。T_plus²纯链的 +100 [100,100] 是该有限样本bootstrap退化区间，不证明总体必然100%。

2000次paired bootstrap按世界/record_id，IID/OOD分别抽取同一套80世界索引，所有视图/路径同抽；minus3只在预定合法世界中取均值。G1−G0与G2−G1逐路径差值和95%区间在evaluation/paired_statistics.json。只有seed42，区间不包括训练随机性。

覆盖变化在同世界、同样本数、同初始化、同路径比例下比较，但有限源分布变化本身包含旧偏移概率的再分配；不能把G1叫额外增加相同训练量。新增否定与模板分布为本批受控生成规律；具体地，模板家族奇偶与否定标记相关，未解耦所有语言因素。该相关性三组完全一致，合法offset×operation×status×polarity单元均有样本，但仍限制语言泛化结论。训练/测试没有新词或自然文本，因此不作开放语言泛化断言。

**辅助诊断与机制猜测分开：** A识别出明确源表达覆盖不足，同时覆盖内仍有纯链失败。重编码好于纯链只提示编辑表示继续使用的问题；没有未对齐隐藏距离证据，不能宣称“离开流形”或“BART固有缺陷”。G2只直接监督T_plus²；其余路径的收益才是未训练序列迁移，三步收益也只能是这两条有限序列。若原子/事实退化，必须把取舍一起报告。

## 7. 资源、审查与复现

'''
 text+=f"本轮累计 **{budget.get('consumed_gpu_seconds',0)} GPU分配秒（{budget.get('consumed_gpu_seconds',0)/3600:.4f} GPU小时）**，上限7200秒，始终单GPU。队列等待独立记在budget.json/sacct，父与step不重复相加。实际执行的三组训练没有追加更新或seed。核心神经输出{analysis['neural_rows']}，对照输出{analysis['baseline_rows']}；另有扩展源原子诊断，不参与checkpoint选择。\n"
 text+='''
engine.infer纯链只编码原句一次，保留原mask；中间解码用于离线诊断，不输入后续隐藏链。每步frame更新与评分保存。计时将actual_path与diagnostic_decode分开，重编码包含所有编解码；不以edit-only时间或参数量推断端到端加速。

固定20个测试世界的匿名方法与路径审查表：review/blind_review.csv，独立映射private_mapping.json。尚无真人标签。19条可读解释性案例位于[review/CASES.md](review/CASES.md)，机器可读版为review/explanatory_cases.jsonl，便利抽样涵盖覆盖修复、链修复（若有）、仍失败和事实受损，不能估计频率。

复现入口：prepare.py（已有数据拒绝覆盖）、preflight.py、diagnostic_a.py、train.py G0/G1/条件G2、test.py、analyze.py、report.py；GPU均通过run.slurm+srun。实际命令在commands.log。每次恢复先按budget.json历史job核算剩余总额，不能重置预算。最新optimizer/RNG仅本地，best权重及冻结哈希保存。新探索另开目录，v1不变。

本批未运行自然文本/长文、现代LLM/Agent/HE、probe/SAE/层扫描/谱正则、rank/LR搜索、seed43/44。这些未执行是明确范围限制，不是缺失结果。
'''
 (ROOT/'REPORT.md').write_text(text)
if __name__=='__main__':main()
