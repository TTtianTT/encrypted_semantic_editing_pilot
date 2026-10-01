"""CPU-only bounded G15 late-regression audit; no model forward or gradient claims."""
import statistics
from common_g16 import *

def main():
    source_hashes={};worlds={w['record_id']:w for w in read(G15/'data/worlds.jsonl')}
    stages=read(G15/'learning_per_example.jsonl.gz');atomic=[];cap=[];periods=[];quotas=[];checks=[]
    from transformers import AutoTokenizer
    tok=AutoTokenizer.from_pretrained(REPO/'models/bart-base',local_files_only=True)
    tokenlen={}
    def nt(w,d,p='first'):
        k=w['record_id'],d,p
        if k not in tokenlen:tokenlen[k]=len(tok(render(w,frame(w,d,p)))['input_ids'])
        return tokenlen[k]
    for seed in [42,43,44]:
        schedule=read(G15/f'data/schedule_s{seed}.jsonl');trainplans=[w for w in worlds.values() if w['split']=='train' and w['record_status']=='recorded_plan']
        tokens=[]
        for b in schedule:
            bw=[trainplans[i] for i in b['main_indices']];mw=[trainplans[i] for i in b['maintenance_indices']]
            replay=[(worlds[r['record_id']],r['offset'],r['perspective']) for r in b['replay']]
            for w,d,p in replay:
                assert (d,p) in atomic_specs(w)
                assert advance(frame(w,d,p),'T_plus')==frame(w,d-1,p)
            tokens.append(dict(A=sum(nt(w,0) for w in bw),B=sum(nt(w,d-1,p) for w,d,p in replay),C=sum(nt(w,-2) for w in mw),D=sum(nt(w,-1) for w in bw)))
        for method in ['N','F','O']:
            meta=json.loads((G15/f'training/{method}_s{seed}.json').read_text());logs=read(G15/f'training/{method}_s{seed}_steps.jsonl.gz')
            assert [l['step'] for l in logs]==list(range(1,201)) and [l['tokens'] for l in logs]==tokens
            for l,b in zip(logs,schedule):
                assert [o['world_id'] for o in l['current_records']]==[trainplans[i]['record_id'] for i in b['main_indices']]
                for o in l['current_records']:assert o['gold']==render(worlds[o['world_id']],frame(worlds[o['world_id']],0))
            assert meta['counts']['instances']==6400 and digest(G15/meta['final_path'])==meta['final_sha256']
            assert meta['schedule_sha256']==digest(G15/f'data/schedule_s{seed}.jsonl')
            assert all(len(l['current_records'])==8 and abs(l['loss']-sum(l['block_losses'].values())/4)<=1e-6*max(1,abs(l['loss'])) for l in logs)
            # FP32 scalar arithmetic may differ from Python averaging by <=1e-8.
            for lo,hi in [(1,100),(101,150),(151,200)]:
                ls=logs[lo-1:hi];bs=schedule[lo-1:hi]
                cc=collections.Counter((worlds[r['record_id']]['record_status'],r['offset'],r['perspective']) for b in bs for r in b['replay'])
                assert len(cc)==40 and len(set(cc.values()))==1
                for cell,n in sorted(cc.items()):quotas.append(dict(seed=seed,method=method,start_step=lo,end_step=hi,status=cell[0],offset=cell[1],perspective=cell[2],replay_n=n))
                for block in 'ABCD':periods.append(dict(seed=seed,method=method,start_step=lo,end_step=hi,block=block,optimizer_updates=len(ls),instances=len(ls)*8,tokens=sum(l['tokens'][block] for l in ls),mean_block_CE=statistics.mean(l['block_losses'][block] for l in ls),first_CE=ls[0]['block_losses'][block],last_CE=ls[-1]['block_losses'][block],C_source_counts=json.dumps(collections.Counter(str(s) for b in bs for s in b['maintenance_sources']))))
            for step in [100,150,200]:
                for split in ['train','dev']:
                    rs=[r for r in stages if r['seed']==seed and r['method']==method and r['step']==step and r['split']==split]
                    for status,d,p in sorted({(r['status'],r['offset'],r['perspective']) for r in rs if r['kind']=='atomic'}):
                        ss=[r for r in rs if r['kind']=='atomic' and (r['status'],r['offset'],r['perspective'])==(status,d,p)]
                        atomic.append(dict(seed=seed,method=method,step=step,split=split,status=status,offset=d,perspective=p,k=sum(r['joint'] for r in ss),n=len(ss),joint_rate=sum(r['joint'] for r in ss)/len(ss),exact_k=sum(r['exact'] for r in ss),NLL=sum(r['loss_sum'] for r in ss)/sum(r['target_tokens'] for r in ss),target_tokens=sum(r['target_tokens'] for r in ss)))
                    for kind in ['seen_A','seen_D']:
                        ss=[r for r in rs if r['kind']==kind];cap.append(dict(seed=seed,method=method,step=step,split=split,task=kind,D_source='fixed P' if method=='F' else 'current T detached' if method=='O' else 'natural E',k=sum(r['joint'] for r in ss),n=len(ss),full_k=sum(r.get('full',r['joint']) for r in ss),NLL=sum(r['loss_sum'] for r in ss)/sum(r['target_tokens'] for r in ss)))
                    old=collections.defaultdict(dict)
                    for r in rs:
                        if r['kind']=='old' and r['matched']:old[r['world_id']][r['source']]=r
                    for source in ['H0','H1','H2','all3']:
                        k=sum(all(r['joint'] for r in v.values()) if source=='all3' else v[source]['joint'] for v in old.values())
                        cap.append(dict(seed=seed,method=method,step=step,split=split,task=source,k=k,n=len(old),NLL=None if source=='all3' else sum(v[source]['loss_sum'] for v in old.values())/sum(v[source]['target_tokens'] for v in old.values())))
            checks.append(dict(seed=seed,method=method,steps_1_to_200=True,tokens_reconstructed_equal=True,instances=6400,final_sha256=meta['final_sha256'],initial_state_hash=meta['initial_hash'],schedule_sha256=meta['schedule_sha256'],D_producer_distinct=len({l['D_producer_hash'] for l in logs}),first_joint_wrong=meta['counts']['first_current_joint_wrong'],original_job_id=meta['job_id'],stage100_150_weights='not in Git; archived local G15 snapshot paths recorded separately',optimizer_state_history='per-step optimizer internal state not in uploaded logs; resume code and final/hash/log evidence accessible'))
    for path in [G15/n for n in ['PROTOCOL.md','INTERPRETATION.md','REPORT.md','run.py','checkpoints_manifest.json','data/manifest.json','data/worlds.jsonl','learning_per_example.jsonl.gz','learning_curves.csv','optimizer_steps.csv','resume_evaluation_audit.json']]+list((G15/'training').glob('*')):
        if path.is_file():source_hashes[str(path.relative_to(REPO))]=digest(path)
    csvwrite(ROOT/'g15_atomic_stage_audit.csv',atomic);csvwrite(ROOT/'g15_capability_stage_audit.csv',cap);csvwrite(ROOT/'g15_loss_budget_periods.csv',periods);csvwrite(ROOT/'g15_replay_period_quotas.csv',quotas);csvwrite(ROOT/'g15_state_step_audit.csv',checks)
    # Original local snapshots are read/hash only, never loaded for GPU inference.
    oldlocal=Path('/dataset1/zailong/workspace/encrypted_semantic_editing_pilot/.g15-worktree/experiments/g15_self_state_transfer_v1/local')
    snapshots=[]
    for s in [42,43,44]:
        for m in ['N','F','O']:
            for t in [100,150,200]:
                p=oldlocal/f'{m}_s{s}_step{t}.pt';snapshots.append(dict(seed=s,method=m,step=t,path=str(p),accessible=p.exists(),sha256=digest(p) if p.exists() else None))
    csvwrite(ROOT/'g15_snapshot_paths.csv',snapshots)
    dump(ROOT/'g15_audit.json',dict(passed=True,definite_invalidating_engineering_error=False,no_GPU=True,no_G15_step150_U_evaluated=True,source_sha256=source_hashes,all_40_cells_all_seeds_methods=True,quota_target_step_token_checks_passed=True,gradient_conflict_measured=False,scope='G15 committed records and bounded local snapshot SHA only; no historical branch resurvey'))
    out=['# G15末段退化CPU审计','', '直接观察：完整N/F/O、seed42/43/44、100/150/200 train/dev的40-cell、NLL、维护/保护/已监督D均已重建；详见CSV。各阶段原子分母每cell16，主诊断32，不能冒充完整确认集。','', 'seed44 F在150的train/dev原子macro均100%，200为89.219%/88.438%；O为100%→87.031%/85.469%。已有固定200确认的IID F/O为89.563%/87.359%。A和各自已监督D诊断仍成功，旧维护诊断仍成功。完整逐cell表保留其他seed与自然控制，不只列失败cell。','', '每个训练末段回放配额仍对40cell平衡：1–100各cell20次、101–150及151–200各10次。N/F/O的每步目标token数与重新渲染/原tokenizer逐项一致；C来源等频轮换，所有200个global step连续，6400实例、final checkpoint SHA及schedule SHA核验通过。未发现确定的任务标签、配额或记录错配错误。','', '可能解释：固定多任务训练的晚期更新行为与维护不足值得检查；现有记录不能唯一归因。梯度冲突未测量，没有gradient cosine/投影诊断，不从CE上升宣称梯度冲突或必然任务权衡。train/dev共同下降不足以直接支持普通样本过拟合。','', '缺少证据：G15较小诊断不是step150完整IID/OOD确认；本轮未新增G15 GPU推断，尤其未测试step150 U、未替换G15历史主模型。中间权重仅记录可访问本地路径与SHA；逐步optimizer内部状态和完整梯度历史未上传，不能声称排除所有优化机制。已知seed43只在最终评估超时，补跑未重训且旧工件SHA一致，不解释训练退化。','', '审计没有发现使G16计划无效的确定工程错误，科学设置与选择阈值不据本审计修改。']
    (ROOT/'g15_late_regression_audit.md').write_text('\n'.join(out)+'\n');print('G15 CPU audit passed; no invalidating engineering error')

if __name__=='__main__':main()
