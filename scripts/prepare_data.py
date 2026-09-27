import json,hashlib,re,random,collections
from pathlib import Path
from transformers import AutoTokenizer
from sklearn.feature_extraction.text import TfidfVectorizer
ROOT=Path(__file__).resolve().parents[1]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def norm(s): return re.sub(r'\W+',' ',s.lower()).strip()
def write(p,rows): p.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows))
def main():
 tok=AutoTokenizer.from_pretrained(ROOT/'models/bart-base',local_files_only=True)
 lines=(ROOT/'data/fulldata.h16').read_text().splitlines(); rows=[]
 for i,line in enumerate(lines):
  if re.fullmatch(r'TFU\d+',line):
   rows.append(dict(original_id=line,input=lines[i+1],reference=lines[i+2]))
 n=len(rows); stats={'raw_pairs':n,'license':'CC BY 4.0','source':'https://github.com/lvyiwei1/StylePTB','revision':json.load(open(ROOT/'data/styleptb_revision.json'))['sha'],'raw_sha256':sha(ROOT/'data/fulldata.h16')}
 groups={s:{} for s in ['train','dev','test']}; excluded=collections.Counter()
 for i,row in enumerate(rows):
  split='dev' if i<n//20 else ('test' if i<n//10 else 'train')
  k=norm(row['input']); lens=[len(tok(t)['input_ids']) for t in [row['input'],row['reference']]]
  if max(lens)>96: excluded[split+'_length']+=1;continue
  if not k: excluded[split+'_empty']+=1;continue
  if k in groups[split]: groups[split][k]['references'].append(row['reference']);excluded[split+'_grouped']+=1;continue
  row.update(source_id=hashlib.sha256(k.encode()).hexdigest()[:20],split=split,task='StylePTB_TFU',references=[row['reference']],token_lengths=lens)
  groups[split][k]=row
 # Preserve official splits and protect test from leakage; never move rows.
 kept=[]; splitrows={}; collisions=[]
 for split in ['test','dev','train']:
  items=list(groups[split].values()); keys=[norm(x['input']) for x in items]
  prior={norm(x['input']) for x in kept}
  filtered=[]
  if kept and items:
   vectorizer=TfidfVectorizer(analyzer='char_wb',ngram_range=(3,5),min_df=1)
   mat=vectorizer.fit_transform([x['input'].lower() for x in kept+items])
   left=mat[:len(kept)]; right=mat[len(kept):]
   # sparse pairwise product; only report high similarities, no full dense N^2.
   sim=(right@left.T).tocoo(); bad=set()
   for a,b,v in zip(sim.row,sim.col,sim.data):
    if v>=.92 and min(len(items[a]['input']),len(kept[b]['input']))/max(len(items[a]['input']),len(kept[b]['input']))>=.8:
     bad.add(int(a));collisions.append({'removed':items[a]['source_id'],'protected':kept[b]['source_id'],'cosine':float(v),'split':split})
   for j,row in enumerate(items):
    if keys[j] in prior or j in bad: excluded[split+'_cross_split_duplicate']+=1
    else: filtered.append(row)
  else: filtered=items
  splitrows[split]=filtered; kept+=filtered
 rng=random.Random(42)
 for split,cap in [('train',5000),('dev',500),('test',1000)]:
  items=splitrows[split]; stats[split+'_eligible']=len(items)
  if len(items)>cap: items=rng.sample(items,cap)
  items=sorted(items,key=lambda x:x['source_id']);write(ROOT/f'data/{split}.jsonl',items)
  stats[split]={'n':len(items),'sha256':sha(ROOT/f'data/{split}.jsonl'),'max_tokens':max(max(x['token_lengths']) for x in items)}
 ids=[{x['source_id'] for x in splitrows[s]} for s in ['train','dev','test']]
 assert all(not (ids[a]&ids[b]) for a,b in [(0,1),(0,2),(1,2)])
 stats['exclusions']=dict(excluded);stats['split_algorithm']='official checkout order: dev <N//20; test <N//10; remaining train';stats['seed']=42
 (ROOT/'data/manifest.json').write_text(json.dumps(stats,indent=2));write(ROOT/'data/near_duplicates.jsonl',collisions)
 print(json.dumps(stats,indent=2))
if __name__=='__main__':main()
