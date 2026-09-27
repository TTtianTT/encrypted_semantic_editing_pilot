"""Posthoc audit of known synthetic-template ground truth, NOT a new main score.
Shows that tense-auxiliary removal is wrongly rejected by strict lemma matching.
"""
import json,re,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def canon(s):return re.sub(r'[^a-z0-9]+',' ',s.lower()).strip()
rows=[]
for p in sorted((ROOT/'results').glob('diagnostic_*.jsonl')):
 data=[json.loads(x) for x in p.read_text().splitlines()]
 for r in data:
  r['template_joint_auto_posthoc']=canon(r['output'])==canon(r['reference'])
  r['specified_fact_components_auto']=all(r['metrics'][k+'_preserved_auto'] for k in ['entities','numbers','dates','negation'])
  rows.append(r)
groups=collections.defaultdict(list)
for r in rows:groups[(r['method'],r['seed'])].append(r)
summary=[]
for (m,sd),rr in groups.items():summary.append({'method':m,'seed':sd,'n':len(rr),'preregistered_joint_n':sum(x['metrics']['Joint_auto'] for x in rr),'posthoc_exact_template_target_n':sum(x['template_joint_auto_posthoc'] for x in rr),'entities_numbers_dates_negation_preserved_n':sum(x['specified_fact_components_auto'] for x in rr)})
out={'posthoc':True,'not_used_for_model_selection_or_gate':True,'reason':'Original strict content rule retains lemma do when did is correctly removed in did not -> will not. Thus Joint_auto=0 on this template is a scorer failure, not evidence of universal semantic failure. Exact whole-template target match is a narrow correctness check, not general fact verification.','rows':summary}
(ROOT/'results/diagnostic_posthoc_audit.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
