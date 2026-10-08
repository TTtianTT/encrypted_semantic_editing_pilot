"""CPU preparation of a reviewable test amendment; never authorizes it."""
from .common import *


def prepare_proposal():
    final=read(ROOT/'configs/FINAL_METHOD_CHECKPOINT_LOCK.json')
    assert final['methods_ready'] and len(final['checkpoints'])==12
    worlds=rows(ROOT/'configs/worlds.jsonl');test=[w for w in worlds if w['split']=='test_iid']
    exposure=read(ROOT/'results/COUNTERFACTUAL_EXPOSURE_AUDIT.json')
    excluded=sorted({r['donor_world_id'] for r in exposure['collisions'] if r['donor_split']=='test_iid'})
    assert len(test)==128 and len(excluded)==5
    eligible=[w['world_id'] for w in test if w['world_id'] not in excluded]
    assert len(eligible)==123 and not (set(excluded)&set(eligible))
    checkpoints=final['checkpoints']
    for r in checkpoints:assert sha(r['path'])==r['sha256']
    proposal=dict(version='S4-amended-unexposed123-v1',status='PROPOSED_NOT_AUTHORIZED',
        original_registered_test_status='BLOCKED_TEST_INTEGRITY',original_scan_worlds=128,
        original_split_hash=sha(ROOT/'configs/SPLIT_LOCK.json'),worlds_hash=sha(ROOT/'configs/worlds.jsonl'),
        excluded_worlds=excluded,excluded_reason='Prior counterfactual encoder exposure before S4; not outcome-based exclusion',
        eligible_worlds=eligible,eligible_denominator=123,replacement_search=False,new_worlds=0,
        original_endpoint_restored=False,primary='explicit amended independent123-world joint source-balanced success',
        source_weights={'natural':.5,'history':.5},operation_records_per_seed=123*24,
        trajectory_lengths=[1,2,3,5],bootstrap_draws=20000,cluster='core world',
        primary_Holm_family=['Mechanism-guided vs Output-only','Mechanism-guided vs Random-site'],
        methods=['Original','Plain','Output-only','Mechanism-guided','Random-site'],training_seeds=[42,43,44],
        final_checkpoint_lock_sha256=sha(ROOT/'configs/FINAL_METHOD_CHECKPOINT_LOCK.json'),
        mechanism_lock_sha256=sha(ROOT/'configs/MECHANISM_LOCK.json'),
        random_preservation_lock_sha256=sha(ROOT/'configs/RANDOM_PRESERVATION_LOCK.json'),
        hyperparameter_lock_sha256=sha(ROOT/'configs/TRAINING_HYPERPARAMETER_LOCK.json'),
        selection_lock_sha256=sha(ROOT/'configs/TRAINING_SELECTION_LOCK.json'),
        no_test_based_training_or_selection=True,all_parameters_selected_before_test=True,
        mechanism_confirmation=dict(seed=42,scan_worlds=128,eligible_worlds=123,
            qualification_min_independent_worlds=40,source_pairs='unchanged A priority; all exclusions retained',
            conditions=['AA','BA','AB','BB','same normal-color value resampling'],
            sites=read(ROOT/'configs/MECHANISM_LOCK.json')['selected']+read(ROOT/'configs/MECHANISM_LOCK.json')['random_sites'],
            head=0,curve_worlds='first eight eligible IDs in original locked order; exploratory small subset',
            curve_alphas=[-.5,0,.25,.5,.75,1,1.25,1.5],random_seeds=list(range(61001,61009)),
            matched_retention_amplitude='unchanged validation-only RANDOM_PRESERVATION_LOCK',
            donor_control='same predetermined color change; reject reserved/test cores; accept only previously exposed training/validation/historical cores; no replacement search'),
        original128_reporting='128 scanned metadata; five prior-exposed excluded with NA; 123 amended estimate separately labelled',
        template_OOD='UNAVAILABLE',T5Gemma_new_methods='NOT_RUN',test_unseal_authorized=False)
    dump(ROOT/'configs/S4_PROTOCOL_AMENDMENT_PROPOSAL.json',proposal)
    dump(ROOT/'configs/FINAL_TEST_LOCK.json',dict(all_seeds_locked=True,
        independent_test_unseal_stage='S4',checkpoints=checkpoints,
        checkpoint_lock_sha256=sha(ROOT/'configs/FINAL_METHOD_CHECKPOINT_LOCK.json'),
        amendment_proposal_sha256=sha(ROOT/'configs/S4_PROTOCOL_AMENDMENT_PROPOSAL.json'),
        test_unseal_authorized=False,endpoint='proposed amended123; original128 remains blocked'))
    text(ROOT/'reports/S4_AMENDMENT_PROPOSAL.md',f'''# S4测试终点修订提案（尚未批准）

原定128个IID core world中，5个已在S1/S2派生颜色donor对照被encoder处理。原128全部独立的终点不能恢复。本提案只允许一个显式的新终点：保留原128扫描索引，5个预暴露world以NA和原因列出，对其余固定123个此前未暴露world进行评测。不补样本，不改变split/world SHA，不按输出或成功率排除。

所有四方法三个seed的12个checkpoint、超参、L5/L0组件、keep位置、随机匹配幅度已经锁定；checkpoint锁SHA：{proposal['final_checkpoint_lock_sha256']}。123-world单操作分母每seed2952（自然/history各1476），仍按50/50汇总；主指标目标、保护内容、可解析、grammar、正常EOS的交集。原128主终点仍标BLOCKED，不将123称原协议完整确认。

同一解封批次测一般SAME_TEXT资格/概率，以及预选L5/L0双向K/V和正常颜色resampling；不足40独立world则只探索，零pair则NOT_ESTIMABLE。有限alpha/随机曲线仅固定前8个eligible world，是小子集，不强行称全池确认。纯latent1/2/3/5步使用各方法自己的状态，全部三seed完整记录。20,000次paired world bootstrap及两项主对比Holm保持原规则；0/100%另给world比例Wilson区间。

预暴露ID：{', '.join(excluded)}。精确123个ID、所有锁文件SHA和运行规则在configs/S4_PROTOCOL_AMENDMENT_PROPOSAL.json。没有新的训练或test选型，也没有donor用于主编辑器推理。只允许已有train/validation/historical core充当诊断颜色donor；任何test/reserved core拒绝，不能补搜到可用donor。

只有用户显式同意此修订，才生成S4_AMENDMENT_AUTHORIZATION.json并启动Slurm作业；当前test_unseal_authorized=False，正式test评测仍为0。预计额外约3小时墙钟（两GPU上限），具体以队列和首批实际耗时修正；包括正式编辑、轨迹和锁定机制诊断，40 GPU-hours总预算和失败计费继续生效。若不同意，保留原阻塞报告，交付已完成的validation结果。
''')
    print(dict(proposal=str(ROOT/'reports/S4_AMENDMENT_PROPOSAL.md'),eligible_worlds=123,authorized=False))


if __name__=='__main__':prepare_proposal()
