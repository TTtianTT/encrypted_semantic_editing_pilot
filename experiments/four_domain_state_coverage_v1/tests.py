import copy
from common import *
from semantics import gold,render,advance,states
from evaluator import score,parse

def main():
    checks=0
    for d in DOMAINS:
        for w in rows(ROOT/f'data/{d}/worlds.jsonl')[96:100]:
            for s in states(d):
                for t in range(7 if d=='person' else 6):
                    text=render(w,s,t);g=gold(w,s,t)
                    assert score(text,g,w)['success'],(d,s,t,text,parse(text,d,t));checks+=1
                    assert not score(text+' Aliens destroyed the city.',g,w)['success'];checks+=1
                    assert not score(text.replace(w['color'],'purple'),g,w)['success'];checks+=1
                    if d=='emotion':
                        other=next(n for n in w['people'][:2] if n!=w['focus'])
                        wrong=copy.deepcopy(g);wrong['target_level']=(s+1)%5
                        assert not score(text,wrong,w)['success'];checks+=1
                    if d=='person' and t==0:
                        assert not score(text.replace('I give','Me gives'),g,w)['success'] if 'I give' in text else True;checks+=1
                    if t==5 and d=='time':assert not score(text.replace('"The event is tomorrow."','"The event is today."'),g,w)['success'];checks+=1
            for s in states(d):
                for op in ('plus','minus'):
                    try:n=advance(d,s,op)
                    except ValueError:continue
                    assert advance(d,n,'minus' if op=='plus' else 'plus')==s;checks+=1
    dump(ROOT/'independent_parser_checks.json',dict(checks=checks,passed=True,negative_controls=['invented fact','objective color','wrong sentiment level','invalid nominative','historical quote change'],human_review=False))
    print(f'{checks} CPU semantic/parser checks passed')

if __name__=='__main__':main()
