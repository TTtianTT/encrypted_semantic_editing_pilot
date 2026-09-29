import copy,torch
from common import *
from engine import Engine,new_editors,tensorhash

def validate(eng):
 rows=read('data/train_G1.jsonl');worlds={w['record_id']:w for w in read('data/train_worlds.jsonl')};b=next(b for b in read('data/sample_schedule.jsonl') if 0<sum(b['g2_replace'])<16)
 rs=[copy.deepcopy(rows[i]) for i in b['pair_indices']];flags=b['g2_replace'];terminal=copy.deepcopy(rs)
 for r,flag in zip(terminal,flags):
  if flag:r['target_text']=render(worlds[r['record_id']],advance(r['frames'][-1],'T_plus'))
 results=[]
 for source in [ROOT/'checkpoints/initial.pt',V2/'checkpoints/G2/best.pt']:
  eds=new_editors();eds.load_state_dict(torch.load(source,weights_only=True));eds.zero_grad(set_to_none=True)
  ref,nt,_=eng.loss(eds,terminal,flags);ref.backward();grads={n:p.grad.clone() for n,p in eds.named_parameters() if p.grad is not None}
  eds.zero_grad(set_to_none=True);new,stats=eng.stage_loss(eds,rs,flags,worlds,0.,1.);new.backward()
  errors={n:float((p.grad-grads[n]).abs().max()) for n,p in eds.named_parameters() if p.grad is not None};rel={n:float((p.grad-grads[n]).norm()/(grads[n].norm()+1e-10)) for n,p in eds.named_parameters() if p.grad is not None}
  assert torch.allclose(ref,new,rtol=1e-5,atol=1e-6),(ref.item(),new.item())
  for n,p in eds.named_parameters():
   if n in grads:assert torch.allclose(p.grad,grads[n],rtol=2e-4,atol=2e-6),(n,errors[n],rel[n])
  eds.zero_grad(set_to_none=True);formal,stats,first,second=eng.stage_loss(eds,rs,flags,worlds,return_parts=True)
  params=list(eds['T_plus'].parameters());g1=torch.autograd.grad(first,params,retain_graph=True);g2=torch.autograd.grad(second,params,retain_graph=True)
  norms=[float(torch.sqrt(sum((g*g).sum() for g in gs))) for gs in [g1,g2]];assert all(v>0 and v<float('inf') for v in norms)
  formal.backward();assert all(p.grad is None and not p.requires_grad for p in eng.model.parameters());assert not eng.model.training
  x=eng.batch([r['source_text'] for r in rs]);h,mask,_=eng.encode([r['source_text'] for r in rs]);h_again,_,_=eng.encode([r['source_text'] for r in rs]);assert torch.equal(h,h_again)
  edited=eds['T_plus'](h,mask);assert torch.equal(edited[mask==0],h[mask==0]);assert torch.equal(mask,x.attention_mask)
  for a,z,flag in zip(rs,terminal,flags):
   assert score(a['target_text'],a['frames'][-1],worlds[a['record_id']])['joint_ok']
   if flag:assert score(z['target_text'],advance(a['frames'][-1],'T_plus'),worlds[a['record_id']])['joint_ok']
  results.append(dict(state=str(source.relative_to(REPO)),reference_loss=ref.item(),zero_one_loss=new.item(),max_gradient_errors=errors,relative_gradient_errors=rel,stage_gradient_norms=norms,formal_loss=formal.item(),stats=stats))
 dump('calibration/implementation_check.json',{'passed':True,'mixed_batch_step':b['step'],'chain_N':sum(flags),'ordinary_N':16-sum(flags),'results':results,'bart_gradient_none':True,'deterministic_eval':True,'padding_unchanged':True,'restored_coefficients':[.5,.5]})
 print('VALIDATION PASSED',flush=True)
if __name__=='__main__':validate(Engine())
