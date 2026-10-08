"""Actual raw and post-processor generation scores plus observed head readouts."""
import math
import torch
from transformers.modeling_outputs import BaseModelOutput
from .common import *
from .engine import hooks
from .readout import pairs,token_sites,tensor_difference

@torch.no_grad()
def run(eng,folder):
    worlds=rows(ROOT/'configs/worlds.jsonl');ws=[w for w in worlds if w['split']=='train'][:4]+[w for w in worlds if w['split']=='validation'][:4]
    records=[];heads=[];configs=dict(native_generation_config=eng.model.generation_config.to_dict(),runtime_overrides=eng.kw)
    dump(folder/'DECODING_CONFIG.json',configs)
    for wi,w in enumerate(ws):
        ps,_,_=pairs(eng,w,folder)
        for pair,a,b,mask in ps:
            captures=[]
            for side,h in [('a',a),('b',b)]:
                calls=eng.encoder_calls
                g=eng.model.generate(encoder_outputs=BaseModelOutput(last_hidden_state=h),attention_mask=mask,**eng.kw,return_dict_in_generate=True,output_scores=True,output_logits=True)
                assert eng.encoder_calls==calls
                assert g.sequences[0].tolist()==pair[side]['token_ids'],'Score capture changed native tokens'
                assert len(g.scores)==len(g.logits)==g.sequences.shape[1]-1
                for j,(raw,processed) in enumerate(zip(g.logits,g.scores)):
                    token=int(g.sequences[0,j+1]);r=raw[0].float();s=processed[0].float();finite=torch.isfinite(r)&torch.isfinite(s)
                    competitor=s.clone();competitor[token]=-torch.inf;value=float(s[token]-competitor.max())
                    raw_comp=r.clone();raw_comp[token]=-torch.inf
                    records.append(dict(world_id=w['world_id'],split=w['split'],source_pair=pair['source_pair'],side=side,position=j,token_id=token,raw_target_margin=float(r[token]-raw_comp.max()),processed_target_margin=value if math.isfinite(value) else 'FORCED_INFINITY',raw_argmax=int(r.argmax()),processed_argmax=int(s.argmax()),actual_token=token,processor_finite_max_difference=float((s-r)[finite].abs().max()) if finite.any() else None,processor_masked_vocab_count=int((torch.isfinite(r)&~torch.isfinite(s)).sum()),encoder_calls_during_generation=eng.encoder_calls-calls))
                if wi==0:torch.save(dict(ids=g.sequences.cpu(),raw=[x.cpu() for x in g.logits],processed=[x.cpu() for x in g.scores]),folder/(pair['source_pair'].replace(':','_')+'_'+side+'_actual_generation_scores.pt'))
                ids=g.sequences;av={}
                with hooks([(module.out_proj,lambda mod,args,name=name:av.__setitem__(name,args[0].detach().clone()),True) for name,module in eng.cross]):eng.logits(h,mask,decoder_ids=ids[:,:-1])
                captures.append(av)
            groups=token_sites(eng,pair['a']['text'])
            for name,module in eng.cross:
                xa,xb=captures[0][name],captures[1][name];pieces=[]
                for head in range(module.num_heads):
                    lo=head*module.head_dim;hi=lo+module.head_dim;weight=module.out_proj.weight[:,lo:hi]
                    ca=xa[...,lo:hi]@weight.T;cb=xb[...,lo:hi]@weight.T;pieces.append(cb-ca)
                    for group in ('content','attribute','other','special'):
                        sites=[i for i,g in enumerate(groups) if g==group and i<xa.shape[1]]
                        if sites:heads.append(dict(world_id=w['world_id'],split=w['split'],source_pair=pair['source_pair'],module=name,head=head,group=group,positions=len(sites),**tensor_difference(ca[:,sites],cb[:,sites]),site='AV head contribution after W_O slice, global bias cancels in delta',classification='observational; A changes may include upstream Q changes'))
                whole=sum(pieces);ratio=float(whole.norm()/(sum(p.norm() for p in pieces)+1e-9))
                heads.append(dict(world_id=w['world_id'],split=w['split'],source_pair=pair['source_pair'],module=name,head='ALL',group='all_native',linear_head_delta_sum_norm=float(whole.norm()),sum_head_delta_norms=sum(float(p.norm()) for p in pieces),linear_cancellation_ratio=ratio,classification='observational linear sum cancellation, not causal sufficiency'))
        jsonl(folder/'raw_processed_decisions.jsonl',records);jsonl(folder/'head_readouts.jsonl',heads);print('generation audit worlds',wi+1,flush=True)
    ordinary=[r for r in records if r['position']>0]
    return dict(passed=True,worlds=len(ws),generation_token_records=len(records),non_initial_token_records=len(ordinary),non_initial_raw_argmax_disagrees=sum(r['raw_argmax']!=r['actual_token'] for r in ordinary),non_initial_processed_argmax_disagrees=sum(r['processed_argmax']!=r['actual_token'] for r in ordinary),forced_token_records=sum(r['processed_target_margin']=='FORCED_INFINITY' for r in records),observational_head_records=len(heads),generation_encoder_calls=0,test_evaluations=0,resources=eng.resources())
