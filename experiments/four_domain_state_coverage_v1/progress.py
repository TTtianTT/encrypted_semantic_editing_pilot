"""CPU filesystem snapshot; no GPU work or scheduler mutation."""
import datetime
from collections import Counter
from common import *

def main():
    status=[]
    for study in ('four_domain_state_coverage_v1','space_relation_confirmation_v1'):
        base=ROOT.parent/study
        for t in read(base/'tasks.json'):
            if t['phase'] not in ('formal','symbol'):continue
            name=f"{t['model']}_{t['domain']}_s{t['seed']}";p=base/'runs'/t['phase']/name;done=p/'complete.json';gate=p/'dev/admission.json';index=p/'checkpoint_index.json'
            record=dict(study=study,stage=t['phase'],model=t['model'],domain=t['domain'],seed=t['seed'],status=read(done)['status'] if done.exists() else 'technical_failure' if (p/'failure.json').exists() else 'in_progress' if p.exists() else 'not_started',gate_passed=read(gate)['passed'] if gate.exists() else None,checkpoints=list(read(index)) if index.exists() else [],completed_prediction_shards=len(list((p/'outputs').rglob('*.jsonl'))))
            status.append(record)
    for file,stage in [('identity_probe_tasks.json','identity_probe'),('linguistic_tasks.json','linguistic_controls'),('position_tasks.json','position_foils')]:
        for t in read(ROOT/file):
            base=ROOT.parent/t['study'];p=base/'runs/formal'/f"{t['model']}_{t['domain']}_s{t['seed']}"/'identity_probe' if stage=='identity_probe' else base/('language_controls' if stage=='linguistic_controls' else 'position_foils')/f"{t['model']}_{t['domain']}";cp=p/'complete.json';status.append(dict(**t,stage=stage,status=read(cp).get('status','completed') if cp.exists() else 'in_progress' if p.exists() else 'not_started'))
    stages={stage:dict(Counter(r['status'] for r in status if r['stage']==stage)) for stage in sorted({r['stage'] for r in status})};budget=read(ROOT/'budget.json');now=datetime.datetime.now(datetime.timezone.utc).isoformat();snapshot=dict(at_utc=now,stages=stages,tasks=status,gpu_hours_at_last_account=budget['actual_gpu_hours'],historical_max_concurrent_gpus=budget['max_concurrent_gpus'],job_ids=[dict(phase=r['phase'],job_id=r['job_id']) for r in read(ROOT/'submissions.json')]);dump(ROOT/'PROGRESS.json',snapshot)
    text='# 当前进度（工件快照，非最终结果）\n\nUTC '+now+'。所有GPU计算经Slurm；历史峰值'+str(budget['max_concurrent_gpus'])+'卡，最近账本累计'+f"{budget['actual_gpu_hours']:.3f}"+' GPU小时。\n\n'
    for stage,v in stages.items():text+=f'- {stage}: '+json.dumps(v,ensure_ascii=False)+'\n'
    text+='\n任务/准入/checkpoint/已写预测分片见PROGRESS.json。作业和依赖见submissions.json；分配、时限和退出状态见budget.json。\n\n恢复批次2620只接续原正式数组的技术超时，所有后续GPU批次均排在此前。CPU汇总2590在全部阶段之后运行，生成报告及工件核验；Git提交与推送由监督代理另行完成。\n';(ROOT/'PROGRESS.md').write_text(text);print(json.dumps(dict(at_utc=now,stages=stages,gpu_hours=budget['actual_gpu_hours'],peak_gpus=budget['max_concurrent_gpus'])))

if __name__=='__main__':main()
