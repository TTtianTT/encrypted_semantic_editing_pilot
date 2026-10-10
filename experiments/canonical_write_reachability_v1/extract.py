"""Frozen canonical state cache; no fitting and no evaluation-driven selection."""
from shared import *

@torch.no_grad()
def main():
    protocol=verify();eng,_=frozen_engine();render,*_=semantics()
    for split in ('train','eval'):
        worlds=rows(V2/f'{split}_worlds.jsonl')
        for t in protocol['eval_templates']:
            for s in protocol['states']:
                name=f'local/{split}_t{t}_s{s}.pt'
                if (ROOT/name).exists():continue
                hs=[];ms=[]
                for start in range(0,len(worlds),16):
                    h,m=eng.encode([render(w,s,t) for w in worlds[start:start+16]])
                    hs.append(h.cpu());ms.append(m.cpu())
                h=torch.cat(hs);m=torch.cat(ms);length=int(m.sum(1).max())
                save(name,dict(h=h[:,:length],m=m[:,:length],world_ids=[w['world_id'] for w in worlds],state=s,template=t))
                print('canonical',split,t,s,tuple(h[:,:length].shape),flush=True)
    dump('results/extract_complete.json',dict(training_updates=0,resources=eng.resources(),protocol_sha256=sha(ROOT/'protocol.json'),cache_hashes={p.name:sha(p) for p in (ROOT/'local').glob('*_t*_s*.pt')}))

if __name__=='__main__':main()
