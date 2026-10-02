"""CPU source comparisons with literal-current-text matching as well as frozen normalization."""
from collections import defaultdict
from common import *
from analyze import writecsv,keyrow

def main():
    coverage=[];disagreements=[];contrasts=[];examples=[]
    for study in ('four_domain_state_coverage_v1','space_relation_confirmation_v1'):
        base=ROOT.parent/study
        for run in sorted((base/'runs/formal').glob('*')):
            m,d,s=run.name.split('_');meta=dict(study=study,model=m,domain=d,seed=int(s[1:]))
            for path in sorted((run/'outputs').glob('*/matrix*.jsonl')):
                role=path.parent.name;rr=rows(path);by=defaultdict(dict)
                for r in rr:by[(r['world_id'],r['state'],r['operation'])][r['source']]=r
                for cohort in ('normalized_fulltext','literal_fulltext'):
                    selected=[]
                    for key,group in by.items():
                        assert set(group)=={'P','Q','U'}
                        if not all(r['common_match'] for r in group.values()):continue
                        if cohort=='literal_fulltext' and len({r['current_prediction'] for r in group.values()})!=1:continue
                        selected.append(group)
                    coverage.append(dict(**meta,condition=role,shard=path.stem,cohort=cohort,candidates=len(by),matched=len(selected),worlds=len({g['P']['world_id'] for g in selected})))
                    for lhs,rhs in [('P','Q'),('P','U'),('Q','U')]:
                        a=sum(g[lhs]['score']['success'] and not g[rhs]['score']['success'] for g in selected);b=sum(not g[lhs]['score']['success'] and g[rhs]['score']['success'] for g in selected)
                        parsed=[g for g in selected if g[lhs]['score']['parseable'] and g[rhs]['score']['parseable']]
                        sa=sum(g[lhs]['score']['scope'] and not g[rhs]['score']['scope'] for g in parsed);sb=sum(not g[lhs]['score']['scope'] and g[rhs]['score']['scope'] for g in parsed)
                        disagreements.append(dict(**meta,condition=role,shard=path.stem,cohort=cohort,lhs=lhs,rhs=rhs,n=len(selected),lhs_only_success=a,rhs_only_success=b,discordant=a+b,both_next_parseable_n=len(parsed),lhs_only_semantic_match=sa,rhs_only_semantic_match=sb,semantic_discordant=sa+sb,next_unresolved_either=len(selected)-len(parsed)))
                        if cohort=='literal_fulltext':
                            for g in selected:
                                if g[lhs]['score']['success']!=g[rhs]['score']['success']:
                                    examples.append(dict(**meta,condition=role,shard=path.stem,lhs=lhs,rhs=rhs,current_full_text=g[lhs]['current_prediction'],left=g[lhs],right=g[rhs]))
            for h in range(2):
                for template in (0,2):
                    name=f'matrix_h{h}_t{template}.jsonl';sp=run/'outputs'/f'S_h{h}'/name;mp=run/'outputs'/f'M_h{h}'/name
                    if not(sp.exists() and mp.exists()):continue
                    sr=rows(sp);mr=rows(mp);ml={keyrow(r):r for r in mr};texts=defaultdict(dict)
                    for r in sr:texts[(r['world_id'],r['state'],r['operation'])][r['source']]=r['current_prediction']
                    for source in ('P','Q','U'):
                        chosen=[(r,ml[keyrow(r)]) for r in sr if r['source']==source and r['state_heldout'] and r['common_match'] and len(set(texts[(r['world_id'],r['state'],r['operation'])].values()))==1]
                        if chosen:contrasts.append(dict(**meta,holdout_split=h,template=template,source=source,cohort='literal_fulltext_mask_depth',n=len(chosen),worlds=len({a['world_id'] for a,b in chosen}),S_k=sum(a['score']['success'] for a,b in chosen),M_k=sum(b['score']['success'] for a,b in chosen),M_minus_S=sum(b['score']['success']-a['score']['success'] for a,b in chosen)/len(chosen)))
    writecsv(ROOT/'literal_fulltext_coverage.csv',coverage);writecsv(ROOT/'same_text_source_disagreement.csv',disagreements);writecsv(ROOT/'literal_fulltext_M_vs_S.csv',contrasts)
    examples.sort(key=lambda r:digest_text(json.dumps([r['study'],r['model'],r['domain'],r['seed'],r['condition'],r['shard'],r['left']['world_id'],r['lhs'],r['rhs']],sort_keys=True)))
    # Every discordance is retained in raw predictions; this small audit uses a
    # deterministic hash, rather than selecting the largest or best-seed effect.
    jsonl(ROOT/'same_text_source_cases.jsonl',examples[:48]);print('Source comparison rows',len(disagreements),'; literal holdout contrasts',len(contrasts))

def digest_text(text):
    import hashlib
    return hashlib.sha256(text.encode()).hexdigest()

if __name__=='__main__':main()
