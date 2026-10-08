"""CPU numerical collection of all trained candidates; test never opened."""
import shutil
from .common import *


def audit_run(source,dest,summary):
    candidates=[]
    plain=rows(source/'Plain/Plain_validation.jsonl')
    reference={(r['world_id'],r['state'],r['operation'],r['source']):r for r in plain}
    assert len(reference)==1536
    reference_draws=rows(source/'Plain/training.jsonl')
    for path in sorted(source.glob('*/*_validation.jsonl')):
        rs=rows(path);name=path.parent.name
        assert len(rs)==1536 and {r['world_id'] for r in rs}=={r['world_id'] for r in plain}
        assert {(r['world_id'],r['state'],r['operation'],r['source']) for r in rs}==set(reference)
        for r in rs:
            ref=reference[(r['world_id'],r['state'],r['operation'],r['source'])]
            assert ref['current']==r['current'],'Current H readout differs from SHA-matched Plain source'
        meta=read(path.parent/'TRAINING_COMPLETE.json')
        draws=rows(path.parent/'training.jsonl');assert len(draws)==400
        assert all((a['operation'],a['draws'])==(b['operation'],b['draws']) for a,b in zip(draws,reference_draws))
        score={k:sum(r['prediction']['score'][field] for r in rs) for k,field in [('joint','success'),('target','target'),('content','preserved'),('parseable','parseable')]}
        scores={k:dict(numerator=v,denominator=1536,rate=v/1536) for k,v in score.items()}
        scores['EOS']=dict(numerator=sum(r['prediction']['ended'] for r in rs),denominator=1536)
        candidate=dict(name=name,seed=summary['seed'],worlds=64,records=1536,scores=scores,
            source_scores={s:dict(numerator=sum(r['prediction']['score']['success'] for r in rs if r['source']==s),denominator=sum(r['source']==s for r in rs)) for s in ('natural','history')},
            checkpoint_sha256=sha(path.parent/'update400.pt'),validation_sha256=sha(path),
            keep_weight=meta['metadata']['keep_weight'],mechanism_weight=meta['metadata']['mechanism_weight'],
            sites=meta['metadata']['sites'],updates=400,matched_Plain_initialization_seed=True,
            matched_400_minibatches=True,training_wall_seconds=meta['wall_seconds'],
            teacher_forwards_per_update=meta['teacher_forwards_per_update'],
            student_forwards_per_update=meta['student_forwards_per_update'],backwards_per_update=meta['backwards_per_update'],
            reused=(path.parent/'REUSE_RECEIPT.json').exists())
        candidates.append(candidate)
        for filename in ('TRAINING_COMPLETE.json','MATCHED_DRAW_ACCEPTANCE.json','REUSE_RECEIPT.json'):
            p=path.parent/filename
            if p.exists():shutil.copy2(p,dest/path.parent.name/filename)
    assert summary['frozen_backbone_sha_before']==summary['frozen_backbone_sha_after']
    assert summary['frozen_history_sha_before']==summary['frozen_history_sha_after']
    audit=dict(passed=True,seed=summary['seed'],worlds=64,candidates=candidates,
        frozen_backbone_unchanged=True,frozen_history_unchanged=True,
        independent_test_evaluations=0,scientific_scope='EXPLORATORY_VALIDATION_ONLY')
    dump(dest/'NUMERICAL_AUDIT.json',audit)
    allocation=read(dest/'RUN_STATUS.json')['allocation']
    table='\n'.join(f"| {r['name']} | {r['scores']['joint']['numerator']}/1536 | {r['scores']['target']['numerator']}/1536 | {r['scores']['content']['numerator']}/1536 | {r['keep_weight']} | {r['mechanism_weight']} |" for r in candidates)
    text(dest/'REPORT.md',f'''# BART S3 seed{summary['seed']} training/validation terminal\n\nCOMPLETED；Slurm{allocation['job_id']}；allocation GPU-hours{allocation['GPU_hours']:.6f}。192train worlds、64validation worlds，每world12合法操作×自然/history两来源，来源各768，均未按方法成功筛样本；所有方法rank16/400updates、同seed初始化与全部400 minibatch序列已逐条核验。Plain重用已完成checkpoint及预测，未额外复训，旧allocation已在账本中计费。\n\n| 方法/候选 | 联合成功 | 目标正确 | 非目标内容 | keep权重 | mechanism权重 |\n| --- | --- | --- | --- | --- | --- |\n{table}\n\n每方法64独立world，1536操作不是1536独立样本；当前源读出与旧Plain完整记录一致。全部逐样本预测、400更新日志及小checkpoint保存；NUMERICAL_AUDIT从全量记录独立重算。teacher分支无梯度、student H→decoder保留梯度，backbone/history前后SHA相同。所有推理输入H/mask/op，一次latent forward，无donor/目标全文/重编码/推理反传。训练gold仅用于loss。\n\n候选或正式训练的validation结果均为探索性；固定128独立test仍因5个派生core暴露阻塞，正式test评测0，不能作为独立机制编辑确认。方法选择只能按锁定validation规则；同单操作分数不意味着相同长期轨迹。完整轨迹本run未执行，后续需要在各方法自己的latent输出上测1/2/3/5步。\n\n计算成本：Plain训练每update8 student forward/8 backward；keep/mech方法额外8 teacher forward。同更新预算不是同GPU耗时，实际train walltime/前反向次数记录在NUMERICAL_AUDIT；初始化参数量相同。扰动norm全样本已记录，将按训练前锁定norm bins汇总。全部失败/负结果保留。\n''')
    text(dest/'INTERPRETATION.md','本run完成监督编辑和内容保护候选或锁定方法，只有validation结果。主比较vsOutput-only/vsRandom-site需三seed配对world统计；若无差异只说明本批validation未见增量，不能推广普遍无效。独立test阻塞保留，长链不能由单操作推断。\n')
    return audit
