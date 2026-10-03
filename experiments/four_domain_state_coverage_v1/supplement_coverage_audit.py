"""Actual current/next-label supervision by signed head and source family."""
from collections import Counter
import importlib.util
from common import *
from analyze import writecsv

def main():
    cells=Counter();files=[]
    for study in ('four_domain_state_coverage_v1','space_relation_confirmation_v1'):
        base=ROOT.parent/study;spec=importlib.util.spec_from_file_location('coverage_'+study,base/'semantics.py');sem=importlib.util.module_from_spec(spec);spec.loader.exec_module(sem)
        for run in sorted((base/'runs/formal').glob('*')):
            model,d,s=run.name.split('_');seed=int(s[1:]);ws={w['world_id']:w for w in rows(base/f'data/{d}/worlds.jsonl')}
            for p in sorted((run/'training').glob('[NSM]_h*/training.jsonl')):
                role=p.parent.name;condition=role[0];h=int(role[-1]);rr=rows(p);assert len(rr)==200
                budget=Counter()
                for r in rr:
                    assert len(r['states'])==len(r['world_ids'])==len(r['roles'])==r['supervised_semantic_units']==8
                    for state,wid,stream in zip(r['states'],r['world_ids'],r['roles']):
                        nxt=sem.advance(d,state,r['operation']);budget[stream]+=1;family='natural' if condition=='N' or stream=='natural' else 'P_edited' if stream=='focus' else 'Q_edited';w=ws[wid]
                        current=sem.gold(w,state)['relation'] if d=='space' else str(state);target=sem.gold(w,nxt)['relation'] if d=='space' else str(nxt)
                        cells[(study,model,d,seed,condition,h,stream,family,r['operation'],state,nxt,current,target)]+=1
                assert budget==dict(natural=800,focus=400,old=400),budget
                files.append(dict(study=study,run=run.name,condition=condition,holdout_split=h,sha256=digest(p),path=str(p.relative_to(base)),semantic_units=1600,by_stream=dict(budget)))
    names=['study','model','domain','seed','condition','holdout_split','stream','exposure_family','operation','current_label','next_label','current_observable_state','next_observable_state']
    writecsv(ROOT/'supplement_supervision_coverage.csv',[dict(zip(names,k),semantic_units=n) for k,n in sorted(cells.items())]);dump(ROOT/'SUPPLEMENT_SUPERVISION_COVERAGE_AUDIT.json',dict(files=files,checkpoint_runs=len(files),every_run_1600_units=True,actual_draws_not_intended_counts=True,old_space_labels_absolute_heading=True,current_and_next_observable_relations_separately_recorded=True))
    print('Supplement input/output coverage:',len(files),'checkpoints;',len(cells),'signed-source-state cells')

if __name__=='__main__':main()
