"""Position diagnostics; primary scientific modules are left unchanged."""
import re
from datetime import date,timedelta

def prepare_world(w):
    w=dict(w)
    if w['domain']=='time':w['quote_date']=(date.fromisoformat(w['event_date'])-timedelta(days=3)).isoformat()
    return w

def make_functions(base_gold,base_render,base_score):
    def gold(w,state,variant=0,symbolic=False):
        assert variant in (0,1) and not symbolic
        structure=5 if w['domain']=='time' else 4
        g=base_gold(w,state,structure,False);g['foil_variant']=variant
        if w['domain']=='time':g['foil_quote']=f"The {w['object']} event is dated three days from now."
        return g
    def render(w,state,variant=0,symbolic=False):
        assert not symbolic and variant in (0,1)
        d=w['domain'];text=base_render(w,state,5 if d=='time' else 4,False)
        if d=='time':
            quote=f"The {w['object']} event is dated three days from now."
            text=text.replace('The event is tomorrow.',quote)
            if variant:
                match=re.search(r' On \d{4}-\d{2}-\d{2}, [A-Za-z]+ said to [A-Za-z]+, "[^"]*"$',text);assert match
                text=match[0].strip()+' '+text[:match.start()].strip()
        elif d=='person' and variant:
            match=re.search(r' [A-Za-z]+ said to [A-Za-z]+, "[^"]*"$',text);assert match
            text=match[0].strip()+' '+text[:match.start()].strip()
        elif d=='space' and variant:
            match=re.match(r"(Observer: [A-Za-z]+\. The [a-z]+ is [^.]+\.) (.*)",text);assert match
            text=match[2]+' '+match[1]
        elif d=='emotion' and variant:
            match=re.match(r"(Focus: [A-Za-z]+'s view of the [a-z]+\.) ([^.]+\.) ([^.]+\.) (.*)",text);assert match
            # Same evaluator's other object first, then the other evaluator,
            # then the target evaluation. No actor/object inference from order.
            tail=re.search(r' ([A-Za-z]+ dislikes the [a-z]+\.)$',match[4]);assert tail
            facts=match[4][:tail.start()]
            text=' '.join((match[1],tail[1],match[3],match[2],facts))
        return text
    def score(text,g,w,ended=True):
        if g['domain']!='time':return base_score(text,g,w,ended)
        quotes=list(re.finditer(r'"([^"]*)"',text));valid=len(quotes)==1 and re.sub(r'\s+',' ',quotes[0][1].strip()).lower()==g['foil_quote'].lower()
        if len(quotes)==1:
            q=quotes[0];adapted=text[:q.start(1)]+'The event is tomorrow.'+text[q.end(1):]
        else:adapted=text
        result=base_score(adapted,g,w,ended)
        if not valid:
            result=dict(result,success=False,scope=False,preserved=False)
        return result
    return gold,render,score
