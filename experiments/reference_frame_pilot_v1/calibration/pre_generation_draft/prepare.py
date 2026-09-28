import json,random,hashlib
from pathlib import Path
from datetime import date,timedelta
from semantics import score,select_operation,text_rule,parse
ROOT=Path(__file__).resolve().parent
FAMILIES=[
 'The record describes {event} {time}.',
 'For {time}, the record describes {event}.',
 'According to the record, {event} is dated {time}.',
 '{event}, dated {time}, is described in the record.',
 'The record contains an account of {event} {time}.',
 'In the record, {time} is the date of {event}.',
 'The subject of the record is {event} {time}.',
 '{time} is when the record places {event}.',
 'What the record describes for {time} is {event}.',
 'It is {event} that the record describes for {time}.',
 'As described in the record, {event} has the date {time}.',
 'The date assigned in the record to {event} is {time}.',
]
# Renderer constants intentionally independent of parser constants.
REL={-4:'four days ago',-3:'three days ago',-2:'two days ago',-1:'yesterday',0:'today',1:'tomorrow',2:'in two days',3:'in three days',4:'in four days'}
WORDS=['zero','one','two','three','four','five','six','seven','eight','nine']
GERUND={'send':'sending','give':'giving','bring':'bringing','deliver':'delivering'}
def dump(path,obj):
 p=ROOT/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')
def write(path,rows):
 p=ROOT/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in rows))
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def frame(w,offset=0,perspective='first'):
 return {'view_date':(date.fromisoformat(w['c0'])+timedelta(days=offset)).isoformat(),'perspective':perspective}
def render(w,c,compact=False):
 owner='my' if c['perspective']=='first' else w['author']+"'s"
 status={'recorded_plan':'plan to','reported_completed':'report of','reported_cancelled':'cancelled plan to'}[w['record_status']]
 verb=GERUND[w['action']] if w['record_status']=='reported_completed' else w['action']
 event=f"{owner} {status} {'not ' if w['polarity']=='negative' else ''}{verb} {WORDS[w['quantity']]} {w['object']}{'s' if w['quantity']!=1 else ''} to {w['recipient']}"
 relative=REL[(date.fromisoformat(w['event_date'])-date.fromisoformat(c['view_date'])).days]
 body=FAMILIES[w['template_family']].format(event=event,time=relative)
 body=body[0].upper()+body[1:]
 disclaimer='' if w['record_status']=='reported_completed' else ' This record does not establish that the event occurred.'
 return f"Author: {w['author']}. Record date: {w['record_date']}. {body}{disclaimer}"
def worlds(split,n,seed,used):
 rng=random.Random(seed);out=[]
 for i in range(n):
  while True:
   author,recipient=rng.sample(['Alice','Bob','Carol','David','Emma','Frank','Grace','Henry'],2)
   rd=date(2026,7,1)+timedelta(days=rng.randrange(85));c0=rd+timedelta(days=1)
   status=['recorded_plan','reported_completed','reported_cancelled'][i%3]
   offset=rng.choice([-2,-1]) if status=='reported_completed' else [-2,-1,0,1,2][(i//3)%5]
   w=dict(record_id=f'{split}_{i:04d}',split=split,author=author,actor=author,recipient=recipient,action=rng.choice(list(GERUND)),object=rng.choice(['sensor','book','parcel','ticket']),quantity=rng.randrange(1,10),record_date=rd.isoformat(),event_date=(c0+timedelta(days=offset)).isoformat(),record_status=status,polarity='negative' if (i//3)%5==0 else 'positive',attribution=author,c0=c0.isoformat(),template_family=(8+i%4 if split=='test_template_ood' else i%(12 if split.startswith('calibration') else 8)))
   key=json.dumps({k:v for k,v in w.items() if k not in ['record_id','split','template_family','c0']},sort_keys=True)
   if key not in used:used.add(key);break
  assert c0-timedelta(days=1)>=rd
  assert status!='reported_completed' or date.fromisoformat(w['event_date'])<=rd
  out.append(w)
 return out
def pairs(ws):
 out=[]
 for w in ws:
  for offset,p0,p1 in [(1,'first','first'),(1,'third','third'),(-1,'first','first'),(-1,'third','third'),(0,'first','third'),(0,'third','first')]:
   source=frame(w,0,p0);target=frame(w,offset,p1);op=select_operation(source,target)
   out.append(dict(pair_id=w['record_id']+'_'+op+'_'+p0,gold_record_id=w['record_id'],source_text=render(w,source),target_text=render(w,target),allowed_context={'source_frame':source,'target_frame':target},operation_ids=[op],path=op+'_'+p0,template_family=w['template_family']))
 return out
def views(ws):
 return [dict(gold_record_id=w['record_id'],view_id=w['record_id']+f'_{offset}_{p}',source_text=render(w,frame(w,offset,p)),allowed_context={'source_frame':frame(w,offset,p),'target_frame':frame(w,offset,p)},operation_ids=[],path='reconstruction') for w in ws for offset,p in [(0,'first'),(0,'third'),(1,'first'),(1,'third'),(-1,'first'),(-1,'third'),(2,'first')]]
def main():
 assert not (ROOT/'data/split_manifest.json').exists(),'Frozen data exists; do not overwrite'
 used=set();splits={s:worlds(s,n,20260929+j,used) for j,(s,n) in enumerate([('calibration',60),('train',480),('dev',80),('test_iid',80),('test_template_ood',80)])}
 texts={};coverage=rules=0
 for split,ws in splits.items():
  write(f'data/{split}_worlds.jsonl',ws);ps=pairs(ws);write(f'data/{split}_pairs.jsonl',ps);wm={w['record_id']:w for w in ws}
  for row in ps:
   w=wm[row['gold_record_id']];c=row['allowed_context']
   assert score(row['target_text'],c['target_frame'],w)['joint_ok'],row
   coverage+=1
   transformed,err=text_rule(row['source_text'],c['source_frame'],c['target_frame'])
   assert err is None and score(transformed,c['target_frame'],w)['joint_ok'],row
   rules+=1
   for text in [row['source_text'],row['target_text']]:texts.setdefault(' '.join(text.lower().split()),set()).add(split)
  for v in views(ws):assert score(v['source_text'],v['allowed_context']['target_frame'],wm[v['gold_record_id']])['joint_ok']
 write('data/test_worlds.jsonl',splits['test_iid']+splits['test_template_ood'])
 write('data/calibration_views.jsonl',views(splits['calibration']))
 dump('data/template_families.json',{'families':FAMILIES,'train_dev_iid':list(range(8)),'ood':list(range(8,12)),'calibration':list(range(12))})
 collisions=[k for k,v in texts.items() if len(v)>1];assert not collisions
 # Mutation and alternative expression checks, independent of reference exact match.
 w=splits['calibration'][0];c=frame(w);s=render(w,c)
 checks={}
 for key,mut in [('quantity',s.replace(WORDS[w['quantity']],WORDS[1 if w['quantity']!=1 else 2],1)),('recipient',s.replace('to '+w['recipient'],'to '+w['author'])),('date',s.replace(REL[(date.fromisoformat(w['event_date'])-date.fromisoformat(w['c0'])).days],'in four days')),('polarity',s.replace('not ','')),('extra_assertion',s+' Alice sent the sensors.')]:
  checks[key]=not score(mut,c,w)['joint_ok'];assert checks[key],key
 alt=s.replace('The record describes','The record mentions').replace(WORDS[w['quantity']],str(w['quantity']))
 checks['alternative_expression']=score(alt,c,w)['joint_ok'];assert checks['alternative_expression']
 dump('calibration/scorer_checks.json',{'gold_pairs':coverage,'gold_coverage':1.,'text_rule_pairs':rules,'text_rule_joint':1.,'mutation_and_alternative_checks':checks,'human_review':False})
 dump('data/leakage_audit.json',{'semantic_worlds_unique':len(used),'cross_split_normalized_text_collisions':collisions,'record_grouped':True,'template_overlap_train_ood':[],'test_generated_not_evaluated':True})
 dump('data/split_manifest.json',{'seed':20260929,'records':{s:len(w) for s,w in splits.items()},'pairs':{s:6*len(w) for s,w in splits.items()},'files':{p.name:digest(p) for p in sorted((ROOT/'data').glob('*')) if p.is_file()}})
 write('review/calibration_records.jsonl',[dict(world=w,views=[v for v in views([w])]) for w in splits['calibration'][:30]])
 print('Prepared 780 worlds; 100% gold and text-rule checks; no cross-split collisions')
if __name__=='__main__':main()
