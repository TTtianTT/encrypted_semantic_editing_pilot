"""Independent outer reference/case controls, without inference."""
from itertools import permutations
from common import *
from semantics import render,gold
from evaluator import score
from person_quote_attribution_score import score_person_attributions,adapt_outer_attribution

def main():
    worlds=rows(ROOT/'data/person/worlds.jsonl');fixture=dict(worlds[0]);names=('Alice','Bob','Carol','David','Emma','Frank','Grace','Henry');positive=negative=0
    for people in permutations(names,3):
        w=dict(fixture,people=list(people));a,b,c=people
        for state in range(3):
            text=render(w,state,4);g=gold(w,state,4);speaker=g['speaker'];listener=g['listener']
            actor='I' if b==speaker else 'you' if b==listener else b
            receiver='me' if c==speaker else 'you' if c==listener else c
            equivalent=text.replace(f'{b} said to {c},',f'{actor} said to {receiver},')
            result=score_person_attributions(equivalent,g,w,True,score)
            assert result['success'],(people,state,equivalent,result)
            assert adapt_outer_attribution(equivalent).split('"')[1]==equivalent.split('"')[1]
            positive+=1
            for bad in (text.replace(f'{b} said to {c},',f'{a} said to {c},'),text.replace(f'{b} said to {c},',f'{b} said to {a},'),equivalent.replace('I give you my key.','I give you your key.'),equivalent.replace(f'Speaker: {speaker}.',f'Speaker: {listener}.'),text.replace(f'{b} said to {c},',f'me said to {c},'),text.replace(f'{b} said to {c},',f'{b} said to I,')):
                assert not score_person_attributions(bad,g,w,True,score)['success'],(people,state,bad)
                negative+=1
    for text in ('Speaker: Alice. Listener: Bob. Bob said to Alice, "I said to you."','Speaker: Alice. Speaker: Carol. Listener: Bob. I said to Bob, "I give you my key."','Speaker: I. Listener: Bob. I said to Bob, "I give you my key."'):
        assert adapt_outer_attribution(text)==text
    dump(ROOT/'PERSON_QUOTE_ATTRIBUTION_CHECK.json',dict(positives=positive,negatives=negative,protected_cases=3,actual_headers_only=True,quote_words_unchanged=True))
    print('Person quotation aliases:',positive,'positive,',negative,'negative controls')

if __name__=='__main__':main()
