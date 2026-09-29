import collections,random
from common import *
CROSS=ROOT.parent/'reference_frame_cross_backbone_v1'
NAME='t5gemma-2b-2b-ul2-it'
ORDERS={'T_then_P':['T_plus','P_13'],'P_then_T':['P_13','T_plus']}
SEED=2026092905
def world_key(w):return json.dumps({k:w[k] for k in FIELDS},sort_keys=True)
def support_counts():
 return collections.Counter((r['operations'][0],r['offsets'][0],r['record_status'],r['polarity'],r['frames'][0]['perspective']) for r in read(CROSS/'data/train_G1.jsonl'))
def joint_row(w,off,support):
 orders={}
 for name,ops in ORDERS.items():
  if not eligible(w,ops,off):return None
  r=make_row(w,name,ops,off)
  keys=[(op,d,w['record_status'],w['polarity'],c['perspective']) for op,d,c in zip(ops,r['offsets'],r['frames'])]
  if not all(support[k]>0 for k in keys):return None
  r['actual_training_support_counts']=[support[k] for k in keys];orders[name]=r
 a,b=orders.values();assert a['source_text']==b['source_text'] and a['frames'][-1]==b['frames'][-1] and a['target_text']==b['target_text']
 return dict(row_id=f"{w['record_id']}/joint/{off}",record_id=w['record_id'],split=w['split'],source_text=a['source_text'],target_text=a['target_text'],source_frame=a['frames'][0],target_frame=a['frames'][-1],source_offset=off,record_status=w['record_status'],polarity=w['polarity'],template_family=w['template_family'],orders=orders)
def metric(text,c,w,ended):
 s=score(text,c,w,ended);p=s['parsed'];s['person_ok']=s['perspective_ok'];s['field_ok']={f:p is not None and p[f]==w[f] for f in NONDATE};return s
def worlds():return {w['record_id']:w for p in (ROOT/'data').glob('*worlds.jsonl') for w in read(p)}
def assert_lock():
 lock=json.loads((ROOT/'data/lock.json').read_text())
 for f,h in lock['files'].items():assert digest(ROOT/f)==h,f
 return lock
