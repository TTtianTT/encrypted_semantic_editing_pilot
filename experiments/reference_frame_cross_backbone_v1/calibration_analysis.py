"""Descriptive diagnostics only; never change the locked parser or admission scores."""
import collections,re
from common import *
def main():
 summary=[];patterns=[];examples=[]
 for model in MODELS:
  p=ROOT/f'calibration/{model}/admission.json'
  if not p.exists():continue
  a=json.loads(p.read_text())
  for wrapper in ['A','B']:
   file=ROOT/f'calibration/{model}/{wrapper}_scored.jsonl'
   if not file.exists():continue
   rows=read(file.relative_to(ROOT))
   for role in ['source','target']:
    for status in ['recorded_plan','reported_completed','reported_cancelled']:
     rr=[r for r in rows if r['role']==role and r['status']==status];summary.append(dict(model=model,wrapper=wrapper,selected=wrapper==a.get('selected_wrapper'),role=role,status=status,N=len(rr),joint=sum(r['score']['joint_ok'] for r in rr),exact=sum(r['exact'] for r in rr),normal_end=sum(r['ended'] for r in rr),unresolved=sum(r['score']['parse_unresolved'] for r in rr),parsed_N=sum(r['score']['parsed'] is not None for r in rr),parsed_nondate_errors=sum(r['score']['parsed_nondate_error'] for r in rr),parsed_date_errors=sum(r['score']['parsed_date_error'] for r in rr)))
   rr=[r for r in rows if r['role']=='source'];norm=lambda t:' '.join(re.sub(r'[^\w\s]','',t).split());patterns.append(dict(model=model,wrapper=wrapper,N=len(rr),missing_author_header=sum(not r['output'].startswith('Author: ') for r in rr),repeated_author_header=sum(r['output'].count('Author:')>1 for r in rr),empty=sum(not r['output'].strip() for r in rr),header_only=sum(bool(re.fullmatch(r'Author: \w+\. Record date: [\d-]+\.?',r['output'].strip())) for r in rr),unresolved_punctuation_only=sum(r['score']['parse_unresolved'] and norm(r['output'])==norm(r['text']) for r in rr),score_adjusted=False))
 csvwrite('evaluation/calibration_summary.csv',summary);csvwrite('evaluation/calibration_surface_diagnostics.csv',patterns)
 print('calibration diagnostic rows',len(summary))
if __name__=='__main__':main()
