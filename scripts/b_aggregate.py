import json,collections,hashlib
from pathlib import Path
import numpy as np
from b_pilot import ROOT,O,metrics,read
summary=json.load(open(O/'summary.json'));test=read('test_heldout_combo');gold=[metrics(r['input'],r['reference'],r['reference'],True) for r in test]
cal={'n':len(test),'note':'posthoc held-out reference coverage diagnostic; no threshold/model changes permitted',**{k:float(np.mean([x[k] for x in gold])) for k in ['Joint_auto','content_auto','future_auto','passive_auto','root_roles_preserved_auto','lexical_bag_preserved_auto']}}
(O/'evaluator_coverage.json').write_text(json.dumps(cal,indent=2));by={}
for s in ['vector_add','independent_lowrank','composition_trained_lowrank']:
 for path in ['latent_once','decode_reencode']:
  rr=[json.loads(x) for x in (O/f'{s}_{path}.jsonl').read_text().splitlines()];by[(s,path)]={r['group_id']:r for r in rr};assert len(by[(s,path)])==100
ids=sorted(by[('vector_add','latent_once')]);rng=np.random.default_rng(42);ix=rng.integers(0,len(ids),size=(2000,len(ids)));results={}
for a,b in [(('independent_lowrank','latent_once'),('vector_add','latent_once')),(('composition_trained_lowrank','latent_once'),('independent_lowrank','latent_once')),(('independent_lowrank','latent_once'),('independent_lowrank','decode_reencode'))]:
 diff=np.array([int(by[a][i]['metrics']['Joint_auto'])-int(by[b][i]['metrics']['Joint_auto']) for i in ids]);results[str(a)+' minus '+str(b)]={'difference_pp':float(diff.mean()*100),'ci95_pp':np.percentile(diff[ix].mean(1)*100,[2.5,97.5]).tolist(),'independent_source_groups':100,'exploratory_single_seed':True}
(O/'paired_statistics.json').write_text(json.dumps(results,indent=2));print(json.dumps({'coverage':cal,'paired':results},indent=2))
