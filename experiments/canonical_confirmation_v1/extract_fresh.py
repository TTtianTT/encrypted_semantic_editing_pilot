"""One frozen extraction of prospectively generated confirmation worlds."""
from futils import *
@torch.no_grad()
def main():
 verify();eng,_=old.frozen_engine();render,_,_,states,_=old.semantics()
 for domain,split,templates in [('time','eval',[0,3]),('person','train',[0]),('person','eval',[0,3])]:
  ww=ws(domain,split)
  for t in templates:
   for s in states(domain):
    file=f'local/{domain}_{split}_t{t}_s{s}.pt'
    if (ROOT/file).exists():continue
    hh=[];mm=[]
    for lo in range(0,len(ww),16):
     h,m=eng.encode([render(w,s,t) for w in ww[lo:lo+16]]);hh.append(h.cpu());mm.append(m.cpu())
    h=torch.cat(hh);m=torch.cat(mm);n=int(m.sum(1).max());save(file,dict(h=h[:,:n].contiguous(),m=m[:,:n].contiguous(),state=s,template=t,world_ids=[w['world_id'] for w in ww]))
   print('extracted',domain,split,t,flush=True)
 # Person RRR16 uses only mask-identical train edges, fixed ridge from time study.
 sys.path.append(str(c.PRIOR));from fit import sufficient,solve
 ff={};scale={};coverage={}
 for op,it in items('person').items():
  xs=[];ys=[]
  for i,s,_ in it:
   y=old.semantics()[2]('person',s,op);a,b=cache('person','train',0,s),cache('person','train',0,y);n=max(a['h'].shape[1],b['h'].shape[1]);h,m=old.pad(a['h'][i:i+1],a['m'][i:i+1],n);g,gm=old.pad(b['h'][i:i+1],b['m'][i:i+1],n);assert torch.equal(m,gm);valid=m.bool();xs.append(h[valid]);ys.append((g-h)[valid])
  x=torch.cat(xs).double();y=torch.cat(ys).double();ff[op]=solve(sufficient(x,y),.0001,[16])[16];scale[op]=float(y.square().mean());coverage[op]=dict(items=len(it),source_counts={str(s):sum(v[1]==s for v in it) for s in states('person')},tokens=len(x))
 save('local/person_rrr.pt',ff);dump('results/person_fit.json',dict(relative_ridge=.0001,scale=scale,coverage=coverage,selection='Inherited fixed ridge, not selected on person evaluation',fit_sha256=sha(ROOT/'local/person_rrr.pt')))
 dump('results/extraction_complete.json',dict(resources=eng.resources(),cache_hashes={p.name:sha(p) for p in (ROOT/'local').glob('*_t*_s*.pt')}))
if __name__=='__main__':main()
