"""Conservative three-way surface grammar, without gold/domain completeness.

True: all emitted clauses recognized and agreement/case licensed. False: a
recognized clause has an explicit agreement/case error. None: outside coverage.
This is a finite controlled-English check, not a general English grammar judge.
"""
import re
from functools import lru_cache

N=r'[a-z]+'
NP=r'(?:the [a-z]+|it)'
POS=r"(?:my|your|his|her|[a-z]+'s)"
SUB=r'(i|you|he|she|[a-z]+)'
OBJ=r'(me|you|him|her|[a-z]+)'
REL=r'(?:three days ago|two days ago|yesterday|today|tomorrow|two days from now|three days from now|three days before this anchor|two days before this anchor|one day before this anchor|one day after this anchor|on this day|two days after this anchor|three days after this anchor|a day ago)'
NAMES={'alice','bob','carol','david','emma','frank','grace','henry'}
PLAIN_SUBJECTS={'i','you','we','they'}
BAD_SUBJECTS={'me','him','her','my','your','us','them','our','their'}
BAD_OBJECTS={'i','he','she','we','they','my','your','our','their'}

def licensed_subject(subject):return subject in NAMES or subject in PLAIN_SUBJECTS or subject in ('he','she','it')

def agreement(subject,verb,base):
    if subject in BAD_SUBJECTS:return False
    if not licensed_subject(subject):return None
    return verb==(base if subject in PLAIN_SUBJECTS else base+'s')

def clause(c):
    c=c.strip()
    if not c:return True,False
    if re.fullmatch(r"(?:observer|speaker|listener|narrator): "+N,c) or re.fullmatch(r"focus: "+N+r"'s view of the "+N,c):return True,False
    plain=[r'the '+N+r' is (?:blue|red|green|white|black)',r'its status is (?:planned|completed|cancelled)',r'its absolute date is \d{4}-\d{2}-\d{2}',r'it is two days after the fixed launch',r'its world direction is (?:east|west|north|south)',r'the '+N+r' is north of the marker',r'(?:the '+N+r' event is dated|the date of the '+N+r' event is) '+REL,r'the event is '+REL,r'the (?:giver|recipient|owner) is '+N,r'it is the '+N,r'(?:on \d{4}-\d{2}-\d{2}, )?'+N+r' said(?: to '+N+r')?, QUOTE']
    if any(re.fullmatch(p,c) for p in plain):return True,True
    m=re.fullmatch(r'there (is|are) ([1-9]) (copy|copies)',c)
    if m:return (m[1]=='is' and m[2]=='1' and m[3]=='copy') or (m[1]=='are' and m[2]!='1' and m[3]=='copies'),True
    spatial=[r'the '+N+r' is (?:in front of me|behind me|to my (?:right|left))',r"from "+N+r"'s viewpoint, (?:the "+N+r'|it) is on the (?:front|right|back|left) side',r'i see the '+N+r'(?: that is)? (?:ahead(?: of me)?|behind(?: me)?|in front of me|(?:to|on) (?:my|the) (?:front|back|left|right))']
    if any(re.fullmatch(p,c) for p in spatial):return True,True
    # Role binding and gender are semantics, not this syntax check.
    m=re.fullmatch(SUB+r' (give|gives) '+OBJ+' '+POS+' '+N,c)
    if m:return (False if m[3] in BAD_OBJECTS else agreement(m[1],m[2],'give')),True
    m=re.fullmatch(POS+' '+N+r' is what '+SUB+r' (give|gives) '+OBJ,c)
    if m:return (False if m[3] in BAD_OBJECTS else agreement(m[1],m[2],'give')),True
    m=re.fullmatch(SUB+r' (receive|receives) '+POS+' '+N+' from '+OBJ,c)
    if m:return (False if m[3] in BAD_OBJECTS else agreement(m[1],m[2],'receive')),True
    m=re.fullmatch(SUB+r' (keep|keeps) '+POS+r' key for (?:myself|yourself|herself|himself)',c)
    if m:return agreement(m[1],m[2],'keep'),True
    m=re.fullmatch(SUB+r' (see|sees) '+N+' and '+N,c)
    if m:return agreement(m[1],m[2],'see'),True
    # Exact aspect/degree distinctions are left to the semantic scorer.
    c=re.sub(r'^as for the '+N+r', ','',c)
    m=re.fullmatch(SUB+r' (?:strongly )?(like|likes|dislike|dislikes|detest|detests|hate|hates|love|loves|adore|adores) (?:the '+N+r'|it)',c)
    if m:return agreement(m[1],m[2],m[2][:-1] if m[2].endswith('s') else m[2]),True
    m=re.fullmatch(SUB+r' (am|is|are) neutral about (?:the '+N+r'|it)',c)
    if m:return (False if m[1] in BAD_SUBJECTS else m[2]==('am' if m[1]=='i' else 'are' if m[1] in PLAIN_SUBJECTS else 'is') if licensed_subject(m[1]) else None),True
    m=re.fullmatch(SUB+r' (have|has) (?:no preference about|a (?:negative|positive) opinion of) (?:the '+N+r'|it)',c)
    if m:return (False if m[1] in BAD_SUBJECTS else m[2]==('have' if m[1] in PLAIN_SUBJECTS else 'has') if licensed_subject(m[1]) else None),True
    m=re.fullmatch(SUB+r' (do|does) not (like|likes|dislike|dislikes) (?:the '+N+r'|it)(?: at all)?',c)
    if m:return (False if m[1] in BAD_SUBJECTS else m[2]==('do' if m[1] in PLAIN_SUBJECTS else 'does') and not m[3].endswith('s') if licensed_subject(m[1]) else None),True
    m=re.fullmatch(SUB+r' neither (like|likes) nor (dislike|dislikes) (?:the '+N+r'|it)',c)
    if m:return agreement(m[1],m[2],'like') and agreement(m[1],m[3],'dislike'),True
    if ' and ' in c or ' but ' in c:
        parts=re.split(r' (?:and|but) ',c);rr=[clause(p) for p in parts]
        if all(x[1] for x in rr):return (False if any(x[0] is False for x in rr) else True if all(x[0] is True for x in rr) else None),True
    return None,False

@lru_cache(maxsize=16384)
def surface_grammar(text):
    t=re.sub(r'\s+',' ',text.strip().replace('\u2019',"'")).lower()
    if not t:return None
    quoted=re.findall(r'"([^\"]*)"',t)
    if t.count('"')!=2*len(quoted):return None
    qq=[surface_grammar(q) for q in quoted]
    outer=re.sub(r'"[^\"]*"','QUOTE',t)
    rr=[clause(c) for c in re.split(r'[.;]\s*',outer) if c.strip()]
    if any(r[0] is False for r in rr) or any(q is False for q in qq):return False
    if rr and any(r[1] for r in rr) and all(r[0] is True for r in rr) and all(q is True for q in qq):return True
    return None
