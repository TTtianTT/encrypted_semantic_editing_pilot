"""Slurm-only validation of all selected editors on their own latent states."""
import time
import torch
from .common import *
from .engine import editors,render,advance


@torch.no_grad()
def run(eng,folder):
    seed=eng.task['seed'];lock=read(ROOT/'configs/FINAL_METHOD_CHECKPOINT_LOCK.json')
    selected=[r for r in lock['checkpoints'] if r['seed']==seed]
    assert {r['method'] for r in selected}=={'Plain','Output-only','Mechanism-guided','Random-site'}
    models={}
    for item in selected:
        assert sha(item['path'])==item['sha256']
        ed=editors(eng.d,seed);ed.load_state_dict(torch.load(item['path'],map_location='cuda',weights_only=False)['editor']);ed.eval();models[item['method']]=ed
    worlds=[w for w in rows(ROOT/'configs/worlds.jsonl') if w['split']=='validation']
    reuse=next(r for r in read(ROOT/'configs/S3_REUSE_LOCK.json')['entries'] if r['seed']==seed)
    plain=next(r for r in selected if r['method']=='Plain')
    assert plain['sha256']==reuse['checkpoint_sha256'], 'Reused Plain trajectories require unchanged checkpoint'
    old=read(ROOT/'manifests/S3_VALIDATION_TRAJECTORIES.json');oldfolder=Path(old['output_root'])/f'bart_s{seed}'
    sequences=[['plus','minus','plus','minus','plus'],['plus','plus','minus','minus','plus']]
    tracks=[];bench=[]
    for wi,w in enumerate(worlds):
        path=folder/(w['world_id']+'_trajectories.jsonl');marker=folder/(w['world_id']+'_COMPLETE.json')
        benchmark_path=folder/(w['world_id']+'_benchmark.jsonl')
        if marker.exists():
            tracks.extend(rows(path))
            if benchmark_path.exists():bench.extend(rows(benchmark_path))
            continue
        source=reuse['source_worlds'][w['world_id']];assert sha(source['path'])==source['sha256']
        cache=torch.load(source['path'],map_location='cpu',weights_only=False)
        r=cache[(w['world_id'],0,'natural')];h0=r['hidden'][None].cuda();mask=r['mask'][None].cuda()
        # Existing Original/Plain tracks use identical H and unchanged checkpoints.
        previous_path=oldfolder/(w['world_id']+'_trajectories.jsonl')
        indexed=next(x for x in read(oldfolder/'RUN_STATUS.json')['artifacts'] if x['path']==str(previous_path))
        assert sha(previous_path)==indexed['sha256']
        chains=rows(previous_path)
        assert {r['method'] for r in chains}=={'Original','Plain'} and len(chains)==8
        for order,sequence in enumerate(sequences):
            for direction in ('forward','inverse'):
                ops=sequence if direction=='forward' else ['minus' if op=='plus' else 'plus' for op in sequence]
                for method in ('Output-only','Mechanism-guided','Random-site'):
                    h=h0.clone();state=0;steps=[]
                    for step,op in enumerate(ops,1):
                        state=advance('time',state,op);h=models[method][op](h,mask);pred=eng.evaluate(h,mask,w,state)
                        steps.append(dict(step=step,operation=op,state=state,prediction=pred))
                    chains.append(dict(world_id=w['world_id'],split='validation',seed=seed,method=method,source='natural_start',order=order,direction=direction,steps=steps,length_success={str(n):all(s['prediction']['score']['success'] for s in steps[:n]) for n in (1,2,3,5)},latent_only=True,gold_state_replacements=0,donor_used=False))
        jsonl(path,chains);tracks.extend(chains);world_bench=[]
        # Fixed 8-world benchmark, all methods, both sources/ops, five repeats.
        if wi<8:
            for source_name in ('natural','history'):
                cr=cache[(w['world_id'],0,source_name)];hh=cr['hidden'][None].cuda();mm=cr['mask'][None].cuda()
                for method in ('Plain','Output-only','Mechanism-guided','Random-site'):
                    for op in ('plus','minus'):
                        measurements=[]
                        for repeat in range(6):
                            start=torch.cuda.Event(enable_timing=True);end=torch.cuda.Event(enable_timing=True)
                            start.record();hp=models[method][op](hh,mm);end.record();torch.cuda.synchronize()
                            editor_ms=start.elapsed_time(end);begin=time.perf_counter();p=eng.evaluate(hp,mm,w,advance('time',0,op));decode_ms=(time.perf_counter()-begin)*1000
                            if repeat:measurements.append(dict(editor_GPU_ms=editor_ms,decode_and_score_wall_ms=decode_ms))
                        world_bench.append(dict(world_id=w['world_id'],seed=seed,source=source_name,method=method,operation=op,measurements=measurements,editor_parameters=sum(p.numel() for p in models[method].parameters()),donor_used=False,test_time_backward=False))
        if world_bench:jsonl(benchmark_path,world_bench);bench.extend(world_bench)
        dump(marker,dict(world_id=w['world_id'],completed=True))
        if (wi+1)%8==0:print('selected validation trajectories',seed,wi+1,flush=True)
    jsonl(folder/'inference_benchmark.jsonl',bench)
    summary=[]
    for method in ('Original','Plain','Output-only','Mechanism-guided','Random-site'):
        rs=[r for r in tracks if r['method']==method];assert len(rs)==256
        for length in (1,2,3,5):
            summary.append(dict(method=method,length=length,complete_numerator=sum(r['length_success'][str(length)] for r in rs),trajectory_denominator=256,worlds=64))
    return dict(passed=True,worlds=64,seed=seed,trajectories=summary,scientific_scope='EXPLORATORY_VALIDATION_ONLY',test_accessed=0,old_Original_Plain_reused=True,own_latent_states=True,inference_benchmark_records=len(bench),resources=eng.resources())
