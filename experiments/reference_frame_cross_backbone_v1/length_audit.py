"""CPU-only check against already frozen tokenizer/length caps; never selects limits."""
from common import *
from transformers import AutoTokenizer

def main():
 rows=[r for split in ['test_iid','test_template_ood'] for kind in ['atomic','chains'] for r in read(f'data/{split}_{kind}.jsonl')]
 bodies=sorted({t for r in rows for t in [r['source_text']]+r['gold_step_texts']});results=[]
 for model in MODELS+['BART']:
  m=json.loads((ROOT/f'models/{model}.json').read_text());cfg=json.loads((ROOT/f'models/{model}_interface.json').read_text());a=json.loads((ROOT/f'calibration/{model}/admission.json').read_text());tok=AutoTokenizer.from_pretrained(m['directory'],local_files_only=True);chat=model=='t5gemma-2b-2b-ul2-it'
  def wrap(text):
   body=('Copy the following text exactly. Output only the copied text.\n\n' if a['selected_wrapper']=='B' else '')+text
   return tok.apply_chat_template([{'role':'user','content':body}],tokenize=False,add_generation_prompt=True) if chat else body
  source=[len(x) for x in tok([wrap(t) for t in bodies],add_special_tokens=not chat)['input_ids']]
  target=[len(tok(t,add_special_tokens=False)['input_ids'])+1 for t in bodies] if model.startswith('t5gemma') else [len(x) for x in tok(bodies)['input_ids']]
  assert max(source)<=cfg['source_length'] and max(target)<cfg['max_new_tokens']
  results.append(dict(model=model,N_unique_bodies=len(bodies),max_source_tokens=max(source),max_target_tokens=max(target),frozen_source_cap=cfg['source_length'],frozen_generation_cap=cfg['max_new_tokens'],interface_hash=digest(ROOT/f'models/{model}_interface.json'),passed=True,limits_not_changed=True))
 dump('evaluation/confirmation_length_audit.json',dict(passed=True,models=results));print(results)
if __name__=='__main__':main()
