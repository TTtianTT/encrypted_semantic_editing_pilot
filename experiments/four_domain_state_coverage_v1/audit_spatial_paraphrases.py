"""Uniform post hoc CPU rescoring; never overwrites raw formal predictions."""
from collections import defaultdict
import importlib.util
from common import *
from evaluator import score,normalize
from analyze import writecsv,keyrow
from spatial_paraphrase_score import score_spatial_paraphrases,normalize_spatial_paraphrases

def main():
    groups=defaultdict(lambda:dict(n=0,raw_k=0,adjudicated_k=0,rescued_k=0,rejected_k=0,raw_parseable_k=0,adjudicated_parseable_k=0,aliases_k=0));changes=[];examples=[];contrasts=[];coverage=[];total=0
    for study in ('four_domain_state_coverage_v1','space_relation_confirmation_v1'):
        base=ROOT.parent/study;ws={w['world_id']:w for w in rows(base/'data/space/worlds.jsonl')}
        spec=importlib.util.spec_from_file_location('audit_'+study,base/'semantics.py');sem=importlib.util.module_from_spec(spec);spec.loader.exec_module(sem)
        assert digest(base/'evaluator.py')==digest(ROOT/'evaluator.py')
        for run in sorted((base/'runs/formal').glob('*_space_*')):
            model,_,s=run.name.split('_');meta=dict(study=study,model=model,domain='space',seed=int(s[1:]));matrices={}
            paths=list((run/'outputs').glob('*/*.jsonl'))+list(run.glob('test_*.jsonl'))
            for path in sorted(paths):
                if path.name.startswith('cohort'):continue
                role=path.parent.name if path.parent.parent.name=='outputs' else 'P';rr=rows(path);mm={};by=defaultdict(dict)
                for line,r in enumerate(rr,1):
                    if r.get('gold') is None:continue
                    w=ws[r['world_id']];raw=score(r['prediction'],r['gold'],w,r['score']['ended']);assert raw==r['score'],(path,line)
                    adj=score_spatial_paraphrases(r['prediction'],r['gold'],w,raw['ended'],score);_,count=normalize_spatial_paraphrases(r['prediction']);total+=1
                    cell=dict(**meta,condition=role,kind=r['kind'],template=r['template'],mode=r.get('mode','atomic_or_source'));key=json.dumps(cell,sort_keys=True);v=groups[key];v['n']+=1;v['raw_k']+=raw['success'];v['adjudicated_k']+=adj['success'];v['rescued_k']+=adj['success'] and not raw['success'];v['rejected_k']+=raw['success'] and not adj['success'];v['raw_parseable_k']+=raw['parseable'];v['adjudicated_parseable_k']+=adj['parseable'];v['aliases_k']+=count>0
                    if raw['success']!=adj['success']:
                        entry=dict(**meta,condition=role,artifact=str(path.relative_to(base)),line=line,world_id=r['world_id'],template=r['template'],raw_success=raw['success'],adjudicated_success=adj['success']);changes.append(entry)
                        if len(examples)<48:examples.append(dict(**entry,prediction=r['prediction'],gold=r['gold'],raw_score=raw,adjudicated_score=adj))
                    if r['kind']=='source_matrix':
                        current=score_spatial_paraphrases(r['current_prediction'],sem.gold(w,r['state'],r['template']),w,r['current_score']['ended'],score)
                        mm[keyrow(r)]=(r,adj,current);by[(r['world_id'],r['state'],r['operation'])][r['source']]=(r,adj,current)
                if path.name.startswith('matrix'):
                    cohort=rows(path.with_name(path.name.replace('matrix','cohort')));locked={(r['world_id'],r['state']):r for r in cohort};qualified=set();literal=set()
                    for key,gg in by.items():
                        assert set(gg)=={'P','Q','U'}
                        old=all(x[0]['common_match'] for x in gg.values())
                        # The frozen cohort establishes full-mask and edited-depth
                        # equality before continuation. Only its current-score
                        # failure may be removed, never a text/mask/depth failure.
                        reasons=locked[key[:2]]['reasons'];new=not (set(reasons)-{'one_or_more_current_semantically_incorrect'}) and all(x[2]['success'] for x in gg.values())
                        if new:qualified.add(key)
                        if new and len({x[0]['current_prediction'] for x in gg.values()})==1:literal.add(key)
                    coverage.append(dict(**meta,condition=role,shard=path.stem,candidate_world_state_operations=len(by),raw_triple_k=sum(all(x[0]['common_match'] for x in gg.values()) for gg in by.values()),posthoc_triple_k=len(qualified),posthoc_literal_triple_k=len(literal),current_own_raw_k=sum(x[0]['current_score']['success'] for x in mm.values()),current_own_adjudicated_k=sum(x[2]['success'] for x in mm.values()),current_candidates=len(mm)))
                    matrices[(role,path.stem)]=(mm,qualified,literal)
            for h in range(2):
                for t in (0,2):
                    name=f'matrix_h{h}_t{t}';sk=(f'S_h{h}',name);mk=(f'M_h{h}',name)
                    if sk not in matrices or mk not in matrices:continue
                    sm,sq,sl=matrices[sk];mm,mq,ml=matrices[mk];assert sq==mq and sl==ml
                    for source in ('P','Q','U'):
                        for label in ('original_fixed_cohort','posthoc_current_adjudicated_cohort','posthoc_current_adjudicated_literal_cohort','all_candidates'):
                            pairs=[]
                            for key,(r,adj,cur) in sm.items():
                                if r['source']!=source or not r['state_heldout']:continue
                                triple=key[:3]
                                if label=='original_fixed_cohort' and not r['common_match']:continue
                                if label=='posthoc_current_adjudicated_cohort' and triple not in sq:continue
                                if label=='posthoc_current_adjudicated_literal_cohort' and triple not in sl:continue
                                pairs.append(((r,adj,cur),mm[key]))
                            n=len(pairs)
                            contrasts.append(dict(**meta,holdout_split=h,template=t,source=source,cohort=label,n=n,worlds=len({a[0]['world_id'] for a,b in pairs}),raw_S_k=sum(a[0]['score']['success'] for a,b in pairs),raw_M_k=sum(b[0]['score']['success'] for a,b in pairs),adjudicated_S_k=sum(a[1]['success'] for a,b in pairs),adjudicated_M_k=sum(b[1]['success'] for a,b in pairs),adjudicated_M_minus_S=sum(b[1]['success']-a[1]['success'] for a,b in pairs)/n if n else None))
    table=[dict(**json.loads(k),**v,raw_rate=v['raw_k']/v['n'],adjudicated_rate=v['adjudicated_k']/v['n']) for k,v in sorted(groups.items())]
    writecsv(ROOT/'spatial_paraphrase_by_seed.csv',table);writecsv(ROOT/'spatial_paraphrase_changes.csv',changes);jsonl(ROOT/'spatial_paraphrase_review_cases.jsonl',examples);writecsv(ROOT/'spatial_paraphrase_M_vs_S.csv',contrasts);writecsv(ROOT/'spatial_paraphrase_source_coverage.csv',coverage)
    dump(ROOT/'SPATIAL_PARAPHRASE_AUDIT.json',dict(predictions_rescored=total,raw_scores_preserved=True,posthoc=True,groups=len(table),raw_k=sum(v['raw_k'] for v in groups.values()),adjudicated_k=sum(v['adjudicated_k'] for v in groups.values()),rescued_k=sum(v['rescued_k'] for v in groups.values()),rejected_k=sum(v['rejected_k'] for v in groups.values()),scorer_sha=digest(ROOT/'spatial_paraphrase_score.py'),fixture_sha=digest(ROOT/'SPATIAL_PARAPHRASE_CHECK.json'),current_cohorts_never_use_continuation_outcomes=True))
    print('Uniform spatial post hoc adjudication:',total,'predictions;',len(changes),'changed success flags')

if __name__=='__main__':main()
