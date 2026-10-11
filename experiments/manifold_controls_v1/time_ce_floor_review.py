from mutil import *
import runpy
worldmean=runpy.run_path(str(ROOT/'summarize.py'))['worldmean']
def main():
 verify();rs=[]
 for group in ('CE_all','floor'):
  for seed in SEEDS:
   for t in (0,3):
    label=f'{group}_s{seed}';single=[r for path in (ROOT/'results/shards').glob(f'single_time_confirm_{label}_t{t}_*.jsonl') for r in old.stream(path)];chain=[r for path in (ROOT/'results/shards').glob(f'chain_time_confirm_{label}_t{t}_*.jsonl') for r in old.stream(path)];assert len(single)==160*12 and len(chain)==160*20
    aligned=[r for r in single if r['aligned']];rr=dict(group=group,seed=seed,template=t,single=worldmean(single,lambda r:r['output']['score']['success']),preserved=worldmean(single,lambda r:r['output']['score']['preserved']),token_mse=worldmean(aligned,lambda r:r['token_mse']),paths={})
    for path in paths('time'):rr['paths'][path]={f'R{k}':old.rate([r['trajectory_success'] for r in chain if r['path']==path and r['step']==k]) for k in range(1,6)}
    rs.append(rr)
 dump('results/time_ce_floor_review.json',dict(job_id=os.environ['SLURM_JOB_ID'],gpus=0,rows=rs));print(json.dumps([dict(group=r['group'],seed=r['seed'],template=r['template'],single=r['single']['mean'],mse=r['token_mse']['mean'],R5=r['paths']['aligned_from_plus_one']['R5']['rate']) for r in rs]),flush=True)
if __name__=='__main__':main()
