"""CPU-only fixture generation and independent scoring checks."""
import argparse,sys,re
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--study',required=True);p.add_argument('--domain',required=True);args=p.parse_args()
PARENT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(PARENT/args.study))
from common import *
from semantics import gold as original_gold,render as original_render,advance,states
from evaluator import score as original_score
from position_spec import prepare_world,make_functions
gold,render,score=make_functions(original_gold,original_render,original_score)

def main():
    dest=ROOT/'position_foils/data'/args.domain;dest.mkdir(parents=True,exist_ok=True)
    worlds=[prepare_world(w) for w in rows(ROOT/f'data/{args.domain}/worlds.jsonl') if w['split'] in ('dev','test')];checks=0
    jsonl(dest/'worlds.jsonl',worlds)
    for split in ('dev','test'):
        records=[]
        for w in worlds:
            if w['split']!=split:continue
            for s in states(args.domain):
                for variant in (range(4) if args.domain=='emotion' else range(2)):
                    text=render(w,s,variant);g=gold(w,s,variant);assert score(text,g,w)['success'],(args.domain,variant,text,score(text,g,w));checks+=1
                    wrong=text.replace(' is '+w['color']+'.',' is '+('red' if w['color']!='red' else 'blue')+'.');assert not score(wrong,g,w)['success'];checks+=1
                    if args.domain in ('time','person') or (args.domain=='emotion' and variant>=2):
                        altered=re.sub(r'"[^"]*"','"The wrong person speaks."',text);assert not score(altered,g,w)['scope'];checks+=1
                    if args.domain=='emotion' and variant>=2:
                        altered=text.replace(f"Narrator: {w['focus']}.",f"Narrator: {w['people'][2]}.");assert not score(altered,g,w)['scope'];checks+=1
                        malformed=text.replace('I am neutral about','I is neutral about').replace('I strongly dislike the','I strongly dislikes the').replace('I dislike the','I dislikes the').replace('I strongly like the','I strongly likes the').replace('I like the','I likes the');assert not score(malformed,g,w)['success'];checks+=1
                    for op in ('plus','minus'):
                        try:nxt=advance(args.domain,s,op)
                        except ValueError:continue
                        ng=gold(w,nxt,variant);target=render(w,nxt,variant);assert score(target,ng,w)['success'];assert not score(text,ng,w)['success'];checks+=2
                        records.append(dict(world_id=w['world_id'],domain=args.domain,state=s,operation=op,template=variant,symbolic=False,source=text,target=target,gold=ng))
        jsonl(dest/f'{split}.jsonl',records)
    dump(dest/'manifest.json',dict(domain=args.domain,study=args.study,checks=checks,world_split_preserved=True,files=[dict(path=p.name,sha256=digest(p),rows=len(rows(p))) for p in sorted(dest.glob('*.jsonl'))]))
    print(json.dumps(dict(domain=args.domain,checks=checks)))

if __name__=='__main__':main()
