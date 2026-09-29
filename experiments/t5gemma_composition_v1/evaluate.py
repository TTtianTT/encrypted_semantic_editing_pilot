"""Locked G5 worlds: frozen T5Gemma pure and decode/re-encode trajectories."""
import json,sys,time
from pathlib import Path
import torch
import torch.nn.functional as F

HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from core import CFG,V3,Engine,Editor,frame,score,digest,readjsonl,writejson,writejsonl,pooled
G5=HERE.parent/'projection_hypothesis_v1'

def dist(a,g):return dict(cosine=float(1-F.cosine_similarity(a[None],g[None]).item()),normalized_l2=float((a-g).norm().item()/g.norm().item()))
def scored(text,f,w,ended):
 s=score(text,f,w,ended)
 return dict(success=bool(s['joint_ok']),fact_preservation=bool(s['nondate_facts_ok']),parse_unresolved=bool(s['parse_unresolved']),decoded_semantic_state=s['parsed'],normal_end=bool(ended))

@torch.no_grad()
def main():
 started=time.monotonic();g5p=json.loads((G5/'provenance.json').read_text());selected=g5p['world_ids']
 assert all(len(v)==53 for v in selected.values())
 g5pure=readjsonl(G5/'pure_reset_controls.jsonl');idx={(r['split'],r['world_id'],r['step']):r for r in g5pure};assert len(idx)==530
 worlds={w['record_id']:w for s in selected for w in readjsonl(V3/f'data/{s}_worlds.jsonl')}
 eng=Engine();ed=Editor(eng.hidden,CFG['editor_rank']).cuda().eval()
 ed.load_state_dict(torch.load(HERE/'editor_best.pt',map_location='cuda',weights_only=True))
 for p in ed.parameters():p.requires_grad_(False)
 rows=[];vectors={};identity=[];gold_controls=[]
 for split,ids in selected.items():
  for begin in range(0,len(ids),8):
   sub=ids[begin:begin+8];source=[idx[split,w,1]['source_text'] for w in sub]
   h0,m0=eng.encode(source)
   idtext,idend=eng.decode(h0,m0)
   for i,w in enumerate(sub):identity.append(dict(split=split,world_id=w,source_text=source[i],decoded_text=idtext[i],score=scored(idtext[i],frame(worlds[w],1),worlds[w],idend[i])))
   gold={}
   for k in range(1,6):
    gh,gm=eng.encode([idx[split,w,k]['gold_text'] for w in sub]);gold[k]=pooled(gh,gm)
    gt,ge=eng.decode(gh,gm)
    for i,w in enumerate(sub):gold_controls.append(dict(split=split,world_id=w,step=k,gold_text=idx[split,w,k]['gold_text'],decoded_text=gt[i],score=scored(gt[i],idx[split,w,k]['gold_frame'],worlds[w],ge[i])))
   for path in ('pure_latent','decode_reencode'):
    current=h0;mask=m0;previous_text=source
    for k in range(1,6):
     edited=ed(current,mask)
     texts,ended=eng.decode(edited,mask)
     reencoded,rm=eng.encode(texts)
     ep=pooled(edited,mask);rp=pooled(reencoded,rm)
     residual=((edited.float()-current.float())*mask[...,None]).norm(dim=(1,2))/mask.sum(1).sqrt()
     for i,w in enumerate(sub):
      r=idx[split,w,k];g=gold[k][i];key=f'{path}/{split}/{w}/{k}'
      rows.append(dict(path=path,split=split,world_id=w,step=k,source_text=source[i],input_text=previous_text[i],decoded_text=texts[i],gold_text=r['gold_text'],gold_frame=r['gold_frame'],gold_semantic_state=r['gold_semantic_state'],edited=scored(texts[i],r['gold_frame'],worlds[w],ended[i]),edited_distance=dist(ep[i],g),reset_distance=dist(rp[i],g),residual_norm=float(residual[i]),edited_mask_length=int(mask[i].sum()),reset_mask_length=int(rm[i].sum())))
      vectors[key]=dict(edited=ep[i].cpu(),reset=rp[i].cpu(),gold=g.cpu())
     if path=='decode_reencode':current,mask=reencoded,rm
     else:current=edited
     previous_text=texts
   print('completed',split,begin+len(sub),'/',len(ids),flush=True)
 assert len(rows)==1060 and len(identity)==106 and len(gold_controls)==530
 writejsonl(HERE/'trajectories.jsonl',rows);writejsonl(HERE/'identity_controls.jsonl',identity);writejsonl(HERE/'gold_autoencode_controls.jsonl',gold_controls)
 torch.save(vectors,HERE/'pooled_representations.pt')
 writejson(HERE/'eval_provenance.json',dict(config_sha256=digest(HERE/'config.json'),editor_checkpoint_sha256=digest(HERE/'editor_best.pt'),train_provenance_sha256=digest(HERE/'training_provenance.json'),g5_provenance_sha256=digest(G5/'provenance.json'),g5_pure_sha256=digest(G5/'pure_reset_controls.jsonl'),g5_dre_sha256=digest(G5/'decode_reencode_trajectories.jsonl'),world_file_sha256={s:digest(V3/f'data/{s}_worlds.jsonl') for s in selected},world_ids=selected,long_chain_training=False,gold_text_chain_feedback=False))
 writejson(HERE/'eval_complete.json',dict(completed=True,trajectory_rows=len(rows),identity_rows=len(identity),gold_control_rows=len(gold_controls),trajectories_sha256=digest(HERE/'trajectories.jsonl'),vectors_sha256=digest(HERE/'pooled_representations.pt'),elapsed_seconds=time.monotonic()-started,peak_cuda_bytes=torch.cuda.max_memory_allocated()))
if __name__=='__main__':main()
