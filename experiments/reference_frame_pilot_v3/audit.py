import torch,collections
from common import *

def main():
 readonly=json.loads((ROOT/'v1_v2_readonly_manifest.json').read_text())
 for p,h in readonly.items():assert digest(REPO/p)==h,p
 lock=json.loads((ROOT/'data/lock.json').read_text())
 for f,h in lock['files'].items():assert digest(ROOT/'data'/f)==h
 assert digest(ROOT/'config.json')==lock['config'];assert digest(ROOT/'PROTOCOL.md')==lock['protocol']
 for f in ['sample_schedule.jsonl','train_G1.jsonl','train_worlds.jsonl','dev_atomic.jsonl','dev_chains.jsonl']:
  assert digest(ROOT/'data'/f)==digest(V2/'data'/f)
 ck=json.loads((ROOT/'checkpoints/G3/complete.json').read_text());old=json.loads((V2/'checkpoints/G2/complete.json').read_text())
 assert ck['steps']==600 and ck['beststep']==600 and ck['replaced_occurrences']==1600
 for op in OPS:
  assert ck['counts'][op]['endpoint_weight_tokens']==old['counts'][op]['supervision_tokens']
  assert ck['counts'][op]['operator_sample_calls']==old['counts'][op]['operator_sample_calls']
 states={g:torch.load((ROOT if g=='G3' else V2)/f'checkpoints/{g}/best.pt',map_location='cpu',weights_only=True) for g in ['G1','G2','G3']};diff={}
 for op in ['T_minus','P_13','P_31']:
  diff[op]={n:float((v-states['G2'][n]).abs().max()) for n,v in states['G3'].items() if n.startswith(op+'.')}
  for n,v in states['G3'].items():
   if n.startswith(op+'.'):assert torch.allclose(v,states['G2'][n],atol=2e-5,rtol=2e-4),(n,diff[op][n])
 coverage=collections.Counter()
 for split in ['test_iid','test_template_ood']:
  for r in read(f'data/{split}_atomic.jsonl')+read(f'data/{split}_chains.jsonl'):
   for i,(op,offset,support) in enumerate(zip(r['operations'],r['offsets'],r['source_support_G1'])):coverage[split,r['path'],i+1,op,offset,r['record_status'],r['polarity'],support]+=1
 csvwrite('data/confirmation_coverage_counts.csv',[dict(split=k[0],path=k[1],step=k[2],operation=k[3],source_offset=k[4],status=k[5],polarity=k[6],source_supported=k[7],N=n) for k,n in coverage.items()])
 dump('evaluation/implementation_audit.json',{'v1_v2_files_unchanged':len(readonly),'schedule_and_inputs_byte_identical':True,'G2_endpoint_weights_and_operator_calls_matched':True,'other_heads_max_abs_differences':diff,'note':'Ordinary loss uses algebraically identical per-sample token reduction; floating point summation can produce tiny weight differences, not additional supervision or training.'})
 print('audit passed',diff)
if __name__=='__main__':main()
