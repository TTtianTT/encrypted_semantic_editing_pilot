"""CPU-only preparation; no model outputs. Reuses the frozen v2 world grammar."""
import random,collections,subprocess
from common import *
# Vendor only the original generator definitions, not v2 main or its ROOT.
exec((V2/'prepare.py').read_text().split('def main():')[0])
SEED=2026093003

def main():
 assert not (ROOT/'data/lock.json').exists()
 oldpaths=[p for root in [V1,V2] for p in (root/'data').glob('*worlds.jsonl')]
 old=[json.loads(l) for p in oldpaths for l in p.read_text().splitlines()];used={world_key(w) for w in old};oldkeys=used.copy();ids={w['record_id'] for w in old}
 splits={s:build_worlds(s,80,SEED+j,used) for j,s in enumerate(['test_iid','test_template_ood'])}
 exclusions=[];allrows=[]
 for j,(split,ws) in enumerate(splits.items()):
  for w in ws:w['record_id']=w['record_id'].replace('v2_','v3_confirmation_');assert w['record_id'] not in ids and world_key(w) not in oldkeys
  write(f'data/{split}_worlds.jsonl',ws);rng=random.Random(SEED+200+j);atom=[];chains=[]
  for w in ws:
   legal=[d for d in range(-2,3) if all(eligible(w,ops,d,'third' if p.endswith('third') else 'first') for p,ops in ATOMIC.items())];off=rng.choice(legal)
   for path,ops in ATOMIC.items():atom.append(make_row(w,path,ops,off,'third' if path.endswith('third') else 'first'))
   for path,ops in CHAINS.items():
    lim=1 if len(ops)==3 else 2;legal=[d for d in range(-lim,lim+1) if eligible(w,ops,d)]
    if not legal:exclusions.append(dict(record_id=w['record_id'],split=split,path=path,reason='pre-output structural date inapplicability',status=w['record_status']));continue
    row=make_row(w,path,ops,rng.choice(legal));assert all(ok for op,ok in zip(ops,row['source_support_G1']) if op.startswith('T'));chains.append(row)
  for kind,rows in [('atomic',atom),('chains',chains)]:write(f'data/{split}_{kind}.jsonl',rows);allrows+=rows
 csvwrite('data/structural_inapplicability.csv',exclusions)
 worlds={w['record_id']:w for ws in splits.values() for w in ws}
 for r in allrows:
  text=r['source_text'];w=worlds[r['record_id']]
  for gold,c0,c1 in zip(r['gold_step_texts'],r['frames'],r['frames'][1:]):
   assert score(gold,c1,w)['joint_ok'];text,err=text_rule(text,c0,c1);assert err is None and score(text,c1,w)['joint_ok']
 from transformers import AutoTokenizer
 tok=AutoTokenizer.from_pretrained(REPO/'models/bart-base',local_files_only=True)
 texts=[t for r in allrows for t in [r['source_text']]+r['gold_step_texts']];lengths=[len(x) for x in tok(texts)['input_ids']];assert max(lengths)<=96 and max(lengths)<60
 # Same inputs and grammar, no fresh calibration generation.
 gate=json.loads((V2/'calibration/gate.json').read_text());assert gate['passed'] and gate['joint_successes']==920
 artifacts=json.loads((V2/'artifact_manifest.json').read_text())
 dump('calibration/reuse.json',{'gate':gate,'files':{str(p.relative_to(REPO)):digest(p) for p in (V2/'calibration').rglob('*') if p.is_file()},'source_manifest_hash':digest(V2/'source_model_manifest.json'),'repeated_gpu_calibration':False})
 oldout=[];audit={}
 for group in ['G1','G2']:
  rs=[json.loads(l) for l in (V2/f'outputs/{group}.jsonl').read_text().splitlines()]
  for split in splits:
   sub=[r for r in rs if r['split']==split and r['path']=='plus_plus' and r['mode']=='latent_chain'];assert len(sub)==80
   audit[f'{group}/{split}']={'N':80,'first':sum(r['steps'][0]['score']['joint_ok'] for r in sub),'endpoint':sum(r['score']['joint_ok'] for r in sub),'trajectory':sum(all(s['score']['joint_ok'] for s in r['steps']) for r in sub)}
  for rid in ['v2_test_iid_0001','v2_test_iid_0002']:
   if group=='G2':oldout += [r for r in rs if r['record_id']==rid and r['path']=='plus_plus' and r['mode']=='latent_chain']
 assert audit['G2/test_iid']==dict(N=80,first=41,endpoint=80,trajectory=41)
 write('evaluation/v2_example_audit.jsonl',oldout);dump('evaluation/v2_evidence_audit.json',audit)
 selected=[]
 for split,ws in splits.items():selected += random.Random(SEED+999).sample([w['record_id'] for w in ws],10)
 dump('review/selected_worlds.json',selected)
 count=collections.Counter((r['split'],r['path']) for r in allrows)
 dump('data/precheck.json',{'seed':SEED,'suggested_seed_2026092903_already_used_by_v2_train':True,'complete_fact_overlap':0,'worlds':160,'max_token_length':max(lengths),'rule_gold_checks':len(allrows),'counts':{str(k):n for k,n in count.items()},'exclusions':len(exclusions),'old_world_files':{str(p.relative_to(REPO)):digest(p) for p in oldpaths}})
 dump('data/lock.json',{'files':{p.name:digest(p) for p in (ROOT/'data').glob('*') if p.is_file()},'config':digest(ROOT/'config.json'),'protocol':digest(ROOT/'PROTOCOL.md'),'initial':digest(ROOT/'checkpoints/initial.pt'),'before_training_and_confirmation_model_outputs':True})
 dump('v1_v2_readonly_manifest.json',{str(p.relative_to(REPO)):digest(p) for root in [V1,V2] for p in root.rglob('*') if p.is_file() and '__pycache__' not in str(p)})
 dump('code_version.json',{'starting_head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'reviewed_public_v2':'8bf6d42','vendored_v2_sources':{n:digest(V2/n) for n in ['common.py','engine.py','evaluation.py','renderer_v1.py','semantics_v1.py','prepare.py','train.py']}})
 print(json.dumps(audit));print('locked',len(allrows),max(lengths))
if __name__=='__main__':main()
