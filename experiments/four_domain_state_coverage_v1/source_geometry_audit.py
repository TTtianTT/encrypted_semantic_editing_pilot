"""CPU-only tokenizer/mask metadata audit; no model forward or fitted probe."""
import torch
from transformers import AutoTokenizer
from collections import defaultdict
from common import *
from analyze import writecsv

def main():
    output=[];groups=defaultdict(list)
    for study in ('four_domain_state_coverage_v1','space_relation_confirmation_v1'):
        base=ROOT.parent/study;cfg=read(base/'config.json');models=read(base/'model_manifest.json')
        for model in MODELS:
            tok=AutoTokenizer.from_pretrained(models[model]['directory'],local_files_only=True)
            for run in sorted((base/'local/formal').glob(model+'_*')):
                for path in sorted((run/'sources').glob('*.pt')):
                    manifest=path.with_suffix('.json')
                    if not manifest.exists():continue
                    m=read(manifest);assert digest(path)==m['cache_sha']
                    cache=torch.load(path,map_location='cpu',weights_only=False)
                    for r in cache:
                        text=r['current_gold'];source_text=r['source_text']
                        def length(t):
                            wrapped=tok.apply_chat_template([dict(role='user',content=cfg['copy_instruction']+t)],tokenize=False,add_generation_prompt=True) if model=='t5gemma' else t
                            return len(tok(wrapped,add_special_tokens=model!='t5gemma')['input_ids'])
                        original_length=length(source_text);current_length=length(text);mask_length=int(r['mask'].sum());assert mask_length==original_length
                        row=dict(study=study,run=run.name,cache=path.name,state=r['state'],world_id=r['world_id'],template=r['template'],source_operation=r['source_operation'],source_depth=r['source_depth'],source_mask_length=mask_length,natural_current_length=current_length,current_length_matches_source_mask=mask_length==current_length,current_correct=r['current_score']['success']);output.append(row)
                        groups[(study,run.name,path.name,r['state'])].append(row)
    writecsv(ROOT/'source_mask_length_by_world.csv',output)
    summary=[dict(study=st,run=run,cache=cache,state=state,n=len(rr),correct=sum(r['current_correct'] for r in rr),source_mask_length_min=min(r['source_mask_length'] for r in rr),source_mask_length_max=max(r['source_mask_length'] for r in rr),source_mask_length_mean=sum(r['source_mask_length'] for r in rr)/len(rr),natural_current_length_min=min(r['natural_current_length'] for r in rr),natural_current_length_max=max(r['natural_current_length'] for r in rr),mask_vs_natural_length_equal_n=sum(r['current_length_matches_source_mask'] for r in rr)) for (st,run,cache,state),rr in sorted(groups.items())]
    writecsv(ROOT/'source_mask_length_summary.csv',summary)
    dump(ROOT/'source_geometry_limitations.json',dict(no_cuda_initialized=not torch.cuda.is_initialized(),source_pair_matching='P/Q/U exact source masks/depth within a given world/current state checked by matrix; byte-current-text subset also reported',natural_control='natural encoding has depth0 and may differ in valid token length; it is not a perfectly depth/mask-matched edited-source comparison',state_coverage='Changing focus states may also change incoming-operation/text/token-length distribution. Equal updates/endpoint units do not isolate a causal semantic-state mechanism.',historical_coverage='One deterministic incoming direction per state per frozen source editor. Other incoming directions are exercised in rollouts, not a second fully matched source matrix.'))
    print('Source/mask metadata rows',len(output))

if __name__=='__main__':main()
