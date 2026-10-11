from mutil import *
from baseline_train import labels,Discriminator,normalization,sample_real,real_bank
@torch.no_grad()
def main():
 p=verify();eng,_=old.frozen_engine();index=int(os.environ.get('PART_INDEX','0'));tasks=[f'{n}_s{s}' for n in labels(p) for s in SEEDS][index::2];diag=[]
 for label in tasks:
  ed=baseline_editor(eng,label);run_eval(eng,ed,'time','dev',label)
  if label.startswith('adv_'):
   kind=label.split('_')[1];D=Discriminator(kind,*normalization(kind)).cuda();D.load_state_dict(load(ROOT/f'local/{label}.pt')['discriminator']);D.eval();ww=ws('time','dev');rng=random.Random(88001);bank=defaultdict(list)
   for s in old.semantics()[3]('time'):
    a=cache('time','dev',0,s)
    for i,m in enumerate(a['m']):bank[int(m.sum())].append((s,i))
   scores=[]
   for op,it in items('time','dev').items():
    for lo in range(0,len(it),16):
     part=it[lo:lo+16];h,m,_,_,_=batch('time','dev',0,part);rr=[]
     for mask in m:
      n=int(mask.sum());s,i=rng.choice(bank[n]);a=cache('time','dev',0,s);v=a['h'][i][a['m'][i].bool()];rr.append(torch.nn.functional.pad(v,(0,0,0,m.shape[1]-n)))
     a=D(torch.stack(rr).cuda(),m);b=D(ed[op](h,m),m)
     for j,(i,s,_) in enumerate(part):scores.append(dict(world_id=ww[i]['world_id'],source_state=s,operation=op,real_logit=float(a[j]),fake_logit=float(b[j]),mask_length=int(m[j].sum())))
   write(f'results/discriminator_dev_{label}.jsonl',scores)
 dump(f'results/baseline_dev_part{index}_complete.json',dict(job_id=os.environ['SLURM_JOB_ID'],tasks=tasks,resources=eng.resources()))
if __name__=='__main__':main()
