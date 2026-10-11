"""Inspect completed person development panel, without reading confirmation."""
from mutil import *
import runpy
metric=runpy.run_path(str(ROOT/'select.py'))['metric']
def main():
 p=verify();fits=load(ROOT/'local/person_fits.pt');ss=[]
 for rank in p['person']['ranks']:
  v=metric('person',f'RRR{rank}');ss.append(dict(rank=rank,**v,operators={op:dict(effective_rank=fits[op,rank]['effective_rank'],relative_ridge=fits[op,rank]['relative_ridge'],training_tokens=fits[op,rank]['training_tokens'],singular_values=fits[op,rank]['singular_values']) for op in ('plus','minus')}))
 dump('results/person_dev_review.json',dict(job_id=os.environ['SLURM_JOB_ID'],gpus=0,confirmation_consulted=False,ranks=ss));print(json.dumps([{k:r[k] for k in ('rank','R5','single','aligned_token_mse')} for r in ss]),flush=True)
if __name__=='__main__':main()
