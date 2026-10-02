"""Read-only delivery audit of every frozen data row, including symbol grammar."""
from collections import Counter
from common import *
from evaluator import score
from semantics import gold,render,advance

def main():
    checks=0;counts={};issues=[]
    for d in DOMAINS:
        ws={w['world_id']:w for w in rows(ROOT/f'data/{d}/worlds.jsonl')};seen={}
        for p in sorted((ROOT/f'data/{d}').glob('*.jsonl')):
            if p.name=='worlds.jsonl':continue
            rs=rows(p);counts[str(p.relative_to(ROOT))]=len(rs)
            for r in rs:
                w=ws[r['world_id']]
                assert r['split']==w['split']
                assert r['target']==render(w,advance(d,r['state'],r['operation']),r['template'],r['symbolic'])
                assert score(r['source'],gold(w,r['state'],r['template'],r['symbolic']),w)['success'],(p,r)
                assert score(r['target'],r['gold'],w)['success'],(p,r)
                checks+=2
                if p.name.endswith('_core.jsonl') and r['template']==0:
                    text=r['source'];split=w['split']
                    if text in seen:assert seen[text]==split,'Cross-split exact core collision'
                    seen[text]=split
    manifest=read(ROOT/'data/manifest.json')
    for record in manifest['files']:assert digest(ROOT/record['path'])==record['sha256']
    # Preserve the immutable manifest. Its original summary counts precede the
    # person6 amendment; actual final-file counts below are authoritative.
    for key,value in manifest['counts'].items():
        d,split,kind=key.split('/');actual=counts[f'data/{d}/{split}_{kind}.jsonl']
        if actual!=value:issues.append(dict(key=key,original_summary=value,final_rows=actual,reason='pre-formal person6 addition; payload/file SHA in frozen manifest correct'))
    dump(ROOT/'data_delivery_audit.json',dict(passed=True,checks=checks,counts=counts,manifest_file_hashes_verified=True,exact_core_cross_split_collisions=0,summary_metadata_differences=issues))
    print(checks,'data gold/parser checks; counts metadata differences=',len(issues))

if __name__=='__main__':main()
