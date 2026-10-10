"""Canonical-write RRR, frozen CE and decode-reencode on identical evaluation worlds."""
from shared import *

@torch.no_grad()
def main():
    p=verify();eng,load_editor=frozen_engine();advance=semantics()[2];worlds=rows(V2/'eval_worlds.jsonl')
    fits=device(load(ROOT/'local/rrr.pt'));bases={s:load(V2/f'local/fit_s{s}.pt')['q'].cuda() for s in SEEDS}
    models={f'RRR_{c}_r{r}':dict(kind='rrr',condition=c,rank=r,seed=None) for c in p['fit_conditions'] for r in p['ranks']}
    for s in SEEDS:
        models[f'CE_s{s}']=dict(kind='ce',condition='CE',rank=16,seed=s)
        models[f'reencode_s{s}']=dict(kind='reencode',condition='reencode',rank=16,seed=s)
    for name,spec in models.items():
        editor=None
        if spec['seed'] is not None:
            editor=load_editor(eng,previous.task(spec['seed'])['checkpoint']);editor.requires_grad_(False)
        def edit(h,m,op):
            return apply_rrr(h,m,fits[spec['condition'],op,spec['rank']]) if spec['kind']=='rrr' else editor[op](h,m)
        for t in p['eval_templates']:
            cs={s:canonical('eval',t,s) for s in p['states']}
            for start in range(0,len(worlds),16):
                ws=worlds[start:start+16];stop=start+len(ws);records=[]
                shard=f'results/shards/{name}_t{t}_b{start:03d}.jsonl'
                if (ROOT/shard).exists():continue
                # One-step evaluations start from canonical states. Reencoding
                # uses the same CE operator here, so there is no hidden oracle.
                for s in p['states']:
                    source=cs[s];h=source['h'][start:stop].cuda();m=source['m'][start:stop].cuda()
                    for op in p['operators']:
                        try:target=advance('time',s,op)
                        except ValueError:continue
                        z=edit(h,m,op);out=evaluate(eng,z,m,ws,target,t)
                        ref=cs[target];metric=residual_metrics(z,m,ref['h'][start:stop].cuda(),ref['m'][start:stop].cuda(),bases)
                        for i,w in enumerate(ws): records.append(dict(panel='single',model=name,**spec,world_id=w['world_id'],template=t,source_state=s,target_state=target,operation=op,output=out[i],**metric[i]))
                for seqname,seq in p['sequences'].items():
                    source=cs[0];h=source['h'][start:stop].cuda();m=source['m'][start:stop].cuda();state=0;outs=[[] for _ in ws];success=[[] for _ in ws]
                    text=None
                    for step,op in enumerate(seq):
                        if step and spec['kind']=='reencode': h,m=eng.encode(text)
                        h=edit(h,m,op);state=advance('time',state,op);out=evaluate(eng,h,m,ws,state,t);text=[r['text'] for r in out]
                        ref=cs[state];metric=residual_metrics(h,m,ref['h'][start:stop].cuda(),ref['m'][start:stop].cuda(),bases)
                        for i,w in enumerate(ws):
                            success[i].append(out[i]['score']['success']);outs[i].append(dict(step=step+1,state=state,operation=op,output=out[i],**metric[i]))
                    for i,w in enumerate(ws):records.append(dict(panel='chain',model=name,**spec,world_id=w['world_id'],template=t,sequence=seqname,step_successes=success[i],full_trajectory=[all(success[i][:k]) for k in range(1,6)],steps=outs[i]))
                write(shard,records);print('evaluated',name,t,stop,flush=True)
        del editor
    # All model shards, including CE and reencode, belong in the same ledger.
    write('results/evaluation.jsonl',(r for f in sorted((ROOT/'results/shards').glob('*_t*_b*.jsonl')) if not f.name.startswith('controls_') for r in stream(f)))
    assert all(q.grad is None for q in eng.model.parameters())
    dump('results/evaluate_complete.json',dict(training_updates=0,resources=eng.resources(),records=sum(1 for _ in stream(ROOT/'results/evaluation.jsonl')),protocol_sha256=sha(ROOT/'protocol.json')))

if __name__=='__main__':main()
