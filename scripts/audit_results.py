"""No tuning: audits fixed outputs, reference coverage, grouped denominators."""
import json,collections,hashlib
from pathlib import Path
import numpy as np
from evaluate import features,evaluate
ROOT=Path(__file__).resolve().parents[1]
def read(p):return [json.loads(s) for s in p.read_text().splitlines()]
def dump(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False))
dev=read(ROOT/'data/dev.jsonl');fail=[];counts=collections.Counter()
for r in dev:
 m=evaluate(r['input'],r['reference'],r['reference'])
 if not m['content_auto']:
  counts.update(k for k in ['lemma','entities','dates','numbers','negation'] if not m[k+'_preserved_auto']);fail.append({**r,'metrics':m,'source_features':features(r['input']),'reference_features':features(r['reference'])})
dump(ROOT/'results/evaluator_failure_counts.json',dict(counts));(ROOT/'results/evaluator_failure_examples.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in fail))
# supplement exact-reference proportion with paired source bootstrap: exploratory,
# never use it to reselect checkpoint or alter A's primary metric.
methods={}
for kind in ['shift','lowrank_affine','nonlinear_bottleneck']:
 rr=[read(ROOT/f'results/test_{kind}_s{sd}.jsonl') for sd in [42,43,44]];ids=sorted(r['source_id'] for r in rr[0]);a=[]
 for seedrows in rr:
  d={r['source_id']:r for r in seedrows};a.append([d[k]['output'] in d[k]['references'] for k in ids])
 methods[kind]=np.mean(a,axis=0)
rng=np.random.default_rng(42);ix=rng.integers(0,len(ids),size=(2000,len(ids)));d=methods['lowrank_affine']-methods['shift'];dump(ROOT/'results/exact_reference_supplement.json',{'posthoc_auxiliary':True,'lowrank_minus_shift_pp':float(d.mean()*100),'ci95_pp':np.percentile(d[ix].mean(1)*100,[2.5,97.5]).tolist()})
# Same fixed 100 sources for local prompt comparison; parse raw output without
# quote removal or permissive cleanup, to keep scoring rule unchanged.
p=ROOT/'results/direct_rewrite.jsonl'
if p.exists() and len(read(p))==100:
 chosen={r['source_id'] for r in read(p)};summary=[]
 for p in [p]+sorted((ROOT/'results').glob('test_*.jsonl')):
  rr=[r for r in read(p) if r['source_id'] in chosen];summary.append({'method':rr[0]['method'],'seed':rr[0]['seed'],'n':len(rr),'joint_n':sum(r['metrics']['Joint_auto'] for r in rr),**{k:float(np.mean([r['metrics'][k] for r in rr])) for k in ['Joint_auto','attribute_auto','content_auto','valid_auto']},'mean_total_s':float(np.mean([r['timing_s']['total'] for r in rr]))})
 dump(ROOT/'results/direct_same_subset.json',summary)
print('OUTPUT_AUDIT_COMPLETE')
