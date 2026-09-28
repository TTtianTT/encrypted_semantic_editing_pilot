import json,hashlib
from pathlib import Path
from transformers import AutoTokenizer
from prepare import ROOT,dump,digest
REPO=ROOT.parents[1]
assert not (ROOT/'config.json').exists()
manifest=json.loads((REPO/'models/manifest.json').read_text());verified=[]
for entry in manifest:
 if '/bart-base/' not in entry['path']:continue
 p=REPO/'models/bart-base'/Path(entry['path']).name
 h=digest(p);assert h==entry['sha256'],p
 verified.append({'file':str(p),'sha256':h,'bytes':p.stat().st_size})
dump('source_model_manifest.json',{'model':'facebook/bart-base','revision':json.loads((REPO/'config.json').read_text())['model_revision'],'actual_files':verified,'adaptation':False,'weights_read_only':True})
tok=AutoTokenizer.from_pretrained(REPO/'models/bart-base',local_files_only=True)
lengths=[]
for p in (ROOT/'data').glob('*pairs.jsonl'):
 for line in p.read_text().splitlines():
  r=json.loads(line)
  lengths.extend(len(tok(r[k])['input_ids']) for k in ['source_text','target_text'])
# Include +2 paths, not just atomic pairs.
from prepare import views
for p in (ROOT/'data').glob('*worlds.jsonl'):
 for r in views([json.loads(l) for l in p.read_text().splitlines()]):lengths.append(len(tok(r['source_text'])['input_ids']))
maximum=max(lengths);assert maximum<=128
cfg=dict(model_revision=json.loads((REPO/'config.json').read_text())['model_revision'],methods=['Shift','LowRank16'],seeds=[42,43,44],lr=.001,weight_decay=0.,batch=16,gradient_accumulation=1,max_updates=600,eval_interval=100,gradient_clip=1.,precision='float32',rank=16,source_length=96 if maximum<=96 else 128,max_gold_tokens=maximum,max_new_tokens=maximum+8,do_sample=False,num_beams=1,forced_eos_token_id=None,selection='dev target-token NLL only',schedule='600 updates, round-robin six paths, batch 16, independent operator parameters; no LR decay',gpu_budget_seconds=7200,e0_gate={'joint':.98,'each_status':.95},e1_gate={'joint':.85,'time':.80,'perspective':.80,'plan_to_completed':.02},test_locked=True,bootstrap_replicates=2000)
dump('config.json',cfg)
dump('budget.json',{'limit_gpu_seconds':7200,'gpu_count':1,'jobs':[],'consumed_gpu_seconds':0,'accounting':'max(parent,steps) elapsed per single-GPU allocation; no resetting on retries','status':'prepared'})
dump('frozen_manifest.json',{'files':{str(p.relative_to(ROOT)):digest(p) for p in [ROOT/'config.json',ROOT/'source_model_manifest.json',ROOT/'semantics.py',ROOT/'prepare.py',*sorted((ROOT/'data').glob('*'))] if p.is_file()},'test_access':'Gold construction/coverage/length audits only; no model test generation or selection before checkpoint lock'})
print(json.dumps({'max_gold_tokens':maximum,'source_length':cfg['source_length'],'max_new_tokens':cfg['max_new_tokens'],'weight_hash_verified':True}))
