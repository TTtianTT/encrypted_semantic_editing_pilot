from mutil import *
@torch.no_grad()
def main():
 p=verify();eng,_=old.frozen_engine()
 for r in p['person']['ranks']:run_eval(eng,person_editor(r),'person','dev',f'RRR{r}')
 run_eval(eng,None,'person','dev','reencode')
 dump('results/person_dev_complete.json',dict(job_id=os.environ['SLURM_JOB_ID'],resources=eng.resources()))
if __name__=='__main__':main()
