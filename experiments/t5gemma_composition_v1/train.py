"""Train T+ only on the G3 atomic/2-step schedule; select by atomic dev NLL."""
import json,time,random,sys
from pathlib import Path
import torch

HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from core import CFG,V3,Engine,Editor,readjsonl,writejson,frame,advance,render,digest

def main():
 torch.manual_seed(CFG['seed']);random.seed(CFG['seed'])
 eng=Engine();editor=Editor(eng.hidden,CFG['editor_rank']).cuda();optim=torch.optim.AdamW(editor.parameters(),lr=CFG['learning_rate'],weight_decay=CFG['weight_decay'])
 rows=readjsonl(V3/'data/train_G1.jsonl');worlds={w['record_id']:w for w in readjsonl(V3/'data/train_worlds.jsonl')}
 schedule=[b for b in readjsonl(V3/'data/sample_schedule.jsonl') if b['path'].startswith('T_plus')]
 assert len(schedule)==200 and all(rows[i]['operations']==['T_plus'] for b in schedule for i in b['pair_indices'])
 dev=[r for r in readjsonl(V3/'data/dev_atomic.jsonl') if r['operations']==['T_plus']]
 assert len(dev)==160
 best=float('inf');beststep=0;history=[];started=time.monotonic()
 for step in range(1,CFG['training_steps']+1):
  b=schedule[(step-1)%200];batch=[rows[i] for i in b['pair_indices']];flags=b['g2_replace'];assert len(batch)==len(flags)==16
  texts=[r['source_text'] for r in batch];x=eng.batch(texts)
  with torch.no_grad():h0=eng.model.get_encoder()(**x).last_hidden_state
  h1=editor(h0,x.attention_mask)
  l1,n1=eng.ce(h1,x.attention_mask,[r['target_text'] for r in batch])
  ids=[i for i,x in enumerate(flags) if x];assert ids
  h2=editor(h1[ids],x.attention_mask[ids])
  second=[render(worlds[batch[i]['record_id']],advance(batch[i]['frames'][-1],'T_plus')) for i in ids]
  l2,n2=eng.ce(h2,x.attention_mask[ids],second)
  loss=CFG['stage1_weight']*l1+CFG['stage2_weight']*l2
  assert torch.isfinite(loss)
  optim.zero_grad(set_to_none=True);loss.backward();assert all(p.grad is None for p in eng.model.parameters())
  torch.nn.utils.clip_grad_norm_(editor.parameters(),CFG['gradient_clip']);optim.step()
  if step in (1,10,50) or step%100==0:print('update',step,'loss',float(loss.detach()),'stage1',float(l1.detach()),'stage2',float(l2.detach()),'seconds',round(time.monotonic()-started),flush=True)
  if step%100==0:
   editor.eval();total=n=0
   with torch.no_grad():
    for j in range(0,len(dev),8):
     rs=dev[j:j+8];hh,mm=eng.encode([r['source_text'] for r in rs]);ell,tokens=eng.ce(editor(hh,mm),mm,[r['target_text'] for r in rs]);total+=float(ell)*tokens;n+=tokens
   nll=total/n;history.append(dict(update=step,dev_atomic_target_token_nll=nll,elapsed_seconds=time.monotonic()-started))
   if nll<best:
    best=nll;beststep=step;torch.save(editor.state_dict(),HERE/'editor_best.pt')
   editor.train();print('dev',history[-1],'best',beststep,flush=True)
   torch.save(dict(editor=editor.state_dict(),optimizer=optim.state_dict(),step=step),HERE/'editor_latest.pt')
 writejson(HERE/'training.json',dict(best_update=beststep,best_dev_atomic_target_token_nll=best,history=history,training_updates=CFG['training_steps'],stage2_sample_calls=3*sum(sum(b['g2_replace']) for b in schedule),source_rows=960,dev_rows=160,seed=CFG['seed'],elapsed_seconds=time.monotonic()-started,peak_cuda_bytes=torch.cuda.max_memory_allocated()))
 writejson(HERE/'training_provenance.json',dict(base_model=CFG['base_model'],local_model=CFG['local_model'],model_config_sha256=digest(eng.root/'config.json'),model_index_sha256=digest(eng.root/'model.safetensors.index.json'),tokenizer_sha256=digest(eng.root/'tokenizer.json'),train_rows_sha256=digest(V3/'data/train_G1.jsonl'),train_worlds_sha256=digest(V3/'data/train_worlds.jsonl'),schedule_sha256=digest(V3/'data/sample_schedule.jsonl'),dev_atomic_sha256=digest(V3/'data/dev_atomic.jsonl'),editor_best_sha256=digest(HERE/'editor_best.pt'),backbone_trainable_parameters=0,trained_operators=['T_plus'],long_chain_training=False))
if __name__=='__main__':main()
