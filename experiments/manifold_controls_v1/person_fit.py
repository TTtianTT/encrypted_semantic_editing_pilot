from mutil import *
def paired(split,op):
 xx=[];yy=[]
 for i,s,_ in items('person',split,True)[op]:
  target=old.semantics()[2]('person',s,op);a,b=cache('person',split,0,s),cache('person',split,0,target);n=max(a['h'].shape[1],b['h'].shape[1]);h,m=old.pad(a['h'][i:i+1],a['m'][i:i+1],n);y,ym=old.pad(b['h'][i:i+1],b['m'][i:i+1],n);assert torch.equal(m,ym);xx.append(h[m.bool()]);yy.append((y-h)[m.bool()])
 return torch.cat(xx).double(),torch.cat(yy).double()
def main():
 p=verify();sys.path.append(str(c.PRIOR));from fit import sufficient,solve,mse
 result=[];fits={}
 for op in ('plus','minus'):
  x,y=paired('train',op);dx,dy=paired('dev',op);st=sufficient(x,y);scores={};fs={}
  for ridge in p['person']['ridge_grid']:
   fs[ridge]=solve(st,ridge,p['person']['ranks'])
   for rank,fit in fs[ridge].items():
    v=mse(dx,dy,fit);scores[ridge,rank]=v;result.append(dict(operation=op,rank=rank,relative_ridge=ridge,dev_token_mse=v,train_token_mse=mse(x,y,fit)))
  for rank in p['person']['ranks']:
   ridge=min(p['person']['ridge_grid'],key=lambda l:scores[l,rank]);fits[op,rank]=fs[ridge][rank]
  print('person RRR',op,'train tokens',len(x),'dev tokens',len(dx),flush=True)
 save('local/person_fits.pt',fits);dump('results/person_ridge_selection.json',result);dump('results/person_fit_complete.json',dict(job_id=os.environ['SLURM_JOB_ID'],gpus=0,updates=0,chosen_ridge={op:{str(r):fits[op,r]['relative_ridge'] for r in p['person']['ranks']} for op in ('plus','minus')}))
if __name__=='__main__':main()
