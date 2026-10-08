"""CPU conservative audit of cores actually appearing in prior generated text."""
import re
from itertools import product
from .common import *


def text_cores(value):
    lower=value.lower().replace('\u2019',"'")
    # Necessary lexical markers for either accepted complete-core grammar.
    # Skipping other metadata strings preserves exactly the same parser result.
    if 'status' not in lower or ('cop' not in lower and 'quantity' not in lower):return set()
    text=re.sub(r'\s+',' ',lower)
    facts=re.findall(r'the ([a-z]+) is (blue|red|green|white|black)\.',text)
    quantities=re.findall(r'there (?:are|is) ([1-9]) cop(?:y|ies)\.',text)
    statuses=re.findall(r'its status is (planned|completed|cancelled)\.',text)
    event_objects=re.findall(r'the ([a-z]+) event is dated',text)
    result=set()
    for (obj,color),quantity,status in product(facts,quantities,statuses):
        result.add((obj,color,int(quantity),status))
        for event in event_objects:result.add((event,color,int(quantity),status))
    symbolic={key:re.findall(r'\b'+key+r'\s*=\s*([a-z0-9]+)',text) for key in ('object','event_object','color','quantity','status')}
    for obj,color,quantity,status in product(symbolic['object']+symbolic['event_object'],symbolic['color'],symbolic['quantity'],symbolic['status']):
        if quantity.isdigit() and 1<=int(quantity)<=9 and color in ('blue','red','green','white','black') and status in ('planned','completed','cancelled'):result.add((obj,color,int(quantity),status))
    return result


def strings(value,path=()):
    if isinstance(value,dict):
        for key,v in value.items():
            if isinstance(v,str):yield path+(key,),v
            elif isinstance(v,(dict,list)):yield from strings(v,path+(str(key),))
    elif isinstance(value,list):
        for i,v in enumerate(value):
            if isinstance(v,str):yield path+(str(i),),v
            else:yield from strings(v,path+(str(i),))


def audit():
    worlds=rows(ROOT/'configs/worlds.jsonl');reserved={core(w):w for w in worlds if w['split'] in ('test_iid','reserved_iid')}
    hits=[];files=0;seen_text=0;checked=set()
    for manifest in sorted((ROOT/'manifests').glob('*_registration.json')):
        reg=read(manifest);m=read(reg['manifest'])
        if m['stage']=='S4':continue # This audit concerns pre-unseal provenance only.
        root=Path(m['output_root'])
        for path in sorted(root.rglob('*')):
            if path.suffix not in ('.jsonl','.json') or path in checked:continue
            checked.add(path)
            value=rows(path) if path.suffix=='.jsonl' else read(path)
            files+=1
            for field,text_value in strings(value):
                seen_text+=1
                for key in text_cores(text_value):
                    if key not in reserved:continue
                    w=reserved[key]
                    hits.append(dict(world_id=w['world_id'],split=w['split'],core_content=list(key),stage=m['stage'],file=str(path),field='/'.join(field),text=text_value,manifest_sha256=sha(reg['manifest'])))
    observed_test=sorted({r['world_id'] for r in hits if r['split']=='test_iid'})
    prior=sorted({r['donor_world_id'] for r in read(ROOT/'results/COUNTERFACTUAL_EXPOSURE_AUDIT.json')['collisions'] if r['donor_split']=='test_iid'})
    result=dict(files_scanned=files,text_fields_scanned=seen_text,prior_test_cores=prior,generated_text_test_cores=observed_test,additional_test_cores=sorted(set(observed_test)-set(prior)),hits=hits,neural_model_loaded=False,new_test_model_evaluations=0,conservative_rule='Complete object/color/quantity/status clauses, including grammatical errors or multiple possible cores; no model execution')
    dump(ROOT/'results/PREDICTED_CORE_EXPOSURE_AUDIT.json',result)
    print({k:v for k,v in result.items() if k!='hits'})
    return result


if __name__=='__main__':audit()
