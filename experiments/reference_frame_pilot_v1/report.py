import json,csv,statistics
from prepare import ROOT

def readcsv(path):return list(csv.DictReader((ROOT/path).open()))
def pct(x):return f'{float(x)*100:.2f}%'
def main():
 stats=readcsv('evaluation/seed_summary.csv');summary=readcsv('evaluation/summary.csv');audit=json.loads((ROOT/'evaluation/audit.json').read_text());budget=json.loads((ROOT/'budget.json').read_text());slots=readcsv('evaluation/slot_errors.csv');consistency=readcsv('evaluation/composition_consistency.csv');inverse=readcsv('evaluation/inverse_forward_return.csv')
 def stat(m,s,p):return next(r for r in stats if r['method']==m and r['stratum']==s and r['path']==p)
 lr=stat('LowRank16','test_iid','atomic_all');lo=stat('LowRank16','test_template_ood','atomic_all');sh=stat('Shift','test_iid','atomic_all')
 lc=stat('LowRank16','test_iid','time_then_person/latent_chain');rc=stat('LowRank16','test_iid','time_then_person/decode_reencode');lc2=stat('LowRank16','test_iid','time_twice/latent_chain')
 text=f'''# 文本参考系转换 v1：实际运行报告

1. **单步能否做到？** 在受控模板与固定操作 ID 上，LowRank16 的三 seed 单步联合成功率 IID 均值为 {pct(lr['mean'])}（范围 {pct(lr['minimum'])}–{pct(lr['maximum'])}），OOD 为 {pct(lo['mean'])}。Shift 的 IID 均值为 {pct(sh['mean'])}，相同600组更新预算下主要受时间转换限制。这不是 Shift 的性能上限。
2. **损坏了哪些不变量？** 已解析输出中，Shift损坏了事件日期、主体、接收者、数量和取消状态；LowRank16的已解析不一致只涉及事件日期。但两者时间纯表示链的未决输出中均出现记录锚点、事件事实丢失及不可理解词串，不能据已解析子集声称内容始终保持。自动未检测到计划→完成；未决输出未被穷尽审核，这不是零风险证明。
3. **两步还能做到？** LowRank16 在 IID 的时间→人称纯表示链联合成功率均值为 {pct(lc['mean'])}，相应重编码链为 {pct(rc['mean'])}；连续两次时间+1纯表示链为 {pct(lc2['mean'])}。其他顺序、OOD和往返见完整表，单步成功不自动推出组合成功。
4. **是否泛化到未见模板？** OOD使用4个未进入训练的句法家族，词汇共享；单步与组合分别评价。结果只能支持这个受控结构迁移范围，不能支持自然长文或开放指令。
5. **下一步？** 先停止向自然文本/长文扩展，优先另立版本诊断时间算子在已编辑表示上的稳定性，以及中间相对日期表达的训练源覆盖。单步和时间×人称组合有信号，但时间连续及往返的纯表示链均未过工程线；本批已完成规定六组训练和全部核心测试，不自动新增训练或资源。未有人类审核，整体标为“结构化自动检查 + 模型复核”。

## 已执行范围与资源

- E0：420/420自由生成逐字重构成功，各状态140/140；直接generate与encoder_outputs路径一致，BART梯度为空，编辑梯度非零、padding有效。
- train/dev/test：480/80/160条独立记录；另有60 calibration；每记录6原子训练/评价路径。无组合训练、无编辑输出训练输入。
- Shift和LowRank16各seed42/43/44，共六组，每组四个独立算子，均600更新；best均由单步dev目标token NLL选择。E1 LowRank16达到100%通过门槛后才启动E2。
- 原始BART SHA256：`1bd3ac8e5b3ac71c77cf18fbcd8b113e0bfceced94c5cfbbb9a2b4bb4781190b`；float32、输入96、生成60、greedy。全部最长gold为52 tokens，未静默截断。
- 本轮单GPU累计 {budget.get('consumed_gpu_seconds',0)} 分配秒（{budget.get('consumed_gpu_seconds',0)/3600:.4f} GPU小时），上限7200秒；sacct父/step取最大不重复累加。详见budget.json与logs/slurm_accounting.tsv。
- 正式输出 {audit['total_rows']} 条：atomic {audit['atomic_rows']}、composition {audit['composition_rows']}、两次重建 {audit['reconstruction_rows']}；到达生成上限 {audit['truncated_rows']} 条。全固定分母保留。

## 三 seed 单步与组合

以下为joint_ok。范围是三个独立训练seed范围，不是置信区间。完整逐seed、逐状态、逐路径N及其他指标在evaluation/summary.csv、status_summary.csv。

|方法|测试层|路径|seed42|seed43|seed44|均值|范围|
|---|---|---|---:|---:|---:|---:|---|
'''
 paths=['atomic_all','atomic_time','atomic_perspective','time_then_person/latent_chain','person_then_time/latent_chain','time_twice/latent_chain','time_then_person/decode_reencode','person_then_time/decode_reencode','time_twice/decode_reencode']
 for m in ['Shift','LowRank16']:
  for st in ['test_iid','test_template_ood']:
   for p in paths:
    r=stat(m,st,p);text+=f"|{m}|{st}|{p}|{pct(r['seed42'])}|{pct(r['seed43'])}|{pct(r['seed44'])}|{pct(r['mean'])}|{pct(r['minimum'])}–{pct(r['maximum'])}|\n"
 text+='''
## 对照与不变量

Copy、Identity评价目标转换，因此即使复制保真也不能通过目标参考系。Target reconstruction仅为可重构性诊断，不是数学上界。Text-rule从源文本和框架解析字段，不读取W。Wrong-operation只对LowRank16使用固定每测试层前10个记录×6原子路径×3seed；不用于选模型。

|对照|测试层|N|joint_ok|content_ok|plan_to_completed|parse_unresolved|
|---|---|---:|---:|---:|---:|---:|
'''
 for r in summary:
  if r['method'] not in ['Shift','LowRank16'] and r['path'] in ['atomic_all','two_reconstructions']:
   text+=f"|{r['method']} s{r['seed']}|{r['test_stratum']}|{r['N']}|{pct(r['joint_ok'])}|{pct(r['content_ok'])}|{pct(r['plan_to_completed'])}|{pct(r['parse_unresolved'])}|\n"
 errors={}
 for r in slots:
  if r['method'] in ['Shift','LowRank16']:errors[(r['method'],r['field'])]=errors.get((r['method'],r['field']),0)+int(r['count'])
 text+='\n已成功解析输出中的槽位不一致次数（跨所有种子、路径；诊断计数，不视为独立样本）：\n\n|方法|槽位|次数|\n|---|---|---:|\n'
 for (m,f),n in sorted(errors.items()):text+=f'|{m}|{f}|{n}|\n'
 text+=f"\n神经方法解析未决共 {audit['unresolved_neural_rows']} 条；已解析的非日期不变量错误输出共 {audit['parsed_nondate_invariant_error_rows']} 条。原始分数保持冻结；模型复核见review/model_review.md，不能用便利抽查估计总体准确率。\n"
 text+='\n## 顺序一致和往返\n\nShift的加法天然交换，输出一致不证明语义独立。两条顺序都正确的比例与一致率分别报告。以下按三seed取均值；单seed见CSV。\n\n|方法|测试层|执行方式|语义一致|两条都正确|\n|---|---|---|---:|---:|\n'
 for m in ['Shift','LowRank16']:
  for st in ['test_iid','test_template_ood']:
   for mode in ['latent_chain','decode_reencode']:
    rs=[r for r in consistency if r['method']==m and r['stratum']==st and r['mode']==mode];text+=f"|{m}|{st}|{mode}|{pct(statistics.mean(float(r['semantic_consistency']) for r in rs))}|{pct(statistics.mean(float(r['both_correct']) for r in rs))}|\n"
 text+='\n|方法|测试层|往返路径|前向正确|回程正确|两者都正确|\n|---|---|---|---:|---:|---:|\n'
 for m in ['Shift','LowRank16']:
  for st in ['test_iid','test_template_ood']:
   for path in ['time_return/latent_chain','person_return/latent_chain','time_return/decode_reencode','person_return/decode_reencode']:
    rs=[r for r in inverse if r['method']==m and r['stratum']==st and r['path']==path];text+=f"|{m}|{st}|{path}|"+'|'.join(pct(statistics.mean(float(r[k]) for r in rs)) for k in ['forward_joint','return_joint','both_correct'])+'|\n'
 text+='''
计划跨事件日结果见evaluation/plan_crossing.csv，未把reported_completed/cancelled混入计划分母。逆向算子独立训练；回程单独成功不能排除Identity式无作用。

## 时间组合失败的附加诊断

LowRank16 IID的连续两次T_plus和T_minus∘T_plus纯表示链三seed均为0%；同样任务的重编码链三seed均为66.25%，而同次数无编辑重建对照为100%。这提示编辑后表示上的算子稳定性问题，但不足以给出唯一机制归因。

额外按中间目标相对日期分层（明确为事后诊断，不替换主分母）：每个IID seed的80记录中，27条中间应表达three days ago（offset=-3）；T_plus/T_minus训练源只覆盖offset=-2…+2。重编码链这27条均失败，其余53/53成功。纯表示链在这53条中仍为0/53。因此既有源表达支持范围外的问题，也有在该范围内的纯表示链失败，不能把所有失败归咎于未见日期词。完整分层见temporal_support_diagnostic.csv。

计划跨日小组不含所有相对日期条件，不能用它代替整体时间组合评价。建议后续独立版本先检验输入支持范围闭合及编辑后表示稳定性，保留本轮结果不改分母、不追加本轮训练。

## 统计、时延及限制

2000次配对bootstrap以record_id为单位，IID/OOD内分别重采样；同记录全部视图、路径和seed一起保留。对三seed平均记录分数的区间只覆盖记录抽样，不覆盖全部训练随机性。逐seed表、均值/范围和paired differences均保存，不把多个视图当独立样本。

计时包括实际encode/edit/decode、CPU规则和重复编解码；latent链的诊断中间解码单列，也计入total，core_without_diagnostic另存原始输出。数据准备、CPU评分不包含在模型推理计时，GPU分配总耗时则保守包含作业内全部操作。主生成批大小16，Wrong-operation末批4；禁止把它与批16直接比较。Copy为直接字符串引用，未进行可信微基准，时间0不能解读为零成本。这里只提供分阶段原始描述性计时，不宣称端到端加速。

评分器完整消费受控句子并接受部分非reference替代表达，但不覆盖任意自然改写。parse_unresolved不是已证实语义错误；保守通过率不计成功。recorded_plan/reported_cancelled阴性样例在本生成方案中与较早事件日有相关性，因而不能声称完整解耦泛化。negative reported_completed按已发生时间段的否定事件报告解释；取消“不做”的计划不推导“做了”。

数据协议预检前唯一修订是明确event date作用域，旧草稿留档；没有根据测试修改数据/评分/阈值。身份词汇共享，不能声称未见人物或词汇迁移。源标题与record_date均为输入的一部分，无目标前缀。所有框架条件由外部提供，不是学会日历计算或任意指令理解。

固定40个test record_id、按方法匿名的全部关键路径在review/blind_review.csv；private_method_map.json单独保存。尚无人类填写。该包既含IID也含OOD，不用便利审查估总体准确率。

## 固定20例

16个固定随机记录的原子路径（方法/路径在查结果前固定），加每层首记录两方法的时间→人称纯表示链4例。没有按成功筛选。全部为seed42；包括原句、外部框架、目标语义、输出及冻结判定。
'''
 for i,r in enumerate(map(json.loads,(ROOT/'review/report_cases.jsonl').read_text().splitlines()),1):
  text+=f"\n### {i}. {r['gold_record_id']} / {r['method']} / {r['path']}\n\n- 原句：{r['source_text']}\n- 框架：`{json.dumps(r['allowed_context'],ensure_ascii=False)}`\n- 目标语义：`{json.dumps({k:v for k,v in r['world'].items() if k not in ['split','template_family','c0']},ensure_ascii=False)}`\n- 输出：{r['output']}\n- 判定：joint={r['score']['joint_ok']}，frame={r['score']['frame_ok']}，content={r['score']['content_ok']}，unresolved={r['score']['parse_unresolved']}，原因={r['score']['uncertain_reason']}。\n"
 text+='''
## 文件与复现

准备脚本：prepare.py、configure.py（已有冻结文件时拒绝覆盖）。GPU入口：run_e0.slurm、run_train.slurm、run_eval.slurm（必须先核算剩余累计预算，再指定更短时限；不能重置预算）。train.py按相同seed/路径顺序恢复latest.pt的optimizer和RNG；evaluate_locked.py按uid续写缺失输出，锁定best哈希必须相同。CPU汇总：`.venv/bin/python experiments/reference_frame_pilot_v1/analyze.py`，报告：同路径report.py。

PROTOCOL.md、config.json、source_model_manifest.json、frozen_manifest.json、checkpoints/locked.json、commands.log、budget.json给出冻结与执行证据。未更改旧实验、未运行HE、未发布或推送。本报告不作新颖性承诺。
'''
 (ROOT/'REPORT.md').write_text(text)
if __name__=='__main__':main()
