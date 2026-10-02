"""Correct invisible-heading holdout BEFORE any formal space task starts."""
import gzip,shutil
from common import *
from prepare import records
from semantics import render,gold,advance

def main():
    event=ROOT/'protocol_revisions/space_relation_holdout.json'
    if event.exists():raise RuntimeError('Correction already recorded')
    assert not list((ROOT/'runs/formal').glob('*_space_*/dev/admission.json'))
    assert not list((ROOT/'local/formal').glob('*_space_*')),'Formal space must not have started'
    previous=read(ROOT/'data/manifest.json');archive=ROOT/'data_revisions/space_before_relation_holdout';archive.mkdir(parents=True,exist_ok=True);dump(archive/'manifest.json',previous)
    ws=rows(ROOT/'data/space/worlds.jsonl')
    for p in sorted((ROOT/'data/space').glob('*.jsonl')):
        if p.name=='worlds.jsonl':continue
        with gzip.open(archive/(p.name+'.gz'),'wb') as f:f.write(p.read_bytes())
        if p.name=='audit.jsonl':rs=records(ws[96:100],range(6))+records(ws[96:100],(0,),True)
        else:
            split,kind=p.stem.split('_');subset=[w for w in ws if w['split']==split]
            templates={'core':(0,1),'expression':(2,),'challenge':(3,4,5),'symbol':(0,)}[kind]
            rs=records(subset,templates,kind=='symbol')
        jsonl(p,rs)
    for f in previous['files']:
        if f['path'].startswith('data/space/'):
            p=ROOT/f['path'];f.update(sha256=digest(p),bytes=p.stat().st_size)
    previous['space_state_definition']='observable relative bearing index0front/1right/2back/3left; heading reconstructed from fixed cardinal world ray; plus heading+1 gives bearing−1'
    dump(ROOT/'data/manifest.json',previous)
    # Exhaustive regression: non-space file bytes/renderer/gold/transitions are
    # unchanged, despite the one shared Python module's new hash.
    for d in ('time','emotion','person'):
        worlds={w['world_id']:w for w in rows(ROOT/f'data/{d}/worlds.jsonl')}
        for p in (ROOT/f'data/{d}').glob('*_core.jsonl'):
            for r in rows(p):
                w=worlds[r['world_id']]
                assert r['source']==render(w,r['state'],r['template'],r['symbolic'])
                nxt=advance(d,r['state'],r['operation']);assert r['target']==render(w,nxt,r['template'],r['symbolic']) and r['gold']==gold(w,nxt,r['template'],r['symbolic'])
    cfg=read(ROOT/'config.json');cfg['space_state_definition']=previous['space_state_definition'];cfg['data_manifest_sha']=digest(ROOT/'data/manifest.json');dump(ROOT/'config.json',cfg)
    before=read(ROOT/'protocol_revisions/initial_formal_lock/formal_lock.json');new=read(ROOT/'formal_lock.json')
    for f in new['files']:
        p=ROOT/f['path'];f['sha256']=digest(p)
    new['revision']='observable-space-current-state correction before any formal space train/test; non-space computations/data unchanged'
    new['preceding_lock_sha']=digest(ROOT/'protocol_revisions/initial_formal_lock/formal_lock.json');dump(ROOT/'formal_lock.json',new)
    dump(event,dict(reason='Holding out a heading not expressed in core text is not holding out the current observable relative semantic state',new_state=previous['space_state_definition'],H=[1,3],S=[0],M=[0,2],before_formal_space=True,space_test_outputs_seen=False,nonspace_test_outputs_seen=True,nonspace_payload_and_transform_regression_passed=True,unchanged=['world content/splits','train/dev/test world count','all legal natural atomic transitions','rank/lr/updates/seeds','Slurm globalGPU limit','all non-space data/operators'],old_lock_sha=digest(ROOT/'protocol_revisions/initial_formal_lock/formal_lock.json'),new_lock_sha=digest(ROOT/'formal_lock.json')))
    print('Space observable-state holdout corrected before domain formal runs')

if __name__=='__main__':main()
