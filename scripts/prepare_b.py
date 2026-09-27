"""Official Tense+Voice data, connected-component grouping of ALL variants.
Edges for held-out combinations are used only for grouping, never for fitting.
"""
import json,re,hashlib,collections,random
from pathlib import Path
from transformers import AutoTokenizer
from sklearn.feature_extraction.text import TfidfVectorizer
ROOT=Path(__file__).resolve().parents[1];D=ROOT/'data/b';D.mkdir(exist_ok=True)
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
allrows=[]
for split,fn in [('train','train'),('dev','valid'),('test','test')]:
 for line in (ROOT/f'data/compositions/tense_voice_{fn}.tsv').read_text().splitlines():
  src,tgt=line.split('\t');a,b,src=src.split(' ',2);union(norm(src),norm(tgt));allrows.append({'input':src,'reference':tgt,'code':a+b,'split':split})
for r in allrows:r['group_id']=sha(find(norm(r['input'])))
sets={s:{r['group_id'] for r in allrows if r['split']==s} for s in ['test','dev','train']}
blocked={'test':set(),'dev':sets['test'],'train':sets['test']|sets['dev']}
counts=collections.Counter();tok=AutoTokenizer.from_pretrained(ROOT/'models/bart-base',local_files_only=True)
clean=[]
for r in allrows:
 if r['group_id'] in blocked[r['split']]:counts[r['split']+'_cross_group_removed']+=1;continue
 if max(len(tok(r[k])['input_ids']) for k in ['input','reference'])>96:counts[r['split']+'_length_removed']+=1;continue
 clean.append(r)
# Exclude additional near duplicates across splits based on every input variant.
protected=[];filtered=[]
for split in ['test','dev','train']:
 candidates=[r for r in clean if r['split']==split];bad=set()
 if protected and candidates:
  left=list(dict.fromkeys(r['input'] for r in protected));right=list(dict.fromkeys(r['input'] for r in candidates));v=TfidfVectorizer(analyzer='char_wb',ngram_range=(3,5));mat=v.fit_transform(left+right)
  sim=(mat[len(left):]@mat[:len(left)].T).tocoo();badtext={right[a] for a,b,x in zip(sim.row,sim.col,sim.data) if x>=.92 and min(len(right[a]),len(left[b]))/max(len(right[a]),len(left[b]))>=.8}
  bad={r['group_id'] for r in candidates if r['input'] in badtext}
 kept=[r for r in candidates if r['group_id'] not in bad];counts[split+'_near_removed_rows']=len(candidates)-len(kept);filtered+=kept;protected+=kept
rng=random.Random(42);manifest={'grouping':'union all source/target variants, preserve official splits; test>dev>train; char3-5 near duplicate >=.92 group exclusion','heldout_code':'11 future+passive','seen_training_combination':'31 present+passive','operation_codes':{'future':'10','present':'30','passive':'01'},'seed':42,'exclusions':dict(counts),'files':{}}
def write(name,rr):
 unique={}
 for r in rr:
  k=(r['group_id'],r['input'],r['code']);unique[k]=r
 rr=list(unique.values());rr.sort(key=lambda r:(r['group_id'],r['input']))
 for r in rr:r.update(source_id=sha(r['input']+'|'+r['code']),task='StylePTB_'+r['code'],references=[r['reference']])
 p=D/(name+'.jsonl');p.write_text(''.join(json.dumps(r)+'\n' for r in rr));manifest['files'][name]={'n':len(rr),'groups':len({r['group_id'] for r in rr}),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
for split in ['train','dev']:
 rr=[r for r in filtered if r['split']==split];groups=sorted({r['group_id'] for r in rr});cap=1000 if split=='train' else 100;chosen=set(rng.sample(groups,min(cap,len(groups))))
 for op,code in [('future','10'),('present','30'),('passive','01'),('seen_combo','31')]:
  candidates=[r for r in rr if r['code']==code and r['group_id'] in chosen]
  # One pair per common source group per operation.
  chosenrows={}
  for r in sorted(candidates,key=lambda r:r['input']):chosenrows.setdefault(r['group_id'],r)
  write(split+'_'+op,list(chosenrows.values()))
rr=[r for r in filtered if r['split']=='test' and r['code']=='11'];bygroup={}
for r in sorted(rr,key=lambda r:r['input']):bygroup.setdefault(r['group_id'],r)
rr=sorted(bygroup.values(),key=lambda r:r['group_id'])[:100];write('test_heldout_combo',rr)
assert all(not (set(json.loads(s)['group_id'] for s in (D/'test_heldout_combo.jsonl').read_text().splitlines()) & set(json.loads(s)['group_id'] for s in (D/f'train_{op}.jsonl').read_text().splitlines())) for op in ['future','present','passive','seen_combo'])
(D/'manifest.json').write_text(json.dumps(manifest,indent=2));print(json.dumps(manifest,indent=2))
