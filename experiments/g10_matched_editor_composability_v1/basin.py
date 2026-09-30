"""G8-equivalent directional basin profiles for each dev-matched G10 editor."""
import argparse,importlib.util,sys,time,json,os
import torch
from g10_common import *
sys.path.insert(0,str(G7));sys.path.insert(0,str(V3))
sys.path.insert(0,str(ROOT))
spec=importlib.util.spec_from_file_location('g10_g8_extract',G8/'extract.py');g8=importlib.util.module_from_spec(spec);spec.loader.exec_module(g8)
sys.path.insert(0,str(ROOT))
from train import LowRank
from common import advance,render
CFG=json.loads((ROOT/'config.json').read_text());G8CFG=g8.CFG

@torch.no_grad()
def main(index):
 assert os.environ.get('SLURM_JOB_ID'),'Use sbatch+srun for directional basin scans'
 ids=[f'rank{r}_seed{s}' for r in CFG['ranks'] for s in CFG['seeds']];ident=ids[index]
 gate=json.loads((ROOT/'evaluation/gate_lock.json').read_text())
 if ident not in gate['matched_editors']:
  dump(f'basin/{ident}.json',dict(editor=ident,skipped='did not pass locked dev single-step gate'));print('skipped',ident,flush=True);return
 trajectory=read(f'outputs/trajectory_{ident}.jsonl');tr={(x['split'],x['record_id'],x['step']):x for x in trajectory}
 rows=read('data/composition_iid.jsonl')+read('data/composition_template_ood.jsonl')
 world_index={s:{w['record_id']:w for w in read(f'data/{s}_worlds.jsonl')} for s in ['composition_iid','composition_template_ood']}
 base=g8.Backbone('BART');rank=int(ident.split('_')[0][4:]);ed=LowRank(base.U.shape[0],rank).cuda().eval();ck=ROOT/f'checkpoints/rank{rank}/{ident}.pt'
 ed.load_state_dict(torch.load(ck,weights_only=True,map_location='cuda'));base.ed=ed
 state_rows=[];scan_rows=[];started=time.monotonic();alpha_grid=G8CFG['coarse_alpha'];directions=G8CFG['directions']
 for split in ['composition_iid','composition_template_ood']:
  sr=[r for r in rows if r['split']==split]
  for start in range(0,len(sr),8):
   batch=sr[start:start+8];ws=[world_index[split][r['record_id']] for r in batch];h,m=base.encode([r['source_text'] for r in batch]);frames=[r['source_frame'] for r in batch]
   for step in range(1,5):
    h=ed(h,m);frames=[advance(f,'T_plus') for f in frames];decoded,ended,_,_=base.eng.decode(h,m)
    for j,(r,w) in enumerate(zip(batch,ws)):
     old=tr[split,r['record_id'],step];assert decoded[j]==old['output'] and bool(ended[j])==old['normal_end']
     if not old['score']['joint_ok']:continue
     hi=h[j:j+1];mi=m[j:j+1];current=render(w,frames[j]);nxtframe=advance(frames[j],'T_plus');nextgold=render(w,nxtframe);gh,gm=base.encode([current])
     hnext=ed(hi,mi);res=(hnext.float()-hi.float())*mi[...,None]
     # The same world/step random seed is paired across every editor.
     key=('BART',split,r['record_id'],step);dirs=g8.normalized_directions(hi,mi,res,gh,gm,key)
     meta=dict(backbone='BART',editor=ident,split=split,world_id=r['record_id'],step=step)
     state_rows.append(dict(**meta,current_text=decoded[j],current_gold=current,next_gold=nextgold,
       residual_norm=float(g8.masked_norm(res)),input_tokens=int(mi.sum()),
       g8_direction_norms={name:float(g8.masked_norm(v)) for name,v in dirs.items()}))
     samples=[]
     for alpha in alpha_grid:
      requests=[(direction,alpha) for direction in directions]
      samples.extend(g8.evaluate(base,hi,mi,dirs,requests,w,frames[j],nxtframe,current,nextgold,meta))
     intervals={}
     for direction in directions:
      lo=0.;hi_bound=None
      for alpha in alpha_grid:
       point=next(x for x in samples if x['direction']==direction and x['alpha']==alpha)
       if not point['corridor_success']:hi_bound=alpha;break
       lo=alpha
      if hi_bound is not None:intervals[direction]=[lo,hi_bound]
     for _ in range(G8CFG['refinement_rounds']):
      requests=[(direction,sum(bound)/2) for direction,bound in intervals.items()]
      if not requests:break
      for point in g8.evaluate(base,hi,mi,dirs,requests,w,frames[j],nxtframe,current,nextgold,meta):
       samples.append(point);bound=intervals[point['direction']];bound[0 if point['corridor_success'] else 1]=point['alpha']
     scan_rows.extend(samples)
   print('basin',ident,split,start+len(batch),'/',len(sr),'states',len(state_rows),'points',len(scan_rows),'seconds',round(time.monotonic()-started),flush=True)
 write(f'basin/states_{ident}.jsonl',state_rows);write(f'basin/scan_{ident}.jsonl',scan_rows)
 dump(f'basin/{ident}.json',dict(editor=ident,checkpoint_sha256=digest(ck),states=len(state_rows),scan_points=len(scan_rows),
      states_sha256=digest(ROOT/f'basin/states_{ident}.jsonl'),scan_sha256=digest(ROOT/f'basin/scan_{ident}.jsonl'),
      g8_config_sha256=digest(G8/'config.json'),g8_extractor_sha256=digest(G8/'extract.py'),
      g8_directions=directions,alpha_grid=alpha_grid,refinement_rounds=G8CFG['refinement_rounds'],elapsed_seconds=time.monotonic()-started,slurm_job_id=os.environ['SLURM_JOB_ID']))
 print('basin complete',ident,len(state_rows),len(scan_rows),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--index',type=int,choices=range(9),required=True);main(p.parse_args().index)
