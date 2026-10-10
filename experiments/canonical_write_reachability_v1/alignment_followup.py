"""Post-hoc order check constrained to the mask-aligned three-state component."""
from shared import *

@torch.no_grad()
def main():
    p=verify();follow=read(ROOT/'alignment_followup_protocol.json')
    for k,v in follow['sources'].items():assert sha(ROOT/k)==v,k
    eng,load_editor=frozen_engine();advance=semantics()[2];worlds=rows(V2/'eval_worlds.jsonl');fits=device(load(ROOT/'local/rrr.pt'))
    bases={s:load(V2/f'local/fit_s{s}.pt')['q'].cuda() for s in SEEDS}
    models={f'RRR_{c}_r{r}':dict(kind='rrr',condition=c,rank=r,seed=None) for c in p['fit_conditions'] for r in (16,768)}
    for s in SEEDS:
        models[f'CE_s{s}']=dict(kind='ce',condition='CE',rank=16,seed=s)
        models[f'reencode_s{s}']=dict(kind='reencode',condition='reencode',rank=16,seed=s)
    for name,spec in models.items():
        ed=load_editor(eng,previous.task(spec['seed'])['checkpoint']) if spec['seed'] is not None else None
        if ed is not None:ed.requires_grad_(False)
        for t in p['eval_templates']:
            cs={s:canonical('eval',t,s) for s in (-1,0,1)}
            for seqname,seqspec in follow['paths'].items():
                for start in range(0,len(worlds),16):
                    shard=f'results/alignment_shards/{name}_t{t}_{seqname}_b{start:03d}.jsonl'
                    if (ROOT/shard).exists():continue
                    ws=worlds[start:start+16];stop=start+len(ws);state=seqspec['initial_state'];source=cs[state]
                    h=source['h'][start:stop].cuda();m=source['m'][start:stop].cuda();out=[[] for _ in ws];success=[[] for _ in ws];text=None
                    for k,op in enumerate(seqspec['operations']):
                        if k and spec['kind']=='reencode':h,m=eng.encode(text)
                        h=apply_rrr(h,m,fits[spec['condition'],op,spec['rank']]) if spec['kind']=='rrr' else ed[op](h,m)
                        state=advance('time',state,op);decoded=evaluate(eng,h,m,ws,state,t);text=[r['text'] for r in decoded]
                        ref=cs[state];metrics=residual_metrics(h,m,ref['h'][start:stop].cuda(),ref['m'][start:stop].cuda(),bases)
                        for i,w in enumerate(ws):
                            # Reencode may use malformed actual outputs. Its mask
                            # is evaluated honestly; only canonical RRR inputs
                            # are guaranteed aligned throughout these paths.
                            if spec['kind']=='rrr':assert metrics[i]['aligned']
                            success[i].append(decoded[i]['score']['success']);out[i].append(dict(step=k+1,state=state,operation=op,output=decoded[i],**metrics[i]))
                    records=[dict(model=name,**spec,world_id=w['world_id'],template=t,sequence=seqname,initial_state=seqspec['initial_state'],step_successes=success[i],full_trajectory=[all(success[i][:k]) for k in range(1,6)],steps=out[i]) for i,w in enumerate(ws)]
                    write(shard,records);print('aligned follow-up',name,t,seqname,stop,flush=True)
        del ed
    write('results/alignment_followup.jsonl',(r for f in sorted((ROOT/'results/alignment_shards').glob('*.jsonl')) for r in stream(f)))
    dump('results/alignment_followup_complete.json',dict(training_updates=0,post_hoc=True,resources=eng.resources(),followup_protocol_sha256=sha(ROOT/'alignment_followup_protocol.json')))

if __name__=='__main__':main()
