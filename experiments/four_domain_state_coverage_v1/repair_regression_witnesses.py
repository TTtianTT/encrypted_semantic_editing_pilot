"""Join fixed-source repairs and old atomic losses within the same checkpoint."""
from common import *
from analyze import keyrow,writecsv

def main():
    witnesses=[];counts=[]
    for study in ('four_domain_state_coverage_v1','space_relation_confirmation_v1'):
        base=ROOT.parent/study
        for run in sorted((base/'runs/formal').glob('*')):
            ip=run/'checkpoint_index.json'
            if not ip.exists():continue
            index=read(ip);natural=run/'outputs/P/atomic_core.jsonl'
            if not natural.exists():continue
            old_natural={keyrow(r):r for r in rows(natural)}
            for role in ('N_h0','S_h0','M_h0','N_h1','S_h1','M_h1'):
                after=run/'outputs'/role;ap=after/'atomic_core.jsonl'
                if role not in index or not ap.exists():continue
                lost=[];repairs=[]
                for r in rows(ap):
                    b=old_natural[keyrow(r)];assert r['source']==b['source'] and r['gold']==b['gold']
                    if b['score']['success'] and not r['score']['success']:lost.append(dict(before=b,after=r))
                for shard in sorted(after.glob('matrix_*.jsonl')):
                    original=run/'outputs/P'/shard.name
                    if not original.exists():continue
                    old={keyrow(r):r for r in rows(original)}
                    for r in rows(shard):
                        b=old[keyrow(r)];assert r['current_prediction']==b['current_prediction'] and r['current_score']==b['current_score'] and r['gold']==b['gold']
                        if b['current_score']['success'] and not b['score']['success'] and r['score']['success']:repairs.append(dict(shard=shard.name,before=b,after=r))
                meta=dict(study=study,run=run.name,condition=role,behavior_complete=(run/'complete.json').exists(),checkpoint=index[role],baseline_checkpoint=index['P'])
                counts.append(dict(study=study,run=run.name,condition=role,behavior_complete=meta['behavior_complete'],source_repairs=len(repairs),natural_losses=len(lost),both_observed=bool(repairs and lost)))
                if repairs and lost:
                    repaired=min(repairs,key=lambda x:(x['shard'],keyrow(x['after'])))
                    regression=min(lost,key=lambda x:keyrow(x['after']))
                    witnesses.append(dict(**meta,source_repair=repaired,natural_regression=regression,interpretation='Same frozen receiver checkpoint repairs a fixed-source controlled task and loses a previously passing natural task. Unresolved old/new outputs are not independently labelled semantic errors. First lexicographic witness, all qualifying checkpoints retained.'))
    jsonl(ROOT/'repair_regression_witnesses.jsonl',witnesses);writecsv(ROOT/'repair_regression_joint_counts.csv',counts)
    dump(ROOT/'REPAIR_REGRESSION_WITNESS_AUDIT.json',dict(checkpoints_checked=len(counts),joint_witnesses=len(witnesses),no_gpu=True,selection='first lexicographic row per qualifying checkpoint; no seed selection',errors_are_controlled_task_failures_not_unrestricted_semantic_judgements=True))
    print('Repair/loss joint witnesses:',len(witnesses),'checkpoints')

if __name__=='__main__':main()
