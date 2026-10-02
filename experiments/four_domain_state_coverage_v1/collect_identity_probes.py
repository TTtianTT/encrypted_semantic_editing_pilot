"""CPU aggregation of completed identity probes and frozen continuation failures."""
from collections import defaultdict
from common import *
from analyze import writecsv

def main():
    metrics=[];failures=[];statuses=[]
    for task in read(ROOT/'identity_probe_tasks.json'):
        base=ROOT.parent/task['study'];run=base/'runs/formal'/f"{task['model']}_{task['domain']}_s{task['seed']}";out=run/'identity_probe';meta={k:v for k,v in task.items() if k!='index'}
        if not (out/'complete.json').exists():statuses.append(dict(**meta,status='running_or_not_started'));continue
        complete=read(out/'complete.json');statuses.append(dict(**meta,status=complete['status']))
        if complete['status']!='completed':continue
        metrics.extend(dict(**meta,**r) for r in read(out/'metrics.json'));pr=rows(out/'predictions.jsonl');lookup={(r['world_id'],r['state'],r['test_source'],r['variable']):r for r in pr};variables=sorted({r['variable'] for r in pr})
        for p in sorted((run/'outputs').glob('*/matrix_h*_t0.jsonl')):
            rr=rows(p)
            for variable in variables:
                selected=[lookup[(r['world_id'],r['state'],r['source'],variable)] for r in rr if r['current_score']['success'] and not r['score']['success']]
                if selected:failures.append(dict(**meta,condition=p.parent.name,shard=p.stem,variable=variable,n=len(selected),worlds=len({r['world_id'] for r in selected}),probe_correct_k=sum(r['correct'] for r in selected),probe_accuracy=sum(r['correct'] for r in selected)/len(selected)))
    writecsv(ROOT/'identity_probe_metrics.csv',metrics);writecsv(ROOT/'identity_probe_on_failures.csv',failures);writecsv(ROOT/'identity_probe_status.csv',statuses);print('Identity probes:',len(metrics),'metric rows;',len(statuses),'statuses')

if __name__=='__main__':main()
