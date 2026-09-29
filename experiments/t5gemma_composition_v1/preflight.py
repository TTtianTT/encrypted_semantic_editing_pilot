"""Check identity decode of the frozen local T5Gemma on training worlds only."""
import json,sys
from pathlib import Path
import torch
from transformers import AutoTokenizer,AutoModelForSeq2SeqLM
from transformers.modeling_outputs import BaseModelOutput

HERE=Path(__file__).resolve().parent
V3=HERE.parent/'reference_frame_pilot_v3'
sys.path.insert(0,str(V3))
from common import frame,render,score

MODEL=Path('/dataset1/zailong/models/reference-frame-cross-backbone/t5gemma-2b-2b-ul2-it')
PREFIX='Return exactly one copy of the text below, with no introduction, ending, or extra text.\n\n'
def main():
 assert torch.cuda.is_available()
 tok=AutoTokenizer.from_pretrained(MODEL,local_files_only=True)
 model=AutoModelForSeq2SeqLM.from_pretrained(MODEL,local_files_only=True,dtype=torch.bfloat16,attn_implementation='sdpa').cuda().eval()
 for p in model.parameters():p.requires_grad_(False)
 worlds=[json.loads(s) for s in (V3/'data/train_worlds.jsonl').read_text().splitlines()][:16]
 fs=[frame(w,1 if w['record_status']=='recorded_plan' else -1) for w in worlds]
 texts=[render(w,f) for w,f in zip(worlds,fs)]
 prompts=[tok.apply_chat_template([{'role':'user','content':PREFIX+t}],tokenize=False,add_generation_prompt=True) for t in texts]
 x=tok(prompts,padding=True,truncation=False,return_tensors='pt').to('cuda')
 with torch.no_grad():
  h=model.get_encoder()(**x).last_hidden_state
  out=model.generate(encoder_outputs=BaseModelOutput(last_hidden_state=h),attention_mask=x.attention_mask,max_new_tokens=80,do_sample=False,num_beams=1)
 decoded=tok.batch_decode(out,skip_special_tokens=True,clean_up_tokenization_spaces=False)
 scores=[score(t,f,w,True) for t,f,w in zip(decoded,fs,worlds)]
 result=dict(model=str(MODEL),prefix=PREFIX,chat_template=True,parameter_count=sum(p.numel() for p in model.parameters()),hidden_size=h.shape[-1],input_max_tokens=int(x.attention_mask.sum(1).max()),identity_joint=sum(s['joint_ok'] for s in scores),identity_exact=sum(t==d for t,d in zip(texts,decoded)),n=len(scores),examples=[dict(source=t,output=d,success=bool(s['joint_ok'])) for t,d,s in zip(texts,decoded,scores)])
 (HERE/'preflight.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items() if k!='examples'},indent=2),flush=True)
 for e in result['examples'][:4]:print(e,flush=True)
if __name__=='__main__':main()
