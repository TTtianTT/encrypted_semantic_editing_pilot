import time,copy
from engine import *
def main():
 assert_lock();be=Backend(NAME);rows=read('data/train_joint.jsonl')[:4];texts=[r['source_text'] for r in rows];targets=[r['target_text'] for r in rows];h,m,_=be.encode(texts);hagain,_,_=be.encode(texts);assert torch.equal(h,hagain)
 baseline,_=be.generate(h,m);proof=[];bench={}
 for rank in [16,32]:
  ed=new_joint(be.d,rank);assert sum(p.numel() for p in ed.parameters())==(2*rank+1)*be.d
  original=copy.deepcopy(ed.state_dict());j=ed(h,m);assert torch.equal(h,j);out,_=be.generate(j,m);assert out==baseline
  j.retain_grad();ce,n=be.token_ce(j,m,targets);loss=(ce*n).sum()/n.sum();loss.backward();assert torch.isfinite(j.grad).all() and j.grad.norm()>0
  grads={k:float(p.grad.norm()) for k,p in ed.named_parameters() if p.grad is not None};assert grads['u.weight']>0 and all(torch.isfinite(p.grad).all() for p in ed.parameters() if p.grad is not None);assert all(p.grad is None for p in be.model.parameters())
  with torch.no_grad():ed.b.fill_(.1);ed.u.weight.fill_(.01);z=ed(h,m);assert torch.equal(z[m==0],h[m==0]) and not torch.equal(z[m.bool()],h[m.bool()])
  ed.load_state_dict(original);ed.zero_grad(set_to_none=True);start=time.monotonic()
  for i in range(4):
   hh,mm,_=be.encode(texts);ce,n=be.token_ce(ed(hh,mm),mm,targets);((ce*n).sum()/n.sum()).backward()
  torch.cuda.synchronize();secs=time.monotonic()-start;bench[str(rank)]=secs*600*1.5
  torch.save(original,ROOT/f'checkpoints/initial_rank{rank}.pt');proof.append(dict(rank=rank,parameters=sum(p.numel() for p in ed.parameters()),hidden_gradient_norm=float(j.grad.norm()),editor_gradient_norms=grads,padding_check_nonzero_residual=True,zero_edit_identical=True,backbone_gradients_none=True,backbone_frozen=all(not p.requires_grad for p in be.model.parameters()),initial_hash=digest(ROOT/f'checkpoints/initial_rank{rank}.pt'),initial_tensor_hash=tensorhash(original),estimated_training_seconds=bench[str(rank)]))
 eds=old_editors(be);archive=read(CROSS/f'outputs/{NAME}/G1.jsonl');matches=[];start=time.monotonic()
 for path,order in [('plus_person','T_then_P'),('person_plus','P_then_T')]:
  rr=[r for r in archive if r['path']==path and r['mode']=='latent_chain' and r['split']=='test_iid'][:16];ss,_,_=be.infer([r['source_text'] for r in rr],eds,ORDERS[order])
  for r,s in zip(rr,ss):matches.append(dict(row_id=r['row_id'],order=order,exact=[x['output'] for x in s]==[x['output'] for x in r['steps']]))
 assert all(r['exact'] for r in matches);evaluation_estimate=(time.monotonic()-start)/64*1600*1.5
 folds=[]
 with torch.no_grad():
  for order,(a,b) in ORDERS.items():
   folded=fold(eds[a],eds[b],be.d);seq=eds[b](eds[a](h,m),m);one=folded(h,m);delta=(seq-one)[m.bool()];folds.append(dict(order=order,max_abs=float(delta.abs().max()),relative_l2=float(delta.norm()/seq[m.bool()].norm())));assert torch.isfinite(delta).all() and folds[-1]['relative_l2']<1e-4
 dump('calibration/interface_check.json',dict(passed=True,deterministic=True,model=NAME,ranks=proof,archive_matches=matches,fold_checks=folds,evaluation_reserve_seconds=evaluation_estimate,training_estimates=bench,planned_remaining_estimate=sum(bench.values())+evaluation_estimate,optimizer_updates=0))
 print('PREFLIGHT PASSED',bench,'evaluation reserve',evaluation_estimate,flush=True)
if __name__=='__main__':main()
