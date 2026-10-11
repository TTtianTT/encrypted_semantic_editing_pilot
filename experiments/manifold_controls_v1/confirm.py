from mutil import *
@torch.no_grad()
def main():
 verify();eng,_=old.frozen_engine();sel=read(ROOT/'selection.json');index=int(os.environ.get('PART_INDEX','0'))
 if index==0:
  for rank in read(ROOT/'protocol.json')['person']['ranks']:run_eval(eng,person_editor(rank),'person','confirm',f'RRR{rank}',(0,3))
  run_eval(eng,None,'person','confirm','reencode',(0,3))
 if index==1:run_eval(eng,None,'time','confirm','reencode',(0,3))
 tasks=[f'{n}_s{s}' for n in sel['time']['selected_groups'] for s in SEEDS][index::2]
 for label in tasks:run_eval(eng,baseline_editor(eng,label),'time','confirm',label,(0,3))
 dump(f'results/confirmation_part{index}_complete.json',dict(job_id=os.environ['SLURM_JOB_ID'],tasks=tasks,person_ranks=index==0,resources=eng.resources(),selection_sha256=sha(ROOT/'selection.json')))
if __name__=='__main__':main()
