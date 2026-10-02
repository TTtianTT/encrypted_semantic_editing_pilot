"""CPU Chinese findings presentation; no scores/cohorts/estimators/inference changed."""
from common_g17 import *
def main():
    p=ROOT/'REPORT.md';text=p.read_text();start=text.index('seed42: F=');text='# G17 跨语义状态 × 表示来源迁移边界\n\n'+text[start:]
    lead='''**主检验仅获seed42支持，没有达到跨三个seed稳定正向迁移的预设条件。** 零新增训练，固定G16 F/N-final200及P，四锚点、三个冻结生产者均按原计划评估。

IID +2/U：F为106/160、0/160、0/157，N及P分别为0/160、0/160、0/157。三seed均值差+22.08pp，sample SD38.25pp，paired-world95%CI[+19.58,+24.38]；均值CI支持这些固定模型的平均增量，但两个seed无增量，不能用平均盖住方向差异。F/N的该锚点自然续步在各seed均160/160，所以IID新状态接收失败不能归为基本自然规则不会做。全零bootstrap[0,0]只描述已观测固定模型世界差，Wilson比例区间仍保留。

**四状态边界：** today/P和today/U正对照的F三个seed均160/160、N均0/160；+2/P仅seed42 F30/160对N0、+2/U仅seed42 F106/160对N0；−2/U仅seed42 F18/160对N0，其余该锚点P/U/G的F/N均0，且−2有祖先两步监督，不能冒充新路径泛化。yesterday/G的F/N均160/160，维护成立；这不等于保持所有yesterday来源，例如seed44 yesterday/U为F20/160、N160/160。+2/G在seed42上F27/158比N2/158改善，却低于补训前P87/158，不能只用F−N讲成总体来源修复。

**固定输入增量与自身运行只有限对应。** IID +2 的F自身第一步均160/160、full2为20/160、0/160、0/160；N/P均full2为0。seed42有小幅自身路径改善，但远低于90%展示线，固定U的106/160不能冒充自身完整路径。today的F自身full2为159/160、160/160、160/160，已修复锚点恢复；yesterday自身F为145/160、140/160、40/160，−2自身F/N/P各seed均0，旧G −2自身仍各160/160。这些是两次调用的状态边界，不推出无限重复使用或纯latent编辑不可能。

**模板与接口限制：** OOD +2/U仅seed42 F110/160对N0；seed43为0/160，seed44为0/131。OOD seed44的+2自然F155/160、N142/160；today自然F为127/160、122/160、160/160，不能将OOD所有失败说成仅编辑来源问题。+2/0/−1自然和编辑mask在原始160世界逐例相同；−2自然/编辑mask全部不同，严格相等mask子集为空。固定F−N仍使用同一完整编辑态而有效；−2的重编码改善属于完整接口控制，不能单独归因memory。

真实历史标签：+2=已审计参数谱系未直接监督edited续步（自然规则已见）；today/P是F直接修复，today/U/G有相关祖先暴露；yesterday/G是维护条件，P/U并非精确修复来源；−2=repair未见但祖先G10两步暴露。没有将Git祖先当作权重祖先，也没有声称全部不可访问历史无监督。

'''
    text=text.replace('# G17 跨语义状态 × 表示来源迁移边界\n\n','# G17 跨语义状态 × 表示来源迁移边界\n\n'+lead,1)
    text+='''
工程与完成范围：全部320新世界×4相关锚点×3seed完成；完整130,560逐例输出经CPU独立重评分，12项CPU检查、历史576条复现、cache重放/冻结与真实reset一致性通过。无未完成科学条件，无追加训练、生产者、锚点、候选或三步以上路径。

保留两项GPU工程故障：2533历史metadata索引失败，2534修正后通过；2535_1安全时间检查中断最后OOD−2分片，2538_1在整个主数组结束后只补缺失分片，七个已有输出和八个缓存SHA不变。没有因分数差重试。申请用量包括失败和恢复：0.950000GPU小时；实际0.366667；峰值2。NVIDIA B300 SXM6 AC，PyTorch最大allocated717,850,624bytes，Slurm采样GPUmem峰值1554M（两种度量不同；短smoke零采样不是零GPU使用）。allocation起止/退出码/rawID与step内存记录均保留。

确认期间科学锁及旧依赖SHA保持不变。CPU测试入口、旧source=Q索引和JSON标量修复均记录于engineering_events；所有修订发生在新确认输出之前。后处理helper只改展示与验收，不改评分、cohort、draw或假设。下一次干预不自动执行。
'''
    p.write_text(text.rstrip()+'\n')
    readme=ROOT/'README.md';t=readme.read_text();t+='''
CPU交付验收（collect后，不重新推断）：

```bash
.venv/bin/python experiments/g17_state_source_transfer_v1/finalize.py
.venv/bin/python experiments/g17_state_source_transfer_v1/publish_report.py
.venv/bin/python experiments/g17_state_source_transfer_v1/check_delivery.py
```

若唯一缺失评估分片因已诊断的安全时间故障中断，本次实际使用resume_missing.py依赖主数组afterany，仅补seed43的最后OOD−2分片；恢复锁核验原7输出/8缓存SHA。它不是分数差重试。工程修改/历史锁版本保留，确认阶段科学锁不变。输出shards本地路径/hash与完整公开聚合archive一一对应。Slurm步骤显存原记录在slurm_step_usage.psv，只allocation计GPU小时。
''';readme.write_text(t.rstrip()+'\n')
    dump(ROOT/'protocol_deviations.json',dict(scientific_scope_configuration_unchanged=True,engineering_events=json.loads((ROOT/'engineering_events.json').read_text()),GPU_jobs=[r['job_id'] for r in json.loads((ROOT/'submissions.json').read_text())],budget=json.loads((ROOT/'budget.json').read_text()),all_scientific_conditions_completed=True,uncompleted=[]))
    # Public output and presentation helpers are explicit post-lock assets; science untouched.
    dump(ROOT/'gpu_resources.json',dict(gpu='NVIDIA B300 SXM6 AC',peak_torch_allocated_bytes=max(json.loads((ROOT/f'seed_s{s}_complete.json').read_text())['peak_cuda_bytes'] for s in CFG['seeds']),Slurm_peak_sampled_GPUmem='1554M',short_smoke_zero_sampling_is_not_zero_GPU_use=True,step_memory_not_added_to_allocation_hours=True))
    print('Chinese primary/negative boundaries and resource deviations published')
if __name__=='__main__':main()
