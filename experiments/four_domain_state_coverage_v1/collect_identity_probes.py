"""CPU aggregation of completed identity probes and frozen continuation failures."""
from collections import Counter, defaultdict
from common import *
from analyze import writecsv
from identity_probe import labels

def frequency_baselines(train_labels, predictions, classes):
    """CPU-only baselines; all prediction rules use train frequencies only."""
    counts=Counter(train_labels)
    assert counts and all(0<=v<classes for v in counts)
    majority=min(counts, key=lambda v: (-counts[v],v))
    n=len(predictions)
    assert n and all(0<=r['label']<classes for r in predictions)
    majority_rate=sum(r['label']==majority for r in predictions)/n
    frequency_rate=sum(counts[r['label']]/len(train_labels) for r in predictions)/n
    probe_rate=sum(r['correct'] for r in predictions)/n
    return dict(n=n,worlds=len({r['world_id'] for r in predictions}),classes=classes,
        train_n=len(train_labels),train_class_count=len(counts),train_majority_label=majority,
        uniform_class_accuracy=1/classes,train_majority_accuracy=majority_rate,
        train_frequency_random_accuracy=frequency_rate,probe_accuracy=probe_rate,
        probe_minus_train_majority=probe_rate-majority_rate,
        unseen_test_class_n=sum(r['label'] not in counts for r in predictions),
        unseen_test_class_rate=sum(r['label'] not in counts for r in predictions)/n)

def main():
    metrics=[];failures=[];statuses=[];baselines=[];frequencies=[]
    for task in read(ROOT/'identity_probe_tasks.json'):
        base=ROOT.parent/task['study'];run=base/'runs/formal'/f"{task['model']}_{task['domain']}_s{task['seed']}";out=run/'identity_probe';meta={k:v for k,v in task.items() if k!='index'}
        if not (out/'complete.json').exists():statuses.append(dict(**meta,status='running_or_not_started'));continue
        complete=read(out/'complete.json');statuses.append(dict(**meta,status=complete['status']))
        if complete['status']!='completed':continue
        raw_metrics=read(out/'metrics.json');metrics.extend(dict(**meta,**r) for r in raw_metrics);pr=rows(out/'predictions.jsonl');lookup={(r['world_id'],r['state'],r['test_source'],r['variable']):r for r in pr};variables=sorted({r['variable'] for r in pr})
        assert len(lookup)==len(pr),'Repeated probe prediction keys'
        worlds={w['world_id']:w for w in rows(base/f"data/{task['domain']}/worlds.jsonl")}
        trainpath=base/'local/formal'/run.name/'probe/P_train.jsonl';train=rows(trainpath);manifest=read(trainpath.with_suffix('.json'))
        expected={(w,s) for w in manifest['world_ids'] for s in manifest['states']}
        assert len(train)==manifest['candidates']==len(expected)
        assert {(r['world_id'],r['state']) for r in train}==expected
        train_targets={variable:[labels(r,worlds[r['world_id']])[variable] for r in train] for variable in variables}
        for metric in raw_metrics:
            variable=metric['variable'];source=metric['test_source'];target=train_targets[variable];classes=metric['classes']
            assert sorted(set(target))==metric['train_classes']
            selected=[r for r in pr if r['variable']==variable and r['test_source']==source]
            assert len(selected)==metric['n']
            assert all(r['label']==labels(r,worlds[r['world_id']])[variable] for r in selected)
            for subset,rr in [('all',selected),('current_correct',[r for r in selected if r['current_correct']])]:
                if rr:baselines.append(dict(**meta,variable=variable,test_source=source,subset=subset,**frequency_baselines(target,rr,classes)))
            for sample,rr in [('train_P',[dict(label=v,world_id=r['world_id']) for r,v in zip(train,target)]),('test_'+source,selected)]:
                count=Counter(r['label'] for r in rr)
                for label in range(classes):
                    frequencies.append(dict(**meta,variable=variable,sample=sample,label=label,n=count[label],sample_n=len(rr),frequency=count[label]/len(rr),worlds=len({r['world_id'] for r in rr if r['label']==label})))
        for p in sorted((run/'outputs').glob('*/matrix_h*_t0.jsonl')):
            rr=rows(p)
            for variable in variables:
                selected=[lookup[(r['world_id'],r['state'],r['source'],variable)] for r in rr if r['current_score']['success'] and not r['score']['success']]
                if selected:
                    unique={(r['world_id'],r['state'],r['test_source']):r for r in selected}
                    classes=next(m['classes'] for m in raw_metrics if m['variable']==variable)
                    failures.append(dict(**meta,condition=p.parent.name,shard=p.stem,variable=variable,n=len(selected),worlds=len({r['world_id'] for r in selected}),probe_correct_k=sum(r['correct'] for r in selected),probe_accuracy=sum(r['correct'] for r in selected)/len(selected),unique_representation_n=len(unique),**{'unique_'+k:v for k,v in frequency_baselines(train_targets[variable],list(unique.values()),classes).items()}))
    writecsv(ROOT/'identity_probe_metrics.csv',metrics);writecsv(ROOT/'identity_probe_on_failures.csv',failures);writecsv(ROOT/'identity_probe_status.csv',statuses);writecsv(ROOT/'identity_probe_frequency_baselines.csv',baselines)
    # The train distribution is shared across test sources; write it only once.
    seen=set();frequency_rows=[]
    for r in frequencies:
        key=tuple(r[k] for k in ('study','model','domain','seed','variable','sample','label'))
        if key not in seen:seen.add(key);frequency_rows.append(r)
    writecsv(ROOT/'identity_probe_class_frequency.csv',frequency_rows)
    print('Identity probes:',len(metrics),'metric rows;',len(statuses),'statuses;',len(baselines),'baseline rows')

if __name__=='__main__':main()
