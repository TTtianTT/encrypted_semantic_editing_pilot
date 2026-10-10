"""Supplementary artifact, initialization and trajectory consistency audit."""
import gzip, platform, importlib.metadata
from cutil import *

def main():
    p=verify();index=[]
    for g in ('C1','C2','C3','C4','C5'):
     for s in SEEDS:
      for k in p['training']['evaluation_C4_checkpoints'] if g=='C4' else [600]:
        file=ROOT/f'local/{g}_s{s}_{k:04d}.pt';ck=load(file)
        assert ck['step']==k and ck['protocol_sha256']==sha(ROOT/'protocol.json')
        sd=ck['editor'];assert sum(v.numel() for v in sd.values())==50688
        for op in ('plus','minus'):
            assert sd[f'{op}.v.weight'].shape==(16,768) and sd[f'{op}.u.weight'].shape==(768,16)
        index.append(dict(group=g,seed=s,step=k,path=str(file.relative_to(ROOT)),sha256=sha(file),parameter_count=50688,rank=16))
    dump('checkpoint_index.json',index)
    for r in read(ROOT/'results/prediction_archives.json'):
        archive=ROOT/r['archive'];assert sha(archive)==r['archive_sha256'];h=hashlib.sha256()
        with gzip.open(archive,'rb') as z:
            for chunk in iter(lambda:z.read(1048576),b''):h.update(chunk)
        assert h.hexdigest()==r['raw_sha256']
    # Balanced C4 and original RRR endpoint must have identical observed scores.
    dose={(r['seed'],r['template'],r['path'],r['world_id'],r['step']):r for r in old.stream(ROOT/'results/dose.jsonl') if r['lambda_']==1}
    n=0
    for r in old.stream(ROOT/'results/chain.jsonl'):
        if r['group']=='C4' and r['checkpoint']==0:
            ref=dose[r['seed'],r['template'],r['path'],r['world_id'],r['step']]
            assert r['output']['score']==ref['output']['score']
            assert r['trajectory_success']==ref['trajectory_success'];n+=1
    # Complete trajectory indicators are exact cumulative success, including past failures.
    by=defaultdict(list)
    for r in old.stream(ROOT/'results/chain.jsonl'):by[r['group'],r['seed'],r['checkpoint'],r['template'],r['path'],r['world_id']].append(r)
    for values in by.values():
        values.sort(key=lambda x:x['step']);assert [r['step'] for r in values]==[1,2,3,4,5];success=True
        for r in values:success=success and r['output']['score']['success'];assert success==r['trajectory_success']
    dump('delivery_audit.json',dict(passed=True,C4_initial_RRR_score_matches=n,complete_trajectories=len(by),archives_verified=7,checkpoint_entries=len(index),parameter_count=50688,backbone_frozen=True,python=platform.python_version(),libraries={n:importlib.metadata.version(n) for n in ('torch','transformers','numpy','scipy','matplotlib')},notes=['Derived post-lock analysis scripts do not change inference or training.','Pooled affine geometry is computed on CPU; tokenwise GPU residuals are the primary aligned metrics.']))
    print('delivery audit passed',n,len(by))

if __name__=='__main__':main()
