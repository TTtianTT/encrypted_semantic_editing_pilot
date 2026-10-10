"""Fixed-example TF likelihood at every historical C4 checkpoint; no updates."""
from futils import *
@torch.no_grad()
def main():
 eng,_=old.frozen_engine();render=old.semantics()[0];ww=c.worlds('eval');qs=c.bases();out=[]
 for seed in (42,43,44):
  for k in read(EX/'protocol.json')['training']['evaluation_C4_checkpoints']:
   ed=c.load_new(eng,'C4',seed,k).requires_grad_(False)
   for t in (0,3):
    for op,it in c.transition_items('eval').items():
     for lo in range(0,len(it),16):
      part=it[lo:lo+16];h,m,y,ym,ts=c.batch('eval',t,part);texts=[render(ww[i],s,t) for (i,_,_),s in zip(part,ts)];z=ed[op](h,m);nll,_=eng.ce(z,m,texts);rnll,_=eng.ce(y,ym,texts);ms=old.residual_metrics(z,m,y,ym,qs)
      for j,(i,s,_) in enumerate(part):out.append(dict(seed=seed,checkpoint=k,template=t,world_id=ww[i]['world_id'],source_state=s,operation=op,nll=float(nll[j]),canonical_nll=float(rnll[j]),**ms[j]))
   print('fixed historical likelihood',seed,k,flush=True)
 write('results/historical_c4_fixed_likelihood.jsonl',out)
 # Post-hoc cost reference, independent of model selection. Synchronized timings.
 ed=model(eng,'C3',42);fresh=ws()[:80];cost=[]
 for mode in ('latent_C3','decode_symbolic_reencode'):
  for rep in range(4):
   torch.cuda.synchronize();start=time.monotonic();current_correct=0;final_correct=0
   for lo in range(0,len(fresh),16):
    chunk=fresh[lo:lo+16];a=cache('time','eval',0,1);h=a['h'][lo:lo+len(chunk)].cuda();m=a['m'][lo:lo+len(chunk)].cuda();s=1
    for op in PATHS['aligned_from_plus_one']['operations']:
     if mode=='decode_symbolic_reencode':
      current=old.evaluate(eng,h,m,chunk,s,0);current_correct+=sum(r['score']['success'] for r in current);s=old.semantics()[2]('time',s,op);h,m=eng.encode([render(w,s,0) for w in chunk])
     else:s=old.semantics()[2]('time',s,op);h=ed[op](h,m)
    final=old.evaluate(eng,h,m,chunk,s,0);final_correct+=sum(r['score']['success'] for r in final)
   torch.cuda.synchronize();cost.append(dict(mode=mode,repetition=rep,warmup=rep==0,worlds=80,steps=5,batch=16,seconds=time.monotonic()-start,current_correct_checked=current_correct,final_correct=final_correct,includes='Start encoder cache fetch; five state updates and final decode. Reencode additionally decodes/parses current eachstep and invokes frozen encoder; controlled symbolic transform uses known world fields and state (oracle upper bound if copying ever fails). No start encoding in either mode.'))
 dump('results/compute_reference.json',cost);dump('results/historical_likelihood_complete.json',dict(training_updates=0,resources=eng.resources()))
if __name__=='__main__':main()
