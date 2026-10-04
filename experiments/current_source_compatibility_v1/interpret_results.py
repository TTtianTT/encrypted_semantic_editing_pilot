"""Seven quantitative answers from complete, fixed-checkpoint tables (CPU only)."""
import csv, statistics
from study import ROOT, read

SEEDS = (42, 43, 44)

def csvrows(name):
    return list(csv.DictReader((ROOT/name).open()))

def main():
    assert read(ROOT/'ANALYSIS_AUDIT.json')['all_seeds_complete']
    summary = csvrows('summary_by_seed.csv')
    paired = csvrows('paired_contrasts.csv')
    attribution = csvrows('repair_attribution.csv')
    changes = csvrows('old_capability_changes.csv')
    costs = csvrows('condition_compute.csv')

    def pick(seed, method, test, source, metric, cohort='all'):
        rs = [r for r in summary if r['seed']==str(seed) and r['condition']==method
              and r['update']==('0' if method=='T0' else '200')
              and r['test']==test and r['source']==source
              and r['metric']==metric and r['cohort']==cohort]
        assert len(rs)==1, (seed,method,test,source,metric,cohort,len(rs))
        return rs[0]

    def rates(method, test, source, metric, cohort='all'):
        rs = [pick(s,method,test,source,metric,cohort) for s in SEEDS]
        return '/'.join(f"{100*float(r['rate']):.2f}% ({r['k']}/{r['denominator']})"
                        if r['rate'] else 'NA (0/0)' for r in rs)

    def delta(test, source, metric, contrast='R-F', cohort='all'):
        rs = [next(r for r in paired if r['seed']==str(s) and r['update']=='200'
                   and r['test']==test and r['source']==source and r['metric']==metric
                   and r['contrast']==contrast and r['cohort']==cohort) for s in SEEDS]
        vs = [float(r['delta_pp']) for r in rs]
        return ('/'.join(f'{v:+.2f}' for v in vs)+f' pp；均值 {statistics.mean(vs):+.2f} pp；'
                +('三个 seed 均严格正向' if all(v>0 for v in vs) else '未满足三个 seed 均严格正向的预设稳定优势判据'))

    lines = ['# 七个研究问题的定量回答', '',
             '以下按 seed 42/43/44 排列，主结果固定 update 200；百分点差值使用相同世界配对。'
             '具体区间见 paired_contrasts.csv，按 32 个内容世界聚类，不含完整训练随机性。', '',
             '## 1. R 是否优于 F？', '',
             'IID 自身两步完整率 R−F：'+delta('iid','self','full2')+'。',
             'IID 固定 T0 来源：'+delta('iid','fixed_T0','full2')+'；IID U 来源：'
             +delta('iid','U','full2')+'。',
             '普通自然补训对照 F−N 的 IID 自身两步差值：'
             +delta('iid','self','full2','F-N')+'。', '',
             '## 2. 改善是否仅限于训练的第二步？', '']
    for test in ('iid','ood'):
        for step in (3,4,5):
            metric=f'full{step}_all'
            lines.append(f'{test.upper()} 纯 latent 完整 {step} 步：R '+rates('R',test,'latent',metric,'long_paths')
                         +'；F '+rates('F',test,'latent',metric,'long_paths')+'；R−F '
                         +delta(test,'latent',metric,cohort='long_paths')+'。')
    lines += ['这些是所有前步均正确的完整率，不能由最终 endpoint 替代。'
              '长度结果来自预先固定的合法混合方向与单向路径，不含非法边界标签。', '',
              '## 3. 更新后的编辑器能否处理自己的输出？', '']
    for method in ('N','F','R'):
        lines.append(method+' 的 IID 自身第一步：'+rates(method,'iid','self','first')
                     +'；两步完整：'+rates(method,'iid','self','full2')
                     +'；训练前固定诊断集两步完整：'
                     +rates(method,'iid','self','full2','fixed_diagnostic')+'。')
    lines += ['固定诊断集不会随方法重新筛选，补训后第一步错误仍保留为失败；'
              '当前方法的条件成功分母另列在 RESULTS.md，不能独立用于排名。', '',
              '## 4. 是否迁移到独立来源 U 和模板 OOD？', '']
    for method in ('N','F','R'):
        lines.append(method+' 的 U 两步完整 IID：'+rates(method,'iid','U','full2')
                     +'；U OOD：'+rates(method,'ood','U','full2')
                     +'；自身 OOD：'+rates(method,'ood','self','full2')+'。')
    lines += ['OOD 自身 R−F：'+delta('ood','self','full2')+'；OOD U R−F：'
              +delta('ood','U','full2')+'。',
              'T0 的模板 OOD 自然单步：'+rates('T0','ood','natural','atomic_macro')
              +'；T0 OOD gold-current-reencode 第二步 endpoint：'
              +rates('T0','ood','gold_reencode','endpoint2')+'。',
              '因此 OOD 结果还包含基础表达识别能力的限制；U 是冻结的其他 seed 原子编辑器，'
              '不是第四个独立训练重复。', '', '## 5. 旧自然单步能力是否退化？', '']
    for seed in SEEDS:
        for method in ('N','F','R'):
            r=pick(seed,method,'iid','natural','atomic_macro')
            b=pick(seed,'T0','iid','natural','atomic_macro')
            diff=100*(float(r['rate'])-float(b['rate']))
            ss=[x for x in changes if x['seed']==str(seed) and x['condition']==method and x['update']=='200']
            lost=sum(int(x['old_success_lost']) for x in ss)
            gained=sum(int(x['old_failure_repaired']) for x in ss)
            lines.append(f"seed {seed} {method}：macro {100*float(r['rate']):.2f}%，"
                         +f'相对 T0 {diff:+.2f} pp；旧成功损失 {lost}，旧失败修复 {gained}，'
                         +f'净变化 {gained-lost:+d}；'+('通过' if diff>=-2 else '未通过')+'下降≤2 pp 判据。')
    lines += ['逐例 ID 与合法状态/操作变化保留在 old_capability_changes.csv。', '',
              '## 6. 收益来自正确前缀续步，还是失败前缀恢复？', '']
    for seed in SEEDS:
        for test in ('iid','ood'):
            ss=[r for r in attribution if r['seed']==str(seed) and r['contrast']=='R-F'
                and r['source']=='self' and r['test']==test]
            assert len(ss)==4
            both=next(r for r in ss if r['stratum']=='both_correct')
            fd=sum(int(r['full2_count_delta']) for r in ss)
            ed=sum(int(r['endpoint2_count_delta']) for r in ss)
            rd=sum(int(r['failed_prefix_endpoint_recovery_count_delta']) for r in ss)
            assert ed==fd+rd
            changed=fd-int(both['full2_count_delta'])
            lines.append(f'seed {seed} {test.upper()} R−F：两步完整成功数差 {fd:+d}/704；'
                         +f"双方第一步均正确的 {both['n']} 条中差 {int(both['full2_count_delta']):+d}；"
                         +f'第一步正确性不一致分层贡献 {changed:+d}；'
                         +f'失败前缀端点恢复数差 {rd:+d}；总 endpoint 差 {ed:+d}。')
    lines += ['上述更新后分层用于描述收益归属，不能代替总体指标或训练前固定诊断集。'
              '错误前缀的 endpoint 恢复不计入完整轨迹；训练刷新质量另列 prefix_quality.csv，'
              '未解析前缀与已知相对状态错误分开统计。', '', '## 7. 相比 F，R 增加多少 GPU 时间？', '']
    extra=[]
    for seed in SEEDS:
        rr={r['condition']:r for r in costs if r['seed']==str(seed)}
        inc=float(rr['R']['source_pipeline_seconds'])-float(rr['F']['source_pipeline_seconds'])
        train=float(rr['R']['training_wall_seconds'])-float(rr['F']['training_wall_seconds'])
        total=float(rr['R']['completed_stage_seconds'])-float(rr['F']['completed_stage_seconds'])
        extra.append(inc/3600)
        lines.append(f'seed {seed}：来源 pipeline 额外 {inc:.1f} 秒（{inc/3600:.4f} GPUh）；'
                     +f'训练阶段净差 {train/3600:+.4f} GPUh；含两次评估阶段净差 {total/3600:+.4f} GPUh。')
    lines += [f'三个 seed 额外来源 pipeline 合计 {sum(extra):.4f} GPUh。'
              '这是单卡 allocation 内壁钟时间，包含新编码、前缀、质量解码与缓存 I/O，'
              '不是 GPU 内核利用率；总分配成本还含模型加载、技术失败和恢复，见 RESOURCE_USAGE.md。', '',
              '## 观察与解释的边界', '',
              '以上只判断本模型、时间核心任务、原有 rank16 双头及固定 200 更新设置。'
              '当前来源补训即便改善某些指标，也不能确定来源滞后是唯一失败机制。'
              '本轮未执行新领域、复杂引语、范围挑战、新 probe、因果干预或超参数搜索。']
    (ROOT/'RESEARCH_ANSWERS.md').write_text('\n\n'.join(lines)+'\n')
    print('Seven quantitative answers written from all seeds at fixed update200')

if __name__=='__main__':
    main()
