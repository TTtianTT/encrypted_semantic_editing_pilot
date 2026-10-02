"""CPU-only independent rescoring and paired order comparison."""
from collections import defaultdict
from common import *
from semantics import gold,render
from evaluator import score as primary_score
from position_spec import make_functions
from analyze import writecsv,summary
_,_,score=make_functions(gold,render,primary_score)

def main():
    gates=[];summaries=[];statuses=[];pairs=[];count=0
    for t in read(ROOT/'position_tasks.json'):
        base=ROOT.parent/t['study'];dest=base/'position_foils'/f"{t['model']}_{t['domain']}";meta={k:v for k,v in t.items() if k!='index'};statuses.append(dict(**meta,status=read(dest/'complete.json')['status'] if (dest/'complete.json').exists() else 'running_or_not_started'))
        if (dest/'gates.json').exists():
            for gate in read(dest/'gates.json'):
                row=dict(**meta,seed=gate['seed'],variant=gate.get('variant'),status=gate['status'])
                for kind in ('reconstruction','atomic','gold_next'):
                    if kind in gate:row.update({kind+'_'+k:gate[kind][k] for k in ('n','success','rate','min_cell')})
                gates.append(row)
        ws={w['world_id']:w for w in rows(base/'position_foils/data'/t['domain']/'worlds.jsonl')}
        for path in sorted(dest.rglob('*.jsonl')):
            groups=defaultdict(list);paired=defaultdict(dict)
            for r in rows(path):
                if r.get('gold') is not None:assert score(r['prediction'],r['gold'],ws[r['world_id']],r['score']['ended'])==r['score']
                count+=1
                if 'trajectory' in r:cell=dict(seed=int(path.parent.parent.name[1:]),condition=path.parent.name,variant=r['template'],kind='trajectory',mode=r['mode'],trajectory=r['trajectory'],step=r['step'])
                else:
                    parent=path.parent;role=parent.name if parent.parent.name.startswith('s') else 'P' if parent.name.startswith('s') else 'identity';seed=int(parent.parent.name[1:]) if parent.parent.name.startswith('s') else int(parent.name[1:]) if parent.name.startswith('s') else 'shared_backbone';cell=dict(seed=seed,condition=role,variant=r['template'],kind=path.stem)
                    paired[(r['world_id'],r['state'],r['operation'])][r['template']]=r
                groups[json.dumps(cell,sort_keys=True)].append(r)
            for cell,rr in groups.items():summaries.append(dict(**meta,**json.loads(cell),**summary(rr)))
            if paired:
                for lhs,rhs in ([(0,1),(2,3)] if t['domain']=='emotion' else [(0,1)]):
                    rr=[v for v in paired.values() if lhs in v and rhs in v]
                    if not rr:continue
                    left=sum(v[lhs]['score']['success'] for v in rr);right=sum(v[rhs]['score']['success'] for v in rr);pairs.append(dict(**meta,artifact=str(path.relative_to(base)),pair_family='narrator_quote_order' if lhs==2 else 'clause_order',left_variant=lhs,right_variant=rhs,pairs=len(rr),original_order_success=left,reversed_order_success=right,both_success=sum(v[lhs]['score']['success'] and v[rhs]['score']['success'] for v in rr),original_only=sum(v[lhs]['score']['success'] and not v[rhs]['score']['success'] for v in rr),reversed_only=sum(not v[lhs]['score']['success'] and v[rhs]['score']['success'] for v in rr),delta_percentage_points=100*(right-left)/len(rr)))
    writecsv(ROOT/'position_foils_by_seed.csv',summaries);writecsv(ROOT/'position_foils_gates.csv',gates);writecsv(ROOT/'position_foils_status.csv',statuses);writecsv(ROOT/'position_order_pairs.csv',pairs);dump(ROOT/'position_foils_audit.json',dict(predictions_independently_rescored=count,statuses=len(statuses),post_formal_extension=True,no_training=True));print('Position diagnostics rescored',count,'predictions')

if __name__=='__main__':main()
