"""Exclusive error categories plus overlapping facts; no causal inference from text."""
from shared import *
sys.path.insert(0,str(previous.SOURCE))
from evaluator import parse

def classify(output,previous_state,target,history,operation,template):
    score=output['score'];parsed,grammar=parse(output['text'],'time',template)
    actual=parsed.get('relative') if parsed else None
    if score['success']:category='success';subtype=None
    elif parsed is None or not grammar or not output['ended']:category='unparseable_or_invalid_grammar';subtype=None
    elif not score['preserved']:category='non_target_corruption';subtype=None
    elif actual==previous_state:category='edit_not_executed';subtype=None
    else:
        category='wrong_state';step=-1 if operation=='plus' else 1
        subtype='overshoot_one' if actual==target+step else 'historical_state' if actual in history else 'other_state'
    return dict(category=category,wrong_state_subtype=subtype,actual_state=actual,expected_state=target,previous_state=previous_state,
        target_correct=score['target'],non_target_preserved=score['preserved'],parseable=score['parseable'],grammar=score['grammar'],ended=output['ended'])

def main():
    verify();out=[];seqs=read(V2/'protocol.json')['sequences']
    for r in stream(V2/'results/projection.jsonl'):
        state=0;history=[0]
        for step in r['steps']:
            op=seqs[r['sequence']][step['step']-1];target=step['state']
            out.append(dict(panel='historical_v2',seed=r['seed'],model=r['method'],random_seed=r['random_seed'],world_id=r['world_id'],template=r['template'],sequence=r['sequence'],step=step['step'],
                **classify(step['output'],state,target,history,op,r['template'])))
            state=target;history.append(target)
    for r in stream(ROOT/'results/evaluation.jsonl'):
        if r['panel']!='chain':continue
        state=0;history=[0]
        for step in r['steps']:
            target=step['state'];out.append(dict(panel='reachability',seed=r['seed'],model=r['model'],random_seed=None,world_id=r['world_id'],template=r['template'],sequence=r['sequence'],step=step['step'],
                **classify(step['output'],state,target,history,step['operation'],r['template'])))
            state=target;history.append(target)
    write('results/failure_categories.jsonl',out)
    dump('results/failures_complete.json',dict(records=len(out),training_updates=0,text_only_attribution=True,priority=read(ROOT/'protocol.json')['failure_priority']))
    print('Classified',len(out),'saved outputs')

if __name__=='__main__':main()
