"""Four matched free-generation paths on a pre-reviewed retrospective sample."""
import hashlib,importlib.metadata,json,os,platform,time
from datetime import datetime,timezone
from pathlib import Path
import torch
from transformers.modeling_outputs import BaseModelOutput
from pilot import ROOT,Runner,Editor,seed,dump
from evaluate import evaluate
P=ROOT/'experiments/single_step_diagnosis_v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
@torch.no_grad()
def main():
 started=time.monotonic();cfg=json.loads((P/'config.json').read_text());ch=sha(P/'config.json');frozen=json.loads((P/'task_review_frozen.json').read_text());samplemd=json.loads((P/'sample_manifest.json').read_text())
 assert frozen['before_new_outputs'] and sha(P/'task_validity.csv')==frozen['task_validity_sha256'];assert sha(P/'PROTOCOL.md')==frozen['protocol_sha256'];assert sha(P/'sample_manifest.json')==frozen['sample_manifest_sha256'];assert sha(P/'samples.jsonl')==samplemd['samples_sha256'] and ch==samplemd['config_sha256']
 for p,h in cfg['model_files'].items():assert sha(ROOT/p)==h
 for d in cfg['checkpoints'].values():assert sha(ROOT/d['path'])==d['sha256']
 seed(cfg['seed']);r=Runner();assert not r.model.training and all(not p.requires_grad for p in r.model.parameters());torch.cuda.reset_peak_memory_stats()
 eds={'identity_source':Editor('identity').cuda().eval(),'identity_target':Editor('identity').cuda().eval(),'shift':Editor('shift').cuda().eval(),'lowrank':Editor('lowrank_affine',r=64).cuda().eval()}
 for name in ['shift','lowrank']:eds[name].load_state_dict(torch.load(ROOT/cfg['checkpoints'][name]['path'],weights_only=True))
 gen={'do_sample':False,'num_beams':1,'max_new_tokens':100,'forced_eos_token_id':None}
 def tokens(text):
  x=r.tok(text,padding='max_length',max_length=96,truncation=False,return_tensors='pt').to('cuda');assert x.input_ids.shape[1]==96;assert torch.equal(x.attention_mask,(x.input_ids!=r.tok.pad_token_id).long());return x
 samples=[json.loads(s) for s in (P/'samples.jsonl').read_text().splitlines()]
 smoke=[]
 for field in ['input','reference']:
  x=tokens([q[field] for q in samples[:3]]);z=r.model.get_encoder()(**x).last_hidden_state
  a=r.model.generate(**x,**gen);b=r.model.generate(encoder_outputs=BaseModelOutput(last_hidden_state=z),attention_mask=x.attention_mask,**gen)
  assert torch.equal(a,b),'encoder_outputs changed generation'
  for kind in ['identity_source','identity_target']:assert torch.equal(eds[kind](z,x.attention_mask),z)
  assert all(bool((g[1:]==r.tok.eos_token_id).any()) for g in a)
  smoke.append({'input_field':field,'n':3,'direct_vs_wrapped_ids_equal':True,'identity_memory_equal':True,'padding_mask_correct':True,'eos_present':True})
 dump(P/'smoke.json',{'checks':smoke,'EG_eval':not r.model.training,'EG_frozen':all(not p.requires_grad for p in r.model.parameters()),'teacher_forcing_used':False,'special_tokens':{k:getattr(r.model.config,k) for k in ['bos_token_id','eos_token_id','pad_token_id','decoder_start_token_id']}})
 dump(P/'runtime_environment.json',{'job_id':os.environ.get('SLURM_JOB_ID'),'node':platform.node(),'GPU':torch.cuda.get_device_name(0),'GPU_count':torch.cuda.device_count(),'CPU_threads':torch.get_num_threads(),'cuda_build':torch.version.cuda,'versions':{k:importlib.metadata.version(k) for k in ['torch','transformers','tokenizers','numpy','spacy']},'generation_config':r.model.generation_config.to_dict(),'overrides':gen,'config_sha256':ch,'started_at':datetime.now(timezone.utc).isoformat()})
 output=P/'outputs.jsonl';done={}
 if output.exists():
  for line in output.read_text().splitlines():
   q=json.loads(line);assert q['config_hash']==ch;key=(q['source_id'],q['path']);assert key not in done;done[key]=q
 with output.open('a') as f:
  for path in cfg['paths']:
   for i in range(0,len(samples),16):
    batch=[q for q in samples[i:i+16] if (q['source_id'],path) not in done]
    if not batch:continue
    if time.monotonic()-started>cfg['max_gpu_wall_s']:raise TimeoutError('Budget stop; resume same command')
    field='reference' if path=='identity_target' else 'input';failure=None;torch.cuda.synchronize();t=time.perf_counter()
    try:
     x=tokens([q[field] for q in batch]);z=r.model.get_encoder()(**x).last_hidden_state;ze=eds[path](z,x.attention_mask)
     g=r.model.generate(encoder_outputs=BaseModelOutput(last_hidden_state=ze),attention_mask=x.attention_mask,**gen)
     texts=r.tok.batch_decode(g,skip_special_tokens=True,clean_up_tokenization_spaces=False);ends=[bool((a[1:]==r.tok.eos_token_id).any()) for a in g];lengths=[int((a!=r.tok.pad_token_id).sum()) for a in g];inputlengths=x.attention_mask.sum(1).cpu().tolist()
    except Exception as ex:failure=type(ex).__name__+': '+str(ex);texts=['']*len(batch);ends=[False]*len(batch);lengths=[0]*len(batch);inputlengths=[None]*len(batch)
    torch.cuda.synchronize();elapsed=time.perf_counter()-t
    for q,text,end,n,inp_n in zip(batch,texts,ends,lengths,inputlengths):
     old=evaluate(q[field],text,q['reference'],end)
     record={'case_id':q['case_id'],'source_id':q['source_id'],'split':'test_retrospective_sample','task':'StylePTB_TFU','path':path,'method':path,'seed':cfg['seed'],'config_hash':ch,'repo_commit':samplemd['repo_commit'],'checkpoint':cfg['checkpoints'].get(path),'model_revision':cfg['model_revision'],'input':q['input'],'reference':q['reference'],'generation_input':q[field],'output':text,'input_tokens':inp_n,'generated_tokens_including_start':n,'eos_found':end,'truncated':not end,'failure':failure,'timing_s':elapsed/len(batch),'old_auto_diagnostic':old,'exact_input':text==q[field],'exact_reference':text==q['reference'],'generated_at':datetime.now(timezone.utc).isoformat()}
     f.write(json.dumps(record)+'\n');f.flush();done[q['source_id'],path]=record
   print('GENERATED',path,len([k for k in done if k[1]==path]),flush=True)
 assert len(done)==4*len(samples)
 dump(P/'generation_summary.json',{'complete':True,'outputs':len(done),'sources':len(samples),'wall_s':time.monotonic()-started,'peak_allocated_bytes':torch.cuda.max_memory_allocated(),'peak_reserved_bytes':torch.cuda.max_memory_reserved(),'job_id':os.environ.get('SLURM_JOB_ID'),'config_hash':ch,'output_sha256':sha(output),'generated_failures':sum(q['failure'] is not None for q in done.values()),'truncated':sum(q['truncated'] for q in done.values())});print('SINGLE_STEP_GENERATION_COMPLETE',flush=True)
if __name__=='__main__':main()
