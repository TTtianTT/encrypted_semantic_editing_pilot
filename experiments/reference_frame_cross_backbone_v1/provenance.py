"""Add run provenance to completed output rows without changing predictions or scores."""
import hashlib
from common import *
KEYS={'seed','model_revision','editor_hash','interface_hash','model_manifest_hash','gold_record_id'}
def payload(rows):
 h=hashlib.sha256()
 for r in rows:h.update(json.dumps({k:v for k,v in r.items() if k not in KEYS},sort_keys=True).encode())
 return h.hexdigest()
def main():
 auditfile=ROOT/'evaluation/provenance_enrichment.json';history=json.loads(auditfile.read_text()) if auditfile.exists() else {}
 for p in sorted((ROOT/'evaluation').glob('*_complete.json')):
  model=p.name.removesuffix('_complete.json');manifest=json.loads((ROOT/f'models/{model}.json').read_text());lock=json.loads((ROOT/f'checkpoints/{model}/evaluation_lock.json').read_text())
  for group in ['G1','G3']:
   f=f'outputs/{model}/{group}.jsonl';rows=read(f)
   if f in history:
    assert digest(ROOT/f)==history[f]['after_file_hash'];continue
   before=digest(ROOT/f);bodyhash=payload(rows)
   for r in rows:r.update(seed=42,model_revision=manifest['revision'],editor_hash=lock['checkpoints'][group],interface_hash=lock['interface_hash'],model_manifest_hash=digest(ROOT/f'models/{model}.json'),gold_record_id=r['record_id'])
   assert payload(rows)==bodyhash
   write(f,rows);history[f]=dict(before_file_hash=before,after_file_hash=digest(ROOT/f),prediction_score_timing_payload_hash=bodyhash,rows=len(rows),predictions_scores_timing_unchanged=True)
 dump('evaluation/provenance_enrichment.json',history);print('provenance enriched',len(history),'files')
if __name__=='__main__':main()
