"""Equal-update, frozen-backbone rank-16 objective controls, with exact resume."""
import random
from cutil import *

def apply_ops(ed,h,m,ops):return torch.cat([ed[op](h[i:i+1],m[i:i+1]) for i,op in enumerate(ops)])

def main():
    p=verify();cfg=p['training'];eng,_=old.frozen_engine();render,_,advance,*_=old.semantics();ws=worlds('train')
    aligned=transition_items('train',True);all_items=transition_items('train',False)
    for group in ('C1','C2','C3','C4','C5'):
     for seed in SEEDS:
      complete=ROOT/f'results/train_{group}_s{seed}_complete.json'
      if complete.exists():continue
      ed=new_editors(eng,seed,group=='C4');opt=torch.optim.AdamW(ed.parameters(),lr=cfg['lr'],weight_decay=0);rng=random.Random(seed);start=0;hist=[]
      resume=ROOT/f'local/{group}_s{seed}_latest.pt'
      if resume.exists():
        c=load(resume);ed.load_state_dict(c['editor']);opt.load_state_dict(c['optimizer']);rng.setstate(c['random']);torch.set_rng_state(c['torch_rng']);torch.cuda.set_rng_state(c['cuda_rng']);start=c['step'];hist=c['history']
      def checkpoint(step):
        c=dict(group=group,seed=seed,step=step,editor=cpu_state(ed),optimizer=opt.state_dict(),random=rng.getstate(),torch_rng=torch.get_rng_state(),cuda_rng=torch.cuda.get_rng_state(),history=hist,protocol_sha256=sha(ROOT/'protocol.json'))
        save(f'local/{group}_s{seed}_{step:04d}.pt',c);save(f'local/{group}_s{seed}_latest.pt',c)
      if not start:checkpoint(0)
      started=time.monotonic();pool=all_items if group=='C5' else aligned
      for k in range(start,cfg['updates']):
        op=('plus','minus')[k%2];items=[rng.choice(pool[op]) for _ in range(cfg['batch'])]
        # Separate generator keeps the CE batches identical for aligned C1-C4.
        nrng=random.Random(seed*100000+k);next_ops=[]
        for _,s,_ in items:
            y=advance('time',s,op);legal=[q for q in ('plus','minus') if -3<=advance_or_bound(y,q)<=3];next_ops.append(nrng.choice(legal))
        opt.zero_grad(set_to_none=True);tot={'ce':0.,'l2_normalized':0.,'kl':0.,'loss':0.}
        for lo in range(0,len(items),cfg['microbatch']):
          part=items[lo:lo+cfg['microbatch']];h,m,y,ym,targets=batch('train',0,part);edited=ed[op](h,m);chunk=[ws[i] for i,_,_ in part];texts=[render(w,s,0) for w,s in zip(chunk,targets)]
          ce=torch.zeros((),device='cuda');l2=ce;klv=ce
          if group!='C2':ce=eng.ce(edited,m,texts)[0].mean()
          if group in ('C2','C3'):l2=aligned_error(edited,m,y,ym).mean()/cfg['l2_scale'][op]
          if group=='C5':
            ns=next_ops[lo:lo+len(part)];nts=[advance('time',s,q) for s,q in zip(targets,ns)];nt=[render(w,s,0) for w,s in zip(chunk,nts)]
            with torch.no_grad():teacher,_=logits(eng,apply_ops(ed,y,ym,ns),ym,nt)
            student,labels=logits(eng,apply_ops(ed,edited,m,ns),m,nt);klv=kl(teacher,student,labels).mean()
          loss=ce+cfg['l2_weight']*l2+cfg['kl_weight']*klv
          assert torch.isfinite(loss);(loss*len(part)/len(items)).backward()
          for key,v in (('ce',ce),('l2_normalized',l2),('kl',klv),('loss',loss)):tot[key]+=float(v.detach())*len(part)/len(items)
        gn=torch.nn.utils.clip_grad_norm_(ed.parameters(),cfg['clip']);assert torch.isfinite(gn)
        assert all(x.grad is None for x in eng.model.parameters()),'Backbone must be frozen'
        opt.step();hist.append(dict(step=k+1,operation=op,gradient_norm=float(gn),**tot))
        if k+1 in cfg['checkpoints']:
          checkpoint(k+1);write(f'results/train_{group}_s{seed}.jsonl',hist);print('train',group,seed,k+1,tot,flush=True)
      dump(f'results/train_{group}_s{seed}_complete.json',dict(group=group,seed=seed,updates=cfg['updates'],examples=cfg['updates']*cfg['batch'],new_run_seconds=time.monotonic()-started,resources=eng.resources(),final_sha256=sha(ROOT/f'local/{group}_s{seed}_{cfg["updates"]:04d}.pt'),protocol_sha256=sha(ROOT/'protocol.json')))
      del ed,opt
    dump('results/training_complete.json',dict(total_updates=15*cfg['updates'],resources=eng.resources(),protocol_sha256=sha(ROOT/'protocol.json')))

def advance_or_bound(s,op):return s-1 if op=='plus' else s+1

if __name__=='__main__':main()
