import argparse,time,traceback,torch,collections
from transformers.modeling_outputs import BaseModelOutput
from common import *
from backend import Backend,new_editors,tensorhash

def checks(be):
 train=read('data/train_G1.jsonl');b=next(b for b in read('data/sample_schedule.jsonl') if b['path']=='T_plus_first');rows=[train[i] for i in b['pair_indices'][:4]];texts=[r['source_text'] for r in rows];x=be.batch(texts);h,mask,_=be.encode(texts);h_again,_,_=be.encode(texts);assert torch.equal(h,h_again)
 if be.chat:
  direct_ids=be.tok.apply_chat_template([{'role':'user','content':texts[0]}],tokenize=True,add_generation_prompt=True,return_dict=True)['input_ids'];assert direct_ids==x.input_ids[0][x.attention_mask[0].bool()].tolist()
 eds=new_editors(be.d);initial=tensorhash(eds.state_dict());h1=eds['T_plus'](h,mask);assert torch.equal(h1,h);assert torch.equal(h1[mask==0],h[mask==0]);h1.retain_grad()
 before={n:p.detach().clone() for n,p in list(be.model.named_parameters())[:2]}
 y=be.labels([r['target_text'] for r in rows]);shift=be.model.prepare_decoder_input_ids_from_labels(labels=y);expected=y[:,:-1].clone();expected[expected==-100]=be.tok.pad_token_id;assert torch.equal(shift[:,1:],expected)
 with torch.no_grad():
  implicit=be.model(encoder_outputs=BaseModelOutput(last_hidden_state=h),attention_mask=mask,labels=y,use_cache=False)
  explicit=be.model(encoder_outputs=BaseModelOutput(last_hidden_state=h),attention_mask=mask,decoder_input_ids=shift,use_cache=False)
  assert torch.allclose(implicit.logits,explicit.logits,atol=1e-5,rtol=1e-5)
  a,_=be.generate(h,mask);z,_=be.generate(h1,mask);g=be.model.generate(**x,**be.kw);direct=be.tok.batch_decode(g,skip_special_tokens=True,clean_up_tokenization_spaces=False)
  assert [r['output'] for r in a]==direct==[r['output'] for r in z]
 ce,n=be.token_ce(h1,mask,[r['target_text'] for r in rows]);loss=(ce*n).sum()/n.sum();loss.backward();assert torch.isfinite(h1.grad).all() and h1.grad.norm()>0
 grads={n:float(p.grad.norm()) for n,p in eds.named_parameters() if p.grad is not None};assert sum(grads.values())>0 and all(torch.isfinite(p.grad).all() for p in eds.parameters() if p.grad is not None)
 assert all(p.grad is None and not p.requires_grad for p in be.model.parameters());assert not be.model.training
 # Endpoint-only CE through H2 must reach the first output H1.
 eds.zero_grad(set_to_none=True);h1=eds['T_plus'](h,mask);h1.retain_grad();h2=eds['T_plus'](h1,mask);ce,n=be.token_ce(h2,mask,[r['target_text'] for r in rows]);(ce.mean()).backward();assert h1.grad is not None and torch.isfinite(h1.grad).all() and h1.grad.norm()>0
 for n,p in be.model.named_parameters():
  if n in before:assert torch.equal(p,before[n])
 d=ROOT/f'checkpoints/{be.name}';d.mkdir(parents=True,exist_ok=True);torch.save(new_editors(be.d).state_dict(),d/'initial.pt')
 dump(f'checkpoints/{be.name}/initial.json',{'tensor_hash':initial,'file_hash':digest(d/'initial.pt'),'seed':42,'d':be.d,'parameters_per_operator':33*be.d,'all_operators':132*be.d})
 return dict(passed=True,encoder_output_dtype=str(h.dtype),parameter_dtypes=sorted({str(p.dtype) for p in be.model.parameters()}),official_chat_tokenization_equal=True if be.chat else None,dimension=be.d,shape=list(h.shape),mask_lengths=mask.sum(1).tolist(),special_token_ids=be.tok.all_special_ids,labels=y.tolist(),decoder_input_ids=shift.tolist(),label_logits_alignment=True,direct_zero_encoded_generate_identical=True,hidden_gradient_norm=float(h1.grad.norm()),editor_gradient_norms=grads,backbone_gradients_none=True,backbone_parameters_excluded_from_optimizer=True,backbone_sample_weights_unchanged=True,deterministic=True,padding_unchanged=True,chain_endpoint_reaches_H1=True)

def main(name):
 start=time.monotonic();base=ROOT/f'calibration/{name}';base.mkdir(parents=True,exist_ok=True)
 try:
  be=Backend(name,'A');check=checks(be);dump(f'calibration/{name}/interface_check.json',check)
  worlds={w['record_id']:w for w in read('data/calibration_worlds.jsonl')};source=[dict(uid=r['row_id'],record_id=r['record_id'],text=r['source_text'],frame=r['frames'][0],status=r['record_status']) for r in read('data/calibration_views.jsonl')];target=read('data/calibration_targets.jsonl');unique=list(dict.fromkeys(r['text'] for r in source+target));summaries=[]
  for wrapper in ['A','B']:
   be.wrapper=wrapper;dest=base/f'{wrapper}_unique_outputs.jsonl';cache={r['source_text']:r for r in [json.loads(l) for l in dest.read_text().splitlines()]} if dest.exists() else {};todo=[t for t in unique if t not in cache];elapsed=0
   for i in range(0,len(todo),4):
    be.check();texts=todo[i:i+4];t=time.monotonic();ss,timing,lens=be.infer(texts,None,[]);elapsed+=time.monotonic()-t
    with dest.open('a') as f:
     for text,s,n in zip(texts,ss,lens):
      rec=dict(source_text=text,wrapped_input=be.wrap(text),wrapper=wrapper,source_tokens=n,**s[0],timing=timing);cache[text]=rec;f.write(json.dumps(rec)+'\n')
    if i==0:dump(f'calibration/{name}/timing_{wrapper}.json',{'seconds_per_four_examples':elapsed,'estimated_remaining_preflight_seconds':elapsed/len(texts)*(len(todo)-len(texts)+(len(unique) if wrapper=='A' else 0)),'estimated_full_evaluation_seconds':elapsed/len(texts)*26000,'reserve_evaluation_multiplier':1.5})
   rates={};strata={};outputs=[]
   for role,rows in [('source',source),('target',target)]:
    for r in rows:
     result=cache[r['text']];sc=score(result['output'],r['frame'],worlds[r['record_id']],result['ended']);outputs.append({**r,'role':role,'wrapper':wrapper,'output':result['output'],'score':sc,'exact':result['output']==r['text'],'ended':result['ended'],'hit_limit':result['hit_limit']})
    sub=[r for r in outputs if r['role']==role];rates[role]=sum(r['score']['joint_ok'] for r in sub)/len(sub)
    for status in ['recorded_plan','reported_completed','reported_cancelled']:
     rr=[r for r in sub if r['status']==status];strata[role+'/'+status]=dict(N=len(rr),joint=sum(r['score']['joint_ok'] for r in rr),rate=sum(r['score']['joint_ok'] for r in rr)/len(rr))
   write(f'calibration/{name}/{wrapper}_scored.jsonl',outputs);summaries.append(dict(wrapper=wrapper,rates=rates,strata=strata,N=len(outputs),joint=sum(r['score']['joint_ok'] for r in outputs),exact=sum(r['exact'] for r in outputs),normal_end=sum(r['ended'] for r in outputs),unresolved=sum(r['score']['parse_unresolved'] for r in outputs),date_error=sum(r['score']['parsed_date_error'] for r in outputs),nondate_error=sum(r['score']['parsed_nondate_error'] for r in outputs)))
   print(name,wrapper,rates,flush=True)
  chosen=max(summaries,key=lambda r:(min(r['rates'].values()),r['joint']/r['N'],r['wrapper']=='A'));passed=min(chosen['rates'].values())>=.98 and min(v['rate'] for v in chosen['strata'].values())>=.95
  dump(f'calibration/{name}/admission.json',dict(status='passed' if passed else 'reconstruction_failed',passed=passed,selected_wrapper=chosen['wrapper'],summaries=summaries,interface_passed=True,wall_seconds=time.monotonic()-start,peak_cuda_bytes=torch.cuda.max_memory_allocated(),reason=None if passed else 'current frozen interface does not satisfy reconstruction prerequisite',interface_hash=digest(ROOT/f'models/{name}_interface.json')))
 except Exception as e:
  dump(f'calibration/{name}/admission.json',dict(status='incomplete' if isinstance(e,TimeoutError) else 'unsupported',passed=False,reason=type(e).__name__+': '+str(e),traceback=traceback.format_exc(),wall_seconds=time.monotonic()-start));print(traceback.format_exc(),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('name');main(p.parse_args().name)
