"""Descriptive paired decomposition and deterministic error cases, CPU only.

The common-correct-prefix stratum is method dependent, not a replacement for
the pre-training fixed diagnostic cohort or the primary all-sample full2 metric.
"""
import csv,collections
from study import *

def main():
    tables=[];cases=[]
    for seed in (42,43,44):
        baseline=ROOT/f'runs/preflight/s{seed}/T0'
        if not (baseline/'complete.json').exists():continue
        old={r['id']:r for r in rows(baseline/'old_natural.jsonl')}
        old_ood={r['id']:r for r in rows(baseline/'ood_natural.jsonl')}
        for method in ('N','F','R'):
            folder=ROOT/f'runs/formal/s{seed}/{method}_u200'
            if not (folder/'complete.json').exists():continue
            rs=rows(folder/'old_natural.jsonl')
            lost=[r for r in sorted(rs,key=lambda r:r['id']) if old[r['id']]['score']['success'] and not r['score']['success']]
            for r in lost[:2]:cases.append(dict(category='old_natural_success_lost',seed=seed,condition=method,id=r['id'],baseline=old[r['id']],updated=r))
            lost_ood=[r for r in sorted(rows(folder/'ood_natural.jsonl'),key=lambda r:r['id']) if old_ood[r['id']]['score']['success'] and not r['score']['success']]
            for r in lost_ood[:2]:cases.append(dict(category='ood_natural_success_lost',seed=seed,condition=method,id=r['id'],baseline=old_ood[r['id']],updated=r))
            selected=collections.defaultdict(list)
            for r in sorted(rows(folder/'continuation_self.jsonl'),key=lambda r:r['id']):
                category='correct_prefix_failed_next' if r['first_success'] and not r['score']['success'] else 'bad_prefix_endpoint_recovery' if not r['first_success'] and r['score']['success'] else None
                if category and len(selected[category])<2:selected[category].append(r)
            for cat,ss in selected.items():
                for r in ss:cases.append(dict(category=cat,seed=seed,condition=method,id=r['id'],updated=r))
            paths=collections.defaultdict(list)
            for p in sorted((folder/'trajectories').glob('latent_*.jsonl')):
                for r in rows(p):paths[r['id']].append(r)
            longfailed=[rs for _,rs in sorted(paths.items()) if any(r['step']>2 and not r['full_success'] for r in rs) and all(r['full_success'] for r in rs if r['step']<=2)]
            for rs in longfailed[:2]:cases.append(dict(category='two_steps_correct_later_failed',seed=seed,condition=method,id=rs[0]['id'],trajectory=sorted(rs,key=lambda r:r['step'])))
        for right,left in (('R','F'),('F','N')):
            pf=ROOT/f'runs/formal/s{seed}/{right}_u200';qf=ROOT/f'runs/formal/s{seed}/{left}_u200'
            if not all((f/'complete.json').exists() for f in (pf,qf)):continue
            for source in ('fixed_T0','U','self'):
                rr={r['id']:r for r in rows(pf/f'continuation_{source}.jsonl')};ll={r['id']:r for r in rows(qf/f'continuation_{source}.jsonl')}
                assert rr.keys()==ll.keys()
                for t,test in ((0,'iid'),(2,'ood')):
                    groups=collections.defaultdict(list)
                    for identifier,r in rr.items():
                        if r['template']!=t:continue
                        l=ll[identifier]
                        if source in ('fixed_T0','U'):
                            assert r['first_prediction']==l['first_prediction'] and r['first_score']==l['first_score']
                        label='both_correct' if r['first_success'] and l['first_success'] else 'right_only_correct' if r['first_success'] else 'left_only_correct' if l['first_success'] else 'both_failed'
                        groups[label].append((r,l))
                    full_delta=endpoint_delta=recovery_delta=0
                    for stratum in ('both_correct','right_only_correct','left_only_correct','both_failed'):
                        ss=groups[stratum];fd=sum(int(r['full2'])-int(l['full2']) for r,l in ss)
                        ed=sum(int(r['score']['success'])-int(l['score']['success']) for r,l in ss)
                        rd=sum(int(not r['first_success'] and r['score']['success'])-int(not l['first_success'] and l['score']['success']) for r,l in ss)
                        gained=sum(r['full2'] and not l['full2'] for r,l in ss)
                        lost=sum(l['full2'] and not r['full2'] for r,l in ss)
                        assert fd==gained-lost
                        assert ed==fd+rd
                        full_delta+=fd;endpoint_delta+=ed;recovery_delta+=rd
                        tables.append(dict(seed=seed,contrast=right+'-'+left,test=test,source=source,stratum=stratum,n=len(ss),right_full2=sum(r['full2'] for r,l in ss),left_full2=sum(l['full2'] for r,l in ss),right_full2_gain_count=gained,right_full2_loss_count=lost,full2_count_delta=fd,endpoint2_count_delta=ed,failed_prefix_endpoint_recovery_count_delta=rd))
                        if stratum=='both_correct':
                            gains=sorted(((r,l) for r,l in ss if r['full2'] and not l['full2']),key=lambda pair:pair[0]['id'])
                            losses=sorted(((r,l) for r,l in ss if l['full2'] and not r['full2']),key=lambda pair:pair[0]['id'])
                            for cat,selected in (('paired_correct_prefix_gain',gains[:1]),('paired_correct_prefix_loss',losses[:1])):
                                for r,l in selected:cases.append(dict(category=cat,seed=seed,contrast=right+'-'+left,source=source,test=test,id=r['id'],right=r,left=l))
                    assert endpoint_delta==full_delta+recovery_delta
    if tables:
        with (ROOT/'repair_attribution.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=list(tables[0]));w.writeheader();w.writerows(tables)
    jsonl(ROOT/'ERROR_CASES.jsonl',cases)
    dump(ROOT/'CASE_SELECTION.json',dict(rule='lexicographic IDs; up to2/run/category, up to1/source/contrast paired gain/loss; no outcome-dependent checkpoint selection',cases=len(cases),categories=dict(collections.Counter(r['category'] for r in cases)),at_utc=now()))
    print('Descriptive attribution:',len(tables),'rows;',len(cases),'cases for reading')
if __name__=='__main__':main()
