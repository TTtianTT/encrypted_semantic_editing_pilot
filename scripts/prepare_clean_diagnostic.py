"""Candidate task audit only. Never runs editors or treats rules as human review."""
import argparse,collections,csv,hashlib,json,random,re
from pathlib import Path
import spacy
from transformers import AutoTokenizer
from sklearn.feature_extraction.text import TfidfVectorizer
R=Path(__file__).resolve().parents[1];P=R/'experiments/clean_composition_v1'
def norm(x):return re.sub(r'\W+',' ',x.lower()).strip()
def sha(x):return hashlib.sha256(x.encode()).hexdigest()[:20]
parent={}
def find(k):
 parent.setdefault(k,k)
 if parent[k]!=k:parent[k]=find(parent[k])
 return parent[k]
def union(a,b):
 a,b=find(a),find(b)
 if a!=b:parent[max(a,b)]=min(a,b)
def main():
 global P
 ap=argparse.ArgumentParser();ap.add_argument("--include-incomplete-targets",action="store_true");ap.add_argument("--include-tfu-sources",action="store_true");args=ap.parse_args()
 if args.include_tfu_sources:assert args.include_incomplete_targets,"TFU supplement requires explicit incomplete-target flag"
 if args.include_incomplete_targets:P=P/("expanded_tfu_candidates" if args.include_tfu_sources else "incomplete_target_candidates");P.mkdir(exist_ok=True)
 raw=[];files=[]
 for split,suffix in [('train','train'),('dev','valid'),('test','test')]:
  p=R/f'data/compositions/tense_voice_{suffix}.tsv';files.append(p)
  for line in p.read_text().splitlines():
   a,b=line.split('\t');tense,voice,src=a.split(' ',2);raw.append({'source':src,'target':b,'code':tense+voice,'original_split':split});union(norm(src),norm(b))
 if args.include_tfu_sources:
  p=R/'data/fulldata.h16';files.append(p);lines=p.read_text().splitlines();tfu=[(lines[i+1],lines[i+2]) for i,x in enumerate(lines) if re.fullmatch(r'TFU\d+',x)];n=len(tfu)
  for i,(src,tgt) in enumerate(tfu):
   split='dev' if i<n//20 else ('test' if i<n//10 else 'train');union(norm(src),norm(tgt));raw.append({'source':src,'target':tgt,'code':'10','original_split':split})
 used=[]
 for p in sorted((R/'data').glob('*.jsonl'))+sorted((R/'data/b').glob('*.jsonl')):
  if p.name not in ['train.jsonl','dev.jsonl','test.jsonl','train_future.jsonl','train_present.jsonl','train_passive.jsonl','train_seen_combo.jsonl','dev_future.jsonl','dev_present.jsonl','dev_passive.jsonl','dev_seen_combo.jsonl','test_heldout_combo.jsonl']:continue
  files.append(p)
  for line in p.read_text().splitlines():
   x=json.loads(line);texts=[x['input']]+x.get('references',[x['reference']]);used.extend(texts)
   for t in texts[1:]:union(norm(texts[0]),norm(t))
 blocked={find(norm(x)) for x in used};groups=collections.defaultdict(dict);splits=collections.defaultdict(set)
 for r in raw:
  gid=find(norm(r['source']));splits[gid].add(r['original_split'])
  groups[r['original_split'],r['source']][r['code']]=r['target']
 tok=AutoTokenizer.from_pretrained(R/'models/bart-base',local_files_only=True);nlp=spacy.load('en_core_web_sm');reasons=collections.Counter();candidates=[];seen=set()
 for (split,src),targets in sorted(groups.items()):
  gid=find(norm(src))
  if gid in blocked:reasons[split+'_previously_used_component']+=1;continue
  if len(splits[gid])>1:reasons[split+'_cross_split_component']+=1;continue
  if not all(k in targets for k in ['10','01','11']):
   reasons[split+'_missing_targets']+=1
   if not args.include_incomplete_targets:continue
   targets={**{'10':'','01':'','11':''},**targets}
  d=nlp(src);roots=[t for t in d if t.dep_=='ROOT'];root=roots[0] if len(roots)==1 else None
  sub=[t for t in d if root is not None and t.head==root and t.dep_=='nsubj'];obj=[t for t in d if root is not None and t.head==root and t.dep_ in ['dobj','obj']]
  if root is None or root.pos_!='VERB' or len(sub)!=1 or len(obj)!=1 or any(t.dep_ in ['auxpass','nsubjpass'] for t in d):reasons[split+'_no_simple_active_transitive']+=1;continue
  if any(t.dep_ in ['ccomp','xcomp','relcl','advcl','conj','csubj'] for t in d):reasons[split+'_clause_or_coordination']+=1;continue
  if root.lemma_.lower() in {'have','own','possess','contain','cost','lack','resemble','become','fit','weigh','mean','make','take','give','do','get','keep','hold','set'}:reasons[split+'_possession_or_lightverb_risk']+=1;continue
  if any(e.label_ in ['DATE','TIME'] for e in d.ents) or re.search(r'\b(yesterday|ago|last|previously|formerly|earlier|already|once)\b',src,re.I):reasons[split+'_time_conflict_risk']+=1;continue
  if len(d)>25 or max(len(tok(t)['input_ids']) for t in [src]+[targets[k] for k in ['10','01','11']])>96:reasons[split+'_length']+=1;continue
  if gid in seen:continue
  seen.add(gid);candidates.append({'source_id':sha(norm(src)),'group_id':sha(gid),'original_split':split,'source':src,'future_target':targets['10'],'passive_target':targets['01'],'combo_target':targets['11'],'agent_head_draft':sub[0].text,'verb_lemma_draft':root.lemma_,'patient_head_draft':obj[0].text})
 # High similarity to any previously used source or target is excluded.
 if candidates:
  used=sorted(set(used));v=TfidfVectorizer(analyzer='char_wb',ngram_range=(3,5));m=v.fit_transform(used+[x['source'] for x in candidates]);sim=(m[len(used):]@m[:len(used)].T).tocoo();bad={int(i) for i,j,s in zip(sim.row,sim.col,sim.data) if s>=.92 and min(len(candidates[i]['source']),len(used[j]))/max(len(candidates[i]['source']),len(used[j]))>=.8};reasons['near_previous_source_or_target']=len(bad);candidates=[x for i,x in enumerate(candidates) if i not in bad]
 random.Random(42).shuffle(candidates)
 for i,r in enumerate(candidates):r['candidate_id']=f'C{i+1:04d}'
 fields=['candidate_id','source_id','group_id','original_split','source','future_target','passive_target','combo_target','agent_head_draft','verb_lemma_draft','patient_head_draft','source_valid','future_valid','passive_valid','combo_valid','time_compatible','roles_unambiguous','human_reviewer','reviewed_at','notes']
 with (P/'task_review_candidates.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(candidates)
 (P/'candidates.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in candidates))
 result={'status':'candidate_only_NOT_human_verified_NOT_frozen','candidate_counts':dict(collections.Counter(x['original_split'] for x in candidates)),'requested':{'dev':40,'test':100},'exclusions':dict(reasons),'all_prior_A_B_sources_and_targets_excluded_by_component':True,'previous_B_100_groups_excluded':True,'previous_63_ids':'not provided; prior B100 excluded in entirety, external sources require explicit list','includes_TFU_source_pool':args.include_tfu_sources,'includes_missing_target_candidates':args.include_incomplete_targets,'parser_filter_is_not_human_review':True,'seed':42,'files':{str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}
 (P/'candidate_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
