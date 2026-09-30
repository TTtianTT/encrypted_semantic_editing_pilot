"""Independent one-step match-set evaluation; freezes retention before test inference."""
import sys,json,torch
from g10_common import *
sys.path.insert(0,str(G7));sys.path.insert(0,str(V3))
sys.path.insert(0,str(ROOT))
from extract import Backbone,readjsonl
sys.path.insert(0,str(ROOT))
from train import LowRank
from common import score
CFG=json.loads((ROOT/'config.json').read_text())

@torch.no_grad()
def main():
 assert __import__('os').environ.get('SLURM_JOB_ID'),'Use sbatch+srun for GPU screen'
 lock=json.loads((ROOT/'data/lock.json').read_text());assert all(digest(REPO/f)==h for f,h in lock['code'].items())
 base=Backbone('BART');match=read('data/match_iid.jsonl')+read('data/match_template_ood.jsonl');outs=[];summary=[]
 worlds={s:{w['record_id']:w for w in read(f'data/{s}_worlds.jsonl')} for s in ['match_iid','match_template_ood']}
 for rank in CFG['ranks']:
  for seed in CFG['seeds']:
   ident=f'rank{rank}_seed{seed}';ed=LowRank(base.U.shape[0],rank).cuda().eval();p=ROOT/f'checkpoints/rank{rank}/{ident}.pt'
   ed.load_state_dict(torch.load(p,weights_only=True,map_location='cuda'));base.ed=ed
   for split in ['match_iid','match_template_ood']:
    rows=[r for r in match if r['split']==split];good=0
    for i in range(0,len(rows),16):
     sub=rows[i:i+16];h,m=base.encode([r['source_text'] for r in sub]);h=ed(h,m)
     texts,ended,_,_=base.eng.decode(h,m)
     for r,text,end in zip(sub,texts,ended):
      s=score(text,r['target_frames'][0],worlds[split][r['record_id']],end)
      good+=bool(s['joint_ok']);outs.append(dict(editor=ident,rank=rank,seed=seed,split=split,record_id=r['record_id'],source_text=r['source_text'],target_text=r['gold_step_texts'][0],output=text,ended=bool(end),score=s))
    summary.append(dict(editor=ident,rank=rank,seed=seed,split=split,N=len(rows),joint_success=good,rate=good/len(rows)))
   del ed;torch.cuda.empty_cache()
 write('outputs/matching_gate.jsonl',outs);csvwrite('evaluation/matching_gate.csv',summary)
 grouped={r['editor']:{} for r in summary}
 for r in summary:grouped[r['editor']][r['split']]=r['rate']
 retained=sorted(i for i,x in grouped.items() if x['match_iid']>=CFG['matching_gate']['iid_min_joint'] and x['match_template_ood']>=CFG['matching_gate']['template_ood_min_joint'])
 payload=dict(criteria=CFG['matching_gate'],matched_editors=retained,all_editor_rates=grouped,match_output_sha256=digest(ROOT/'outputs/matching_gate.jsonl'),
              match_set_hashes={s:digest(ROOT/f'data/{s}.jsonl') for s in ['match_iid','match_template_ood']},composition_test_hashes={s:digest(ROOT/f'data/{s}.jsonl') for s in ['composition_iid','composition_template_ood']},
              locked_before_composition_inference=True)
 dump('evaluation/gate_lock.json',payload);print('matched cohort frozen:',retained,flush=True)

if __name__=='__main__':main()
