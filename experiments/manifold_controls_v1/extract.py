from mutil import *
@torch.no_grad()
def main():
 verify();eng,_=old.frozen_engine();render,_,_,states,_=old.semantics()
 for domain,split in [('person','dev'),('person','confirm'),('time','confirm')]:
  for t in ((0,) if split=='dev' else (0,3)):
   for s in states(domain):
    file=f'local/{domain}_{split}_t{t}_s{s}.pt'
    if (ROOT/file).exists():continue
    ww=ws(domain,split);hh=[];mm=[]
    for lo in range(0,len(ww),16):
     h,m=eng.encode([render(w,s,t) for w in ww[lo:lo+16]]);hh.append(h.cpu());mm.append(m.cpu())
    h=torch.cat(hh);m=torch.cat(mm);n=int(m.sum(1).max());save(file,dict(h=h[:,:n].contiguous(),m=m[:,:n].contiguous(),world_ids=[w['world_id'] for w in ww]))
   print('extracted',domain,split,t,flush=True)
 # Canonical teacher forcing loss is cached per example, never batch floored.
 ww=ws('time','train');nll={}
 for s in states('time'):
  a=cache('time','train',0,s);v=[]
  for lo in range(0,len(ww),16):
   out=eng.ce(a['h'][lo:lo+16].cuda(),a['m'][lo:lo+16].cuda(),[render(w,s,0) for w in ww[lo:lo+16]])[0];v.extend(out.cpu().tolist())
  nll[s]=v
 save('local/canonical_ce.pt',nll)
 dump('results/extraction.json',dict(job_id=os.environ['SLURM_JOB_ID'],gpus=1,resources=eng.resources(),canonical_ce={str(s):float(np.mean(v)) for s,v in nll.items()}))
if __name__=='__main__':main()
