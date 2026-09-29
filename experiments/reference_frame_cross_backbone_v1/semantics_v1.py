"""Independent interpretation of controlled English; no gold renderer imports."""
import re
from datetime import date, timedelta
NUMBERS=dict(zip('one two three four five six seven eight nine'.split(),range(1,10)))
NAMES=['Alice','Bob','Carol','David','Emma','Frank','Grace','Henry']
ACTIONS={'send':'sending','deliver':'delivering','bring':'bringing','give':'giving'}
OBJECTS=['sensor','book','parcel','ticket']
REL={'four days ago':-4,'three days ago':-3,'two days ago':-2,'yesterday':-1,'today':0,'tomorrow':1,'in two days':2,'in three days':3,'in four days':4}
# These grammars consume all text. Unconsumed assertions are unresolved, not silently ignored.
WRAPPERS=[
 r'The record (?:describes|mentions|documents) (?P<e>.+), with the event dated (?P<t>{rel})',
 r'(?:For|As for) an event dated (?P<t>{rel}), the record (?:describes|mentions) (?P<e>.+)',
 r'According to the record, (?P<e>.+) concerns an event dated (?P<t>{rel})',
 r'(?P<e>.+), with the event dated (?P<t>{rel}), is described in the record',
 r'The record contains an account of (?P<e>.+), with the event dated (?P<t>{rel})',
 r'In the record, (?P<e>.+) has an event date of (?P<t>{rel})',
 r'The subject of the record is (?P<e>.+), with the event dated (?P<t>{rel})',
 r'The event is dated (?P<t>{rel}) in the record describing (?P<e>.+)',
 r'What the record describes for an event dated (?P<t>{rel}) is (?P<e>.+)',
 r'It is (?P<e>.+) that the record describes for an event dated (?P<t>{rel})',
 r'As described in the record, (?P<e>.+) has the event dated (?P<t>{rel})',
 r'The event date assigned in the record to (?P<e>.+) is (?P<t>{rel})',
 # Accepted alternatives not used by the renderer.
 r'The record refers to (?P<e>.+) on (?P<t>{rel})',
 r'On (?P<t>{rel}), the record describes (?P<e>.+)',
]
def parse(text,frame):
 s=' '.join(text.strip().split()).replace('’',"'")
 h=re.fullmatch(r'Author: (\w+)\. Record date: (\d{4}-\d{2}-\d{2})\. (.+)',s)
 if not h:return None,'header_or_extra_text'
 author,rd,body=h.groups()
 if author not in NAMES:return None,'unknown_author'
 disclaimer=' This record does not establish that the event occurred.'
 has_disclaimer=body.endswith(disclaimer)
 if has_disclaimer:body=body[:-len(disclaimer)]
 if not body.endswith('.'):return None,'sentence_boundary'
 body=body[:-1]
 rel='|'.join(sorted(map(re.escape,REL),key=len,reverse=True))
 match=None
 for grammar in WRAPPERS:
  match=re.fullmatch(grammar.format(rel=rel),body,re.I)
  if match:break
 if not match:return None,'unsupported_clause_or_additional_assertion'
 event=match['e']
 names='|'.join(NAMES)
 clause=re.fullmatch(rf"(?P<owner>my|(?:{names})'s) (?P<status>cancelled plan to|plan to|report of) (?P<negative>not )?(?P<verb>send|deliver|bring|give|sending|delivering|bringing|giving) (?P<num>one|two|three|four|five|six|seven|eight|nine|[1-9]) (?P<object>sensor|book|parcel|ticket)s? to (?P<recipient>{names})",event,re.I)
 if not clause:return None,'unsupported_event_or_roles'
 d=clause.groupdict(); owner=d['owner'];first=owner.lower()=='my'
 actor=author if first else next(n for n in NAMES if n.lower()==owner[:-2].lower())
 status={'plan to':'recorded_plan','cancelled plan to':'reported_cancelled','report of':'reported_completed'}[d['status'].lower()]
 verb=d['verb'].lower()
 if status=='reported_completed' and verb not in ACTIONS.values():return None,'completion_grammar'
 if status!='reported_completed' and verb not in ACTIONS:return None,'plan_grammar'
 if status!='reported_completed' and not has_disclaimer:return None,'missing_evidence_scope'
 if status=='reported_completed' and has_disclaimer:return None,'conflicting_evidence_scope'
 action=next((k for k,v in ACTIONS.items() if v==verb),verb)
 try:ed=(date.fromisoformat(frame['view_date'])+timedelta(days=REL[match['t'].lower()])).isoformat();date.fromisoformat(rd)
 except ValueError:return None,'invalid_date'
 return dict(author=author,actor=actor,recipient=d['recipient'].title(),action=action,object=d['object'].lower(),quantity=NUMBERS.get(d['num'].lower(),int(d['num']) if d['num'].isdigit() else None),record_date=rd,event_date=ed,record_status=status,polarity='negative' if d['negative'] else 'positive',attribution=author,perspective='first' if first else 'third'),None
FIELDS='author actor recipient action object quantity record_date event_date record_status polarity attribution'.split()
def score(text,frame,world,ended=True):
 p,reason=parse(text,frame)
 content=p is not None and all(p[k]==world[k] for k in FIELDS)
 # Reference-date movement is measured through event-day interpretation, plus perspective.
 frame_ok=p is not None and p['event_date']==world['event_date'] and p['perspective']==frame['perspective']
 plan_completed=world['record_status']=='recorded_plan' and ((p is not None and p['record_status']=='reported_completed') or bool(re.search(r'\b(?:has|have|had) (?:sent|delivered|brought|given)\b|\b(?:I|Alice|Bob|Carol|David|Emma|Frank|Grace|Henry) (?:sent|delivered|brought|gave)\b',text)))
 return dict(frame_ok=frame_ok,content_ok=content,readable=p is not None,joint_ok=bool(frame_ok and content and ended),collateral_error=bool(frame_ok and not content),plan_to_completed=bool(plan_completed),parse_unresolved=p is None,uncertain_reason=reason,parsed=p,hit_length_limit=not ended)
def select_operation(source,target):
 delta=(date.fromisoformat(target['view_date'])-date.fromisoformat(source['view_date'])).days
 if source['perspective']==target['perspective'] and abs(delta)==1:return 'T_plus' if delta==1 else 'T_minus'
 if delta==0 and source['perspective']!=target['perspective']:return 'P_13' if source['perspective']=='first' else 'P_31'
 raise ValueError('Not an atomic permitted operation')
def text_rule(text,source,target):
 # Interpret source without W; make local replacements without calling gold rendering.
 p,err=parse(text,source)
 if err:return text,err
 select_operation(source,target)
 delta=(date.fromisoformat(p['event_date'])-date.fromisoformat(target['view_date'])).days
 relative=next((s for s,v in REL.items() if v==delta),None)
 if relative is None:return text,'relative_date_out_of_range'
 pattern=r'\b(?:'+'|'.join(sorted(map(re.escape,REL),key=len,reverse=True))+r')\b'
 out=re.sub(pattern,relative,text,flags=re.I)
 if source['perspective']!=target['perspective']:
  if target['perspective']=='third':out=re.sub(r'\bmy\b',p['author']+"'s",out,flags=re.I)
  else:out=out.replace(p['author']+"'s",'my')
 return out,None
