"""CPU adversarial check for wrong first-viewpoint fallback."""
import sys
from pathlib import Path
PRIMARY=Path(__file__).resolve().parent;sys.path.insert(0,str(PRIMARY.parent/'space_relation_confirmation_v1'))
from common import *
from semantics import gold,render
from evaluator import score
from space_scope_guard import valid_target_relation,valid_non_target_relations

def main():
    positives=0;paraphrase_positives=0;negatives=0;legacy_pass=0;examples=[]
    for w in rows(ROOT/'position_foils/data/space/worlds.jsonl'):
        for state in range(4):
            for template in range(6):
                g=gold(w,state,template);text=render(w,state,template);assert valid_target_relation(text,g,w) and valid_non_target_relations(text,g,w);positives+=1
            g=gold(w,state,2);a=w['people'][0];obj=w['object'];phrase={'front':'in front of me','right':'to my right','back':'behind me','left':'to my left'}[g['relation']]
            text=f"Observer: {a}. I see the {obj} that is {phrase}. The {obj} is {w['color']}. "+('There is 1 copy.' if w['quantity']==1 else f"There are {w['quantity']} copies.")
            assert valid_target_relation(text,g,w) is True and score(text,g,w)['success'];paraphrase_positives+=1
        relation=gold(w,0,4)['fixed_relation'];state=['front','right','back','left'].index(relation);g=gold(w,state,4);a,b,c=w['people'];obj=w['object'];wrong='left' if relation!='left' else 'right';x,y=w['object_xy'];ox,oy=w['observer_xy'];direction='east' if x>ox else 'west' if x<ox else 'north' if y>oy else 'south';quantity='There is 1 copy.' if w['quantity']==1 else f"There are {w['quantity']} copies."
        text=f"Observer: {a}. The {obj} is {w['color']}. {quantity} Its world direction is {direction}. From {b}'s viewpoint, it is on the {relation} side. From {a}'s viewpoint, the {obj} is on the {wrong} side."
        legacy=score(text,g,w);legacy_pass+=legacy['success'];assert not valid_target_relation(text,g,w);negatives+=1
        if len(examples)<4:examples.append(dict(world_id=w['world_id'],text=text,gold=g,legacy_score=legacy,independent_guard_passed=False))
        wrong_B=render(w,state,4).replace(f"From {b}'s viewpoint, it is",f"From {b}'s viewpoint, the {w['other_object']} is")
        assert not valid_non_target_relations(wrong_B,g,w);legacy_pass+=score(wrong_B,g,w)['success'];negatives+=1
        marker_gold=gold(w,state,5);wrong_marker=render(w,state,5).replace(f"The {obj} is north of the marker.",f"The {w['other_object']} is north of the marker.")
        assert not valid_non_target_relations(wrong_marker,marker_gold,w);legacy_pass+=score(wrong_marker,marker_gold,w)['success'];negatives+=1
    assert valid_target_relation('Unrecognized relationship wording.',g,w) is None
    dump(PRIMARY/'SPACE_SCOPE_GUARD_CHECK.json',dict(positive_checks=positives,relative_clause_paraphrase_checks=paraphrase_positives,unrecognized_guard_is_unknown=True,adversarial_binding_checks=negatives,legacy_false_positive_examples=legacy_pass,examples=examples,no_gpu=True,reason='First B must not substitute for target A; fixed B and marker relations must concern the gold object. Correct relative clauses accepted; unrecognized wording is not a confirmed contradiction.'))
    print(json.dumps(dict(positives=positives,paraphrases=paraphrase_positives,negatives=negatives,legacy_false_positives=legacy_pass)))

if __name__=='__main__':main()
