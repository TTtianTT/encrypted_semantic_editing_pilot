"""Separate edited-state, producer-source and expression transfer on fixed inputs."""
from collections import defaultdict
from common import *
from analyze import writecsv

def main():
    output=[]
    for study in ('four_domain_state_coverage_v1','space_relation_confirmation_v1'):
        base=ROOT.parent/study
        for run in sorted((base/'runs/formal').glob('*')):
            m,d,s=run.name.split('_');meta=dict(study=study,model=m,domain=d,seed=int(s[1:]))
            for path in sorted((run/'outputs').glob('*/matrix*.jsonl')):
                condition=path.parent.name
                if not condition.startswith(('S_','M_')):continue
                cells=defaultdict(list)
                for r in rows(path):
                    if not(r['state_seen'] or r['state_heldout']):continue
                    state='seen_edited_state' if r['state_seen'] else 'heldout_edited_state';source='seen_source' if r['source_seen'] else 'heldout_source'
                    for cohort in ('all_candidates','current_correct','fixed_normalized_fulltext_mask_depth'):
                        if cohort=='current_correct' and not r['current_score']['success']:continue
                        if cohort=='fixed_normalized_fulltext_mask_depth' and not r['common_match']:continue
                        cells[(r['template'],state,source,cohort)].append(r)
                for (template,state,source,cohort),rr in sorted(cells.items()):
                    sub=defaultdict(list)
                    for r in rr:sub[(r['state'],r['operation'],r['source'])].append(r['score']['success'])
                    output.append(dict(**meta,condition=condition,holdout_split=int(condition[-1]),template=template,state_bin=state,source_bin=source,cohort=cohort,n=len(rr),worlds=len({r['world_id'] for r in rr}),success_k=sum(r['score']['success'] for r in rr),success_rate=sum(r['score']['success'] for r in rr)/len(rr),macro_state_sign_source_rate=sum(sum(x)/len(x) for x in sub.values())/len(sub),cells=len(sub)))
    writecsv(ROOT/'transfer_quad.csv',output);print('Transfer quad rows',len(output))

if __name__=='__main__':main()
