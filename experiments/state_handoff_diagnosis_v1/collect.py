"""CPU terminal collector; failures and partial batches are reportable outcomes."""
import argparse
import gzip
from .common import *
from .resource import refresh,TERMINAL
from .metrics import *

def validate_shards(task):
    folder=Path(task['output']);records=[];shards=[]
    for p in sorted(folder.glob('batch_*.jsonl')):
        meta=p.with_suffix('.meta.json')
        if not meta.exists():continue
        m=read(meta);assert m['scientific_hash']==task['scientific_hash'] and sha(p)==m['sha256']
        batch=rows(p);assert len(batch)==m['rows']
        records+=batch;shards.append(dict(path=str(p),sha256=sha(p),rows=len(batch),execution_commit=m['execution_commit'],worlds=m['worlds']))
    unique=[(r['world_id'],r['kind'],r.get('state'),r.get('operation'),r.get('b'),r.get('condition'),r.get('producer'),r.get('receiver'),r.get('initial_state'),r.get('a'),r.get('sequence_id'),r.get('depth')) for r in records]
    assert len(set(unique))==len(unique),'Duplicated observations'
    complete=read(folder/'complete.json') if (folder/'complete.json').exists() else None
    if complete:
        assert complete['scientific_hash']==task['scientific_hash'] and complete['expected_batches']==len(shards)
        assert complete['expected_worlds']==len({r['world_id'] for r in records})
        expected=18 if task['model']=='bart' and task['round']!='R03' else 112 if task['round']!='R03' else 28 if task['model']=='bart' else 92
        assert len(records)==expected*complete['expected_worlds'],('Incomplete condition cells',len(records),expected)
    return records,shards,complete

def collect_run(task,attempts,ledger):
    run_id=task['run_id'];out=ROOT/'runs'/run_id
    if (out/'receipt.json').exists() and read(out/'receipt.json').get('state')=='PUSH_VERIFIED':return
    records,shards,complete=validate_shards(task)
    status='EXECUTED' if complete else 'PARTIAL' if records else 'BLOCKED'
    if task['round']=='R00' and complete and not all(a['passed'] for a in complete['acceptance']):status='BLOCKED'
    out.mkdir(parents=True,exist_ok=True)
    payload=''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in records).encode();atomic(out/'observations.jsonl.gz',gzip.compress(payload,mtime=0))
    metrics=summarize_records(records);csv_write(out/'metrics.csv',metrics)
    partition=failure_partition(records);csv_write(out/'failure_partition.csv',partition)
    primary_result=primary(records);run_hours=sum(a['gpus']*a['elapsed_seconds']/3600 for a in attempts)
    conclusion=dict(run_id=run_id,scientific_status=status,execution_commits=sorted({s['execution_commit'] for s in shards}),scientific_hash=task['scientific_hash'],protocol_hash=task['protocol_hash'],data_hash=task['world_hash'],checkpoint_hashes={c['condition']:c['sha256'] for c in task['checkpoint_records']},model=task['model'],seed=task['seed'],split=task['split'],completed_worlds=len({r['world_id'] for r in records}),expected_worlds=8 if task['round']=='R00' else 80,records=len(records),primary=primary_result,Slurm_attempts=attempts,GPU_hours=run_hours,cumulative_GPU_hours=ledger['gpu_hours'],maximum_concurrent_GPUs=ledger['maximum_concurrent_gpus'],acceptance=complete.get('acceptance') if complete else None,resource_observation=complete.get('resources') if complete else None,cache_counts={k:complete.get(k) for k in ['new_cache_count','reused_cache_count','encode_calls','decode_calls']} if complete else None,limitations=['Single-seed scope; no three-seed claim.','Reencode changes representation/layout/mask; not isolated latent patch.','No private protocol or unique failure mechanism inferred.','Missing outputs remain missing, never zero.'])
    dump(out/'conclusion.json',conclusion)
    dump(out/'artifact_index.json',dict(shards=shards,output_root=task['output'],observation_sha256=sha(out/'observations.jsonl.gz'),cache_index=str(Path(task['output'])/'artifacts.json'),complete_marker=str(Path(task['output'])/'complete.json') if complete else None))
    dump(out/'manifest.json',task)
    lines=[f'# {run_id}','',f'- 科学状态：{status}',f'- 模型/seed/split：{task["model"]}/{task["seed"]}/{task["split"]}',f'- execution_commit：{conclusion["execution_commits"]}',f'- 科学/协议/数据哈希：{task["scientific_hash"]} / {task["protocol_hash"]} / {task["world_hash"]}',f'- Slurm终态与attempt：{[(a["array_task_id"],a["state"]) for a in attempts]}','','## 本次关键改动','','沿用上述execution_commit；本次无科学代码变化。新增逐例压缩记录、分母检查、metrics、归因表和资源记录；不改旧结果。','','## 结果','',f'完整记录world数：{conclusion["completed_worlds"]}/{conclusion["expected_worlds"]}；记录数{len(records)}。缺失分片不按失败或成功填补。','', '| 条件 | 子集 | 指标 | 分子/分母 | 独立world |','| --- | --- | --- | --- | --- |']
    for m in metrics:
        if m['metric']=='Full':
            label=' / '.join(str(m[k]) for k in ['kind','producer','receiver','state','operation','b','condition','sequence_id','depth'] if k in m)
            lines.append(f'| {label} | {m["subset"]} | Full | {m["numerator"]}/{m["denominator"]} | {m["worlds"]} |')
    lines +=['',f'主对比：`{json.dumps(primary_result,ensure_ascii=False)}`。完整C0/C1/Cbridge/C2表见metrics.csv；原始字符串、token IDs、ended、解析/内容失败均在observations.jsonl.gz。','','## 结论','']
    if task['round']=='R01' or (task['round']=='R00' and task['model']=='bart'):
        counts=collections.Counter(p['category'] for p in partition);lines.append('可测失败归类：'+json.dumps(counts,ensure_ascii=False)+'。oracle canonical能力与actual桥接收益分别报告，不能将gold当算法。')
    elif primary_result['name']=='producer_receiver_interaction_I':
        lines.append('四格及I仅描述此seed与两种固定接收者；共同首步正确/字符串分层在表中。对角交互不是私有协议或唯一机制的证明。')
    else:lines.append('只有完整正确前缀集合能解释当前状态续步；少于20独立正确前缀world为小样本描述或NOT_ESTIMABLE，不扩大候选池。')
    lines+=['','## 完整性与资源','',f'新增/复用计数：{conclusion["cache_counts"]}。顶层allocation GPU-hours={run_hours:.6f}；累计{ledger["gpu_hours"]:.6f}；峰值{ledger["maximum_concurrent_gpus"]}GPU（allocation起止事件）。',f'哈希核验：{len(shards)}个原子分片通过；大文件索引artifact_index.json；日志保留local/logs。', '', '## 重跑','',f'先用新run_id/新output namespace按runs/{run_id}/manifest.json构建manifest并prepare；提交入口python -m experiments.state_handoff_diagnosis_v1.submit --round {task["round"]}。历史结果禁止覆盖；仅同科学哈希缺失分片可--resume。执行环境{PYTHON}，历史execution snapshot见job_ledger；worker用sbatch+srun。']
    report='\n'.join(lines)+'\n';text(out/'REPORT.md',report);text(ROOT/f'reports/{run_id}.md',report)
    dump(out/'receipt.json',dict(run_id=run_id,state='REPORTED',scientific_hash=task['scientific_hash'],reported_at=now()))

def collect(round_):
    with lock('collector'):
        with lock('global-GPU'):ledger=refresh()
        registry=read(ROOT/'task_registry.json')
        for r in registry['runs']:
            if r['round']!=round_:continue
            allocations=[];tasks=[]
            for sub in ledger['submissions']:
                if r['run_id'] not in sub['run_ids']:continue
                i=sub['run_ids'].index(r['run_id']);a=next((a for a in sub.get('allocations',[]) if a['array_task_id']==f'{sub["job_id"]}_{i}'),None)
                if a:allocations.append(a)
                tasks.append(next(t for t in read(sub['manifest'])['tasks'] if t['run_id']==r['run_id']))
            if not allocations or any(a['state'] not in TERMINAL for a in allocations):continue
            collect_run(tasks[-1],allocations,ledger)
            receipt=ROOT/f'runs/{r["run_id"]}/receipt.json'
            r['state']=read(receipt)['state'];print(r['run_id'],r['state'])
        dump(ROOT/'task_registry.json',registry)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--round',required=True);a=p.parse_args();collect(a.round)
