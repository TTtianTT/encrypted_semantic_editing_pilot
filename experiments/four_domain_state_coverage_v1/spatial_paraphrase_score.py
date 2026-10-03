"""Scoring-only spatial aliases; no renderer, transition or target-text access."""
import re
from space_scope_guard import valid_target_relation,valid_non_target_relations
from quantity_guard import consistent_quantity

def normalize_spatial_paraphrases(text):
    # Interpret standalone unquoted I-see clauses using the emitted observer,
    # never the expected observer or expected relation. Quotes remain verbatim.
    outer=re.sub(r'"[^\"]*"',' ',text)
    if len(re.findall(r'\bobserver:\s*[a-z]+\.',outer,re.I))!=1:return text,0
    count=0
    pattern=re.compile(r'(^|(?<=\.)\s+)i see the ([a-z]+)(?: that is)? (in front of me|ahead(?: of me)?|behind(?: me)?|(?:to|on) (?:my|the) (?:right|left))\.',re.I)
    def replace(m):
        nonlocal count
        phrase=m[3].lower()
        relation='in front of me' if phrase.startswith('ahead') or phrase=='in front of me' else 'behind me' if phrase.startswith('behind') else 'to my '+phrase.rsplit(' ',1)[1]
        count+=1
        return m[1]+'The '+m[2]+' is '+relation+'.'
    parts=re.split(r'("[^\"]*")',text)
    for i in range(0,len(parts),2):parts[i]=pattern.sub(replace,parts[i])
    return ''.join(parts),count

def score_spatial_paraphrases(text,g,w,ended,base_score):
    if g['domain']!='space' or g.get('symbolic'):return base_score(text,g,w,ended)
    adapted,_=normalize_spatial_paraphrases(text)
    result=base_score(adapted,g,w,ended)
    outside=re.sub(r'"[^\"]*"','""',adapted)
    target=valid_target_relation(outside,g,w);other=valid_non_target_relations(outside,g,w);quantity=consistent_quantity(text,g)
    if target is not True:result=dict(result,success=False,target=False,scope=False)
    if other is not True or quantity is not True:result=dict(result,success=False,preserved=False,scope=False)
    if target is None or other is None or quantity is None:result=dict(result,parseable=False)
    return result
