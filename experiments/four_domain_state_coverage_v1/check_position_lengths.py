"""CPU-only tokenizer length audit for the locked diagnostic fixtures."""
from transformers import AutoTokenizer
from common import *

def main():
    manifest=read(ROOT/'model_manifest.json');config=read(ROOT/'config.json');checks=[]
    for name in MODELS:
        tok=AutoTokenizer.from_pretrained(manifest[name]['directory'],local_files_only=True)
        for task in read(ROOT/'position_tasks.json'):
            if task['model']!=name:continue
            base=ROOT.parent/task['study'];data=base/'position_foils/data'/task['domain'];rs=rows(data/'dev.jsonl')+rows(data/'test.jsonl');lengths=[]
            for r in rs:
                text=r['source']
                if name=='t5gemma':
                    body=config['copy_instruction']+text
                    text=tok.apply_chat_template([dict(role='user',content=body)],tokenize=False,add_generation_prompt=True)
                source_n=len(tok(text,add_special_tokens=name!='t5gemma')['input_ids'])
                # Conservative extra token for output termination/start handling.
                target_n=len(tok(r['target'],add_special_tokens=name!='t5gemma')['input_ids'])+1
                assert source_n<=config['source_cap'][name],(task,r['world_id'],source_n)
                assert target_n<=config['max_new_tokens'],(task,r['world_id'],target_n)
                lengths.append((source_n,target_n))
            checks.append(dict(**task,examples=len(rs),maximum_source_tokens=max(x[0] for x in lengths),maximum_target_tokens_with_margin=max(x[1] for x in lengths),source_cap=config['source_cap'][name],max_new_tokens=config['max_new_tokens']))
    dump(ROOT/'POSITION_TOKEN_LENGTH_AUDIT.json',dict(no_gpu=True,position_lock_sha=digest(ROOT/'position_lock.json'),checks=checks))
    print(json.dumps(checks))

if __name__=='__main__':main()
