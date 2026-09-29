import torch
from common import *
from engine import Engine,new_editors
from evaluation import Evaluator

def main():
 lock=json.loads((ROOT/'data/lock.json').read_text())
 for f,h in lock['files'].items():assert digest(ROOT/'data'/f)==h
 assert digest(ROOT/'config.json')==lock['config']
 assert (ROOT/'checkpoints/G3/complete.json').exists()
 sources={g:(ROOT if g=='G3' else V2)/f'checkpoints/{g}/best.pt' for g in ['G1','G2','G3']};frozen={g:digest(p) for g,p in sources.items()}
 fp=ROOT/'checkpoints/locked.json'
 if fp.exists():assert json.loads(fp.read_text())['groups']==frozen
 else:dump('checkpoints/locked.json',dict(groups=frozen,config_hash=digest(ROOT/'config.json'),data_lock_hash=digest(ROOT/'data/lock.json'),before_confirmation_outputs=True))
 eng=Engine();ev=Evaluator(eng);new=[];old=[]
 for split in ['test_iid','test_template_ood']:
  for kind in ['atomic','chains']:
   new+=read(f'data/{split}_{kind}.jsonl');old += [json.loads(l) for l in (V2/f'data/{split}_{kind}.jsonl').read_text().splitlines()]
 ev.rules(new,'outputs/confirmation_text_rule.jsonl')
 ev.neural(new,None,'Target reconstruction','outputs/confirmation_target_reconstruction.jsonl',kind='target_reconstruction')
 ev.neural([r for r in new if len(r['operations'])>1],None,'Reconstruction','outputs/confirmation_reconstruction.jsonl','decode_reencode',kind='reconstruction_only')
 for group in sources:
  eds=new_editors();eds.load_state_dict(torch.load(sources[group],weights_only=True))
  for dataset,rows in [('confirmation',new)]+([('diagnostic',old)] if group=='G3' else []):
   dest=f'outputs/{dataset}_{group}.jsonl';ev.neural([r for r in rows if len(r['operations'])==1],eds,group,dest,editor_hash=frozen[group])
   for mode in ['latent_chain','decode_reencode']:ev.neural([r for r in rows if len(r['operations'])>1],eds,group,dest,mode,frozen[group])
 dump('evaluation/test_complete.json',{'completed':True,'confirmation_groups':list(sources),'diagnostic_G1_G2_reused':True,'rows_per_group_per_dataset':3732,'confirmation_controls':len(new)*2+len([r for r in new if len(r['operations'])>1]),'peak_cuda_bytes':torch.cuda.max_memory_allocated()})
if __name__=='__main__':main()
