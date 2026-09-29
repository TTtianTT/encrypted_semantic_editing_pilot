"""G6: one fixed residual reset, trained on semantically correct train stages 1-2."""
import json,sys,time,random
from pathlib import Path

import torch
import torch.nn as nn
import torch.nn.functional as F

HERE=Path(__file__).resolve().parent
V3=HERE.parent/'reference_frame_pilot_v3'
G5=HERE.parent/'projection_hypothesis_v1'
REPO=HERE.parents[1]
sys.path.insert(0,str(V3))
from common import frame,advance,render,score,digest
from engine import Engine,new_editors

CFG=json.loads((HERE/'config.json').read_text())

def readjsonl(path):return [json.loads(line) for line in path.read_text().splitlines()]
def writejson(path,obj):path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def writejsonl(path,rows):path.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows))
def pooled(h,m):return (h.float()*m[...,None]).sum(1)/m.sum(1).clamp(min=1)[:,None]
def distance(a,b):return dict(cosine=float(1-F.cosine_similarity(a[None],b[None]).item()),normalized_l2=float((a-b).norm().item()/b.norm().item()))
def graded(text,f,w,ended):
 s=score(text,f,w,ended)
 return dict(success=bool(s['joint_ok']),fact_preservation=bool(s['nondate_facts_ok']),parse_unresolved=bool(s['parse_unresolved']),decoded_semantic_state=s['parsed'],normal_end=bool(ended))

class Reset(nn.Module):
 def __init__(self,width):
  super().__init__();self.ln=nn.LayerNorm(768,elementwise_affine=False)
  self.down=nn.Linear(768,width);self.context=nn.Linear(768,width,bias=False);self.up=nn.Linear(width,768)
  nn.init.zeros_(self.up.weight);nn.init.zeros_(self.up.bias)
 def forward(self,h,m):
  z=self.ln(h);c=pooled(z,m)
  return h+self.up(F.gelu(self.down(z)+self.context(c)[:,None,:]))*m[...,None]

def collect_train(eng,ed,wlist,heldout):
 pairs=[];manifest=[];start=time.monotonic()
 for begin in range(0,len(wlist),8):
  worlds=wlist[begin:begin+8]
  for perspective in CFG['train_perspectives']:
   fs=[frame(w,CFG['train_source_offsets']['future_event' if w['record_status']=='recorded_plan' else 'completed_event'],perspective) for w in worlds]
   source=[render(w,f) for w,f in zip(worlds,fs)]
   h,m,_=eng.encode(source);previous_valid=[True]*len(worlds)
   for stage in (1,2):
    h=ed(h,m)
    texts,ended,_,_=eng.decode(h,m)
    fs=[advance(f,'T_plus') for f in fs]
    accepted=[previous_valid[i] and bool(score(texts[i],fs[i],w,ended[i])['joint_ok']) for i,w in enumerate(worlds)]
    if any(accepted):
     ids=[i for i,v in enumerate(accepted) if v]
     targets,tm,_=eng.encode([texts[i] for i in ids])
     for j,i in enumerate(ids):
      w=worlds[i]
      pairs.append((h[i].detach().cpu().half(),m[i].detach().cpu().to(torch.uint8),targets[j].detach().cpu().half(),tm[j].detach().cpu().to(torch.uint8),w['record_id'] in heldout))
      manifest.append(dict(world_id=w['record_id'],set='heldout' if w['record_id'] in heldout else 'optimization',perspective=perspective,stage=stage,source_text=source[i],decoded_text=texts[i],source_mask_length=int(m[i].sum()),target_mask_length=int(tm[j].sum()),semantic_success=True))
    previous_valid=accepted
  if (begin+len(worlds))%80==0:print('train collection',begin+len(worlds),'/',len(wlist),'accepted',len(pairs),'seconds',round(time.monotonic()-start),flush=True)
 return pairs,manifest

def loss_batch(net,pairs,ids):
 h=torch.stack([pairs[i][0] for i in ids]).cuda().float();m=torch.stack([pairs[i][1] for i in ids]).cuda().float()
 target=torch.stack([pairs[i][2] for i in ids]).cuda().float();tm=torch.stack([pairs[i][3] for i in ids]).cuda().float()
 pred=net(h,m)
 token=(((pred-target).square().mean(-1))*m).sum()/m.sum()
 pooled_loss=F.mse_loss(pooled(pred,m),pooled(target,tm))
 return token+CFG['loss']['pooled_gold_target_mse']*pooled_loss,token,pooled_loss

def train(net,pairs):
 optids=[i for i,p in enumerate(pairs) if not p[-1]];valids=[i for i,p in enumerate(pairs) if p[-1]]
 assert optids and valids
 rng=random.Random(CFG['seed']);optim=torch.optim.AdamW(net.parameters(),lr=CFG['learning_rate'],weight_decay=CFG['weight_decay'])
 history=[];net.train()
 for step in range(1,CFG['updates']+1):
  ids=rng.sample(optids,CFG['batch_size']);optim.zero_grad(set_to_none=True)
  loss,t,p=loss_batch(net,pairs,ids);loss.backward();nn.utils.clip_grad_norm_(net.parameters(),CFG['gradient_clip']);optim.step()
  if step in (1,50,100,200,300):
   net.eval()
   with torch.no_grad():
    v=[float(loss_batch(net,pairs,valids[i:i+16])[0]) for i in range(0,len(valids),16)]
   net.train();row=dict(update=step,train_loss=float(loss.detach()),train_token_mse=float(t.detach()),train_pooled_mse=float(p.detach()),heldout_imitation_loss=sum(v)/len(v));history.append(row);print('reset train',row,flush=True)
 return history,len(optids),len(valids)

@torch.no_grad()
def evaluate(eng,ed,net,g5pure,worlds,selected):
 lookup={(r['split'],r['world_id'],r['step']):r for r in g5pure};rows=[];vecs={}
 for split,ids in selected.items():
  for begin in range(0,len(ids),8):
   sub=ids[begin:begin+8];source=[lookup[split,w,1]['source_text'] for w in sub]
   current,mask,_=eng.encode(source)
   for step in range(1,6):
    edit=ed(current,mask);pretext,preend,_,_=eng.decode(edit,mask)
    oracle,om,_=eng.encode(pretext)
    reset=net(edit,mask)
    texts,ended,_,_=eng.decode(reset,mask)
    # Same latent values under the mask produced by E(D(edit)); isolates mask length.
    alttext,altend,_,_=eng.decode(reset,om)
    goldtext=[lookup[split,w,step]['gold_text'] for w in sub]
    gh,gm,_=eng.encode(goldtext)
    ep=pooled(edit,mask);rp=pooled(reset,mask);op=pooled(oracle,om);gp=pooled(gh,gm)
    residual=((edit-current)*mask[...,None]).float().norm(dim=(1,2))/mask.sum(1).sqrt()
    reset_delta=((reset-edit)*mask[...,None]).float().norm(dim=(1,2))/mask.sum(1).sqrt()
    for i,w in enumerate(sub):
     original=lookup[split,w,step];f=original['gold_frame'];world=worlds[w]
     srcids=eng.tok(source[i] if step==1 else prior[i])['input_ids']
     oracleids=eng.tok(pretext[i])['input_ids']
     row=dict(path='learned_reset',split=split,world_id=w,step=step,source_text=source[i],input_text=source[i] if step==1 else prior[i],
      decoded_text=texts[i],gold_text=goldtext[i],gold_frame=f,gold_semantic_state=original['gold_semantic_state'],
      edited_text=pretext[i],edited=graded(pretext[i],f,world,preend[i]),reset=graded(texts[i],f,world,ended[i]),
      oracle_mask_text=alttext[i],oracle_mask=graded(alttext[i],f,world,altend[i]),
      edited_distance=distance(ep[i],gp[i]),reset_distance=distance(rp[i],gp[i]),oracle_distance=distance(op[i],gp[i]),
      reset_to_oracle_distance=distance(rp[i],op[i]),residual_norm=float(residual[i]),reset_delta_norm=float(reset_delta[i]),
      input_mask_length=int(mask[i].sum()),oracle_mask_length=int(om[i].sum()),
      source_target_token_ids_equal=srcids==oracleids,source_target_mask_equal=int(mask[i].sum())==int(om[i].sum()))
     rows.append(row);vecs[f'{split}/{w}/{step}']=dict(edited=ep[i].cpu(),reset=rp[i].cpu(),oracle=op[i].cpu(),gold=gp[i].cpu())
    current=reset;prior=texts
   print('evaluation',split,begin+len(sub),'/',len(ids),flush=True)
 return rows,vecs

def main():
 started=time.monotonic();torch.manual_seed(CFG['seed']);random.seed(CFG['seed'])
 assert digest(V3/'checkpoints/G3/best.pt')==json.loads((V3/'checkpoints/locked.json').read_text())['groups']['G3']
 g5prov=json.loads((G5/'provenance.json').read_text())
 assert g5prov['checkpoint_sha256']==digest(V3/'checkpoints/G3/best.pt')
 selected=g5prov['world_ids'];assert all(len(x)==53 for x in selected.values())
 g5pure=readjsonl(G5/'pure_reset_controls.jsonl');assert len(g5pure)==530
 trainworlds=readjsonl(V3/'data/train_worlds.jsonl');assert len(trainworlds)==480
 heldout={w['record_id'] for w in trainworlds[-48:]}
 testids=set(selected['test_iid']+selected['test_template_ood']);assert not testids.intersection({w['record_id'] for w in trainworlds})
 eng=Engine();eds=new_editors();eds.load_state_dict(torch.load(V3/'checkpoints/G3/best.pt',weights_only=True));eds.eval()
 for p in eds.parameters():p.requires_grad_(False)
 ed=eds['T_plus'];pairs,manifest=collect_train(eng,ed,trainworlds,heldout)
 assert all(m['stage'] in (1,2) and m['semantic_success'] for m in manifest)
 writejsonl(HERE/'train_manifest.jsonl',manifest)
 net=Reset(CFG['reset_width']).cuda();history,ntrain,nval=train(net,pairs)
 torch.save(dict(state=net.state_dict(),architecture='residual_token_mlp_pooled_context',width=CFG['reset_width'],updates=CFG['updates'],seed=CFG['seed']),HERE/'reset.pt')
 writejson(HERE/'training.json',dict(history=history,optimization_pairs=ntrain,heldout_pairs=nval,stage_counts={str(k):sum(m['stage']==k for m in manifest) for k in (1,2)},mask_mismatch_count=sum(m['source_mask_length']!=m['target_mask_length'] for m in manifest),train_world_ids=[w['record_id'] for w in trainworlds[:-48]],heldout_world_ids=sorted(heldout)))
 del pairs;torch.cuda.empty_cache();net.eval()
 worlds={w['record_id']:w for split in selected for w in readjsonl(V3/f'data/{split}_worlds.jsonl')}
 rows,vecs=evaluate(eng,ed,net,g5pure,worlds,selected)
 assert len(rows)==530
 writejsonl(HERE/'learned_trajectories.jsonl',rows);torch.save(vecs,HERE/'pooled_representations.pt')
 writejson(HERE/'provenance.json',dict(config=CFG,g3_checkpoint_sha256=digest(V3/'checkpoints/G3/best.pt'),bart_sha256=digest(REPO/'models/bart-base/model.safetensors'),g5_provenance_sha256=digest(G5/'provenance.json'),g5_pure_sha256=digest(G5/'pure_reset_controls.jsonl'),g5_dre_sha256=digest(G5/'decode_reencode_trajectories.jsonl'),train_worlds_sha256=digest(V3/'data/train_worlds.jsonl'),test_world_files_sha256={s:digest(V3/f'data/{s}_worlds.jsonl') for s in selected},world_ids=selected,editor_training='none',editor_hyperparameter_tuning='none',reset_training_stages=[1,2],long_chain_selection='none'))
 writejson(HERE/'run_complete.json',dict(completed=True,rows=len(rows),reset_sha256=digest(HERE/'reset.pt'),trajectories_sha256=digest(HERE/'learned_trajectories.jsonl'),manifest_sha256=digest(HERE/'train_manifest.jsonl'),elapsed_seconds=time.monotonic()-started,peak_cuda_bytes=torch.cuda.max_memory_allocated()))

if __name__=='__main__':main()
