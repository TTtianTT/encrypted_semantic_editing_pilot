"""CPU-only per-terminal-run collection; preserves failed/missing records."""
import argparse
import gzip
import shutil
from .common import *
from .resources import accounting,ACTIVE

def collect(stage):
    ledger=read(CONTROL/'jobs.json');acct=accounting([r['job_id'] for r in ledger]);dump(ROOT/'results/resource_ledger.json',acct)
    m=read(ROOT/f'manifests/{stage}.json');registered=read(ROOT/f'manifests/{stage}_registration.json')
    for i,task in enumerate(m['tasks']):
        folder=Path(m['output_root'])/f"{task['model']}_s{task['seed']}";status_path=folder/'RUN_STATUS.json'
        allocation=next((r for r in acct['allocations'] if r['job_id']==registered['job_id']+'_'+str(i)),None)
        if allocation is None or allocation['state'] in ACTIVE:continue
        status=read(status_path) if status_path.exists() else dict(stage=stage,model=task['model'],seed=task['seed'],completed_samples=0,remaining_samples=8)
        if status.get('status') not in ('COMPLETED','FAILED_TECHNICAL','BLOCKED_BACKEND_PARITY','NOT_LOCALIZED','NOT_ESTIMABLE'):
            status.update(status='TIMEOUT_PARTIAL' if allocation['state']=='TIMEOUT' else 'FAILED_TECHNICAL',error='allocation terminated without complete worker result',exit_code=allocation['exit_code'])
        status['allocation']=allocation
        dest=ROOT/'reports'/f"{stage}_{m['version']}_{task['model']}_s{task['seed']}";dest.mkdir(parents=True,exist_ok=True)
        if (dest/'REPORT.md').exists():continue # terminal report never rewritten by later ledger refresh
        dump(dest/'RUN_STATUS.json',status)
        for name in ('SUMMARY.json','S0_ACCEPTANCE.json','HOOK_MAP.json','GRADIENT_CHECK.json','EAGER_ACCEPTANCE.json','NATIVE_HOOK_ACCEPTANCE.json','PARITY_DIAGNOSTIC.json','FAILURE.txt'):
            if (folder/name).exists():shutil.copy2(folder/name,dest/name)
        for p in folder.rglob('*.jsonl'):
            with p.open('rb') as src:atomic(dest/(str(p.relative_to(folder))+'.gz'),gzip.compress(src.read(),mtime=0))
        for p in folder.rglob('update*.pt'):
            if p.stat().st_size<5_000_000:
                dst=dest/p.relative_to(folder);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst)
        for p in folder.rglob('*LOCK.json'):
            dst=dest/p.relative_to(folder);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst)
        logroot=ROOT/'local/slurm_logs'
        for p in logroot.glob(f"*{registered['job_id']}_{i}.*"):
            atomic(dest/(p.name+'.gz'),gzip.compress(p.read_bytes(),mtime=0))
        summary=read(folder/'SUMMARY.json') if (folder/'SUMMARY.json').exists() else {}
        smoke=summary.get('overfit',{});n=summary.get('worlds',status.get('completed_samples',0))
        outcome=f"8-world smoke联合成功：{smoke.get('joint_success','NA')}/8；CE {smoke.get('initial_CE','NA')} → {smoke.get('final_CE','NA')}，更新{smoke.get('updates','NA')}。这些为训练验收数据，不是方法独立效果。" if stage=='S0' else '结果：'+json.dumps(summary,ensure_ascii=False)+'\n\n失败原因：'+status.get('error','无')
        report=f"""# {stage} {task['model']} seed{task['seed']} 终态\n\n状态：{status['status']}；Slurm {allocation['job_id']} / {allocation['state']}。完成world {n}；剩余{status.get('remaining_samples','NA')}；独立test访问0。GPU-hours={allocation['GPU_hours']:.6f}，本轮累计={acct['GPU_hours']:.6f}，登记allocation峰值={acct['peak_concurrent_GPUs']} GPU。\n\n{outcome}\n\n当前机制、机制相对Output-only/Random-site编辑收益、原子与长期能力、新T5Gemma独立资格均为NA，尚未执行。技术验收失败阻断该模型后续分析，不删除world通过。关键失败详细记录在 FAILURE.txt / 原始压缩日志。\n\n所有源代码来自manifest指向的immutable snapshot；checkpoint、split、代码SHA在RUN_STATUS/manifest。完整逐样本记录及日志压缩提交；大产物路径与SHA索引见 ARTIFACTS.json。\n"""
        text(dest/'REPORT.md',report);text(dest/'INTERPRETATION.md','本run仅实施工具/梯度/训练loss验收。任何科学效应不能由此推断。失败为技术阻塞，不是0%科学结果；未运行项为NA。\n')
        dump(dest/'ARTIFACTS.json',[dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size) for p in folder.rglob('*') if p.is_file()])
        print(str(dest),status['status'])
    return acct

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--stage',required=True);a=p.parse_args();collect(a.stage)
