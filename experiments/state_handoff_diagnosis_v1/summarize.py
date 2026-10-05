"""CPU aggregation from published per-example records."""
import gzip
from .common import *
from .metrics import *

def load_round(round_):
    registry=read(ROOT/'task_registry.json');out=[]
    for r in registry['runs']:
        if r['round']==round_:
            p=ROOT/f'runs/{r["run_id"]}/observations.jsonl.gz'
            if p.exists():out +=[json.loads(s) for s in gzip.decompress(p.read_bytes()).decode().splitlines()]
    return out

def summary_round(round_):
    records=load_round(round_);registry=read(ROOT/'task_registry.json')
    conclusions=[read(ROOT/f'runs/{r["run_id"]}/conclusion.json') for r in registry['runs'] if r['round']==round_]
    lines=[f'# {round_} summary','',f'固定run数{len(conclusions)}，状态{[c["scientific_status"] for c in conclusions]}。每run报告和push回执在runs/。','']
    summary=[]
    for model in sorted({r['model'] for r in records}):
        for seed in (42,43,44):
            rs=[r for r in records if r['model']==model and r['seed']==seed]
            for m in summarize_records(rs):summary.append(dict(model=model,seed=seed,**m))
    csv_write(ROOT/f'results/{round_}_metrics.csv',summary)
    if round_ in ('R01','R02'):
        stat=bootstrap_primary(records,round_);dump(ROOT/f'results/{round_}_primary.json',stat)
        lines +=[f'预注册主对比：{stat["estimate"]:.6f}；world-cluster5000次bootstrap95%CI={stat["ci95"]}；独立world{stat["worlds"]}，seed等权{stat["seeds"]}。',stat['limitations'],'']
    if round_=='R01':
        partition=[]
        for seed in (42,43,44):partition += [dict(seed=seed,**p) for p in failure_partition([r for r in records if r['seed']==seed])]
        csv_write(ROOT/'results/second_step_failure_partition.csv',partition)
        counts=collections.Counter((r['seed'],r['b'],r['category']) for r in partition)
        lines+=['| Seed | Second operation | Category | n |','| --- | --- | --- | --- |']+[f'| {s} | {b} | {c} | {n} |' for (s,b,c),n in sorted(counts.items())]
    if round_=='R02':
        matrix=[r for r in summary if r['kind']=='matrix'];csv_write(ROOT/'results/producer_receiver_matrix.csv',matrix)
        contrasts=[]
        for seed in (42,43,44):
            for subset in ['all','shared_first','shared_raw_exact','shared_trailing_ASCII','shared_parser_semantic']:
                g=[m for m in matrix if m['seed']==seed and m['subset']==subset and m['metric']=='Full'];v={m['producer']+m['receiver']:m['rate'] for m in g}
                formulas={'RF_minus_FF':{'RF':1,'FF':-1},'RR_minus_FR':{'RR':1,'FR':-1},'FR_minus_FF':{'FR':1,'FF':-1},'RR_minus_RF':{'RR':1,'RF':-1},'I':{'FF':1,'RR':1,'FR':-1,'RF':-1}}
                for name,f in formulas.items():contrasts.append(dict(seed=seed,subset=subset,contrast=name,estimate=sum(v[k]*s for k,s in f.items()) if all(v.get(k) is not None for k in f) else None))
        csv_write(ROOT/'results/producer_receiver_contrasts.csv',contrasts)
        lines+=['| Seed | Subset | FF | FR | RF | RR | I |','| --- | --- | --- | --- | --- | --- | --- |']
        for seed in (42,43,44):
            for subset in ['all','shared_first','shared_raw_exact']:
                g={m['producer']+m['receiver']:m for m in matrix if m['seed']==seed and m['subset']==subset and m['metric']=='Full'}
                values=[f'{g[k]["numerator"]}/{g[k]["denominator"]}' for k in ['FF','FR','RF','RR']]
                i=next(r['estimate'] for r in contrasts if r['seed']==seed and r['subset']==subset and r['contrast']=='I');lines.append('| '+' | '.join([str(seed),subset,*values,str(i)])+' |')
        lines+=['','F/F和R/R是旧现象的控制复核；直接F→R、R→F是新增。四格总体包含首步质量；共同首步正确分层不按第二步筛选。I>0不能证明私有协议。']
    if round_=='R03':
        depth=[r for r in summary if r['kind']=='depth'];csv_write(ROOT/'results/depth_handoff_profile.csv',depth)
        lines+=['正确前缀world≥20才解释兼容性；零条件分母为NOT_ESTIMABLE。前缀全错后gold修复不计完整纯链。每个depth诊断只桥接一次，互不串联。']
    if round_ in ('R01','R02'):
        natural=[r for r in summary if r['kind']=='atomic']
        target=ROOT/'results/natural_atomic_cells.csv'
        old=[]
        if target.exists():
            import csv
            old=list(csv.DictReader(target.open()))
            old=[r for r in old if r['model']!=conclusions[0]['model']]
        csv_write(target,old+natural)
    text(ROOT/f'reports/{round_}_SUMMARY.md','\n'.join(lines)+'\n')
