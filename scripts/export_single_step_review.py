"""Create anonymous score sheets; never fabricates judgments."""
import csv,json,random
from pathlib import Path
R=Path(__file__).resolve().parents[1];P=R/'experiments/single_step_diagnosis_v1'
def main():
 rows=[json.loads(s) for s in (P/'outputs.jsonl').read_text().splitlines()];assert len(rows)==400;random.Random(20260928).shuffle(rows)
 fields=['review_id','source','reference','output','evaluation_goal','time_status','meaning_status','readability_status','reason','human_reviewer','human_reviewed_at'];mapping=[]
 with (P/'review_blind.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader()
  for i,r in enumerate(rows,1):
   rid=f'R{i:04}';goal='保留源句原有时态、信息及可读性' if r['path']=='identity_source' else ('保留参考句信息、将来时及可读性；参考可能有错误，单独记录' if r['path']=='identity_target' else '将源句必要事件改将来时，保留允许时态变化以外的信息，语法可读')
   w.writerow({'review_id':rid,'source':r['input'],'reference':r['reference'],'output':r['output'],'evaluation_goal':goal});mapping.append({'review_id':rid,'case_id':r['case_id'],'source_id':r['source_id'],'path':r['path'],'seed':r['seed'],'config_hash':r['config_hash']})
 (P/'method_map.json').write_text(json.dumps(mapping,indent=2)+'\n')
 # Compact actual-output listing for substantive in-session review, every row included.
 rows.sort(key=lambda r:(r['case_id'],['identity_source','identity_target','shift','lowrank'].index(r['path'])))
 with (P/'model_review_listing.txt').open('w') as f:
  for i in range(0,400,4):
   group=rows[i:i+4];r=group[0];f.write(f"{r['case_id']} X: {r['input']}\n     Y: {r['reference']}\n")
   for q in group:
    label='[exact X]' if q['output']==q['input'] else ('[exact Y]' if q['output']==q['reference'] else q['output'])
    f.write(f"  {q['path']}: {label}\n")
 print('400 unscored rows exported; human fields empty')
if __name__=='__main__':main()
