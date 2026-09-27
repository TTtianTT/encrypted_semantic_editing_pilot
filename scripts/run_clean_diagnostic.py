"""Frozen-checkpoint inference only; refuse unreviewed or changed task data."""
import hashlib,json,os,time
from pathlib import Path
import torch
from torch import nn
from pilot import ROOT,Runner,Editor
from b_pilot import metrics as bmetrics
from transformers.modeling_outputs import BaseModelOutput
P=ROOT/'experiments/clean_composition_v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def preflight():
 p=P/'frozen_manifest.json'
 if not p.exists():raise RuntimeError('STOP: no human-reviewed frozen tasks; GPU inference is not authorized before task audit')
 m=json.loads(p.read_text());assert sha(P/'PROTOCOL.md')==m['protocol_sha256']
 for name,h in m['files'].items():assert sha(ROOT/name)==h
 for d in m['checkpoints'].values():assert sha(ROOT/d['path'])==d['sha256']
 return m,sha(p)
@torch.no_grad()
def main():
 md,ch=preflight();start=time.monotonic();r=Runner();outdir=P/'results';outdir.mkdir(exist_ok=True)
 eds={}
 for name,d in md['checkpoints'].items():
  e=nn.ModuleDict({op:Editor('lowrank_affine',r=64).cuda() for op in ['future','present','passive']});e.load_state_dict(torch.load(ROOT/d['path'],weights_only=True));e.eval();eds[name]=e
 def encode(text):
  x=r.tok(text,padding='max_length',max_length=96,truncation=False,return_tensors='pt').to('cuda');assert x.input_ids.shape[1]==96
  return r.model.get_encoder()(**x).last_hidden_state,x.attention_mask
 def decode(z,m):
  g=r.model.generate(encoder_outputs=BaseModelOutput(last_hidden_state=z),attention_mask=m,do_sample=False,num_beams=1,max_new_tokens=100,forced_eos_token_id=None)
  return r.tok.batch_decode(g,skip_special_tokens=True,clean_up_tokenization_spaces=False)[0],bool((g[0,1:]==r.tok.eos_token_id).any())
 for split in ['dev','test']:
  rows=[json.loads(s) for s in (P/f'frozen/{split}.jsonl').read_text().splitlines()];output=outdir/(split+'.jsonl');done={}
  if output.exists():
   for s in output.read_text().splitlines():
    q=json.loads(s);assert q['config_hash']==ch;key=(q['source_id'],q['method'],q['path']);assert key not in done;done[key]=q
  with output.open('a') as f:
   for q in rows:
    plans=[('shared','identity_source'),('shared','identity_passive_target')]+[(name,path) for name in eds for path in ['single_future','single_passive','oracle_intermediate','decode_reencode','latent_once']]
    for method,path in plans:
     key=(q['source_id'],method,path)
     if key in done:continue
     if time.monotonic()-start>3300:raise TimeoutError('55 minute stop; rerun same command to resume')
     torch.cuda.synchronize();t=time.perf_counter();failure=None;mid=None
     try:
      z,m=encode(q['passive_target'] if path in ['oracle_intermediate','identity_passive_target'] else q['source'])
      if path in ['single_future','oracle_intermediate']:z=eds[method]['future'](z,m)
      elif path=='single_passive':z=eds[method]['passive'](z,m)
      elif path in ['latent_once','decode_reencode']:
       z=eds[method]['passive'](z,m)
       if path=='decode_reencode':
        mid,ended=decode(z,m)
        if not ended:raise ValueError('intermediate_no_eos')
        z,m=encode(mid)
       z=eds[method]['future'](z,m)
      text,eos=decode(z,m)
     except Exception as e:text='';eos=False;failure=type(e).__name__+': '+str(e)
     torch.cuda.synchronize();elapsed=time.perf_counter()-t
     # Diagnostic-only old rules, never used to decide human semantic gate.
     metrics=bmetrics(q['source'],text,q['combo_target'],eos)
     record={'source_id':q['source_id'],'group_id':q['group_id'],'split':split,'task':'human_reviewed_future_passive_diagnostic','method':method,'path':path,'seed':42,'config_hash':ch,'input':q['source'],'output':text,'intermediate':mid,'references':{'future':q['future_target'],'passive':q['passive_target'],'combo':q['combo_target']},'metrics_diagnostic_only':metrics,'failure':failure,'timing_s':elapsed,'human_output_review':None}
     f.write(json.dumps(record)+'\n');f.flush();done[key]=record
   assert len(done)==len(rows)*12
 (outdir/'generation_complete.json').write_text(json.dumps({'wall_s':time.monotonic()-start,'job_id':os.environ.get('SLURM_JOB_ID'),'training_steps':0,'human_output_evaluation_pending':True,'config_hash':ch},indent=2)+'\n')
if __name__=='__main__':main()
