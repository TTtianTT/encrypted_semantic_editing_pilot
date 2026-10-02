"""Generate revised labels, check unchanged natural pair sets, and freeze on CPU."""
from common import *
from prepare import records
from semantics import gold,render,advance,relation
from evaluator import score

def main():
    assert not (ROOT/'formal_lock.json').exists(),'Confirmation lock already exists'
    parent=ROOT.parent/'four_domain_state_coverage_v1';ws=rows(ROOT/'data/space/worlds.jsonl');counts={};checks=0
    for split in ('train','dev','test'):
        subset=[w for w in ws if w['split']==split]
        for kind,ts,sym in [('core',(0,1),False),('expression',(2,),False),('challenge',(3,4,5),False),('symbol',(0,),True)]:
            if split=='train' and kind not in ('core','symbol'):continue
            rs=records(subset,ts,sym);path=ROOT/f'data/space/{split}_{kind}.jsonl';jsonl(path,rs);counts[f'space/{split}/{kind}']=len(rs)
            if not sym:
                old=rows(parent/f'data/space/{split}_{kind}.jsonl')
                key=lambda r:(r['world_id'],r['operation'],r['template'],r['source'],r['target'])
                assert sorted(map(key,rs))==sorted(map(key,old)),(split,kind)
            for r in rs:assert score(r['target'],r['gold'],next(w for w in ws if w['world_id']==r['world_id']))['success'];checks+=1
    jsonl(ROOT/'data/space/audit.jsonl',records(ws[96:100],range(6))+records(ws[96:100],(0,),True))
    for w in ws:
        for s in range(4):
            g=gold(w,s);n=advance('space',s,'plus');gn=gold(w,n)
            assert gn['heading']==(g['heading']+1)%4
            assert g['object_xy']==gn['object_xy'] and g['observer_xy']==gn['observer_xy']
            assert g['relation']==['front','right','back','left'][s]
            x=s
            for _ in range(4):x=advance('space',x,'plus')
            assert x==s;checks+=1
    north=dict(object_xy=[0,1],observer_xy=[0,0]);assert [relation(north,s) for s in range(4)]==['front','left','back','right']
    files=sorted((ROOT/'data').glob('*/*.jsonl'))
    dump(ROOT/'data/manifest.json',dict(data_seed=2026100201,worlds_per_domain=dict(train=96,dev=24,test=32),counts=counts,files=[dict(path=str(p.relative_to(ROOT)),sha256=digest(p),bytes=p.stat().st_size) for p in files],parent_manifest_sha=digest(parent/'data/manifest.json'),natural_text_pairs_identical=True,worlds_identical=True,current_state='relative bearing, not physical heading'))
    dump(ROOT/'state_correction_checks.json',dict(passed=True,checks=checks,natural_pair_sets_identical=True,world_splits_identical=True,clockwise_and_four_cycles=True,original_evaluator_sha=digest(parent/'evaluator.py'),new_evaluator_sha=digest(ROOT/'evaluator.py')))
    cfg=read(ROOT/'config.json');cfg.update(scientific_plan_sha=digest(ROOT/'EXPERIMENT_PLAN.md'),data_spec_sha=digest(ROOT/'DATA_SPEC.md'),data_manifest_sha=digest(ROOT/'data/manifest.json'));dump(ROOT/'config.json',cfg)
    lineage=read(ROOT/'SOURCE_LINEAGE.json');lineage.update(config_sha=digest(ROOT/'config.json'),data_manifest_sha=digest(ROOT/'data/manifest.json'));dump(ROOT/'SOURCE_LINEAGE.json',lineage)
    names=[p.name for p in ROOT.glob('*.py')]+['config.json','tasks.json','model_manifest.json','EXPERIMENT_PLAN.md','DATA_SPEC.md','SOURCE_LINEAGE.json','data/manifest.json','job.slurm']
    dump(ROOT/'formal_lock.json',dict(stage='before corrected spatial GPU work',files=[dict(path=n,sha256=digest(ROOT/n)) for n in sorted(names)]))
    print('Frozen corrected spatial protocol;',checks,'checks')

if __name__=='__main__':main()
