"""Audit complete grid, individual worlds, frozen inputs, training and artifacts."""
from cutil import *

def main():
    p=verify();expected={'closure':2*3*80*50,'dose':3*7*2*4*80*5,'mixsingle':3*7*2*8*80,'overshoot':3*2*8*80,'chain':36*2*4*80*5,'single':36*2*12*80,'injection':15*2*80}
    actual={};fingerprints={}
    for kind,n in expected.items():
        rs=rows(ROOT/f'results/{kind}.jsonl');assert len(rs)==n,(kind,len(rs),n);actual[kind]=len(rs)
        keys={'closure':['world_id','template','path','step'],'dose':['seed','lambda_','world_id','template','path','step'],'mixsingle':['seed','lambda_','world_id','template','source_state','operation'],'overshoot':['seed','world_id','template','source_state','operation'],'chain':['group','seed','checkpoint','world_id','template','path','step'],'single':['group','seed','checkpoint','world_id','template','source_state','operation'],'injection':['group','seed','world_id','template']}[kind]
        seen={tuple(r[k] for k in keys) for r in rs};assert len(seen)==n,kind
        assert all(r['world_id'] in p['worlds_eval'] for r in rs)
    for g in ('C1','C2','C3','C4','C5'):
      for s in SEEDS:
        c=read(ROOT/f'results/train_{g}_s{s}_complete.json');assert c['updates']==600 and c['examples']==4800
        h=rows(ROOT/f'results/train_{g}_s{s}.jsonl');assert [r['step'] for r in h]==list(range(1,601));assert all(np.isfinite(r['loss']) for r in h)
        f=load(ROOT/f'local/pca_{g}_s{s}.pt');assert f['world_ids']==p['worlds_train'];assert not(set(f['world_ids'])&set(p['worlds_eval']))
        assert c['final_sha256']==sha(ROOT/f'local/{g}_s{s}_0600.pt')
    for f in ROOT.rglob('*'):
        if f.is_file() and not any(x in ('local','logs','__pycache__','shards') for x in f.relative_to(ROOT).parts) and f.name not in ('audit.json','manifest.json'):
            fingerprints[str(f.relative_to(ROOT))]=sha(f)
    dump('manifest.json',fingerprints);dump('audit.json',dict(passed=True,records=actual,total_records=sum(actual.values()),training_updates=9000,source_files=len(p['sources']),frozen_inputs=len(p['inputs']),protocol_sha256=sha(ROOT/'protocol.json')));print('audit passed',actual)

if __name__=='__main__':main()
