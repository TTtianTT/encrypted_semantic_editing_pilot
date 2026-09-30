"""One-step test for all candidates and pure-latent repeated trajectories for gated editors."""
import sys,torch,json,torch.nn.functional as F
from g10_common import *
sys.path.insert(0,str(G7));sys.path.insert(0,str(V3))
sys.path.insert(0,str(ROOT))
from extract import Backbone,geometry,readjsonl
sys.path.insert(0,str(ROOT))
from train import LowRank
from common import advance,score
CFG=json.loads((ROOT/'config.json').read_text())

@torch.no_grad()
def main():
 assert __import__('os').environ.get('SLURM_JOB_ID'),'Use sbatch+srun for confirmation inference'
 gate=json.loads((ROOT/'evaluation/gate_lock.json').read_text());assert gate['locked_before_composition_inference']
 assert gate['composition_test_hashes']=={s:digest(ROOT/f'data/{s}.jsonl') for s in ['composition_iid','composition_template_ood']}
 base=Backbone('BART');all_rows=read('data/composition_iid.jsonl')+read('data/composition_template_ood.jsonl');worlds={s:{w['record_id']:w for w in read(f'data/{s}_worlds.jsonl')} for s in ['composition_iid','composition_template_ood']}
 retained=set(gate['matched_editors']);meta=[]
 for rank in CFG['ranks']:
  for seed in CFG['seeds']:
   ident=f'rank{rank}_seed{seed}';ed=LowRank(base.U.shape[0],rank).cuda().eval();ck=ROOT/f'checkpoints/rank{rank}/{ident}.pt';ed.load_state_dict(torch.load(ck,weights_only=True,map_location='cuda'));base.ed=ed
   out=[]
   for split in ['composition_iid','composition_template_ood']:
    rows=[r for r in all_rows if r['split']==split]
    for start in range(0,len(rows),8):
     sub=rows[start:start+8];h,m=base.encode([r['source_text'] for r in sub]);frames=[r['source_frame'] for r in sub];prev_res=[None]*len(sub)
     for step in range(1,(CFG['pure_latent_steps'] if ident in retained else 1)+1):
      before=h;h=ed(h,m);res=(h.float()-before.float())*m[...,None];frames=[advance(c,'T_plus') for c in frames]
      texts,ended,_,_=base.eng.decode(h,m)
      for j,r in enumerate(sub):
       w=worlds[split][r['record_id']];sc=score(texts[j],frames[j],w,ended[j]);gh,gm=base.encode([r['gold_step_texts'][step-1]])
       d=geometry(h[j],m[j],gh[0],gm[0]);rr=res[j][m[j].bool()];mean=rr.mean(0)
       cos=None if prev_res[j] is None else float(F.cosine_similarity(mean[None],prev_res[j][None]).item())
       out.append(dict(editor=ident,rank=rank,seed=seed,split=split,record_id=r['record_id'],step=step,
         source_text=r['source_text'],source_frame=r['source_frame'],gold_text=r['gold_step_texts'][step-1],target_frame=frames[j],
         output=texts[j],normal_end=bool(ended[j]),score=sc,pooled_l2=d['pooled_l2'],token_l2=d['token_l2'],
         residual_norm=float(rr.norm()/m[j].sum().sqrt()),residual_previous_cosine=cos,active_tokens=int(m[j].sum())))
       prev_res[j]=mean
     print('trajectory',ident,split,start+len(sub),'/',len(rows),flush=True)
   write(f'outputs/trajectory_{ident}.jsonl',out);meta.append(dict(editor=ident,retained=ident in retained,rows=len(out),checkpoint_sha256=digest(ck),output_sha256=digest(ROOT/f'outputs/trajectory_{ident}.jsonl')))
   del ed;torch.cuda.empty_cache()
 dump('evaluation/trajectory_manifest.json',meta);print('confirmation outputs complete',flush=True)
if __name__=='__main__':main()
