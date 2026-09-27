"""Freeze retrospective sample and checkpoint choice without reading outputs."""
import hashlib,json,random,re,subprocess
from datetime import datetime,timezone
from pathlib import Path
R=Path(__file__).resolve().parents[1];P=R/'experiments/single_step_diagnosis_v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 if (P/'sample_manifest.json').exists():raise SystemExit('Already sampled; preserve existing manifest')
 shifts={int(p.parent.name.split('_s')[-1]):p for p in (R/'experiments/latent_consistency_v1/checkpoints').glob('shift_s*/best.pt')}
 lows={int(p.parent.name.split('_s')[-1]):p for p in (R/'checkpoints').glob('lowrank_affine_r64_s*/best.pt')};common=sorted(shifts.keys()&lows.keys());assert common
 sd=common[0];ck={};history={}
 for name,p in [('shift',shifts[sd]),('lowrank',lows[sd])]:
  md=json.loads((p.parent/'complete.json').read_text());ck[name]={'path':str(p.relative_to(R)),'sha256':sha(p),'seed':sd,'checkpoint_step':md['best_step'],'training_step_limit':md.get('final_step',md.get('steps')),'metadata_sha256':sha(p.parent/'complete.json')};history[name]=md
 source=R/'data/test.jsonl';rows=[json.loads(s) for s in source.read_text().splitlines()];unique={};duplicates=[]
 for r in sorted(rows,key=lambda r:r['source_id']):
  key=re.sub(r'\W+',' ',r['input'].lower()).strip()
  if key in unique:duplicates.append({'retained':unique[key]['source_id'],'duplicate':r['source_id']})
  else:unique[key]=r
 population=sorted(unique.values(),key=lambda r:r['source_id']);sample=sorted(random.Random(20260928).sample(population,min(100,len(population))),key=lambda r:r['source_id'])
 for i,r in enumerate(sample,1):r['case_id']=f'S{i:03}'
 (P/'samples.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in sample))
 model_files={str(p.relative_to(R)):sha(p) for p in sorted((R/'models/bart-base').iterdir()) if p.is_file()};expected=json.loads((R/'models/manifest.json').read_text())
 for d in expected:
  p=R.parent/d['path'];assert p.exists() and sha(p)==d['sha256'],d['path']
 config={'selection_rule':'minimum common seed; extended Shift development-best vs selected-rank lowrank development-best; no test-based choice','common_seeds':common,'seed':sd,'checkpoints':ck,'model_revision':json.loads((R/'config.json').read_text())['model_revision'],'model_files':model_files,'paths':['identity_source','identity_target','shift','lowrank'],'length':96,'max_new_tokens':100,'num_beams':1,'do_sample':False,'forced_eos_token_id':None,'precision':'float32','batch':16,'statistical_seed':20260928,'bootstrap_replicates':2000,'training':False,'review_type':'Codex model semantic review, method information exposed, not independent human blind review','max_gpu_wall_s':900}
 (P/'config.json').write_text(json.dumps(config,indent=2)+'\n')
 manifest={'created_at':datetime.now(timezone.utc).isoformat(),'repo_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),'source_file':str(source.relative_to(R)),'source_sha256':sha(source),'raw_n':len(rows),'unique_sources':len(population),'duplicates':duplicates,'sampling_seed':20260928,'sampling_algorithm':'Python random.Random.sample on source-ID sorted normalized-unique sources, then sort selected IDs','n':len(sample),'samples_sha256':sha(P/'samples.jsonl'),'source_ids':[r['source_id'] for r in sample],'case_ids':[r['case_id'] for r in sample],'config_sha256':sha(P/'config.json'),'data_manifest':json.loads((R/'data/manifest.json').read_text()),'prior_outputs_not_read_for_sampling':True,'retrospective_used_test':True,'new_clean_candidates_not_used':True}
 (P/'sample_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');(P/'checkpoint_metadata.json').write_text(json.dumps(history,indent=2)+'\n')
 for r in sample:print(r['case_id']+' X: '+r['input']+'\n     Y: '+r['reference'])
if __name__=='__main__':main()
