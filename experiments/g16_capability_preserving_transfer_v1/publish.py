"""CPU report presentation and explicitly post-result boundary cases only.

Added after the scientific lock; no inference, selection or estimators change.
Run after analyze.py and finalize.py. All numerical tables come from their CSVs.
"""
from common_g16 import *
stats=load_module('g16_readonly_report_format',G15/'analyze.py')

def csvrows(name):return list(csv.DictReader((ROOT/name).open()))
def pct(value):return f'{float(value)*100:.2f}%'
def boundary_cases():
    selected=[];categories=[]
    for seed in CFG['seeds']:
        rows=read(ROOT/f'per_example_s{seed}.jsonl.gz')
        for split in ['iid','template_ood']:
            candidates=[r for r in rows if r['method']=='F-guard' and r['split']==split and r['kind']=='fixed' and r['source']=='G' and r['matched'] and not r['joint']]
            candidates.sort(key=lambda r:hashlib.sha256(f'g16/post-result/G-boundary/{seed}/{split}/{r["world_id"]}'.encode()).hexdigest())
            categories.append(dict(seed=seed,split=split,count=len(candidates),absent=not candidates,post_result_descriptive=True,rule='first SHA256(g16/post-result/G-boundary/seed/split/world_id)'))
            if candidates:
                rid=candidates[0]['world_id'];sample=[r for r in rows if r['method']=='F-guard' and r['split']==split and r['world_id']==rid and r['kind']!='atomic']
                fixed={r['source']:r for r in sample if r['kind']=='fixed'}
                assert all(r['matched'] and r['current_exact'] and r['current_joint'] for r in fixed.values())
                assert len({fixed[s]['mask_sha256'] for s in ['P','G','U']})==1
                selected.append(dict(seed=seed,split=split,world_id=rid,selection='post-result G-boundary first hash, never used for selection',rows=sample))
    write(ROOT/'boundary_cases.jsonl.gz',selected);csvwrite(ROOT/'boundary_case_categories.csv',categories)
    out=['# G-today 边界的事后描述案例','', '每seed/split在F-guard的G-source失败中按上面公开hash取首例；不存在则absent。不改变12个事前固定案例、模型选择、分母或指标。每例保留同世界E/P/G/U与自身/真实输出重编码控制。','']
    for c in selected:
        out += [f'## seed{c["seed"]} / {c["split"]} / {c["world_id"]}','']
        for r in c['rows']:
            out += [f'{r["kind"]}/{r["source"]}, actual_updates={r["actual_updates"]}, joint={r["joint"]}, exact={r["exact"]}, full={r.get("full","NA")}, error={r["error_type"]}, first_failure={r.get("first_failure","NA")}, date_delta={r["relative_date_delta_days"]}',f'Current: {r.get("current",{}).get("output","natural tomorrow")}',f'Output: {r["output"]}',f'Gold: {r["gold"]}',f'Mask SHA: {r["mask_sha256"]}; length={r["input_length"]}; memory SHA: {r["memory_sha256"]}',f'Parsed: {json.dumps(r["parsed_facts"],ensure_ascii=False)}','']
    (ROOT/'BOUNDARY_CASES.md').write_text('\n'.join(out).rstrip()+'\n')

def main():
    core=csvrows('core_results.csv');cells=csvrows('atomic_by_cell.csv');ds=csvrows('paired_differences.csv');means=csvrows('seed_mean_SD.csv')
    selected={str(s):json.loads((ROOT/f'selection_s{s}.json').read_text())['selected_step'] for s in CFG['seeds']}
    def values(method,split,field):return [r[field] for r in sorted(core,key=lambda r:int(r['seed'])) if r['method']==method and r['split']==split]
    def counts(method,split,field):return ', '.join(f'{v}/160' for v in values(method,split,field))
    def gain(contrast,metric,split='iid'):
        r=next(r for r in ds if (r['seed'],r['split'],r['contrast'],r['metric'])==('mean',split,contrast,metric))
        return f'{float(r["delta_pp"]):+.3f} pp [95% world CI {float(r["ci_lo_pp"]):+.3f}, {float(r["ci_hi_pp"]):+.3f}]; seed SD {float(r["seed_SD_pp"]):.3f} pp'
    direct=[
        '1. **选择结果：seed42→step50，seed43→step25，seed44→step25；没有选择失败。** 原始计数核验最早合格，step0不选，全部F仍训练到200。',
        '2. **所选模型在IID逐seed保住40-cell自然能力和旧yesterday all3，并达到自身两步修复工作标准。** guard原子macro为'+', '.join(pct(x) for x in values('F-guard','iid','atomic_macro'))+'；最低cell为'+', '.join(pct(x) for x in values('F-guard','iid','atomic_min_cell'))+'；旧all3均160/160，自身full2为'+counts('F-guard','iid','full2_k')+'。这是已监督任务的新世界运行检查，不是新长度泛化。',
        '3. **未读取U的规则选择后，IID留出U仍得到正向迁移。** guard为'+counts('F-guard','iid','U_k')+'，P/N各seed均0/160；三个seed均达到U≥90%的工作目标，逐seed配对world CI支持改善。相对P和N的均值改变量均为'+gain('F-guard minus N-final','U')+'。这仅是G15已考察过的精确F2 final200生产者在新世界上的复验。',
        '4. **没有guard相对final200的能力保持优势；G15的seed44 IID末段退化没有在本轮重现。** F-final的全部IID自然cell均160/160，旧all3均160/160，U与自身full2均为'+counts('F-final','iid','U_k')+'。guard−final的原子macro为'+gain('F-guard minus F-final','atomic_macro')+'，U为'+gain('F-guard minus F-final','U')+'，full2为'+gain('F-guard minus F-final','self_full')+'。两个版本均通过三seed IID工作目标，不能据此宣称guard更优或必要。'
    ]
    boundary='**边界：三个guard的OOD自然macro为94.50%、91.00%、91.95%，最低cell为73.13%、75.00%、53.13%，均未通过能力标准。** OOD U为115/160、160/160、160/160，self full2为159/160、160/160、160/160；seed42迁移有改善但未达U≥90%。final的OOD只有seed44通过完整工作目标。IID guard对G-today仅81/160、124/160、30/160，虽P均160/160且U很高，也不能称普遍来源互换。三个IID guard的全部固定来源同时成功仅81/160、124/160、30/160。'
    intro='\n\n'.join(direct)+'\n\n'+boundary+'\n\n'
    current=(ROOT/'REPORT.md').read_text();idx=current.index('|seed|split|版本|')
    (ROOT/'REPORT.md').write_text('# G16 能力约束下的固定来源修复与留出迁移复验\n\n'+intro+current[idx:])
    out=['# G16 结果解释','',intro,
        '主要正结果是固定来源F补训在三个既有初始化上、新的IID世界中，同时保持自然/旧yesterday能力并迁移到U。等200步F-final−N-final的IID U与self full2均为'+gain('F-final minus N-final','U')+'；原子macro和旧all3差均0。N不处理这些编辑态today，不能用自然单步成功替代两步修复。',
        '',
        'guard−final在OOD的U与self改善主要来自seed42，但三个guard的OOD自然能力更差：原子macro差'+gain('F-guard minus F-final','atomic_macro','template_ood')+'；U差'+gain('F-guard minus F-final','U','template_ood')+'；self差'+gain('F-guard minus F-final','self_full','template_ood')+'。这不能被写成整体能力保持成功。guard−N/P含来源训练与更新步两个因素；训练仍完整200步，实际算力没有节省。',
        '',
        '今天主C在每seed/split均160/160，E/P/G/U当前全文与事实正确、正常结束；全部producer mask逐元素相同，自然mask也在本数据160/160相同。G-source与U-source的IID差异因而不能由本数据的mask差异解释；内部原因没有测量。旧yesterday C独立：IID均160，OOD依seed为108、120、119，all3条件均满分，但gate-and-next仅108/160、120/160、119/160。未匹配输出完整保留，不把这些分母强行合并或跨seed逐行等同。',
        '',
        'IID各版本自然today→yesterday及真实当前输出重编码均160/160，reset与自然E的token/mask/memory逐元素一致，重复不是独立证据。OOD有自然技能边界：guard自然today续步155/160、120/160、143/160；不能描述为“只不认识编辑态”。重编码仅用真实自由输出，first错时full不会被gold修正。',
        '',
        'CPU G15审计未发现确定标签/配额/状态错配，梯度冲突未测量。G15小step150诊断没有被当作完整确认，未重新推断step150 U。本轮F-final新IID成功表明固定补训可在本设置达成目标；不能证明G15退化的唯一机制、普通过拟合、必然任务冲突或不可能性。',
        '',
        '完整工作目标通过是经验阈值，不是总体保证。U的配对world区间只包括固定模型的世界抽样，选择/完整训练随机性不在其中；三个seed共有世界不是480个独立训练。Wilson逐比例保留，160/160的95% Wilson下界约97.66%，0/160上界约2.34%；退化bootstrap[0,0]不表示总体零不确定性。',
        '',
        '完成全部6条200步训练、3条不可变selection和3seed确认；没有未完成实验、工程重试或科学配置偏离。实际2.073611 GPU小时、申请3.40、峰值2；7 allocations均COMPLETED/0:0。旧工件SHA不变，科学锁不变。finalize/publish仅为锁后CPU交付格式和报告助手，不改变推断/选择/统计；导出step使用已有actual_updates并保留legacy_final_interface_step。',
        '',
        '最小剩余问题是OOD自然技能与G-today来源的有限兼容性，当前数据没有提供唯一内部解释。本轮不自动追加训练或扩展实验。','']
    (ROOT/'INTERPRETATION.md').write_text('\n'.join(out))
    # Complete per-seed SD presentation for every core rate, not pooled worlds.
    summary=stats.table(['版本','split','metric','mean%','sample SD pp','seed values'],[[r['method'],r['split'],r['metric'],f'{100*float(r["mean"]):.3f}',f'{100*float(r["sample_SD"]):.3f}' if r['sample_SD'] else 'NA',r['per_seed']] for r in means])
    critical=[]
    for r in cells:
        if (r['status'],r['offset'],r['perspective']) in [('recorded_plan','0','first'),('recorded_plan','1','first'),('reported_cancelled','2','third')]:critical.append(r)
    csvwrite(ROOT/'critical_transitions.csv',critical)
    failed=[r for r in cells if float(r['rate'])<.90];csvwrite(ROOT/'failed_cells.csv',failed)
    failures=stats.table(['seed','split','版本','status','offset→next','perspective','joint n/N'],[[r['seed'],r['split'],r['method'],r['status'],f'{r["offset"]}→{int(r["offset"])-1}',r['perspective'],f'{r["k"]}/{r["N"]}'] for r in failed])
    critical_table=stats.table(['seed','split','版本','status','offset→next','perspective','joint n/N'],[[r['seed'],r['split'],r['method'],r['status'],f'{r["offset"]}→{int(r["offset"])-1}',r['perspective'],f'{r["k"]}/{r["N"]}'] for r in critical])
    budget=json.loads((ROOT/'budget.json').read_text());jobs=csvrows('slurm_jobs.csv')
    resources=stats.table(['display ID','raw allocation','state','exit','start','end','GPU h'],[[r['job_id'],r['raw_job_id'],r['state'],r['exit_code'],r['start'],r['end'],r['gpu_hours']] for r in jobs])
    appended='\n## 逐seed失败cell与重点转换\n\n低于90%的全部cell如下，完整40cell与Wilson另见atomic_by_cell.csv。IID各guard无不合格cell，OOD不得以macro覆盖局部失败。\n\n'+failures+'\n\n重点转换保留原权重：\n\n'+critical_table+'\n\n## 三seed均值与sample SD\n\n'+summary+'\n\n## 控制、分母与运行账\n\n'+boundary+'\n\n'+resources+'\n\n实际/申请/峰值GPU：'+json.dumps(budget)+'。型号NVIDIA B300 SXM6 AC；Slurm step显存峰值3396M，PyTorch allocator峰值1574852096 bytes，两者口径单列。step仅用于显存核验，不重复计费。没有GPU重试或科学配置偏离。\n\nCPU单测11项通过，smoke64条历史输出/评分对齐；冻结/缓存/保存恢复/RNG插入检查通过。原始训练入口P/旧昨日各512/512，dev各128/128；选择最早合格的全40cell计数见selection_table.csv。科学锁、旧工件与所有大cache哈希核验通过。\n\n12个事前hash世界见CASES.md；补充G-source边界是公开规则的事后描述见BOUNDARY_CASES.md，不影响估计或选择。完整自由文本/事实/解析/错误与首次失败在逐seed gzip；没有把解析未决称为确认事实错误。\n\n交付仅本轮路径；大cache/候选/optimizer与基础BART留本地，路径/SHA见artifact_manifest.json。导出step标签按已有actual_updates规范化，保留legacy_final_interface_step；这些锁后CPU格式调整不改文本/计分/分母/模型或科学锁。完整复现顺序与本次命令见REPRODUCTION_RESULTS.md。\n'
    with (ROOT/'REPORT.md').open('a') as f:f.write(appended)
    boundary_cases()
    (ROOT/'REPRODUCTION_RESULTS.md').write_text('''# G16 本次执行与CPU结果复现

科学训练/推断入口、配置、数据及依赖在data/lock.json中，未修改。旧G15/G13/G14工件只读。README为事前流程，本文件补充交付顺序：

```bash
.venv/bin/python experiments/g16_capability_preserving_transfer_v1/account.py
.venv/bin/python experiments/g16_capability_preserving_transfer_v1/analyze.py
.venv/bin/python experiments/g16_capability_preserving_transfer_v1/finalize.py
.venv/bin/python experiments/g16_capability_preserving_transfer_v1/publish.py
```

analyze可使用已上传per_example_sSEED.jsonl.gz/learning_per_example_sSEED.jsonl.gz而不加载GPU。重新做完整GPU实验需要精确基础BART与本地模型路径，不能在现有锁/结果上覆盖；使用新的独立实验路径并保留原工件。finalize的执行本地cache证明依赖实际本地大cache/候选/optimizer，Git不包含它们，路径/hash在artifact_manifest.json；execution_timeline使用保存的一次性本地mtime证据，不把clone时间冒充执行时间。

finalize/publish是锁后CPU交付助手。旧final接口原step字段恒200；G16已在原推断中记录actual_updates和精确SHA，导出将step规范化为actual_updates并保留legacy_final_interface_step。文本、gold、解析、联合/exact、gate与模型SHA未改变。没有科学配置修改或GPU工程重试。publish仅展示CSV统计、列失败cell和事后描述G边界案例；不重选模型或增科学比较。

本次smoke2520；训练array2521（raw2522/2523/2521对应seed42/43/44）；确认array2524（raw2525/2526/2524）。全部7allocation成功；实际2.073611GPUh，申请3.40GPUh，峰值2。提交命令在commands.log，资源查询在allocation_details.psv/slurm_step_usage.psv。未上传基础模型、环境、凭据、大型latent或无关历史。
''')
    print('G16 direct-answer report and boundary cases published',flush=True)

if __name__=='__main__':main()
