"""Frozen-editor G7 trajectories and pre-failure features for one backbone."""
import argparse,json,sys,time,math
from pathlib import Path

import torch
import torch.nn.functional as F
from transformers.modeling_outputs import BaseModelOutput

HERE=Path(__file__).resolve().parent
V3=HERE.parent/'reference_frame_pilot_v3'
T5=HERE.parent/'t5gemma_composition_v1'
G5=HERE.parent/'projection_hypothesis_v1'
sys.path.insert(0,str(V3))
from common import frame,advance,render,score,digest
CFG=json.loads((HERE/'config.json').read_text())

def readjsonl(p):return [json.loads(s) for s in p.read_text().splitlines()]
def writejson(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def writejsonl(p,rows):p.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows))
def cosine(a,b):return float(F.cosine_similarity(a[None],b[None]).item())

class Backbone:
 def __init__(self,name):
  self.name=name
  if name=='BART':
   from engine import Engine,new_editors
   self.eng=Engine();eds=new_editors();eds.load_state_dict(torch.load(V3/'checkpoints/G3/best.pt',weights_only=True));self.ed=eds['T_plus'].eval()
   self.checkpoint=V3/'checkpoints/G3/best.pt';self.pad_length=96
   self.kw=self.eng.kw;self.eos={self.eng.tok.eos_token_id}
  else:
   sys.path.insert(0,str(T5))
   from core import Engine,Editor
   self.eng=Engine();self.ed=Editor(self.eng.hidden,16).cuda().eval();self.ed.load_state_dict(torch.load(T5/'editor_best.pt',weights_only=True,map_location='cuda'))
   self.checkpoint=T5/'editor_best.pt';self.pad_length=128
   self.kw=dict(max_new_tokens=96,do_sample=False,num_beams=1);self.eos=self.eng.eos
  self.model=self.eng.model;self.tok=self.eng.tok
  for p in self.model.parameters():p.requires_grad_(False)
  for p in self.ed.parameters():p.requires_grad_(False)
  self.U=self.ed.u.weight.detach().float();self.V=self.ed.v.weight.detach().float()
  self.spectral=self.jacobian_spectral()
 def encode(self,texts):
  x=self.eng.encode(texts)
  return x[0],x[1]
 def apply(self,h,m):return self.ed(h,m)
 def jacobian(self,z):return z+F.linear(F.linear(z,self.V),self.U)
 def jacobian_transpose(self,z):return z+F.linear(F.linear(z,self.U.T),self.V.T)
 @torch.no_grad()
 def jacobian_spectral(self):
  gen=torch.Generator(device='cuda').manual_seed(CFG['seed']);z=torch.randn(self.U.shape[0],device='cuda',generator=gen);z=F.normalize(z,dim=0)
  for _ in range(80):z=F.normalize(self.jacobian_transpose(self.jacobian(z)),dim=0)
  return float(self.jacobian(z).norm())
 @torch.no_grad()
 def target_nll(self,h,m,texts):
  y=self.tok(texts,padding=True,truncation=False,return_tensors='pt').input_ids.cuda();valid=(y!=self.tok.pad_token_id)
  labels=y.masked_fill(~valid,-100)
  out=self.model(encoder_outputs=BaseModelOutput(last_hidden_state=h),attention_mask=m,labels=labels,use_cache=False)
  logp=F.log_softmax(out.logits.float(),dim=-1)
  per=-logp.gather(-1,y[...,None]).squeeze(-1)
  mean=(per*valid).sum(1)/valid.sum(1)
  worst=per.masked_fill(~valid,0).max(1).values
  values=[dict(target_nll=float(mean[i]),target_worst_token_nll=float(worst[i]),target_token_count=int(valid[i].sum()),target_likelihood_geomean=float(torch.exp(-mean[i]))) for i in range(len(texts))]
  del out,logp,per
  return values
 @torch.no_grad()
 def decode_scores(self,h,m):
  output=self.model.generate(encoder_outputs=BaseModelOutput(last_hidden_state=h),attention_mask=m,return_dict_in_generate=True,output_scores=True,**self.kw)
  seq=output.sequences;texts=self.tok.batch_decode(seq,skip_special_tokens=True,clean_up_tokenization_spaces=False)
  B=seq.shape[0];stop=[]
  for i in range(B):
   hits=[j for j,t in enumerate(seq[i,1:].tolist()) if t in self.eos]
   stop.append(hits[0]+1 if hits else len(output.scores))
  ent=[[] for _ in range(B)];margin=[[] for _ in range(B)];topprob=[[] for _ in range(B)]
  for j,logits in enumerate(output.scores):
   z=logits.float();lp=F.log_softmax(z,dim=-1);p=lp.exp();entropy=-torch.xlogy(p,p).sum(-1)
   tops=z.topk(2,dim=-1).values;mg=tops[:,0]-tops[:,1];tp=p.max(-1).values
   for i in range(B):
    # A forced EOS can leave only one finite candidate; it carries no margin information.
    if j<stop[i] and torch.isfinite(tops[i,1]):ent[i].append(float(entropy[i]));margin[i].append(float(mg[i]));topprob[i].append(float(tp[i]))
  metrics=[dict(output_entropy=float(sum(ent[i])/len(ent[i])) if ent[i] else None,output_top1_margin=float(sum(margin[i])/len(margin[i])) if margin[i] else None,output_top1_probability=float(sum(topprob[i])/len(topprob[i])) if topprob[i] else None,output_min_top1_margin=float(min(margin[i])) if margin[i] else None,generated_token_count=stop[i],unforced_scored_tokens=len(ent[i])) for i in range(B)]
  ended=[any(int(t) in self.eos for t in seq[i,1:]) for i in range(B)]
  return texts,ended,metrics

def geometry(h,m,g,gm):
 n1=int(m.sum());n2=int(gm.sum());n=min(n1,n2)
 x=h[:n1].float();y=g[:n2].float();xp=x.mean(0);yp=y.mean(0);a=x[:n];b=y[:n]
 gram_a=F.normalize(a,dim=-1)@F.normalize(a,dim=-1).T
 gram_b=F.normalize(b,dim=-1)@F.normalize(b,dim=-1).T
 spread_a=(a-a.mean(0)).square().sum(-1).mean();spread_b=(b-b.mean(0)).square().sum(-1).mean()
 return dict(pooled_l2=float((xp-yp).norm()/yp.norm()),pooled_cosine_distance=1-cosine(xp,yp),
  token_l2=float((a-b).norm()/b.norm()),token_cosine_distance=float((1-F.cosine_similarity(a,b,dim=-1)).mean()),
  token_gram_rms=float((gram_a-gram_b).square().mean().sqrt()),token_spread_log_ratio=float(torch.log(spread_a/spread_b)),
  active_tokens=n1,gold_tokens=n2,active_token_delta=n1-n2)

@torch.no_grad()
def main(name):
 start=time.monotonic();torch.manual_seed(CFG['seed']);base=Backbone(name)
 selected=json.loads((G5/'provenance.json').read_text())['world_ids']
 testlegacy=readjsonl(G5/'pure_reset_controls.jsonl') if name=='BART' else [r for r in readjsonl(T5/'trajectories.jsonl') if r['path']=='pure_latent']
 legacy={(r['split'],r['world_id'],r['step']):r for r in testlegacy};assert len(legacy)==530
 train=[w for w in readjsonl(V3/'data/train_worlds.jsonl') if w['record_status']=='recorded_plan']
 dev=[w for w in readjsonl(V3/'data/dev_worlds.jsonl') if w['record_status']=='recorded_plan']
 assert len(train)==160 and len(dev)==27
 worlds={s:rs for s,rs in [('train',train),('dev',dev)]}
 for split,ids in selected.items():
  index={w['record_id']:w for w in readjsonl(V3/f'data/{split}_worlds.jsonl')}
  worlds[split]=[index[w] for w in ids]
 assert not set(w['record_id'] for w in train+dev).intersection(set(sum(selected.values(),[])))
 allrows=[];agreement=[]
 for split,ws in worlds.items():
  for begin in range(0,len(ws),CFG['batch_size']):
   sub=ws[begin:begin+CFG['batch_size']];ids=[w['record_id'] for w in sub]
   source=[legacy[split,w['record_id'],1]['source_text'] if split.startswith('test_') else render(w,frame(w,1)) for w in sub]
   h,m=base.encode(source);frames=[frame(w,1) for w in sub]
   prevres=None;firstres=None;sample_rows=[[] for _ in sub]
   for k in range(1,6):
    before=h;h=base.apply(h,m);res=(h.float()-before.float())*m[...,None]
    frames=[advance(f,'T_plus') for f in frames]
    gold=[render(w,f) for w,f in zip(sub,frames)]
    if split.startswith('test_'):
     assert all(gold[i]==legacy[split,ids[i],k]['gold_text'] for i in range(len(sub)))
    gh,gm=base.encode(gold)
    teacher=base.target_nll(h,m,gold)
    decoded,ended,outstats=base.decode_scores(h,m)
    for i,w in enumerate(sub):
     rr=res[i][m[i].bool()];meanres=rr.mean(0)
     gain=float(base.jacobian(rr).norm()/rr.norm())
     prevcos=None if prevres is None else cosine(meanres,prevres[i]);firstcos=1.0 if firstres is None else cosine(meanres,firstres[i])
     info=score(decoded[i],frames[i],w,ended[i]);success=bool(info['joint_ok'])
     if split.startswith('test_'):
      old=legacy[split,w['record_id'],k];agreement.append(dict(split=split,world_id=w['record_id'],step=k,decoded_exact=decoded[i]==old['decoded_text'],success_same=success==old['edited']['success'],pooled_l2_delta=None))
     row=dict(backbone=name,split=split,world_id=w['record_id'],step=k,current_success=success,next_success=None,next_failure=None,
      decoded_text=decoded[i],gold_text=gold[i],normal_end=bool(ended[i]),fact_preservation=bool(info['nondate_facts_ok']),
      **geometry(h[i],m[i],gh[i],gm[i]),**teacher[i],**outstats[i],
      residual_norm=float(rr.norm()/m[i].sum().sqrt()),residual_previous_cosine=prevcos,residual_first_cosine=firstcos,
      jvp_residual_gain=gain,jacobian_spectral_norm=base.spectral)
     if split.startswith('test_'):agreement[-1]['pooled_l2_delta']=abs(row['pooled_l2']-legacy[split,w['record_id'],k]['edited_distance']['normalized_l2'])
     sample_rows[i].append(row)
    prevres=[res[i][m[i].bool()].mean(0).detach() for i in range(len(sub))]
    if firstres is None:firstres=prevres
   for sequence in sample_rows:
    for k,row in enumerate(sequence):
     if k<4:row['next_success']=sequence[k+1]['current_success'];row['next_failure']=not row['next_success']
    allrows.extend(sequence)
   print('completed',name,split,begin+len(sub),'/',len(ws),'seconds',round(time.monotonic()-start),flush=True)
 writejsonl(HERE/f'features_{name.lower()}.jsonl',allrows)
 writejson(HERE/f'agreement_{name.lower()}.json',dict(n=len(agreement),decoded_exact=sum(x['decoded_exact'] for x in agreement),success_same=sum(x['success_same'] for x in agreement),max_pooled_l2_delta=max((x['pooled_l2_delta'] for x in agreement),default=0),mismatches=[x for x in agreement if not x['success_same'] or x['pooled_l2_delta']>0.01][:20]))
 writejson(HERE/f'extraction_{name.lower()}.json',dict(config=CFG,backbone=name,editor_sha256=digest(base.checkpoint),g5_provenance_sha256=digest(G5/'provenance.json'),g5_pure_sha256=digest(G5/'pure_reset_controls.jsonl'),t5_trajectories_sha256=digest(T5/'trajectories.jsonl'),world_file_sha256={s:digest(V3/f'data/{s}_worlds.jsonl') for s in worlds},world_ids={s:[w['record_id'] for w in rs] for s,rs in worlds.items()},n_rows=len(allrows),jacobian_spectral_norm=base.spectral,elapsed_seconds=time.monotonic()-start,features_sha256=digest(HERE/f'features_{name.lower()}.jsonl'),editor_training='none',base_training='none'))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--backbone',choices=['BART','T5Gemma'],required=True);main(p.parse_args().backbone)
