"""Finite Stage B: future+passive held out, present+passive seen constraint.
Seed42 only, fixed rank64, no B hyperparameter tuning; independent new operators.
"""
import json,time,random,hashlib,os,collections
from pathlib import Path
import torch,numpy as np
from torch import nn
from transformers.modeling_outputs import BaseModelOutput
from pilot import ROOT,Runner,Editor,seed,dump
from evaluate import evaluate,features,doc,norm
D=ROOT/'data/b';O=ROOT/'results/b';O.mkdir(exist_ok=True)
CFG={'seed':42,'rank':64,'steps':600,'batch':8,'lr':.001,'heldout':'future+passive','train_combo':'present+passive','order':'passive then tense','constraint':'0.5 primitive CE +0.5 seen-combination CE; no commutativity loss','three_operations':['future','present','passive']};CH=hashlib.sha256(json.dumps(CFG,sort_keys=True).encode()).hexdigest()
def read(name):return [json.loads(s) for s in (D/(name+'.jsonl')).read_text().splitlines()]
def facts(s):
 d=doc(s);a=features(s)
 # Voice may reorder syntax and add auxiliary be/by. Compare semantic lexical
 # multiset plus root agent/patient heads, not A's ordered lemma sequence.
 lex=collections.Counter(t.lemma_.lower() for t in d if not t.is_punct and not t.is_space and t.pos_!='AUX' and not(t.lower_=='by' and t.dep_=='agent'))
 root=next((t for t in d if t.dep_=='ROOT'),None);roles={}
 if root is not None:
  roles['event']=root.lemma_.lower()
  for c in root.children:
   if c.dep_ in {'nsubj','csubj'}:roles['agent']=c.lemma_.lower()
   if c.dep_ in {'dobj','obj','nsubjpass','csubjpass'}:roles['patient']=c.lemma_.lower()
   if c.dep_=='agent':
    for t in c.children:
     if t.dep_=='pobj':roles['agent']=t.lemma_.lower()
 return lex,roles,a

def metrics(src,out,ref,eos):
 base=evaluate(src,out,ref,eos);a,ra,fa=facts(src);b,rb,fb=facts(out)
 passive=any(t.dep_ in {'auxpass','nsubjpass','csubjpass'} for t in doc(out))
 content=a==b and ra==rb and all(collections.Counter(fa[k])==collections.Counter(fb[k]) for k in ['entities','numbers','dates','negation'])
 base.update(passive_auto=passive,future_auto=fb['future'],content_auto=content,root_roles_preserved_auto=ra==rb,lexical_bag_preserved_auto=a==b,Joint_auto=bool(passive and fb['future'] and content and base['valid_auto']))
 return base
class Composition(nn.Module):
 def __init__(self,eds,tense='future'):super().__init__();self.eds=eds;self.tense=tense
 def forward(self,z,m):return self.eds[self.tense](self.eds['passive'](z,m),m)

def main():
 start=time.monotonic();r=Runner();train={op:read('train_'+op) for op in ['future','present','passive','seen_combo']};dev=read('dev_future')+read('dev_passive');r.train=train['future']+train['present']+train['passive'];r.dev=dev
 # Domain reconstruction check, same A automatic content criterion for identity.
 identity=Editor('identity').cuda();zero=r.generate(identity,dev,'B_identity_dev',42,O/'dev_identity.jsonl')
 rate=np.mean([x['metrics']['content_auto'] for x in zero]);invalid=np.mean([not x['metrics']['valid_auto'] for x in zero])
 dump(O/'representation.json',{'n':len(zero),'content_auto':float(rate),'invalid_auto':float(invalid),'exact_reconstruction':float(np.mean([x['metrics']['exact_reconstruction'] for x in zero])),'repair':False})
 if rate<.9 or invalid>.05:
  dump(O/'blocked.json',{'reason':'B-domain reconstruction gate failed; no composition inference claim. A model remains frozen. Controlled B repair not performed in finite extension.'});return
 fits={};allmeta=[]
 for scheme,kind in [('vector_add','shift'),('independent_lowrank','lowrank_affine'),('composition_trained_lowrank','lowrank_affine')]:
  seed(42);eds=nn.ModuleDict({op:Editor(kind,r=64).cuda() for op in ['future','present','passive']});directory=ROOT/'checkpoints/b'/scheme;directory.mkdir(parents=True,exist_ok=True);path=directory/'final.pt';mdpath=directory/'complete.json'
  if path.exists() and mdpath.exists():eds.load_state_dict(torch.load(path,weights_only=True));fits[scheme]=eds;allmeta.append(json.load(open(mdpath)));continue
  opt=torch.optim.AdamW(eds.parameters(),lr=.001,weight_decay=0);rng=np.random.default_rng(42);t=time.monotonic();history=[];begin=0
  latest=directory/'latest.pt'
  if latest.exists():
   ck=torch.load(latest,weights_only=False);eds.load_state_dict(ck['editor']);opt.load_state_dict(ck['opt']);begin=ck['step'];rng.bit_generator.state=ck['rng']
  for step in range(begin,600):
   op=['future','present','passive'][step%3];rr=[train[op][i] for i in rng.integers(0,len(train[op]),size=8)];opt.zero_grad(set_to_none=True);loss,_=r.loss(eds[op],rr)
   if scheme=='composition_trained_lowrank':
    cr=[train['seen_combo'][i] for i in rng.integers(0,len(train['seen_combo']),size=8)];cl,_=r.loss(Composition(eds,'present'),cr);loss=.5*loss+.5*cl
   loss.backward();assert all(p.grad is None for p in r.model.parameters());torch.nn.utils.clip_grad_norm_(eds.parameters(),1.);opt.step()
   if (step+1)%100==0:
    print('B fit',scheme,step+1,loss.item(),flush=True);history.append({'step':step+1,'loss':loss.item()});torch.save({'editor':eds.state_dict(),'opt':opt.state_dict(),'step':step+1,'rng':rng.bit_generator.state},latest)
  torch.save(eds.state_dict(),path);md={'scheme':scheme,'parameters':sum(p.numel() for p in eds.parameters()),'steps':600,'single_examples':4800,'extra_seen_combo_examples':4800 if scheme=='composition_trained_lowrank' else 0,'elapsed_s':time.monotonic()-t,'history':history};dump(mdpath,md);allmeta.append(md);fits[scheme]=eds
 dump(O/'frozen_config.json',{'config':CFG,'config_hash':CH,'fit':allmeta})
 test=read('test_heldout_combo');summary=[]
 # Domain identity test included; test only opened after all B fits frozen.
 r.generate(identity,test,'B_identity_test',42,O/'test_identity.jsonl')
 for scheme,eds in fits.items():
  for pathkind in ['latent_once','decode_reencode']:
   outpath=O/f'{scheme}_{pathkind}.jsonl';records=[]
   if outpath.exists():records=[json.loads(x) for x in outpath.read_text().splitlines()]
   else:
    with outpath.open('w') as f:
     for i in range(0,len(test),8):
      batch=test[i:i+8];x,_=r.batch(batch);torch.cuda.synchronize();t=time.perf_counter()
      with torch.no_grad():
       z=r.model.get_encoder()(**x).last_hidden_state;zm=eds['passive'](z,x.attention_mask);intermediate=['']*len(batch)
       if pathkind=='decode_reencode':
        mid=r.model.generate(encoder_outputs=BaseModelOutput(last_hidden_state=zm),attention_mask=x.attention_mask,do_sample=False,num_beams=1,max_new_tokens=100,forced_eos_token_id=None)
        intermediate=r.tok.batch_decode(mid,skip_special_tokens=True,clean_up_tokenization_spaces=False)
        lens=[len(r.tok(s)['input_ids']) for s in intermediate]
        if max(lens)>96:
         # No silent truncation; mark complete batch as path failure.
         texts=['']*len(batch);eos=[False]*len(batch);g=None
        else:
         x=r.tok(intermediate,padding='max_length',max_length=96,truncation=False,return_tensors='pt').to('cuda');zm=r.model.get_encoder()(**x).last_hidden_state;g=True
       else:g=True
       if g is not None:
        z2=eds['future'](zm,x.attention_mask);g=r.model.generate(encoder_outputs=BaseModelOutput(last_hidden_state=z2),attention_mask=x.attention_mask,do_sample=False,num_beams=1,max_new_tokens=100,forced_eos_token_id=None);texts=r.tok.batch_decode(g,skip_special_tokens=True,clean_up_tokenization_spaces=False);eos=[bool((v[1:]==r.tok.eos_token_id).any()) for v in g]
      torch.cuda.synchronize();elapsed=time.perf_counter()-t
      for row,out,e,mid in zip(batch,texts,eos,intermediate):
       rr={**row,'method':scheme,'path':pathkind,'seed':42,'config_hash':CH,'output':out,'intermediate':mid,'metrics':metrics(row['input'],out,row['reference'],e),'timing_s':{'total':elapsed/len(batch)}};f.write(json.dumps(rr)+'\n');f.flush();records.append(rr)
   assert len(records)==len(test)
   summary.append({'scheme':scheme,'path':pathkind,'n':len(records),'joint_n':sum(x['metrics']['Joint_auto'] for x in records),**{k:float(np.mean([x['metrics'][k] for x in records])) for k in ['Joint_auto','content_auto','future_auto','passive_auto','valid_auto','reference_chrf']},'seconds_per_source':float(np.mean([x['timing_s']['total'] for x in records]))})
 # Single-passive generation on same held-out source for added content drift.
 for scheme,eds in fits.items():
  raw=r.generate(eds['passive'],test,'B_single_passive_'+scheme,42,O/f'single_passive_{scheme}.jsonl',64)
  single=float(np.mean([metrics(x['input'],x['output'],x['reference'],x['metrics']['valid_auto'])['content_auto'] for x in raw]))
  for row in summary:
   if row['scheme']==scheme:row['single_passive_content_auto']=single;row['additional_content_drop_pp']=(single-row['content_auto'])*100
 dump(O/'summary.json',{'rows':summary,'wall_s':time.monotonic()-start,'exploratory_single_seed':True,'constraint_uses_seen_combination_supervision':True,'heldout_combination_never_fitted':True,'config_hash':CH});print('B_COMPLETE',flush=True)
if __name__=='__main__':main()
