"""Post hoc outer attribution aliases; no gold-based textual repair."""
import re

def adapt_outer_attribution(text):
    quotes=list(re.finditer(r'"[^"]*"',text))
    if len(quotes)!=1 or text.count('"')!=2:return text
    quote=quotes[0];outer=text[:quote.start()]+text[quote.end():]
    speakers=re.findall(r'\bSpeaker:\s*([A-Za-z]+)\.',outer,re.I)
    listeners=re.findall(r'\bListener:\s*([A-Za-z]+)\.',outer,re.I)
    if len(speakers)!=1 or len(listeners)!=1:return text
    speaker,listener=speakers[0],listeners[0]
    if any(x.lower() in ('i','me','you','he','she','they','we','it') for x in (speaker,listener)):return text
    matches=list(re.finditer(r'\b([A-Za-z]+) said to ([A-Za-z]+),\s*"',text,re.I))
    matches=[m for m in matches if m.end()-1==quote.start()]
    if len(matches)!=1:return text
    match=matches[0];actor,receiver=match[1],match[2]
    # Keep subject/object case licensing; never fix "me said" or "to I".
    actor={'i':speaker,'you':listener}.get(actor.lower(),actor)
    receiver={'me':speaker,'you':listener}.get(receiver.lower(),receiver)
    if match[1].lower() in ('me','him','her','us','them') or match[2].lower() in ('i','he','she','we','they'):return text
    # Unresolved third-person forms remain for the immutable parser to reject.
    replacement=actor+text[match.end(1):match.start(2)]+receiver+text[match.end(2):match.end()]
    return text[:match.start()]+replacement+text[match.end():]

def score_person_attributions(text,gold,world,ended,base_score):
    adapted=adapt_outer_attribution(text) if gold['domain']=='person' and gold['structure']==4 else text
    return base_score(adapted,gold,world,ended)
