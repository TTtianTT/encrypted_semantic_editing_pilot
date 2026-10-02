"""Cross-backbone comparisons on common content/world/current-text cohorts."""
from collections import defaultdict
from common import *
from analyze import writecsv,keyrow
from evaluator import normalize

def main():
    out=[]
    for d in DOMAINS:
        base=ROOT.parent/'space_relation_confirmation_v1' if d=='space' else ROOT
        for seed in (42,43,44):
            for h in range(2):
                for t in (0,2):
                    name=f'matrix_h{h}_t{t}.jsonl'
                    for condition in ('P',f'N_h{h}',f'S_h{h}',f'M_h{h}'):
                        paths={m:base/'runs/formal'/f'{m}_{d}_s{seed}'/'outputs'/condition/name for m in MODELS}
                        if not all(p.exists() for p in paths.values()):continue
                        rr={m:rows(p) for m,p in paths.items()};lookups={m:{keyrow(r):r for r in values} for m,values in rr.items()};common=set.intersection(*(set(v) for v in lookups.values()))
                        for cohort in ('all_candidates','normalized_fulltext_common_match','literal_fulltext_common_match'):
                            keys=[]
                            for key in common:
                                a,b=(lookups[m][key] for m in MODELS)
                                if cohort!='all_candidates':
                                    if not(a['common_match'] and b['common_match']):continue
                                    if cohort=='literal_fulltext_common_match' and a['current_prediction']!=b['current_prediction']:continue
                                    if cohort=='normalized_fulltext_common_match' and normalize(a['current_prediction'])!=normalize(b['current_prediction']):continue
                                keys.append(key)
                            for source in ('P','Q','U'):
                                for heldout in (False,True):
                                    kk=[k for k in keys if lookups['bart'][k]['source']==source and lookups['bart'][k]['state_heldout']==heldout]
                                    if not kk:continue
                                    left=[lookups['bart'][k] for k in kk];right=[lookups['t5gemma'][k] for k in kk]
                                    out.append(dict(domain=d,seed=seed,holdout_split=h,template=t,condition=condition,source=source,state_heldout=heldout,cohort=cohort,n=len(kk),worlds=len({r['world_id'] for r in left}),bart_k=sum(r['score']['success'] for r in left),t5gemma_k=sum(r['score']['success'] for r in right),bart_own_normalized_matched_n=sum(r['common_match'] and r['source']==source and r['state_heldout']==heldout for r in rr['bart']),t5gemma_own_normalized_matched_n=sum(r['common_match'] and r['source']==source and r['state_heldout']==heldout for r in rr['t5gemma']),bart_mask_length_min=min(r['mask_length'] for r in left),bart_mask_length_max=max(r['mask_length'] for r in left),t5gemma_mask_length_min=min(r['mask_length'] for r in right),t5gemma_mask_length_max=max(r['mask_length'] for r in right),mask_between_backbones_matched=False,depth_between_backbones=1))
    writecsv(ROOT/'cross_backbone_fixed_worlds.csv',out)
    dump(ROOT/'cross_backbone_limitations.json',dict(cohort_selection='current correctness, world/state/operation and full current text only; never next output',mask_matching='exact tensor match within each backbone P/Q/U source cohort; different tokenizers/caps/dimensions prevent cross-backbone mask matching',parameter_budget='rank16 gives different parameter counts; architectures/dtypes/interfaces differ',original_spatial_heading_study_excluded=True,rows=len(out)))
    print('Cross-backbone common-world comparison rows',len(out))

if __name__=='__main__':main()
