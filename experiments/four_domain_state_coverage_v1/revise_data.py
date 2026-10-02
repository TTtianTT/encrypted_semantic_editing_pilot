"""One-time pre-formal grammar/ambiguity correction, preserve earlier data."""
import gzip,shutil
from common import *
from semantics import render,gold

def main():
    stamp=ROOT/'data_revisions/pre_formal_final_correction.json'
    if stamp.exists():return
    original=read(ROOT/'data/manifest.json');archive=ROOT/'data_revisions/engineering_v2';archive.mkdir(parents=True,exist_ok=True)
    dump(archive/'manifest.json',original)
    for d in DOMAINS:
        ws={w['world_id']:w for w in rows(ROOT/f'data/{d}/worlds.jsonl')}
        for p in sorted((ROOT/f'data/{d}').glob('*.jsonl')):
            if p.name=='worlds.jsonl':continue
            with gzip.open(archive/f'{d}_{p.name}.gz','wb') as f:f.write(p.read_bytes())
            rs=rows(p)
            for r in rs:
                w=ws[r['world_id']];r['source']=render(w,r['state'],r['template'],r['symbolic']);r['target']=render(w,r['gold']['state'],r['template'],r['symbolic']);r['gold']=gold(w,r['gold']['state'],r['template'],r['symbolic'])
            jsonl(p,rs)
        if d=='person':
            from prepare import records
            for split in ('dev','test'):
                p=ROOT/f'data/person/{split}_challenge.jsonl';rs=rows(p);rs+=records([w for w in ws.values() if w['split']==split],(6,));jsonl(p,rs)
            p=ROOT/'data/person/audit.jsonl';rs=rows(p);rs+=records([w for w in ws.values() if w['split']=='dev'][:4],(6,));jsonl(p,rs)
    for f in original['files']:
        p=ROOT/f['path'];f.update(sha256=digest(p),bytes=p.stat().st_size)
    original['pre_formal_revision']='singular copy agreement; unambiguous explicit stance alongside negation; explicit co-located secondary observer and marker coordinates in gold'
    dump(ROOT/'data/manifest.json',original)
    dump(stamp,dict(old_manifest_sha=digest(archive/'manifest.json'),new_manifest_sha=digest(ROOT/'data/manifest.json'),reasons=['one copy singular agreement','negation alone does not uniquely imply a positive stance','accept controlled grammatical coordination in independent evaluator'],test_model_outputs_seen=False,old_inputs_preserved=str(archive)))
    tasks=read(ROOT/'tasks.json')
    if not any(t['phase']=='interface' for t in tasks):
        for i,d in enumerate(DOMAINS):tasks.append(dict(phase='interface',model='t5gemma',domain=d,seed=42,index=i))
    dump(ROOT/'tasks.json',tasks)

if __name__=='__main__':main()
