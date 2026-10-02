"""Independent named-observer consistency check; no gold renderer imports."""
import re

def valid_target_relation(text,g,w):
    t=re.sub(r'\s+',' ',text.strip().replace('\u2019',"'")).lower();a=w['people'][0].lower();obj=g['object'];target=[]
    header=re.search(r'observer: ([a-z]+)\.',t)
    first_person=[('front',r'(?:the ([a-z]+) is in front of me|i see the ([a-z]+) ahead)\.'),('back',r'(?:the ([a-z]+) is behind me|i see the ([a-z]+) behind)\.'),('right',r'(?:the ([a-z]+) is to my right|i see the ([a-z]+) on my right)\.'),('left',r'(?:the ([a-z]+) is to my left|i see the ([a-z]+) on my left)\.')]
    for relation,pattern in first_person:
        for m in re.finditer(pattern,t):
            if not header or header[1]!=a:return False
            if (m[1] or m[2])!=obj:return False
            target.append(relation)
    for m in re.finditer(r"from ([a-z]+)'s viewpoint, (?:the ([a-z]+)|(it)) is on the (front|right|back|left) side\.",t):
        if m[1]!=a:continue
        if m[2] is not None and m[2]!=obj:return False
        target.append(m[4])
    return bool(target) and all(relation==g['relation'] for relation in target)

def valid_non_target_relations(text,g,w):
    t=re.sub(r'\s+',' ',text.strip().replace('\u2019',"'")).lower();obj=g['object']
    if g['structure']==4:
        b=w['people'][1].lower();clauses=[m for m in re.finditer(r"from ([a-z]+)'s viewpoint, (?:the ([a-z]+)|(it)) is on the (front|right|back|left) side\.",t) if m[1]==b]
        return bool(clauses) and all((m[2] is None or m[2]==obj) and m[4]==g['fixed_relation'] for m in clauses)
    if g['structure']==5:
        names=re.findall(r'the ([a-z]+) is north of the marker\.',t)
        return bool(names) and all(name==obj for name in names)
    return True
