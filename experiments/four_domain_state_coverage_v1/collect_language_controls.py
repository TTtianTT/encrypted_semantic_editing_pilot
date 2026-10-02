"""Independent CPU rescoring and aggregation of secondary structural controls."""
from collections import defaultdict
from common import *
from evaluator import score
from analyze import writecsv,summary

def main():
    gates=[];summaries=[];statuses=[];count=0
    for task in read(ROOT/'linguistic_tasks.json'):
        base=ROOT.parent/task['study'];out=base/'language_controls'/f"{task['model']}_{task['domain']}";meta={k:v for k,v in task.items() if k!='index'};status=read(out/'complete.json')['status'] if (out/'complete.json').exists() else 'running_or_not_started';statuses.append(dict(**meta,status=status))
        if (out/'gates.json').exists():
            for r in read(out/'gates.json'):
                row=dict(**meta,seed=r['seed'],template=r.get('template'),status=r['status'])
                for kind in ('reconstruction','atomic','gold_next'):
                    if kind in r:row.update({kind+'_'+k:r[kind][k] for k in ('n','success','rate','min_cell')})
                gates.append(row)
        ws={w['world_id']:w for w in rows(base/f"data/{task['domain']}/worlds.jsonl")}
        for path in sorted(out.rglob('*.jsonl')):
            groups=defaultdict(list)
            for r in rows(path):
                if r.get('gold') is not None:assert score(r['prediction'],r['gold'],ws[r['world_id']],r['score']['ended'])==r['score']
                count+=1
                if 'trajectory' in r:cell=dict(seed=int(path.parent.parent.name[1:]),condition=path.parent.name,template=r['template'],kind='trajectory',mode=r['mode'],trajectory=r['trajectory'],step=r['step'])
                else:cell=dict(seed=int(path.parent.name[1:]) if path.parent.name.startswith('s') else 'shared_backbone',condition='P' if path.name.startswith('dev_') and path.parent.name.startswith('s') else 'identity',template=r['template'],kind=path.stem)
                groups[json.dumps(cell,sort_keys=True)].append(r)
            for cell,rr in groups.items():summaries.append(dict(**meta,**json.loads(cell),**summary(rr)))
    writecsv(ROOT/'language_structure_gates.csv',gates);writecsv(ROOT/'language_structure_by_seed.csv',summaries);writecsv(ROOT/'language_structure_status.csv',statuses);dump(ROOT/'language_structure_audit.json',dict(predictions_independently_rescored=count,task_statuses=len(statuses),secondary_extension=True,no_training=True));print('Structure controls rescored',count,'predictions')

if __name__=='__main__':main()
