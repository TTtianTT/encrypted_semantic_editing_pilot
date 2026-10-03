"""CPU adversarial aliases, checked independently of transition generation."""
from common import *
from evaluator import score
from spatial_paraphrase_score import normalize_spatial_paraphrases,score_spatial_paraphrases
import importlib.util

def main():
    p=ROOT.parent/'space_relation_confirmation_v1/semantics.py'
    spec=importlib.util.spec_from_file_location('confirmation_semantics_check',p);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    positive=negative=unchanged=0
    ws=rows(ROOT.parent/'space_relation_confirmation_v1/data/space/worlds.jsonl')
    aliases={'front':['ahead','ahead of me','in front of me'],'back':['behind','behind me'],'right':['on my right','to my right','on the right','to the right'],'left':['on my left','to my left','on the left','to the left']}
    for w in ws:
        a,b,_=w['people'];obj=w['object'];facts=f"The {obj} is {w['color']}. "+('There is 1 copy.' if w['quantity']==1 else f"There are {w['quantity']} copies.")
        for state,relation in enumerate(('front','right','back','left')):
            g=module.gold(w,state,2)
            for phrase in aliases[relation]:
                for relative in ('','that is '):
                    text=f'Observer: {a}. I see the {obj} {relative}{phrase}. {facts}'
                    adapted,n=normalize_spatial_paraphrases(text);assert n==1 and f'The {obj} is ' in adapted
                    assert score_spatial_paraphrases(text,g,w,True,score)['success'],(text,g)
                    positive+=1
                    wrong_observer=text.replace(f'Observer: {a}.',f'Observer: {b}.');assert not score_spatial_paraphrases(wrong_observer,g,w,True,score)['success'];negative+=1
                    wrong_object=text.replace(f'I see the {obj}',f"I see the {w['other_object']}");assert not score_spatial_paraphrases(wrong_object,g,w,True,score)['success'];negative+=1
                    wrong_gold=module.gold(w,(state+1)%4,2);assert not score_spatial_paraphrases(text,wrong_gold,w,True,score)['success'];negative+=1
                    conflicting=text+' '+('There are 2 copies.' if w['quantity']!=2 else 'There are 3 copies.');assert not score_spatial_paraphrases(conflicting,g,w,True,score)['success'];negative+=1
            for structure in range(6):
                g2=module.gold(w,state,structure);text=module.render(w,state,structure);assert score_spatial_paraphrases(text,g2,w,True,score)['success'];positive+=1
            for phrase in ('on my front','on my back','somewhere'):
                text=f'Observer: {a}. I see the {obj} {phrase}. {facts}'
                assert normalize_spatial_paraphrases(text)==(text,0)
                assert not score_spatial_paraphrases(text,g,w,True,score)['success'];unchanged+=1
            text=f'Observer: {a}. I see the {obj} to my left.'
            for protected in (f'Observer: {a}. Bob said, "I see the {obj} to my left."',f"Observer: {a}. From {b}'s viewpoint, I see the {obj} to my left.",f'Observer: {a}. Observer: {b}. I see the {obj} to my left.'):
                assert normalize_spatial_paraphrases(protected)==(protected,0);unchanged+=1
    # Existing constructed binding failures must still fail the revised scorer.
    import subprocess
    subprocess.run([str(PYTHON),str(ROOT/'check_space_scope_guard.py')],check=True)
    for x in read(ROOT/'SPACE_SCOPE_GUARD_CHECK.json')['examples']:
        w=next(w for w in ws if w['world_id']==x['world_id'])
        assert not score_spatial_paraphrases(x['text'],x['gold'],w,True,score)['success'];negative+=1
    dump(ROOT/'SPATIAL_PARAPHRASE_CHECK.json',dict(positive_checks=positive,negative_checks=negative,unsupported_quoted_scoped_or_duplicate_header_unchanged_checks=unchanged,no_gpu=True,normalizer_reads_emitted_text_only=True,scorer_sha=digest(ROOT/'spatial_paraphrase_score.py')))
    print('Spatial alias checks:',positive,negative,unchanged)

if __name__=='__main__':main()
