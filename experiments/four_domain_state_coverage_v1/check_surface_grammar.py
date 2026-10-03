"""CPU grammar coverage with semantic errors separated from syntax errors."""
from common import *
from semantics import gold,render,states
from controlled_surface_grammar import surface_grammar

def main():
    positive=0
    for d in DOMAINS:
        for w in rows(ROOT/f'data/{d}/worlds.jsonl'):
            for s in states(d):
                for template in range(7 if d=='person' else 6):
                    t=render(w,s,template);assert surface_grammar(t) is True,(d,t,surface_grammar(t));positive+=1
    fixtures=[('Observer: David. The parcel is black. There are 6 copies.',True),('Speaker: Alice. Listener: Bob. Bob gives me my book.',True),('Speaker: Alice. Listener: Bob. He gives me her book.',True),('I give you my key.',True),('You give me his book.',True),('Alice gives me your book.',True),('I gives you my key.',False),('You gives me his book.',False),('Alice give me your book.',False),('Alice gives I my book.',False),('I likes the book.',False),('I like the book.',True),('I is neutral about the book.',False),('Alice does not likes the book.',False),('There are 1 copies.',False),('There is 2 copy.',False),('Unrecognized innovative sentence wording.',None),('Observer: David.',None)]
    for t,expected in fixtures:assert surface_grammar(t) is expected,(t,surface_grammar(t),expected)
    dump(ROOT/'SURFACE_GRAMMAR_CHECK.json',dict(generated_positive_checks=positive,independent_case_agreement_and_incomplete_semantics_fixtures=len(fixtures),fixtures=[dict(text=t,expected=x) for t,x in fixtures],no_gold_or_renderer_used_by_checker=True,no_gpu=True,checker_sha=digest(ROOT/'controlled_surface_grammar.py')))
    print('Surface grammar checks:',positive,'generated;',len(fixtures),'independent fixtures')

if __name__=='__main__':main()
