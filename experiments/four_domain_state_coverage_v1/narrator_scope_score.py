"""Independent first-person stance binding adapter; no generator imports.

Resolve only unquoted, grammatically valid first-person stance forms through the
emitted explicit narrator header. Historical quoted I retains its own speaker.
This normalization is scoring-only and never becomes a model input.
"""
import re

def score_narrator(text,g,w,ended,base_score):
    parts=re.split(r'("[^"]*")',text);headers=[]
    for i in range(0,len(parts),2):headers+=list(re.finditer(r'\b(?:Narrator|Speaker): ([A-Za-z]+)\.',parts[i],re.I))
    if len(headers)!=1:return dict(success=False,target=False,preserved=False,scope=False,parseable=False,grammar=False,ended=bool(ended))
    who=headers[0][1];header_ok=who.lower()==g['foil_narrator'].lower()
    third={'strongly dislike':'strongly dislikes','dislike':'dislikes','am neutral about':'is neutral about','strongly like':'strongly likes','like':'likes'}
    pattern=r'\bi (strongly dislike|dislike|am neutral about|strongly like|like) (the [a-z]+|it)\b'
    for i in range(0,len(parts),2):
        parts[i]=re.sub(r'\b(?:Narrator|Speaker): [A-Za-z]+\.\s*','',parts[i],flags=re.I)
        parts[i]=re.sub(pattern,lambda m:who+' '+third[m[1].lower()]+' '+m[2],parts[i],flags=re.I)
    out=base_score(''.join(parts),g,w,ended)
    if not header_ok:out=dict(out,success=False,preserved=False,scope=False)
    return out
