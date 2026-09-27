"""Separate end-to-end local instruction baseline; never used in editor selection."""
import json,time,os,hashlib
from pathlib import Path
import torch
from transformers import AutoTokenizer,AutoModelForCausalLM
from evaluate import evaluate
ROOT=Path(__file__).resolve().parents[1];MODEL='/dataset1/zailong/models/Qwen2.5-7B-Instruct'
torch.set_num_threads(4)
torch.backends.cuda.enable_cudnn_sdp(False)
tok=AutoTokenizer.from_pretrained(MODEL,local_files_only=True);tok.padding_side='left'
if tok.pad_token_id is None:tok.pad_token_id=tok.eos_token_id
start=time.monotonic();model=AutoModelForCausalLM.from_pretrained(MODEL,local_files_only=True,dtype=torch.bfloat16,attn_implementation='sdpa').cuda().eval();load_s=time.monotonic()-start
rs=sorted([json.loads(s) for s in (ROOT/'data/test.jsonl').read_text().splitlines()],key=lambda r:r['source_id'])[:100]
config={'model':MODEL,'config_file_sha256':hashlib.sha256(Path(MODEL,'config.json').read_bytes()).hexdigest(),'prompt':'Rewrite the sentence in future tense. Preserve names, quantities, dates, negation and event participants. Output only the rewritten sentence.','max_new_tokens':100,'greedy':True,'dtype':'bfloat16','subset':'first100 source_id sorted fixed test','seed':42};ch=hashlib.sha256(json.dumps(config,sort_keys=True).encode()).hexdigest()
outputs=[]
with (ROOT/'results/direct_rewrite.jsonl').open('w') as f:
 for i in range(0,len(rs),8):
  batch=rs[i:i+8];prompts=[tok.apply_chat_template([{'role':'user','content':config['prompt']+'\n\n'+r['input']}],tokenize=False,add_generation_prompt=True) for r in batch]
  x=tok(prompts,padding=True,return_tensors='pt').to('cuda');torch.cuda.synchronize();t=time.perf_counter()
  with torch.no_grad():g=model.generate(**x,do_sample=False,num_beams=1,max_new_tokens=100,pad_token_id=tok.pad_token_id)
  torch.cuda.synchronize();elapsed=time.perf_counter()-t;g=g[:,x.input_ids.shape[1]:]
  texts=tok.batch_decode(g,skip_special_tokens=True)
  for r,out,ids in zip(batch,texts,g):
   eos=bool((ids==tok.eos_token_id).any());rr={**r,'method':'local_Qwen2.5_7B_instruction','seed':42,'config_hash':ch,'output':out,'metrics':evaluate(r['input'],out,r['reference'],eos),'timing_s':{'total':elapsed/len(batch)},'generation_error':None};f.write(json.dumps(rr)+'\n');f.flush();outputs.append(rr)
  print('direct rewrite',len(outputs),flush=True)
summary={'n':len(outputs),'config':config,'load_s':load_s,'process_s':time.monotonic()-start,'job':os.environ.get('SLURM_JOB_ID'),'mean_generation_s':sum(r['timing_s']['total'] for r in outputs)/len(outputs)}
for k in ['Joint_auto','attribute_auto','content_auto','valid_auto']:summary[k]=sum(r['metrics'][k] for r in outputs)/len(outputs)
(ROOT/'results/direct_rewrite_summary.json').write_text(json.dumps(summary,indent=2));print('DIRECT_REWRITE_COMPLETE',flush=True)
