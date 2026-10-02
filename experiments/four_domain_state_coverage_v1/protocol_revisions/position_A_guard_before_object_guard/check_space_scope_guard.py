"""CPU adversarial check for wrong first-viewpoint fallback."""
import sys
from pathlib import Path
PRIMARY=Path(__file__).resolve().parent;sys.path.insert(0,str(PRIMARY.parent/'space_relation_confirmation_v1'))
from common import *
from semantics import gold,render
from evaluator import score
from space_scope_guard import valid_target_relation

def main():
    positives=0;negatives=0;legacy_pass=0;examples=[]
    for w in rows(ROOT/'position_foils/data/space/worlds.jsonl'):
        for state in range(4):
            for template in range(6):
                g=gold(w,state,template);assert valid_target_relation(render(w,state,template),g,w);positives+=1
        relation=gold(w,0,4)['fixed_relation'];state=['front','right','back','left'].index(relation);g=gold(w,state,4);a,b,c=w['people'];obj=w['object'];wrong='left' if relation!='left' else 'right';x,y=w['object_xy'];ox,oy=w['observer_xy'];direction='east' if x>ox else 'west' if x<ox else 'north' if y>oy else 'south';quantity='There is 1 copy.' if w['quantity']==1 else f"There are {w['quantity']} copies."
        text=f"Observer: {a}. The {obj} is {w['color']}. {quantity} Its world direction is {direction}. From {b}'s viewpoint, it is on the {relation} side. From {a}'s viewpoint, the {obj} is on the {wrong} side."
        legacy=score(text,g,w);legacy_pass+=legacy['success'];assert not valid_target_relation(text,g,w);negatives+=1
        if len(examples)<4:examples.append(dict(world_id=w['world_id'],text=text,gold=g,legacy_score=legacy,independent_guard_passed=False))
    dump(PRIMARY/'SPACE_SCOPE_GUARD_CHECK.json',dict(positive_checks=positives,adversarial_wrong_A_checks=negatives,legacy_false_positive_examples=legacy_pass,examples=examples,no_gpu=True,reason='Frozen parser falls back to first named viewpoint when first-person relation absent; first B must not substitute for target A.'))
    print(json.dumps(dict(positives=positives,negatives=negatives,legacy_false_positives=legacy_pass)))

if __name__=='__main__':main()
