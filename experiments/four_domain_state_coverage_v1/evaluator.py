"""Independent finite grammar parser. No imports of gold transitions/rendering.

Unknown expressions are unresolved, not silently discarded. These scores apply to
the declared controlled grammar; manual review remains unlabelled until done.
"""
import re
from datetime import date

def normalize(text):
    return re.sub(r'\s+', ' ', text.strip().replace('\u2019', "'")).lower()

def relative(text):
    aliases={-3:['three days ago','three days before this anchor'], -2:['two days ago','two days before this anchor'], -1:['yesterday','one day before this anchor','a day ago'],0:['today','on this day'],1:['tomorrow','one day after this anchor'],2:['two days from now','two days after this anchor'],3:['three days from now','three days after this anchor']}
    for value,terms in aliases.items():
        if text.strip() in terms:return value
    return None

def stance(phrase):
    aliases={0:['strongly dislikes','detests','hates','does not like it at all'],1:['dislikes','has a negative opinion of','does not like it'],2:['is neutral about','has no preference about','neither likes nor dislikes it'],3:['likes','has a positive opinion of','does not dislike it'],4:['strongly likes','adores','loves','does not dislike it at all']}
    for level,terms in aliases.items():
        if phrase in terms:return level
    return None

def resolve(token, speaker, listener, case):
    token=token.lower()
    if case=='subject' and token in ('me','my','your'):return None
    if case=='object' and token in ('i','my','your'):return None
    if case=='owner' and token in ('i','me','you'):return None
    lookup={'i':speaker,'me':speaker,'my':speaker,'you':listener,'your':listener}
    if token in lookup:return lookup[token]
    if case=='owner' and token.endswith("'s"):return token[:-2]
    if re.fullmatch('[a-z]+',token):return token
    return None

def parse(text, domain, structure, symbolic=False):
    t=normalize(text);p={};grammar=True
    if symbolic:
        pairs=re.findall(r'([a-z_]+)=([^;\.]+)',t)
        if len({k for k,v in pairs})!=len(pairs):return None,False
        p=dict(pairs)
        for k in ('relative','level','other_level','heading','copies'):
            if k in p:
                try:p[k]=int(p[k])
                except ValueError:return None,False
        return p,bool(p)
    # Quotes are separate fixed-context spans, never parsed as external stance/date.
    quotes=re.findall(r'"([^"]*)"',t)
    outer=re.sub(r'"[^"]*"','"QUOTE"',t)
    facts=re.findall(r'the ([a-z]+) is (blue|red|green|white|black)\.',outer)
    if len(facts)!=1:return None,False
    p['object'],p['color']=facts[0]
    quantity=re.search(r'there (?:are ([2-9]) copies|is (1) copy)\.',outer)
    if not quantity:return None,False
    p['quantity']=int(quantity[1] or quantity[2])
    if domain=='time':
        m=re.search(r'(?:the ([a-z]+) event is dated|the date of the ([a-z]+) event is) ([^\.]+)\.',outer)
        status=re.search(r'its status is (planned|completed|cancelled)\.',outer)
        if not m or not status:return None,False
        p.update(event_object=m[1] or m[2],relative=relative(m[3]),status=status[1])
        absolute=re.search(r'its absolute date is (\d{4}-\d{2}-\d{2})\.',outer)
        p['absolute']=absolute[1] if absolute else None
        p['fixed_launch']=bool(re.search(r'it is two days after the fixed launch\.',outer))
        q=re.search(r'on (\d{4}-\d{2}-\d{2}), ([a-z]+) said to ([a-z]+), "QUOTE"',outer)
        p['quote']=(q[1],q[2],q[3],quotes[0]) if q and len(quotes)==1 else None
        grammar=p['relative'] is not None
    elif domain=='space':
        m=re.search(r'observer: ([a-z]+)\.',outer)
        view=re.findall(r"from ([a-z]+)'s viewpoint, (?:the [a-z]+|it) is on the (front|right|back|left) side\.",outer)
        observer=m[1] if m else view[0][0] if view else None
        relation=None
        patterns={'front':[r'is in front of me\.',r'i see the [a-z]+ ahead\.'],'back':[r'is behind me\.',r'i see the [a-z]+ behind\.'],'right':[r'is to my right\.',r'i see the [a-z]+ on my right\.'],'left':[r'is to my left\.',r'i see the [a-z]+ on my left\.']}
        for r,patterns_r in patterns.items():
            if any(re.search(x,outer) for x in patterns_r):relation=r
        if relation is None and view:relation=view[0][1]
        p.update(observer=observer,relation=relation,views=dict(view))
        primary_object=re.search(r'(?:the ([a-z]+) is (?:in front of me|behind me|to my (?:right|left))|i see the ([a-z]+))',outer)
        if primary_object:p['relation_object']=primary_object[1] or primary_object[2]
        elif view:
            firstview=re.search(r"from [a-z]+'s viewpoint, the ([a-z]+) is on the (?:front|right|back|left) side\.",outer)
            p['relation_object']=firstview[1] if firstview else None
        absolute=re.search(r'its world direction is (east|west|north|south)\.',outer)
        p['absolute']=absolute[1] if absolute else None
        p['marker_north']=bool(re.search(r'the [a-z]+ is north of the marker\.',outer))
        grammar=observer is not None and relation is not None
    elif domain=='emotion':
        focus=re.search(r"focus: ([a-z]+)'s view of the ([a-z]+)\.",outer)
        if not focus:return None,False
        p.update(focus=focus[1],target_object=focus[2],evaluations={})
        for sentence in outer.split('. '):
            m=re.search(r'^(?:as for the ([a-z]+), )?([a-z]+) (.+?) (?:the ([a-z]+)|it)\.?$',sentence)
            if m:
                level=stance(m[3]); obj=m[1] or m[4] or focus[2]
                if level is not None:p['evaluations'][(m[2],obj)]=level
            m=re.search(r'^([a-z]+) (.+?); it is the ([a-z]+)\.?$',sentence)
            if m:
                level=stance(m[2]);
                if level is not None:p['evaluations'][(m[1],m[3])]=level
        # Accept grammatical coordination and unambiguous "it" anaphora;
        # punctuation must not turn the benchmark into exact string matching.
        terms=['strongly dislikes','has a negative opinion of','has no preference about','has a positive opinion of','strongly likes','is neutral about','dislikes','detests','adores','likes','hates','loves']
        pattern=r"\b([a-z]+) ("+'|'.join(sorted(terms,key=len,reverse=True))+r") (?:the ([a-z]+)|it)\b"
        negation_pattern=r"[a-z]+ (?:does not like|does not dislike|neither likes nor dislikes) the [a-z]+; "
        positive_outer=re.sub(negation_pattern,' ',outer)
        matches=list(re.finditer(pattern,positive_outer));conflict=False
        for m in matches:
            key=(m[1],m[3] or focus[2]);value=stance(m[2])
            if key in p['evaluations'] and p['evaluations'][key]!=value:conflict=True
            p['evaluations'][key]=value
        qm=re.search(r'([a-z]+) said, "QUOTE"',outer)
        p['quote']=(qm[1],quotes[0]) if qm and len(quotes)==1 else None
        residue=positive_outer
        residue=re.sub(r"focus: [a-z]+'s view of the [a-z]+\.",' ',residue)
        residue=re.sub(r'as for the [a-z]+,',' ',residue)
        residue=re.sub(pattern,' ',residue)
        residue=re.sub(r"[a-z]+ (?:does not like it at all|does not dislike it at all|does not like it|does not dislike it|neither likes nor dislikes it); it is the [a-z]+\.",' ',residue)
        residue=re.sub(r'the [a-z]+ is (?:blue|red|green|white|black)\.|there (?:are [2-9] copies|is 1 copy)\.',' ',residue)
        residue=re.sub(r'[a-z]+ said, "QUOTE"',' ',residue)
        residue=re.sub(r'\b(?:and|but)\b',' ',residue)
        residue=re.sub(r'[\s\.,;:]','',residue)
        negated=re.search(r"([a-z]+) (does not like|does not dislike|neither likes nor dislikes) the ([a-z]+);",outer)
        negation_ok=True
        if negated:
            actual=p['evaluations'].get((negated[1],negated[3]));phrase=negated[2]
            negation_ok=actual is not None and (actual<=1 if phrase=='does not like' else actual>=3 if phrase=='does not dislike' else actual==2)
        grammar=len(p['evaluations'])>=2 and not conflict and not residue and negation_ok
    else:
        m=re.search(r'speaker: ([a-z]+)\. listener: ([a-z]+)\.',outer)
        if not m:return None,False
        s,l=m[1],m[2];p.update(speaker=s,listener=l)
        antecedent=re.search(r'the (giver|recipient|owner) is ([a-z]+)\.',outer)
        def bound(token,case):
            expected_role={'subject':'giver','object':'recipient','owner':'owner'}[case]
            if token in ('he','she','him','her','his'):
                if not antecedent or antecedent[1]!=expected_role:return None
                female=antecedent[2] in ('alice','carol','emma','grace')
                expected=('she' if female else 'he') if case=='subject' else ('her' if female else 'him') if case=='object' else ('her' if female else 'his')
                return antecedent[2] if token==expected else None
            return resolve(token,s,l,case)
        m=re.search(r"(?:listener: [a-z]+\. |the (?:giver|recipient|owner) is [a-z]+\. )([a-z]+) (give|gives) ([a-z]+) ([a-z]+(?:'s)?) ([a-z]+)\.",outer)
        if m:
            subj,verb,pat,own,obj=m.groups()
            p.update(agent=bound(subj,'subject'),patient=bound(pat,'object'),owner=bound(own,'owner'),event_object=obj)
            grammar=verb==('give' if subj in ('i','you') else 'gives')
        else:
            m=re.search(r"([a-z]+(?:'s)?) ([a-z]+) is what ([a-z]+) (give|gives) ([a-z]+)\.",outer)
            if m:
                own,obj,subj,verb,pat=m.groups();p.update(agent=resolve(subj,s,l,'subject'),patient=resolve(pat,s,l,'object'),owner=resolve(own,s,l,'owner'),event_object=obj)
                grammar=verb==('give' if subj in ('i','you') else 'gives')
            else:
                m=re.search(r"([a-z]+) (receive|receives) ([a-z]+(?:'s)?) ([a-z]+) from ([a-z]+)\.",outer)
                if not m:return None,False
                pat,verb,own,obj,agent=m.groups();p.update(agent=resolve(agent,s,l,'object'),patient=resolve(pat,s,l,'subject'),owner=resolve(own,s,l,'owner'),event_object=obj)
                grammar=verb==('receive' if pat in ('i','you') else 'receives')
        refl=re.search(r"([a-z]+) (keep|keeps) ([a-z]+(?:'s)?) key for (myself|yourself|herself|himself)\.",outer)
        p['reflexive']=None
        if refl:
            subj,v,own,ref=refl.groups();bound=resolve(subj,s,l,'subject')
            p['reflexive']=(bound,resolve(own,s,l,'owner'),ref)
            expected='myself' if subj=='i' else 'yourself' if subj=='you' else 'herself' if subj in ('alice','carol','emma','grace') else 'himself'
            grammar=grammar and ref==expected and v==('keep' if subj in ('i','you') else 'keeps')
        q=re.search(r'([a-z]+) said to ([a-z]+), "QUOTE"',outer)
        p['quote']=(q[1],q[2],quotes[0]) if q and len(quotes)==1 else None
        static=re.search(r'([a-z]+) sees ([a-z]+) and ([a-z]+)\.',outer)
        p['static_participants']=tuple(static.groups()) if static else None
    base_count=4 if domain=='time' else (3 if structure==1 else 4) if domain=='space' else 5
    extra_count=(1 if structure>=3 else 0)+(1 if structure in (4,5) else 0) if domain in ('time','space') else int(structure in ((4,5) if domain=='emotion' else (3,4,5,6)))
    # Controlled grammar has a fixed number of independently meaningful clauses.
    # Extra invented facts cannot be ignored by a permissive slot extractor.
    count=len(re.findall(r'\.(?:\s|$)|"QUOTE"(?=\s|$)',outer))
    grammar=grammar and (domain=='emotion' or count==base_count+extra_count) and (outer.endswith('.') or outer.endswith('"QUOTE"'))
    return p,grammar

def score(text, gold, world, ended=True):
    domain=gold['domain'];symbol=gold['symbolic'];structure=gold['structure']
    p,grammar=parse(text,domain,structure,symbol)
    preserved=scope=target=False
    if p is not None:
        o=gold['object'];col=gold['color'];a,b,c=[x.lower() for x in gold['people']]
        facts=p.get('object')==o and p.get('color')==col and (p.get('copies')==gold['quantity'] if symbol else p.get('quantity')==gold['quantity'])
        if symbol:
            if domain=='time':
                target=p.get('relative')==gold['relative'] and p.get('anchor')==gold['anchor'];preserved=facts and p.get('event')==gold['event_date'] and p.get('status')==gold['status']
            elif domain=='space':
                target=p.get('heading')==gold['heading'] and p.get('relation')==gold['relation'];preserved=facts and p.get('observer')==a and p.get('fixed_observer')==b and p.get('fixed_relation')==gold['fixed_relation']
                preserved &= all(p.get(k)==str(v) for k,v in zip(('observer_x','observer_y','object_x','object_y'),gold['observer_xy']+gold['object_xy']))
            elif domain=='emotion':
                target=p.get('level')==gold['target_level'];preserved=facts and p.get('focus')==world['focus'].lower() and p.get('other_level')==gold['other_level']
            else:
                target=p.get('speaker')==gold['speaker'].lower() and p.get('listener')==gold['listener'].lower();preserved=facts and all(p.get(k)==gold[k].lower() for k in ('agent','patient','owner'))
        elif domain=='time':
            target=p.get('relative')==gold['relative'];preserved=facts and p.get('event_object')==o and p.get('status')==gold['status']
            if structure>=3:preserved &= p.get('absolute')==gold['event_date']
            if structure==4:preserved &= p.get('fixed_launch',False)
            if structure==5:preserved &= p.get('quote')==(world['quote_date'],b,c,'the event is tomorrow.')
        elif domain=='space':
            target=p.get('relation')==gold['relation'];preserved=facts and p.get('observer')==a and p.get('relation_object')==o
            if structure>=3:
                x,y=world['object_xy'];ox,oy=world['observer_xy'];direct='east' if x>ox else 'west' if x<ox else 'north' if y>oy else 'south'
                preserved &= p.get('absolute')==direct
            if structure==4:preserved &= p.get('views',{}).get(b)==gold['fixed_relation']
            if structure==5:preserved &= p.get('marker_north',False)
        elif domain=='emotion':
            focus=world['focus'].lower();other=b if focus==a else a
            target=p.get('evaluations',{}).get((focus,o))==gold['target_level']
            preserved=facts and p.get('focus')==focus and p.get('target_object')==o and p.get('evaluations',{}).get((other,o))==gold['other_level']
            expected_keys={(focus,o),(other,o)}
            if structure==4:preserved &= p.get('evaluations',{}).get((focus,world['other_object']))==1
            if structure==4:expected_keys.add((focus,world['other_object']))
            preserved &= set(p.get('evaluations',{}))==expected_keys
            if structure==5:preserved &= p.get('quote')==(c,f'i dislike the {o}.')
        else:
            target=p.get('speaker')==gold['speaker'].lower() and p.get('listener')==gold['listener'].lower()
            preserved=facts and p.get('event_object')==o and all(p.get(k)==gold[k].lower() for k in ('agent','patient','owner'))
            if structure==3:preserved &= p.get('reflexive') is not None and p['reflexive'][:2]==(a,a)
            if structure==4:preserved &= p.get('quote')==(b,c,'i give you my key.')
            if structure==5:preserved &= p.get('static_participants')==(c,a,b)
        scope=target and preserved
    return dict(success=bool(ended and grammar and scope),target=bool(target),preserved=bool(preserved),scope=bool(scope),parseable=p is not None,grammar=bool(grammar),ended=bool(ended))
