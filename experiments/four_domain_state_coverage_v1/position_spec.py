"""Position diagnostics; primary scientific modules are left unchanged."""
import re
from datetime import date,timedelta

def prepare_world(w):
    w=dict(w)
    if w['domain']=='time':w['quote_date']=(date.fromisoformat(w['event_date'])-timedelta(days=3)).isoformat()
    return w

def make_functions(base_gold,base_render,base_score):
    def gold(w,state,variant=0,symbolic=False):
        assert variant in (range(4) if w['domain']=='emotion' else range(2)) and not symbolic
        structure=5 if w['domain']=='time' or (w['domain']=='emotion' and variant>=2) else 4
        g=base_gold(w,state,structure,False);g['foil_variant']=variant
        if w['domain']=='time':g['foil_quote']=f"The {w['object']} event is dated three days from now."
        if w['domain']=='emotion' and variant>=2:g['foil_narrator']=w['focus']
        return g
    def render(w,state,variant=0,symbolic=False):
        assert not symbolic and variant in (range(4) if w['domain']=='emotion' else range(2))
        d=w['domain'];text=base_render(w,state,5 if d=='time' or (d=='emotion' and variant>=2) else 4,False)
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
        elif d=='emotion' and variant==1:
            match=re.match(r"(Focus: [A-Za-z]+'s view of the [a-z]+\.) ([^.]+\.) ([^.]+\.) (.*)",text);assert match
            # Same evaluator's other object first, then the other evaluator,
            # then the target evaluation. No actor/object inference from order.
            tail=re.search(r' ([A-Za-z]+ dislikes the [a-z]+\.)$',match[4]);assert tail
            facts=match[4][:tail.start()]
            text=' '.join((match[1],tail[1],match[3],match[2],facts))
        elif d=='emotion' and variant>=2:
            named=['strongly dislikes','dislikes','is neutral about','likes','strongly likes'][state]
            first=['strongly dislike','dislike','am neutral about','like','strongly like'][state]
            target=f"{w['focus']} {named} the {w['object']}.";assert target in text
            text=f"Narrator: {w['focus']}. "+text.replace(target,f"I {first} the {w['object']}.",1)
            if variant==3:
                q=re.search(r' [A-Za-z]+ said, "[^"]*"$',text);assert q
                text=q[0].strip()+' '+text[:q.start()].strip()
        return text
    def score(text,g,w,ended=True):
        if g.get('foil_narrator'):
            from narrator_scope_score import score_narrator
            return score_narrator(text,g,w,ended,base_score)
        if g['domain']!='time':
            result=base_score(text,g,w,ended)
            if g['domain']=='space':
                from space_scope_guard import valid_target_relation,valid_non_target_relations
                if not valid_target_relation(text,g,w):result=dict(result,success=False,target=False,scope=False)
                if not valid_non_target_relations(text,g,w):result=dict(result,success=False,preserved=False,scope=False)
            return result
        quotes=list(re.finditer(r'"([^"]*)"',text));valid=len(quotes)==1 and re.sub(r'\s+',' ',quotes[0][1].strip()).lower()==g['foil_quote'].lower()
        if len(quotes)==1:
            q=quotes[0];adapted=text[:q.start(1)]+'The event is tomorrow.'+text[q.end(1):]
        else:adapted=text
        result=base_score(adapted,g,w,ended)
        if not valid:
            result=dict(result,success=False,scope=False,preserved=False)
        return result
    return gold,render,score
