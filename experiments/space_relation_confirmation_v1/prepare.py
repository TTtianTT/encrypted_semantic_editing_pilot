import json,random,itertools,subprocess
from datetime import date,timedelta
from common import *
from semantics import *
from evaluator import score

def make_worlds(domain):
    rng=random.Random(2026100201+DOMAINS.index(domain))
    result=[];seen=set();seen_surface=set()
    while len(result)<152:
        people=rng.sample(NAMES,3);obj,other=rng.sample(OBJECTS,2);col=rng.choice(COLORS)
        # World grouping ignores dates/coordinates absent from the core text. This
        # prevents near duplicates with identical core content in different splits.
        quantity=rng.randrange(1,10)
        key=tuple(people)+(obj,col,quantity)
        status=rng.choice(['planned','completed','cancelled'])
        if domain=='time':key=(obj,col,quantity,status)
        if key in seen:continue
        seen.add(key)
        event=(date(2026,11,1)+timedelta(days=rng.randrange(60))).isoformat()
        dx,dy=rng.choice([(0,1),(1,0),(0,-1),(-1,0)]);distance=rng.choice([1,2,3]);ox,oy=rng.randrange(-3,4),rng.randrange(-3,4)
        w=dict(domain=domain,people=people,object=obj,other_object=other,color=col,quantity=quantity,event_date=event,quote_date=(date.fromisoformat(event)-timedelta(days=2)).isoformat(),status=status,object_xy=[ox+dx*distance,oy+dy*distance],observer_xy=[ox,oy],fixed_heading=rng.randrange(4),focus=rng.choice(people[:2]),other_level=rng.randrange(5))
        # Deduplicate rendered atomic states across all worlds before split.
        signatures={render(w,s,0) for s in states(domain)}
        if signatures & seen_surface:continue
        seen_surface.update(signatures)
        i=len(result);w['world_id']=f'{domain}_{i:04d}';w['split']='train' if i<96 else 'dev' if i<120 else 'test';result.append(w)
    return result

def records(worlds,templates=(0,1),symbolic=False):
    out=[]
    for w in worlds:
        for t in templates:
            for s in states(w['domain']):
                for op in ('plus','minus'):
                    try:nxt=advance(w['domain'],s,op)
                    except ValueError:continue
                    out.append(dict(world_id=w['world_id'],split=w['split'],state=s,operation=op,template=t,symbolic=symbolic,source=render(w,s,t,symbolic),target=render(w,nxt,t,symbolic),gold=gold(w,nxt,t,symbolic)))
    return out

def main():
    if (ROOT/'data/manifest.json').exists():raise RuntimeError('Prepared data immutable; use another version')
    files=[];counts={}
    for d in DOMAINS:
        ws=make_worlds(d);jsonl(ROOT/f'data/{d}/worlds.jsonl',ws)
        for split in ('train','dev','test'):
            subset=[w for w in ws if w['split']==split]
            for kind,ts,sym in [('core',(0,1),False),('expression',(2,),False),('challenge',(3,4,5),False),('symbol',(0,),True)]:
                if split=='train' and kind not in ('core','symbol'):continue
                rs=records(subset,ts,sym);path=ROOT/f'data/{d}/{split}_{kind}.jsonl';jsonl(path,rs);files.append(path);counts[f'{d}/{split}/{kind}']=len(rs)
        audit=[]
        for w in ws[96:100]:
            for r in records([w],range(6))+records([w],(0,),True):
                assert score(r['source'],gold(w,r['state'],r['template'],r['symbolic']),w)['success'],r
                assert score(r['target'],r['gold'],w)['success'],r
                audit.append(r)
        jsonl(ROOT/f'data/{d}/audit.jsonl',audit)
    # Literal transition table is not calculated with advance; it checks direction.
    assert [advance('time',x,'plus') for x in [-2,-1,0,1,2]]==[-3,-2,-1,0,1]
    assert [advance('emotion',x,'plus') for x in [0,1,2,3]]==[1,2,3,4]
    for d,n in [('space',4),('person',3)]:
        for s in range(n):
            x=s
            for _ in range(n):x=advance(d,x,'plus')
            assert x==s
    check=dict(observer_xy=[0,0],object_xy=[0,1]);assert [relation(check,s) for s in range(4)]==['front','left','back','right']
    check['object_xy']=[1,0];assert [relation(check,s) for s in range(4)]==['right','front','left','back']
    for d in DOMAINS:
        for s in states(d):
            for op in ('plus','minus'):
                try:n=advance(d,s,op)
                except ValueError:continue
                assert advance(d,n,'minus' if op=='plus' else 'plus')==s
    files+=list((ROOT/'data').glob('*/worlds.jsonl'))+list((ROOT/'data').glob('*/audit.jsonl'))
    dump(ROOT/'data/manifest.json',dict(data_seed=2026100201,worlds_per_domain=dict(train=96,dev=24,test=32),counts=counts,files=[dict(path=str(p.relative_to(ROOT)),sha256=digest(p),bytes=p.stat().st_size) for p in files],split_rule='immutable core-content deduplication before world split; all states, histories and paraphrases inherit world split',templates=dict(train=[0,1],expression=[2],challenge=[3,4,5]),leakage='core text exact collision checked globally; shared template skeletons 0/1 intentional IID; templates2-5 excluded from training'))
    dump(ROOT/'cpu_checks.json',dict(gold_roundtrip=True,transition_table=True,cardinal_direction=True,cycles=True,inverses=True,human_review='fixed readable audit generated; no independent human labels claimed'))

if __name__=='__main__':main()
