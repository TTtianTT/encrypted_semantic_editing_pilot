"""CPU-only audit, split lock and immutable execution snapshot preparation."""
import argparse
import importlib.metadata
import random
import shutil
from datetime import datetime, timezone
from .common import *
from .exposure import scan

SOURCE=PROJECT/'.four-domain-worktree/experiments/four_domain_state_coverage_v1'
CAUSAL=PROJECT/'.causal-next-edit-worktree/experiments/causal_next_edit_stability_v1'

def initialize():
    if (ROOT/'configs/SPLIT_LOCK.json').exists():return
    available=scan()
    if len(available)<512:raise RuntimeError('BLOCKED_DATA_CAPACITY: fixed pool cannot be filled without content reuse')
    rng=random.Random(2026100801);rng.shuffle(available)
    prototype=rows(SOURCE/'data/time/worlds.jsonl')[0]
    ws=[]
    for i,key in enumerate(available[:512]):
        w=dict(prototype,object=key[0],color=key[1],quantity=key[2],status=key[3],world_id='drie_'+objsha(key)[:16],core_hash=objsha(key),template=0)
        w['split']='train' if i<192 else 'validation' if i<256 else 'test_iid' if i<384 else 'reserved_iid'
        ws.append(w)
    jsonl(ROOT/'configs/worlds.jsonl',ws)
    lock=dict(seed=2026100801,counts={s:sum(w['split']==s for w in ws) for s in ['train','validation','test_iid','reserved_iid']},sha256=sha(ROOT/'configs/worlds.jsonl'),grouping='object,color,quantity,status; all dates,templates,histories,seeds,sources grouped',OOD='UNAVAILABLE: original templates0-5 already exposed; reserved128 is not renamed OOD',test_unseal='S4 only after mechanism/hyperparameters/all checkpoints locked',mechanism_qualification_min_worlds=40)
    dump(ROOT/'configs/SPLIT_LOCK.json',lock)
    refs={ref.split('/')[-1]:head for ref,head in read(ROOT/'manifests/exposure_inventory.json')['refs']}
    audit=[]
    branches=['causal-next-edit-stability-v1','state-handoff-diagnosis-v1','four-domain-state-coverage-v1','current-source-compatibility-v1','decoder-basin-anisotropy-v1','g11-semantic-history-v1','g14-matched-state-handoff-v1','g17-state-source-transfer-v1']
    for name in branches:
        ref='origin/experiment/'+name;head=command('git','rev-parse',ref)
        dirname=name.replace('-','_');prefix='experiments/'+dirname+'/'
        for p in command('git','ls-tree','-r','--name-only',head,prefix).splitlines():
            if p.endswith(('.md','.py','.yaml','.sh','.slurm','.sbatch','.json','.csv')) and '/local/' not in p:
                raw=subprocess.check_output(['git','show',head+':'+p],cwd=WT)
                audit.append(dict(branch=ref,remote_head=head,path=p,sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),read=True))
    dump(ROOT/'manifests/historical_file_audit.json',audit)
    manifest=read(CAUSAL/'run_manifest.json');checks=[]
    for item in manifest['verified_backbone_files']+manifest['editors']:
        actual=sha(item['path']);assert actual==item['sha256']
        checks.append(dict(path=item['path'],sha256=actual,bytes=Path(item['path']).stat().st_size))
    dump(ROOT/'manifests/INPUTS.json',dict(models=manifest['models'],editors=manifest['editors'],checked_files=checks,native_sources={p.name:sha(p) for p in SOURCE.glob('*.py')},baseline_remote_heads=refs,split_sha=sha(ROOT/'configs/SPLIT_LOCK.json'),worlds_sha=sha(ROOT/'configs/worlds.jsonl'),original_branch=command('git','branch','--show-current',cwd=PROJECT),original_tracked_diff=command('git','diff','HEAD',cwd=PROJECT),environment={k:importlib.metadata.version(k) for k in ['torch','transformers','numpy']},python=str(PYTHON)))
    for d in ('slurm','tests','results','reports','figures','manifests','local'):(ROOT/d).mkdir(exist_ok=True)
    protocol=dict(version='decoder_readout_invariance_editing_v1',date='2026-10-08',models={'bart':'facebook/bart-base FP32','t5gemma':'google/t5gemma-2b-2b-ul2-it BF16'},domain='time',operations={'plus':'relative day decrements','minus':'relative day increments'},historical_condition='P, not person',rank=16,backbone_frozen=True,history_editors_frozen=True,split=lock,budget_GPU_hours=40,max_global_GPUs=2,one_active_stage_array=True,neural_execution='sbatch allocation via srun only',panels={'A':'correct current gold + native exact effective token IDs/raw text + EOS + same valid shape/mask + delta beyond repeat numerical noise; no next fork required','B':'A plus frozen next edit fork','C':'unconditional 50/50 natural/history source; incorrect history retained'},sources=['N','E_future_plus','E_past_minus','R_actual_once','P_locked_PCA'],source_priority=['N:E_future_plus','N:E_past_minus','E_future_plus:E_past_minus','R:E_future_plus','P:E_future_plus'],numerical_dedup=True,token_alignment='exclude decoder start; include forced tokens/EOS; stop first EOS after start; no strip for A',alphas=[-.5,0,.25,.5,.75,1,1.25,1.5],random_seeds=list(range(61001,61009)),random_controls=['per-token matched norm isotropic','per-token matched norm rank4 shared basis','validation-only scalar matching current preservation'],mechanism={'train_discovery':True,'max_validation_components':3,'conditions':['AA','BA','AB','BB'],'bidirectional':True,'no_normalized_recovery':True,'evidence_gate':'reproducible non-target content intervention support on validation; otherwise MECHANISM_NOT_IDENTIFIED'},training=dict(seeds=[42,43,44],rank=16,batch=16,microbatch=2,updates=400,save_updates=[200,400],lr=.001,clip=1.,weight_decay=0.,methods=['Plain','Output-only','Mechanism-guided','Random-site'],lambda_mech=[.1,1.],same_init_and_draws=True,selection='content >= Output-only minus0.02 then joint success; tie lower lambda/cost; keep/size locks shared',test_input=['H','mask','operation'],test_forbidden=['donor','gold text','reencode','decoder gradients','rejection sampling']),evaluation=dict(primary='50/50 source-balanced joint target,preserved,parseable,grammar,EOS',lengths=[1,2,3,5],sequences=[['plus','minus','plus','minus','plus'],['plus','plus','minus','minus','plus']],reverse_directions=True,all_steps_correct=True,bootstrap=20000,unit='paired core world cluster',holm_family=['Mechanism-guided vs Output-only','Mechanism-guided vs Random-site'],boundary='Wilson per seed plus paired counts'),optional={'T5Gemma':'after BART priority; never substitute checkpoint','preconditioning':'only after S0-S4; NOT_RUN_BUDGET if unavailable'},claims='no semantic nullspace/unique complete circuit/long-term solved presumption')
    dump(ROOT/'protocol.yaml',protocol)
    text(ROOT/'.gitignore','local/\n__pycache__/\n')
    text(ROOT/'AUDIT.md',f'''# 实际资源与证据审计\n\n远端 HEAD 与 {len(audit)} 个历史文件的 SHA256 在 manifests/historical_file_audit.json。原工作区和所有已有 worktree 未修改。历史 BART 四维逐有效 token PCA 是大幅 donor-assisted 修补；旧80 worlds 为 replay/discovery。N=R 不重复计来源。P 为历史配置代号。旧 T5Gemma next-fork 排除规则不用于新 SAME_TEXT 面板。Handoff 远端仍只声明 R00 CPU prepared；当前实时作业由 squeue/sacct 单独审计。\n\n跨分支保守排除456个时间 core，1080种原词汇组合中剩624个；新池512在任何模型运行前锁定。模板0-5均已有曝光，模板 OOD 为 UNAVAILABLE，剩余128标 reserved_iid，不作为 OOD。核心忽略不出现在核心文本中的日期和人名。实际输入文件全部 SHA 核验；源码复制进不可变 snapshot，不热加载旧 worktree。\n\n当前环境 torch/transformers 见 INPUTS.json；未升级。B300q 核验 MaxTime=UNLIMITED，AllowAccounts/AllowQos=ALL；单 task gres=gpu:1，64GB host memory，8CPU，1小时 shard（<=3小时规则）。当前 squeue 无本人作业；以后每次提交再查询。外部锁/注册表在 {CONTROL}。峰值/消耗由 allocation级 sacct 计，失败计费，worker不得修改Git。\n''')
    text(ROOT/'README.md',f'''# Decoder readout invariance and latent editing v1\n\n实际执行接口，从 {WT} 运行：\n\n```bash\n{PYTHON} -m experiments.decoder_readout_invariance_editing_v1.prepare --stage S0\n{PYTHON} -m experiments.decoder_readout_invariance_editing_v1.submit_stage --stage S0\n{PYTHON} -m experiments.decoder_readout_invariance_editing_v1.collect --stage S0\n{PYTHON} -m experiments.decoder_readout_invariance_editing_v1.publish --stage S0\n```\n\nCPU orchestration不执行模型；run_stage只接受已登记sbatch+srun。每run终态报告/压缩记录由CPU publisher串行提交，push并核验远端SHA。协议在 protocol.yaml，真实完成状态在 STATUS.md；未执行项不计0。完整大产物位于 ignored local/，索引含SHA与重建入口。\n''')

def prepare(stage):
    initialize()
    if stage=='S4' and (ROOT/'configs/TEST_EXPOSURE_WITHDRAWAL_LOCK.json').exists():
        proposal=ROOT/'configs/S4_PROTOCOL_AMENDMENT_PROPOSAL.json'
        if proposal.exists() and read(proposal).get('status','').startswith('WITHDRAWN'):
            final_exposure=ROOT/'configs/FINAL_EXPOSURE_LOCK.json'
            dump(ROOT/'results/S4_SUBMISSION_STATUS.json',dict(status='BLOCKED_TEST_INTEGRITY',reason='Prior123 proposal withdrawn; encoder/current-output/historical-output core union is audited and no revised endpoint authorized',original_scan_denominator=128,known_exposed=read(final_exposure)['known_exposed_count'] if final_exposure.exists() else None,replacement_sampling=False,formal_test_evaluations=0))
            raise RuntimeError('BLOCKED_TEST_INTEGRITY: withdrawn proposal cannot authorize test unsealing')
        auth=ROOT/'configs/S4_AMENDMENT_AUTHORIZATION.json'
        if not auth.exists() or not read(auth).get('approved',False):
            dump(ROOT/'results/S4_SUBMISSION_STATUS.json',dict(status='BLOCKED_TEST_INTEGRITY',reason='Five counterfactual donor cores were encoded before S4; fixed full128 independent endpoint is compromised',original_scan_denominator=128,replacement_sampling=False,formal_test_evaluations=0))
            raise RuntimeError('BLOCKED_TEST_INTEGRITY; preserve fixed scan and exposure audit, do not silently substitute a new endpoint')
        assert read(auth)['proposal_sha256']==sha(ROOT/'configs/S4_PROTOCOL_AMENDMENT_PROPOSAL.json')
        final=read(ROOT/'configs/FINAL_TEST_LOCK.json')
        assert final['all_seeds_locked'] and final['checkpoint_lock_sha256']==sha(ROOT/'configs/FINAL_METHOD_CHECKPOINT_LOCK.json')
    if stage in ('S3_SELECT','S3_MAIN'):
        review=ROOT/'configs/KEEP_MASK_REVIEW_LOCK.json'
        if not review.exists() or not read(review).get('reviewed_by_human',False):
            dump(ROOT/'results/S3_SUBMISSION_STATUS.json',dict(status='BLOCKED_MASK_REVIEW',
                stage=stage,reason='Protocol section 6.2 requires human spot-check of I_keep accuracy',
                review_material=str(ROOT/'reports/KEEP_MASK_REVIEW.md'),
                review_material_sha256=sha(ROOT/'reports/KEEP_MASK_REVIEW.md'),
                human_review_received=False,submitted_GPU_jobs=0,
                completed_methods=['Plain'],remaining_methods=['Output-only','Mechanism-guided','Random-site']))
            raise RuntimeError('BLOCKED_MASK_REVIEW: no human-reviewed keep-mask lock; review material is prepared')
    if stage not in ('S0','S1','S1_NATIVE','S1_GENERATION_AUDIT','S2','S2_NATIVE','S2_QUERY_BRIDGE','S3_REGULARIZER_SMOKE','S3_SELECT','S3_MAIN','S3_PLAIN','S3_VALIDATION_TRAJECTORIES','S3_SELECTED_VALIDATION_TRAJECTORIES','S3_TRAJECTORY_NORMS','S4','T5_QUALIFICATION','PARITY_DIAG'):raise RuntimeError('Stage implementation/gates must exist before preparation')
    path=ROOT/f'manifests/{stage}.json'
    if path.exists():print(path);return
    inp=read(ROOT/'manifests/INPUTS.json');tasks=[]
    for model in (('bart','t5gemma') if stage=='S0' else ('t5gemma',) if stage=='T5_QUALIFICATION' else ('bart',)):
        if stage!='S0':
            accepted=list((ROOT/'reports').glob('S0_*_'+model+'_s42/S0_ACCEPTANCE.json'))
            assert accepted and read(accepted[-1])['passed'],'Model S0 acceptance required'
        ck=next(e for e in inp['editors'] if e['model']==model and e['seed']==42)
        tasks.append(dict(model=model,seed=42,checkpoint=ck['path'],checkpoint_hash=ck['sha256'],stage=stage))
    if stage.startswith('S2'):assert (ROOT/'configs/S2_CANDIDATES.json').exists()
    if stage.startswith('S3') and stage not in ('S3_PLAIN','S3_VALIDATION_TRAJECTORIES'):
        assert (ROOT/'configs/MECHANISM_LOCK.json').exists()
        assert read(ROOT/'configs/KEEP_MASK_REVIEW_LOCK.json')['reviewed_by_human']
    if stage in ('S3_SELECT','S3_MAIN'):
        assert read(ROOT/'configs/REGULARIZER_ACCEPTANCE_LOCK.json')['passed'],'Regularizer GPU acceptance required'
    if stage in ('S3_MAIN','S3_PLAIN','S3_VALIDATION_TRAJECTORIES','S3_SELECTED_VALIDATION_TRAJECTORIES','S3_TRAJECTORY_NORMS','S4'):
        if stage=='S3_MAIN':assert (ROOT/'configs/TRAINING_SELECTION_LOCK.json').exists()
        tasks=[]
        for seed in ((43,44) if stage=='S3_MAIN' else (42,43,44)):
            ck=next(e for e in inp['editors'] if e['model']=='bart' and e['seed']==seed)
            tasks.append(dict(model='bart',seed=seed,checkpoint=ck['path'],checkpoint_hash=ck['sha256'],stage=stage))
    if stage=='S3_VALIDATION_TRAJECTORIES':assert (ROOT/'configs/PLAIN_CHECKPOINT_LOCK.json').exists()
    if stage=='S3_SELECTED_VALIDATION_TRAJECTORIES':assert (ROOT/'configs/FINAL_METHOD_CHECKPOINT_LOCK.json').exists()
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ');snapshot=ROOT/f'local/snapshots/{stage}_{stamp}'
    target=snapshot/'experiments'/ROOT.name;target.mkdir(parents=True)
    for p in ROOT.glob('*.py'):shutil.copy2(p,target/p.name)
    shutil.copy2(ROOT/'protocol.yaml',target/'protocol.yaml')
    native=target/'native';native.mkdir()
    for p in list(SOURCE.glob('*.py'))+[SOURCE/'config.json',SOURCE/'model_manifest.json']:shutil.copy2(p,native/p.name)
    for folder in ('configs','manifests'):shutil.copytree(ROOT/folder,target/folder)
    filehash={str(p.relative_to(snapshot)):sha(p) for p in snapshot.rglob('*') if p.is_file()}
    hours=1 if stage in ('S0','T5_QUALIFICATION') else .25 if stage in ('PARITY_DIAG','S3_REGULARIZER_SMOKE','S3_TRAJECTORY_NORMS') else 3
    manifest=dict(stage=stage,version=stamp,snapshot=str(snapshot),output_root=str(ROOT/'local/runs'/f'{stage}_{stamp}'),tasks=tasks,python=str(PYTHON),partition='B300q',walltime='01:00:00' if stage in ('S0','T5_QUALIFICATION') else '00:15:00' if stage in ('PARITY_DIAG','S3_REGULARIZER_SMOKE','S3_TRAJECTORY_NORMS') else '03:00:00',reservation_GPU_hours=len(tasks)*hours,gpus_per_task=1,files=filehash,config_hash=sha(ROOT/'protocol.yaml'),split_hash=sha(ROOT/'configs/SPLIT_LOCK.json'),worlds_hash=sha(ROOT/'configs/worlds.jsonl'),checkpoint_hashes={t['checkpoint']:t['checkpoint_hash'] for t in tasks})
    if stage in ('S3_REGULARIZER_SMOKE','S3_SELECT','S3_MAIN'):
        for item in read(ROOT/'configs/S3_REUSE_LOCK.json')['entries']:
            if item['seed'] in {t['seed'] for t in tasks}:
                manifest['checkpoint_hashes'][item['checkpoint']]=item['checkpoint_sha256']
                manifest['checkpoint_hashes'][item['validation']]=item['validation_sha256']
    if stage=='S3_VALIDATION_TRAJECTORIES':
        for item in read(ROOT/'configs/PLAIN_CHECKPOINT_LOCK.json')['checkpoints']:manifest['checkpoint_hashes'][item['path']]=item['sha256']
    if stage in ('S3_SELECTED_VALIDATION_TRAJECTORIES','S3_TRAJECTORY_NORMS','S4'):
        for item in read(ROOT/'configs/FINAL_METHOD_CHECKPOINT_LOCK.json')['checkpoints']:manifest['checkpoint_hashes'][item['path']]=item['sha256']
    if stage=='S4':
        manifest['checkpoint_hashes'][inp['PCA_path']]=inp['PCA_sha256']
    dump(path,manifest)
    print(path)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--stage',required=True);a=p.parse_args();prepare(a.stage)
