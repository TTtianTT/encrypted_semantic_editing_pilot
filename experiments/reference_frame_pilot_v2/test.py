import torch,json
from common import *
from engine import Engine,new_editors
from evaluation import Evaluator

def main():
 eng=Engine();ev=Evaluator(eng);gate=json.loads((ROOT/'evaluation/c_gate.json').read_text());groups=['G0','G1']+(['G2'] if gate['run_G2'] else [])
 frozen={}
 for g in groups:
  assert (ROOT/f'checkpoints/{g}/complete.json').exists();frozen[g]=digest(ROOT/f'checkpoints/{g}/best.pt')
 p=ROOT/'checkpoints/locked.json'
 if p.exists():assert json.loads(p.read_text())['groups']==frozen
 else:dump('checkpoints/locked.json',{'groups':frozen,'config_hash':digest(ROOT/'config.json'),'c_gate_hash':digest(ROOT/'evaluation/c_gate.json'),'test_generation_not_started_at_lock':True})
 rows=[];extended=[]
 for split in ['test_iid','test_template_ood']:
  rows+=read(f'data/{split}_atomic.jsonl')+read(f'data/{split}_chains.jsonl');extended+=read(f'data/{split}_extended.jsonl')
 ev.rules(rows,'outputs/text_rule.jsonl')
 ev.neural(rows,None,'Target reconstruction','outputs/target_reconstruction.jsonl',kind='target_reconstruction')
 ev.neural([r for r in rows if len(r['operations'])>1],None,'Reconstruction','outputs/reconstruction_controls.jsonl','decode_reencode',kind='reconstruction_only')
 for g in groups:
  eds=new_editors();eds.load_state_dict(torch.load(ROOT/f'checkpoints/{g}/best.pt',weights_only=True))
  ev.neural([r for r in rows if len(r['operations'])==1],eds,g,f'outputs/{g}.jsonl',editor_hash=frozen[g])
  for mode in ['latent_chain','decode_reencode']:ev.neural([r for r in rows if len(r['operations'])>1],eds,g,f'outputs/{g}.jsonl',mode,frozen[g])
  ev.neural(extended,eds,g,f'outputs/{g}_extended.jsonl',editor_hash=frozen[g],kind='extended_atomic')
 dump('evaluation/test_complete.json',{'groups':groups,'completed':True,'rows_per_group':len([r for r in rows if len(r['operations'])==1])+2*len([r for r in rows if len(r['operations'])>1]),'baseline_rows':len(rows),'test_tuning':False})
if __name__=='__main__':main()
