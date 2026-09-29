"""Export fixed, text-exact pre-failure worlds with full five-step evidence."""
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
SELECTED=[
 ('BART','test_iid','v3_confirmation_test_iid_0000',3),
 ('BART','test_template_ood','v3_confirmation_test_template_ood_0015',2),
 ('T5Gemma','test_iid','v3_confirmation_test_iid_0000',2),
 ('T5Gemma','test_template_ood','v3_confirmation_test_template_ood_0000',2),
]
KEEP=('step','decoded_text','gold_text','current_success','next_success','fact_preservation',
      'pooled_l2','pooled_cosine_distance','token_l2','token_gram_rms','target_nll',
      'output_entropy','output_top1_margin','residual_norm','residual_previous_cosine',
      'jvp_residual_gain','active_tokens','gold_tokens')

def main():
 rows=[json.loads(line) for name in ('bart','t5gemma') for line in (HERE/f'features_{name}.jsonl').read_text().splitlines()]
 cases=[]
 for backbone,split,world_id,prefailure_step in SELECTED:
  seq=sorted((r for r in rows if (r['backbone'],r['split'],r['world_id'])==(backbone,split,world_id)),key=lambda r:r['step'])
  assert len(seq)==5 and seq[prefailure_step-1]['current_success'] and not seq[prefailure_step]['current_success']
  assert seq[prefailure_step-1]['decoded_text'].strip()==seq[prefailure_step-1]['gold_text']
  cases.append(dict(backbone=backbone,split=split,world_id=world_id,prefailure_step=prefailure_step,
                    trajectory=[{k:r[k] for k in KEEP} for r in seq]))
 (HERE/'pre_failure_trajectories.json').write_text(json.dumps(cases,ensure_ascii=False,indent=2)+'\n')
 print(len(cases),'pre-failure trajectories exported')

if __name__=='__main__':main()
