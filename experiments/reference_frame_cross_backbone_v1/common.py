import json,hashlib,csv
from pathlib import Path
from datetime import date,timedelta
from semantics_v1 import score as v1score,parse,select_operation,text_rule,FIELDS
from renderer_v1 import render,FAMILIES
ROOT=Path(__file__).resolve().parent
V1=ROOT.parent/'reference_frame_pilot_v1'
REPO=ROOT.parents[1]
OPS=['T_plus','T_minus','P_13','P_31']
ATOMIC={'T_plus_first':['T_plus'],'T_plus_third':['T_plus'],'T_minus_first':['T_minus'],'T_minus_third':['T_minus'],'P_13_first':['P_13'],'P_31_third':['P_31']}
CHAINS={'plus_plus':['T_plus','T_plus'],'minus_minus':['T_minus','T_minus'],'plus_minus':['T_plus','T_minus'],'minus_plus':['T_minus','T_plus'],'plus_person':['T_plus','P_13'],'person_plus':['P_13','T_plus'],'person_return':['P_13','P_31'],'plus3':['T_plus']*3,'minus3':['T_minus']*3}
TIME2=['plus_plus','minus_minus','plus_minus','minus_plus']
NONDATE=[k for k in FIELDS if k!='event_date']
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(path,obj):
 p=ROOT/path;p.parent.mkdir(parents=True,exist_ok=True);q=p.with_suffix(p.suffix+'.tmp');q.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n');q.replace(p)
def write(path,rows):
 p=ROOT/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows))
def read(path):return [json.loads(l) for l in (ROOT/path).read_text().splitlines()]
def csvwrite(path,rows):
 if not rows:return
 p=ROOT/path;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def frame(w,offset,perspective='first'):
 return {'view_date':(date.fromisoformat(w['event_date'])-timedelta(days=offset)).isoformat(),'perspective':perspective}
def advance(c,op):
 c=c.copy()
 if op.startswith('T'):c['view_date']=(date.fromisoformat(c['view_date'])+timedelta(days=1 if op=='T_plus' else -1)).isoformat()
 else:
  assert c['perspective']==('first' if op=='P_13' else 'third');c['perspective']='third' if op=='P_13' else 'first'
 return c
def offset_at(w,c):return (date.fromisoformat(w['event_date'])-date.fromisoformat(c['view_date'])).days
def valid(w,frames):return all(c['view_date']>=w['record_date'] and -4<=offset_at(w,c)<=4 for c in frames)
def eligible(w,ops,offset,perspective='first'):
 cs=[frame(w,offset,perspective)]
 for op in ops:cs.append(advance(cs[-1],op))
 return valid(w,cs)
def source_support(w,op,offset,extent):
 if op.startswith('P'):extent=2
 if not -extent<=offset<=extent:return False
 p='third' if op=='P_31' else 'first'
 return eligible(w,[op],offset,p)
def make_row(w,path,ops,offset,perspective='first',tag=''):
 cs=[frame(w,offset,perspective)]
 for op in ops:
  cs.append(advance(cs[-1],op));assert select_operation(cs[-2],cs[-1])==op
 assert valid(w,cs)
 offsets=[offset_at(w,c) for c in cs]
 return dict(row_id=f"{w['record_id']}/{path}/{offset}/{perspective}{tag}",record_id=w['record_id'],split=w['split'],path=path,operations=ops,source_text=render(w,cs[0]),target_text=render(w,cs[-1]),gold_step_texts=[render(w,c) for c in cs[1:]],frames=cs,offsets=offsets,source_support_G0=[source_support(w,op,d,2) for op,d in zip(ops,offsets)],source_support_G1=[source_support(w,op,d,3) for op,d in zip(ops,offsets)],record_status=w['record_status'],polarity=w['polarity'],template_family=w['template_family'])
def score(text,c,w,ended=True):
 out=v1score(text,c,w,ended);p=out['parsed'];nondate=p is not None and all(p[k]==w[k] for k in NONDATE)
 out.update(date_ok=p is not None and p['event_date']==w['event_date'],perspective_ok=p is not None and p['perspective']==c['perspective'],nondate_facts_ok=nondate,normal_end=bool(ended),parsed_nondate_error=p is not None and not nondate,parsed_date_error=p is not None and p['event_date']!=w['event_date'])
 return out

V2=ROOT.parent/'reference_frame_pilot_v2'

V3=ROOT.parent/'reference_frame_pilot_v3'
MODELS=['flan-t5-base','t5gemma-2-270m-270m','flan-t5-large','t5gemma-2b-2b-ul2-it']
