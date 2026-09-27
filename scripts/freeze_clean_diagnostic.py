"""Freeze only after real task review; fail closed on missing approvals or quota."""
import argparse,csv,hashlib,json
from datetime import datetime,timezone
from pathlib import Path
from transformers import AutoTokenizer
from sklearn.feature_extraction.text import TfidfVectorizer
R=Path(__file__).resolve().parents[1];P=R/'experiments/clean_composition_v1'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--review',type=Path,required=True);ap.add_argument('--attestation',type=Path,required=True);a=ap.parse_args()
 attest=json.loads(a.attestation.read_text())
 for key in ['reviewer_is_human','tasks_reviewed_before_any_model_outputs','previous_63_all_within_excluded_old_B100']:
  if attest.get(key) is not True:raise ValueError('Required true human/provenance attestation: '+key)
 if not attest.get('reviewer_id'):raise ValueError('Missing human reviewer identity/code')
 if (P/'frozen_manifest.json').exists():raise ValueError('Already frozen; use a new protocol version to alter data')
 audit=json.loads((P/'candidate_audit.json').read_text())
 for name,h in audit['files'].items():assert digest(R/name)==h,('changed provenance',name)
 canonical=[json.loads(s) for s in (P/'candidates.jsonl').read_text().splitlines()];byid={r['candidate_id']:r for r in canonical};review=list(csv.DictReader(a.review.open()));assert len(review)==len(byid) and {r['candidate_id'] for r in review}==set(byid)
 passed={};rejected=[];fields=['source_valid','future_valid','passive_valid','combo_valid','time_compatible','roles_unambiguous'];tok=AutoTokenizer.from_pretrained(R/'models/bart-base',local_files_only=True)
 for row in review:
  old=byid[row['candidate_id']]
  for k in ['source','source_id','group_id','original_split']:assert row[k]==old[k],('source mutation',k)
  assert all(row[k] in ['1','0','U'] for k in fields),'Unfinished task review'
  assert row['human_reviewer'] and row['reviewed_at'],'Missing per-row human provenance'
  if not all(row[k]=='1' for k in fields):rejected.append({'candidate_id':row['candidate_id'],'ratings':{k:row[k] for k in fields}});continue
  assert all(row[k].strip() for k in ['source','future_target','passive_target','combo_target'])
  assert max(len(tok(row[k])['input_ids']) for k in ['source','future_target','passive_target','combo_target'])<=96
  passed[row['candidate_id']]=row
 selected=[]
 for split,n in [('dev',40),('test',100)]:
  eligible=[passed[x['candidate_id']] for x in canonical if x['candidate_id'] in passed and x['original_split']==split]
  if len(eligible)<n:raise ValueError(f'Insufficient human-approved original {split}: {len(eligible)}/{n}; no automatic split reassignment')
  selected.extend([{**r,'split':split} for r in eligible[:n]])
 assert len({r['group_id'] for r in selected})==140
 v=TfidfVectorizer(analyzer='char_wb',ngram_range=(3,5));m=v.fit_transform([r['source'] for r in selected]);sim=(m@m.T).tocoo()
 for i,j,x in zip(sim.row,sim.col,sim.data):
  if i<j and x>=.92 and min(len(selected[i]['source']),len(selected[j]['source']))/max(len(selected[i]['source']),len(selected[j]['source']))>=.8:raise ValueError('Selected near duplicate; resolve in task review before freeze')
 data=P/'frozen';data.mkdir(exist_ok=True)
 for split in ['dev','test']:(data/(split+'.jsonl')).write_text(''.join(json.dumps(r)+'\n' for r in selected if r['split']==split))
 checkpoints={name:R/f'checkpoints/b/{name}/final.pt' for name in ['independent_lowrank','composition_trained_lowrank']}
 manifest={'frozen_at':datetime.now(timezone.utc).isoformat(),'review_sha256':digest(a.review),'attestation':attest,'attestation_sha256':digest(a.attestation),'protocol_sha256':digest(P/'PROTOCOL.md'),'files':{str(p.relative_to(R)):digest(p) for p in data.glob('*.jsonl')},'checkpoints':{name:{'path':str(p.relative_to(R)),'sha256':digest(p)} for name,p in checkpoints.items()},'task_rejections':rejected,'n_dev':40,'n_test':100,'status':'human_tasks_frozen_outputs_not_yet_generated'}
 (P/'frozen_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print('Frozen 40 development +100 test human-reviewed tasks')
if __name__=='__main__':main()
