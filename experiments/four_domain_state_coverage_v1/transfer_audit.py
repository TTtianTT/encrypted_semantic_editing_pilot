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
                    single=2 if d=='emotion' else 0
                    joint=lambda r: (r['source']=='P' and r['state_seen']) or (r['source']=='Q' and r['state']==single)
                    output.append(dict(**meta,condition=condition,holdout_split=int(condition[-1]),template=template,state_bin=state,source_bin=source,cohort=cohort,n=len(rr),worlds=len({r['world_id'] for r in rr}),success_k=sum(r['score']['success'] for r in rr),success_rate=sum(r['score']['success'] for r in rr)/len(rr),macro_state_sign_source_rate=sum(sum(x)/len(x) for x in sub.values())/len(sub),cells=len(sub),joint_source_state_seen_n=sum(joint(r) for r in rr),joint_source_state_unseen_n=sum(not joint(r) for r in rr)))
    writecsv(ROOT/'transfer_quad.csv',output);dump(ROOT/'TRANSFER_DEFINITIONS.json',dict(source_seen='P/Q producer families were used in S/M edited focus/old-protection pools. U was not.',state_seen='Current state was in this condition\u2019s P focus pool; heldout means excluded from edited focus but included in natural atomic training.',joint_seen='P AND focus state, or Q AND old-protection state(single0, emotion2). Seen source/state factors alone do not mean their joint was trained.',N='Natural-encoding control has no edited-source family exposure; the static historical source labels in original predictions are not N training-exposure claims.',natural_conversion_coverage='Every legal natural atomic state/sign conversion is trained. This study contains no completely-untrained natural conversion condition. Heldout worlds/expressions are separate axes.'))
    print('Transfer quad rows',len(output))

if __name__=='__main__':main()
