"""Fresh historical-match repair/injection with train-only PCA and fixed direction."""
from futils import *
@torch.no_grad()
def main():
 verify();eng,_=old.frozen_engine();render=old.semantics()[0];ww=ws()[:80];rr=[]
 for seed in SEEDS:
  ed=model(eng,'C1',seed);q=load(ROOT/f'local/mechanism_S_s{seed}.pt')['q'].cuda();vv=ed['plus'].v.weight.double();_,_,vh=torch.linalg.svd(vv,full_matrices=False);rq=vh[:16].T.float()
  for t in (0,3):
   for lo in range(0,len(ww),16):
    file=f'results/shards/fresh_mechanism_s{seed}_t{t}_{lo:03d}.jsonl'
    if (ROOT/file).exists():continue
    chunk=ww[lo:lo+16];hi=lo+len(chunk);a=cache('time','eval',t,1);b=cache('time','eval',t,0);n=max(a['h'].shape[1],b['h'].shape[1]);ah,am=old.pad(a['h'][lo:hi].cuda(),a['m'][lo:hi].cuda(),n);bh,bm=old.pad(b['h'][lo:hi].cuda(),b['m'][lo:hi].cuda(),n);assert torch.equal(am,bm)
    bad=ed['plus'](ah,am);e=(bad-bh)*am[...,None];es=(e@q)@q.T;sr=(es@rq)@rq.T;sp=es-sr;gen=torch.Generator(device='cuda').manual_seed(91001+seed*100+lo+t);rand=torch.randn(es.shape,device='cuda',generator=gen)*am[...,None];rand=rand/rand.flatten(1).norm(dim=1)[:,None,None]*es.flatten(1).norm(dim=1)[:,None,None]
    curbad=old.evaluate(eng,bad,am,chunk,0,t);nextbad=old.evaluate(eng,ed['plus'](bad,am),am,chunk,-1,t);curgood=old.evaluate(eng,bh,bm,chunk,0,t);nextgood=old.evaluate(eng,ed['plus'](bh,bm),bm,chunk,-1,t)
    prebase,labels=c.logits(eng,bh,bm,[render(w,0,t) for w in chunk]);prechanged,_=c.logits(eng,bh+sp,bm,[render(w,0,t) for w in chunk]);vpre=c.kl(prebase,prechanged,labels)
    postbase,labels=c.logits(eng,ed['plus'](bh,bm),bm,[render(w,-1,t) for w in chunk]);postchanged,_=c.logits(eng,ed['plus'](bh,bm)+sp,bm,[render(w,-1,t) for w in chunk]);vpost=c.kl(postbase,postchanged,labels)
    for kind,base,sign in [('repair',bad,-1),('inject',bh,1)]:
     for component,delta in [('none',torch.zeros_like(e)),('full',e),('S',es),('S_R',sr),('S_perp',sp),('random_S_norm',rand)]:
      z=base+sign*delta;cur=old.evaluate(eng,z,am,chunk,0,t);nxt=old.evaluate(eng,ed['plus'](z,am),am,chunk,-1,t)
      for i,w in enumerate(chunk):
       eligible=curbad[i]['score']['success'] and not nextbad[i]['score']['success'] and curgood[i]['score']['success'] and nextgood[i]['score']['success'];rr.append(dict(seed=seed,template=t,world_id=w['world_id'],kind=kind,component=component,eligible=eligible,current_baseline=curbad[i] if kind=='repair' else curgood[i],next_baseline=nextbad[i] if kind=='repair' else nextgood[i],current=cur[i],next=nxt[i],delta_norm=float(delta[i].norm()),KL_pre_S_perp=float(vpre[i]),KL_post_S_perp=float(vpost[i])))
    write(file,rr);rr=[]
   print('fresh mechanism',seed,t,flush=True)
 write('results/fresh_mechanism.jsonl',(r for f in sorted((ROOT/'results/shards').glob('fresh_mechanism_*.jsonl')) for r in old.stream(f)));dump('results/fresh_mechanism_complete.json',dict(resources=eng.resources(),protocol_sha256=sha(ROOT/'protocol.json')))
if __name__=='__main__':main()
