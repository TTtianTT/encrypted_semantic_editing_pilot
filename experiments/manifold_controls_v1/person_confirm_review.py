from mutil import *
import runpy
helper=runpy.run_path(str(ROOT/'summarize.py'));worldmean=helper['worldmean']
def main():
 p=verify();result=[]
 for rank in p['person']['ranks']:
  for t in (0,3):
   label=f'RRR{rank}';single=[r for path in (ROOT/'results/shards').glob(f'single_person_confirm_{label}_t{t}_*.jsonl') for r in old.stream(path)];chain=[r for path in (ROOT/'results/shards').glob(f'chain_person_confirm_{label}_t{t}_*.jsonl') for r in old.stream(path)];assert len(single)==160*6 and len(chain)==160*10
   aligned=[r for r in single if r['aligned']];out=dict(rank=rank,template=t,single=worldmean(single,lambda r:r['output']['score']['success']),supported_single=worldmean([r for r in single if (r['source_state'],r['operation']) in [(1,'plus'),(2,'minus')]],lambda r:r['output']['score']['success']),token_mse=worldmean(aligned,lambda r:r['token_mse']),paths={})
   for name in paths('person'):out['paths'][name]={f'R{k}':old.rate([r['trajectory_success'] for r in chain if r['path']==name and r['step']==k]) for k in range(1,6)}
   result.append(out)
 dump('results/person_confirmation_review.json',dict(job_id=os.environ['SLURM_JOB_ID'],gpus=0,selection_sha256=sha(ROOT/'selection.json'),rows=result));print(json.dumps([dict(rank=r['rank'],template=r['template'],supported_single=r['supported_single']['mean'],mse=r['token_mse']['mean'] if r['token_mse'] else None,forward_R5=r['paths']['person_forward']['R5']['rate'],reverse_R5=r['paths']['person_reverse']['R5']['rate']) for r in result]),flush=True)
if __name__=='__main__':main()
