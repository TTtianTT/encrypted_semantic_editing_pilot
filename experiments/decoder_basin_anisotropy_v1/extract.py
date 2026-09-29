"""Scan decoder stability around frozen G7 pure-latent states on one Slurm GPU."""
import argparse,hashlib,json,os,sys,time
from pathlib import Path

import torch

HERE=Path(__file__).resolve().parent
G7=HERE.parent/'repeated_intervention_stability_v1'
V3=HERE.parent/'reference_frame_pilot_v3'
G5=HERE.parent/'projection_hypothesis_v1'
T5=HERE.parent/'t5gemma_composition_v1'
sys.path.insert(0,str(G7));sys.path.insert(0,str(V3))
from extract import Backbone
from common import frame,advance,render,score,digest

CFG=json.loads((HERE/'config.json').read_text())

def readjsonl(p):return [json.loads(s) for s in p.read_text().splitlines()]
def writejson(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def key(split,world,step):return split,world,step
def seed_for(*items):
 h=hashlib.sha256(('|'.join(map(str,items))).encode()).digest()
 return int.from_bytes(h[:8],'little')%(2**63-1)
def masked_norm(x):return x.float().square().sum().sqrt()
def cos(x,y):return float((x.float()*y.float()).sum()/(masked_norm(x)*masked_norm(y)))

def worlds_for_run(pilot,only_split=None):
 train=[w for w in readjsonl(V3/'data/train_worlds.jsonl') if w['record_status']=='recorded_plan']
 dev=[w for w in readjsonl(V3/'data/dev_worlds.jsonl') if w['record_status']=='recorded_plan']
 locked=json.loads((G5/'provenance.json').read_text())['world_ids']
 groups={'train':train,'dev':dev}
 for split,ids in locked.items():
  index={w['record_id']:w for w in readjsonl(V3/f'data/{split}_worlds.jsonl')}
  groups[split]=[index[i] for i in ids]
 selected={'train':train[:CFG['worlds']['train_recorded_plan_first']],
           'dev':dev[:CFG['worlds']['dev_recorded_plan_first']],
           'test_iid':groups['test_iid'],'test_template_ood':groups['test_template_ood']}
 if pilot:
  groups={'train':train,'test_iid':groups['test_iid']}
  selected={'train':train[:1],'test_iid':groups['test_iid'][:1]}
 if only_split:
  assert not pilot and only_split in groups
  groups={only_split:groups[only_split]};selected={only_split:selected[only_split]}
 assert len({w['record_id'] for ws in groups.values() for w in ws})==sum(map(len,groups.values()))
 return groups,{split:{w['record_id'] for w in ws} for split,ws in selected.items()}

def normalized_directions(h,m,edit,g,gm,state_key):
 h32=h.float();mask=m[...,None].float();edit=edit.float()*mask;size=masked_norm(edit)
 assert float(size)>0
 n=min(int(m.sum()),int(gm.sum()));gold=torch.zeros_like(h32);gold[:,:n]=g[:,:n].float()-h32[:,:n]
 def unit_length(v):
  v=v*mask;nv=masked_norm(v)
  assert float(nv)>1e-9,state_key
  return v*(size/nv)
 def random_orthogonal(label,onto):
  gen=torch.Generator(device=h.device).manual_seed(seed_for(CFG['random_seed'],*state_key,label))
  z=torch.randn(h32.shape,device=h.device,dtype=torch.float32,generator=gen)*mask
  z=z-(z*onto).sum()/onto.square().sum()*onto
  return unit_length(z)
 return {
  'editor_forward':edit,
  'editor_reverse':-edit,
  'radial_orthogonal_random':random_orthogonal('radial',h32*mask),
  'toward_gold':unit_length(gold),
  'editor_orthogonal_random':random_orthogonal('edit',edit),
 }

@torch.no_grad()
def evaluate(base,h,m,directions,requests,world,current_frame,next_frame,current_gold,next_gold,meta):
 hs=[];norms=[]
 for label,alpha in requests:
  z=(h.float()+float(alpha)*directions[label]).to(h.dtype)
  hs.append(z)
  actual=masked_norm((z.float()-h.float())*m[...,None]);target=masked_norm(directions[label])*alpha
  norms.append(float(actual/target))
 batch=torch.cat(hs,0);mask=m.expand(len(requests),-1)
 texts,ended,output=base.decode_scores(batch,mask)
 nll_current=base.target_nll(batch,mask,[current_gold]*len(requests))
 nll_next=base.target_nll(batch,mask,[next_gold]*len(requests))
 rows=[]
 for i,(label,alpha) in enumerate(requests):
  s0=score(texts[i],current_frame,world,ended[i]);s1=score(texts[i],next_frame,world,ended[i])
  row=dict(**meta,direction=label,alpha=float(alpha),decoded_text=texts[i],normal_end=bool(ended[i]),
           current_gold_success=bool(s0['joint_ok']),next_gold_success=bool(s1['joint_ok']),
           corridor_success=bool(s0['joint_ok'] or s1['joint_ok']),
           parseable=bool(s0['readable']),fact_preservation=bool(s0['nondate_facts_ok']),
           content_compatible=bool(s0['readable'] and s0['nondate_facts_ok'] and ended[i]),
           effective_norm_ratio=norms[i],target_nll_current=nll_current[i]['target_nll'],
           target_nll_next=nll_next[i]['target_nll'],target_nll_best=min(nll_current[i]['target_nll'],nll_next[i]['target_nll']),
           output_entropy=output[i]['output_entropy'],output_top1_margin=output[i]['output_top1_margin'],
           output_min_top1_margin=output[i]['output_min_top1_margin'],generated_token_count=output[i]['generated_token_count'])
  rows.append(row)
 return rows

@torch.no_grad()
def main(backbone,pilot,only_split=None):
 assert os.environ.get('SLURM_JOB_ID'),'Run GPU extraction through Slurm'
 start=time.monotonic();torch.manual_seed(CFG['seed']);base=Backbone(backbone)
 groups,selected=worlds_for_run(pilot,only_split)
 g7={key(r['split'],r['world_id'],r['step']):r for r in readjsonl(G7/f'features_{backbone.lower()}.jsonl')}
 legacy=readjsonl(G5/'pure_reset_controls.jsonl') if backbone=='BART' else [r for r in readjsonl(T5/'trajectories.jsonl') if r['path']=='pure_latent']
 source={key(r['split'],r['world_id'],1):r['source_text'] for r in legacy}
 tag='pilot_' if pilot else f'{only_split}_' if only_split else ''
 state_path=HERE/f'{tag}states_{backbone.lower()}.jsonl';scan_path=HERE/f'{tag}scan_{backbone.lower()}.jsonl'
 state_count=0;scan_count=0;alpha_one_agreement=0;alpha_one_semantic_agreement=0
 baseline_exact=0;baseline_success_same=0;baseline_checks=0;excluded_baseline_failure=0;max_norm_error=0.
 with state_path.open('w') as states,scan_path.open('w') as scan:
  for split,worlds in groups.items():
   for begin in range(0,len(worlds),8):
    sub=worlds[begin:begin+8]
    if not any(w['record_id'] in selected[split] for w in sub):continue
    texts=[source[key(split,w['record_id'],1)] if split.startswith('test_') else render(w,frame(w,1)) for w in sub]
    hs,ms=base.encode(texts);frames=[frame(w,1) for w in sub]
    for k in range(1,5):
     hs=base.apply(hs,ms);frames=[advance(f,'T_plus') for f in frames]
     if not any(w['record_id'] in selected[split] and g7[key(split,w['record_id'],k)]['current_success'] for w in sub):continue
     decoded,ended,_=base.decode_scores(hs,ms)
     for i,w in enumerate(sub):
      world_id=w['record_id']
      if world_id not in selected[split]:continue
      f=frames[i];old=g7[key(split,world_id,k)]
      assert render(w,f)==old['gold_text']
      baseline_checks+=1;baseline_exact+=decoded[i]==old['decoded_text']
      local_success=bool(score(decoded[i],f,w,ended[i])['joint_ok'])
      baseline_success_same+=local_success==old['current_success']
      if not old['current_success']:continue
      if not local_success:
       excluded_baseline_failure+=1;continue
      h=hs[i:i+1];m=ms[i:i+1]
      nf=advance(f,'T_plus');current_gold=render(w,f);next_gold=render(w,nf)
      g,gm=base.encode([current_gold]);nexth=base.apply(h,m)
      residual=(nexth.float()-h.float())*m[...,None]
      state_key=(backbone,split,world_id,k)
      directions=normalized_directions(h,m,residual,g,gm,state_key)
      direction_info={label:dict(norm=float(masked_norm(v)),cosine_to_editor=cos(v,residual),cosine_to_state=cos(v,h.float()*m[...,None])) for label,v in directions.items()}
      norm=float(masked_norm(residual));assert all(abs(x['norm']/norm-1)<1e-5 for x in direction_info.values())
      meta=dict(backbone=backbone,split=split,world_id=world_id,step=k,next_failure=bool(old['next_failure']))
      state=dict(**meta,current_gold=current_gold,next_gold=next_gold,current_decoded_text=decoded[i],
                 next_original_decoded_text=g7[key(split,world_id,k+1)]['decoded_text'],
                 current_target_nll=old['target_nll'],current_output_entropy=old['output_entropy'],
                 current_output_top1_margin=old['output_top1_margin'],current_pooled_l2=old['pooled_l2'],
                 residual_norm=norm,active_tokens=int(m.sum()),gold_tokens=int(gm.sum()),directions=direction_info,
                 g7_current_text_exact=decoded[i]==old['decoded_text'],source_batch_size=len(sub))
      slot_offset=seed_for(CFG['random_seed'],*state_key,'decode_slot')%len(CFG['directions']) if backbone=='T5Gemma' else 0
      ordered=CFG['directions'][slot_offset:]+CFG['directions'][:slot_offset]
      state['decode_slot_offset']=slot_offset
      samples=[]
      for alpha in CFG['coarse_alpha']:
       requests=[(label,alpha) for label in ordered]
       samples.extend(evaluate(base,h,m,directions,requests,w,f,nf,current_gold,next_gold,meta))
      one=next(r for r in samples if r['direction']=='editor_forward' and r['alpha']==1.)
      state['alpha_one_decoded_text']=one['decoded_text']
      state['alpha_one_next_gold_success']=one['next_gold_success']
      state['alpha_one_match_g7']=one['decoded_text']==state['next_original_decoded_text']
      alpha_one_agreement+=state['alpha_one_match_g7']
      alpha_one_semantic_agreement+=one['next_gold_success']==(not old['next_failure'])
      intervals={}
      for label in CFG['directions']:
       lo=0.;hi=None
       for alpha in CFG['coarse_alpha']:
        match=next(r for r in samples if r['direction']==label and r['alpha']==alpha)
        if not match['corridor_success']:hi=alpha;break
        lo=alpha
       if hi is not None:intervals[label]=[lo,hi]
      for _ in range(CFG['refinement_rounds']):
       if not intervals:break
       requests=[(label,(bounds[0]+bounds[1])/2) for label,bounds in intervals.items()]
       rr=evaluate(base,h,m,directions,requests,w,f,nf,current_gold,next_gold,meta)
       samples.extend(rr)
       for row in rr:
        bounds=intervals[row['direction']]
        bounds[0 if row['corridor_success'] else 1]=row['alpha']
      states.write(json.dumps(state,ensure_ascii=False)+'\n');state_count+=1
      for row in samples:
       scan.write(json.dumps(row,ensure_ascii=False)+'\n');scan_count+=1
       max_norm_error=max(max_norm_error,abs(row['effective_norm_ratio']-1))
    states.flush();scan.flush()
    print('completed',backbone,split,min(begin+len(sub),len(worlds)),'/',len(worlds),'states',state_count,'scan',scan_count,'seconds',round(time.monotonic()-start),flush=True)
 provenance=dict(backbone=backbone,pilot=pilot,only_split=only_split,config=CFG,slurm_job_id=os.environ['SLURM_JOB_ID'],
                 editor_sha256=digest(base.checkpoint),g7_features_sha256=digest(G7/f'features_{backbone.lower()}.jsonl'),
                 g5_provenance_sha256=digest(G5/'provenance.json'),world_ids={split:[w['record_id'] for w in ws if w['record_id'] in selected[split]] for split,ws in groups.items()},
                 states=state_count,scan_rows=scan_count,baseline_checks=baseline_checks,baseline_text_exact=baseline_exact,
                 baseline_success_same=baseline_success_same,excluded_baseline_failure=excluded_baseline_failure,
                 alpha_one_next_state_exact=alpha_one_agreement,alpha_one_next_semantic_same=alpha_one_semantic_agreement,
                 max_effective_norm_ratio_error=max_norm_error,elapsed_seconds=time.monotonic()-start,
                 states_sha256=digest(state_path),scan_sha256=digest(scan_path),base_training='none',editor_training='none')
 writejson(HERE/f'{tag}extraction_{backbone.lower()}.json',provenance)
 print('finished',backbone,provenance['states'],provenance['scan_rows'],flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--backbone',choices=['BART','T5Gemma'],required=True);p.add_argument('--pilot',action='store_true');p.add_argument('--only-split',choices=['test_iid','test_template_ood']);args=p.parse_args()
 main(args.backbone,args.pilot,args.only_split)
