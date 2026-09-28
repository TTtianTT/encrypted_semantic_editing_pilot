import json,random,hashlib
from pathlib import Path
from datetime import date,timedelta
from semantics_v1 import score,select_operation,text_rule,parse
ROOT=Path(__file__).resolve().parent
FAMILIES=[
 'The record describes {event}, with the event dated {time}.',
 'For an event dated {time}, the record describes {event}.',
 'According to the record, {event} concerns an event dated {time}.',
 '{event}, with the event dated {time}, is described in the record.',
 'The record contains an account of {event}, with the event dated {time}.',
 'In the record, {event} has an event date of {time}.',
 'The subject of the record is {event}, with the event dated {time}.',
 'The event is dated {time} in the record describing {event}.',
 'What the record describes for an event dated {time} is {event}.',
 'It is {event} that the record describes for an event dated {time}.',
 'As described in the record, {event} has the event dated {time}.',
 'The event date assigned in the record to {event} is {time}.',
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
