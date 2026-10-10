"""Post-hoc cumulative native K/V patching after no single-layer rescue."""
from decoder import *

@torch.no_grad()
def main():
    protocol=verify_protocol();eng,load_editor=engine();render,gold,advance,states,score=semantics()
    sets=[('prefix',k,list(range(k))) for k in range(1,7)]+[('suffix',k,list(range(6-k,6))) for k in range(1,6)]
    for seed in SEEDS:
        ed=load_editor(eng,task(seed)['checkpoint']);ed.requires_grad_(False);pairs=selections(seed)[:40]
        for start in range(0,len(pairs),8):
            name=f'results/decoder_cumulative/s{seed}_b{start:03d}.jsonl'
            if (ROOT/name).exists():continue
            rs=pairs[start:start+8];bad,good,m=patch_pair_batch(rs);ws=[r['world'] for r in rs];B=len(rs)
            hb,hg=ed['plus'](bad,m),ed['plus'](good,m);texts=[render(w,-1,0) for w in ws]
            reference,y=logits(eng,hg,m,texts);out=[]
            h=hb.repeat(3,1,1);g=hg.repeat(3,1,1);mm=m.repeat(3,1);ww=ws*3;tt=texts*3
            kr=torch.tensor([True]*B+[False]*B+[True]*B,device='cuda');vr=torch.tensor([False]*B+[True]*B+[True]*B,device='cuda')
            for direction,count,selected in sets:
                with kv_hooks(eng,g,mm,selected,kr,vr,mm.bool()):
                    changed,labels=logits(eng,h,mm,tt);free=decode_uncached(eng,h,mm,ww)
                metrics=distribution(reference.repeat(3,1,1),changed,labels)
                for block,condition in enumerate(('K','V','KV')):
                    for i,r in enumerate(rs):
                        k=block*B+i
                        if count==6 and condition=='KV':assert free[k]['score']['success']
                        out.append(dict(seed=seed,world_id=r['world_id'],direction=direction,layer_count=count,layers=selected,
                            condition=condition,next_success=free[k]['score']['success'],output=free[k],teacher_forced_vs_donor=metrics[k],post_hoc=True))
            assert all(not getattr(layer.encoder_attn,kind+'_proj')._forward_hooks for layer in layers(eng) for kind in ('k','v','q'))
            write(name,out);print('cumulative decoder',seed,start+B,flush=True)
        del ed
    write('results/decoder_cumulative.jsonl',[r for p in sorted((ROOT/'results/decoder_cumulative').glob('*.jsonl')) for r in rows(p)])
    dump('results/decoder_cumulative_complete.json',dict(resources=eng.resources(),training_updates=0,post_hoc=True,
        source=sha(__file__),code_sha256=sha(__file__),protocol_sha256=sha(ROOT/'protocol.json')))

if __name__=='__main__':main()
