"""Trusted GPU client decodes all three numerical paths through the same G."""
import json,time,hashlib,os
from pathlib import Path
import numpy as np,torch
from transformers.modeling_outputs import BaseModelOutput
from pilot import ROOT,Runner,Editor,dump
from evaluate import evaluate
r=Runner();T=ROOT/'he/trusted';samples=json.load(open(T/'samples.json'));inp=np.load(T/'inputs.npz');params=json.load(open(T/'parameters.json'));ch=hashlib.sha256(json.dumps(params,sort_keys=True).encode()).hexdigest();records=[];comparisons=[]
ed=Editor('lowrank_affine',r=64).cuda();ed.load_state_dict(torch.load(ROOT/'checkpoints/lowrank_affine_r64_s42/best.pt',weights_only=True))
start=time.monotonic()
with (T/'text_results.jsonl').open('w') as f:
 for i,source in enumerate(samples):
  op=json.load(open(T/f'sample_{i:02}.json'));npz=np.load(T/f'sample_{i:02}.npz') if not op['failure'] else None
  outputs={};tokens={};memories={};times={}
  torch.cuda.synchronize();lt=time.perf_counter()
  with torch.no_grad():
   lx,_=r.batch([source]);lz=r.model.get_encoder()(**lx).last_hidden_state
   torch.cuda.synchronize();le=time.perf_counter();lm=ed(lz,lx.attention_mask);torch.cuda.synchronize();la=time.perf_counter()
   lg=r.model.generate(encoder_outputs=BaseModelOutput(last_hidden_state=lm),attention_mask=lx.attention_mask,do_sample=False,num_beams=1,max_new_tokens=100,forced_eos_token_id=None)
  torch.cuda.synchronize();lgtime=time.perf_counter();local_text=r.tok.decode(lg[0],skip_special_tokens=True,clean_up_tokenization_spaces=False)
  local_timing={'encode_with_tokenize':le-lt,'edit':la-le,'decode':lgtime-la,'total':lgtime-lt}
  for path in ['float','quant','he']:
   if path!='float' and npz is None:out='';ended=False;elapsed=0;ids=[]
   else:
    arr=inp['float_edit'][i] if path=='float' else npz[path]
    memory=torch.from_numpy(arr).float().cuda().unsqueeze(0);mask=torch.from_numpy(inp['mask'][i]).long().cuda().unsqueeze(0);memories[path]=memory
    torch.cuda.synchronize();t=time.perf_counter()
    with torch.no_grad():g=r.model.generate(encoder_outputs=BaseModelOutput(last_hidden_state=memory),attention_mask=mask,do_sample=False,num_beams=1,max_new_tokens=100,forced_eos_token_id=None)
    torch.cuda.synchronize();elapsed=time.perf_counter()-t;ids=g[0].tolist();out=r.tok.decode(ids,skip_special_tokens=True,clean_up_tokenization_spaces=False);ended=r.tok.eos_token_id in ids[1:]
   rr={**source,'method':'CKKS_'+path,'seed':42,'config_hash':ch,'output':out,'metrics':evaluate(source['input'],out,source['reference'],ended),'timing_s':{'generate':elapsed},'failure':op['failure'] if path!='float' else None};f.write(json.dumps(rr)+'\n');f.flush();records.append(rr);outputs[path]=out;tokens[path]=ids;times[path]=elapsed
  c={'source_id':source['source_id'],'he_matches_float':outputs['he']==outputs['float'],'quant_matches_float':outputs['quant']==outputs['float'],'operator':op,'generation_times_s':times,'local_ETG_timing_s':local_timing,'local_ETG_output':local_text,'local_ETG_matches_float':local_text==outputs['float']}
  if tokens['he']!=tokens['float'] and npz is not None:
   at=next((j for j,(a,b) in enumerate(zip(tokens['float'],tokens['he'])) if a!=b),min(len(tokens['float']),len(tokens['he'])))
   prefix=torch.tensor([tokens['float'][:at]],device='cuda')
   c['first_divergence_position']=at;c['token_margin']={}
   if at>0:
    with torch.no_grad():
     for path in ['float','he']:
      logits=r.model(encoder_outputs=BaseModelOutput(last_hidden_state=memories[path]),attention_mask=mask,decoder_input_ids=prefix).logits[0,-1];vals,inds=logits.topk(2);c['token_margin'][path]={'top_tokens':inds.tolist(),'scores':vals.tolist(),'margin':float(vals[0]-vals[1])}
  comparisons.append(c);print('HE decoded',i+1,len(samples),flush=True)
summary={'n':len(samples),'operator_failures':sum(bool(c['operator']['failure']) for c in comparisons),'he_float_text_matches':sum(c['he_matches_float'] for c in comparisons),'quant_float_text_matches':sum(c['quant_matches_float'] for c in comparisons),'local_ETG_matches_float':sum(c['local_ETG_matches_float'] for c in comparisons),'local_ETG_mean_s':float(np.mean([c['local_ETG_timing_s']['total'] for c in comparisons])),'paths':{},'decode_process_s':time.monotonic()-start,'job':os.environ.get('SLURM_JOB_ID')}
for path in ['float','quant','he']:
 rr=[x for x in records if x['method']=='CKKS_'+path];summary['paths'][path]={'n':len(rr),**{k:float(np.mean([x['metrics'][k] for x in rr])) for k in ['Joint_auto','attribute_auto','content_auto','valid_auto']},'generation_seconds_mean':float(np.mean([x['timing_s']['generate'] for x in rr]))}
dump(T/'text_comparisons.json',comparisons);dump(T/'text_summary.json',summary);print('HE_TEXT_COMPLETE',flush=True)
