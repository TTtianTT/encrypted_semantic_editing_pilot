"""CPU-only audits of an explicitly authorized amended test endpoint."""
import gzip
import numpy as np
from .common import *
from .analyze import csv_write,paired_bootstrap,holm
from .metrics import wilson

METHODS=('Original','Plain','Output-only','Mechanism-guided','Random-site')


def atomic_rows(folder):
    rs=[r for p in sorted(folder.glob('*_editing.jsonl')) for r in rows(p)]
    assert len(rs)==14760 and len({r['world_id'] for r in rs})==123
    for r in rs:
        score=r['prediction']['score'];assert r['joint']==score['success']
        assert r['editor_forward_calls']==1 and not r['donor_used'] and not r['target_text_given_to_editor'] and not r['test_time_backward']
    return rs


def summarize_atomic(rs):
    table=[]
    for seed in sorted({r['seed'] for r in rs}):
        for method in METHODS:
            base=[r for r in rs if r['seed']==seed and r['method']==method];assert len(base)==2952
            for source in ('all_50_50','natural','history'):
                selected=base if source=='all_50_50' else [r for r in base if r['source']==source]
                row=dict(seed=seed,method=method,source=source,denominator=len(selected),worlds=123,endpoint='AMENDED_UNEXPOSED123',scope='independent amended endpoint, original128 remains blocked')
                for field in ('joint','target','content','parseable','EOS','exact_match'):row[field+'_numerator']=sum(r[field] for r in selected);row[field+'_rate']=row[field+'_numerator']/len(selected)
                row['mean_update_norm']=float(np.mean([r['update_norm'] for r in selected]));table.append(row)
    return table


def trajectory_rows(folder):
    out=[]
    for p in sorted(folder.glob('*_trajectories.jsonl')):
        tracks=rows(p);assert len(tracks)==20
        for r in tracks:
            for length in (1,2,3,5):
                good=all(step['prediction']['score']['success'] for step in r['steps'][:length]);assert good==r['length_success'][str(length)]
                out.append(dict(world_id=r['world_id'],seed=r['seed'],method=r['method'],length=length,order=r['order'],direction=r['direction'],success=good))
    assert len(out)==9840
    return out


def trajectory_table(rs):
    table=[]
    for seed in sorted({r['seed'] for r in rs}):
        for method in METHODS:
            for length in (1,2,3,5):
                selected=[r for r in rs if (r['seed'],r['method'],r['length'])==(seed,method,length)]
                assert len(selected)==492
                world_good=sum(all(r['success'] for r in selected if r['world_id']==w) for w in {r['world_id'] for r in selected})
                table.append(dict(seed=seed,method=method,length=length,numerator=sum(r['success'] for r in selected),denominator=492,worlds=123,all_four_world_numerator=world_good,all_four_world_Wilson95=wilson(world_good,123),endpoint='AMENDED_UNEXPOSED123'))
    return table


def audit_run(source,dest,summary):
    proposal=read(ROOT/'configs/S4_PROTOCOL_AMENDMENT_PROPOSAL.json');auth=read(ROOT/'configs/S4_AMENDMENT_AUTHORIZATION.json')
    assert auth['approved'] and auth['proposal_sha256']==sha(ROOT/'configs/S4_PROTOCOL_AMENDMENT_PROPOSAL.json')
    samples=atomic_rows(source);tracks=trajectory_rows(source)
    assert {r['world_id'] for r in samples}==set(proposal['eligible_worlds'])
    exclusions=rows(source/'pre_exposure_exclusions.jsonl');assert {r['world_id'] for r in exclusions}==set(proposal['excluded_worlds'])
    atoms=summarize_atomic(samples);chains=trajectory_table(tracks)
    qualification=[r for p in sorted(source.glob('*_qualification.jsonl')) for r in rows(p)]
    panel=[]
    for pair in sorted({r['source_pair'] for r in qualification}):
        rs=[r for r in qualification if r['source_pair']==pair];eligible=[r for r in rs if r['eligible']]
        count=len({r['world_id'] for r in eligible})
        panel.append(dict(source_pair=pair,fixed_scan_worlds=128,input_worlds=123,prior_exposure_excluded_worlds=5,qualified_worlds=count,qualification_status='NOT_ESTIMABLE' if count==0 else 'EXPLORATORY_BELOW40' if count<40 else 'AMENDED_CONFIRMATION_ELIGIBLE',mean_delta_norm=float(np.mean([r['delta_norm'] for r in eligible])) if eligible else None,exclusion_reasons={reason:sum(reason in r['reasons'] for r in rs) for reason in sorted({reason for r in rs for reason in r['reasons']})}))
    boundaries=[]
    for method in METHODS:
        rs=[r for r in samples if r['method']==method]
        good=sum(all(r['joint'] for r in rs if r['world_id']==w) for w in {r['world_id'] for r in rs})
        boundaries.append(dict(method=method,numerator=good,denominator=123,world_Wilson95=wilson(good,123)))
    assert summary['frozen_backbone_sha_before']==summary['frozen_backbone_sha_after']
    assert summary['frozen_history_sha_before']==summary['frozen_history_sha_after']
    audit=dict(passed=True,seed=summary['seed'],original_scan_worlds=128,prior_exposure_exclusions=exclusions,amended_independent_worlds=123,atomic=atoms,trajectories=chains,panel_A=panel,world_boundaries=boundaries,backbone_unchanged=True,history_unchanged=True,original128_endpoint_status='BLOCKED_TEST_INTEGRITY',authorization_sha256=sha(ROOT/'configs/S4_AMENDMENT_AUTHORIZATION.json'))
    dump(dest/'NUMERICAL_AUDIT.json',audit)
    allocation=read(dest/'RUN_STATUS.json')['allocation']
    table='\n'.join(f"| {r['method']} | {r['joint_numerator']}/2952 | {r['target_numerator']}/2952 | {r['content_numerator']}/2952 |" for r in atoms if r['source']=='all_50_50')
    text(dest/'REPORT.md',f'''# BART seed{summary['seed']} amended independent test terminal

COMPLETED; Slurm {allocation['job_id']}; allocation GPU-hours {allocation['GPU_hours']:.6f}. User explicitly approved the hashed amendment before test unsealing. Original registered128 endpoint remains BLOCKED_TEST_INTEGRITY: five prior-exposed worlds are NA, not failures. The fixed remaining123 are evaluated as a distinct amended endpoint; no refill or outcome-based eligibility. Every method has 2952 operations, natural/history each1476, weighted50/50.

| Method | Joint success | Target | Protected content |
| --- | --- | --- | --- |
{table}

Full predictions, qualification exclusions, every own-latent chain step, intervention conditions and curve failures are retained and independently recomputed. Each method sees H/mask/op only, with one editor forward and no donor/target text/re-encoding/test-time gradient/rejection. Diagnostic K/V/resampling uses donor information separately. Checkpoints, hyperparameters, semantic content sites, mechanism/random components and random retention amplitudes were locked before unseal and cannot be revised using these results. Three-seed paired-world comparisons are collected after all runs; this seed alone does not establish mechanism superiority. Full chain success requires every step, and Wilson world-level bounds supplement boundary bootstrap intervals. Template OOD is UNAVAILABLE, not a random split renamed OOD. T5Gemma's later method comparisons are not run.
''')
    text(dest/'INTERPRETATION.md','Report the explicitly amended123 endpoint separately from the unrecoverable original128 endpoint. Interpret mechanism versus Output-only/Random-site with paired world-cluster intervals and the prelocked Holm family. Count core worlds, not source/operation rows, as independent units. Same text and next-output fork do not imply better editing. No component or loss may be reselected from this test.\n')
    return audit


def summarize():
    m=read(ROOT/'manifests/S4.json');all_records=[];tracks=[];run_audits=[]
    for seed in (42,43,44):
        folder=Path(m['output_root'])/f'bart_s{seed}';assert read(folder/'RUN_STATUS.json')['status']=='COMPLETED'
        all_records.extend(atomic_rows(folder));tracks.extend(trajectory_rows(folder))
        report=ROOT/'reports'/f"S4_{m['version']}_bart_s{seed}";run_audits.append(read(report/'NUMERICAL_AUDIT.json'))
    atoms=summarize_atomic(all_records);chains=trajectory_table(tracks)
    flat=[{k:r[k] for k in ('world_id','seed','method','source','state','operation','current_correct','joint','target','content','parseable','EOS','exact_match','update_norm','relative_update_norm','editor_latency_seconds','peak_allocated_bytes')} for r in all_records]
    atomic(ROOT/'results/amended_test_atomic.jsonl.gz',gzip.compress(''.join(json.dumps(r)+'\n' for r in flat).encode(),mtime=0))
    atomic(ROOT/'results/amended_test_trajectories.jsonl.gz',gzip.compress(''.join(json.dumps(r)+'\n' for r in tracks).encode(),mtime=0))
    csv_write(ROOT/'results/amended_test_atomic_summary.csv',atoms);csv_write(ROOT/'results/amended_test_trajectory_summary.csv',chains)
    comparisons=[]
    for a,b in [('Mechanism-guided','Output-only'),('Mechanism-guided','Random-site'),('Output-only','Plain'),('Random-site','Plain')]:
        result=paired_bootstrap(flat,a,b);per_seed={str(seed):paired_bootstrap([r for r in flat if r['seed']==seed],a,b) for seed in (42,43,44)}
        comparisons.append(dict(a=a,b=b,primary_family=a=='Mechanism-guided',**result,per_seed=per_seed,endpoint='AMENDED_UNEXPOSED123'))
    for r,p in zip([r for r in comparisons if r['primary_family']],holm([r['p_value'] for r in comparisons if r['primary_family']])):r['Holm_adjusted_p']=p
    direction=[];strata=[]
    for seed in (42,43,44):
        for method in METHODS:
            base=[r for r in flat if r['seed']==seed and r['method']==method]
            for field in ('operation','state','current_correct'):
                for value in sorted({r[field] for r in base}):
                    rs=[r for r in base if r[field]==value]
                    strata.append(dict(seed=seed,method=method,grouping=field,stratum=value,numerator=sum(r['joint'] for r in rs),denominator=len(rs),worlds=len({r['world_id'] for r in rs})))
            bins=read(ROOT/'configs/METHOD_COMPARISON_LOCK.json')['norm_bins']
            for lo,hi in zip(bins,bins[1:]):
                rs=[r for r in base if lo<=r['update_norm']<hi]
                strata.append(dict(seed=seed,method=method,grouping='update_norm',stratum=f'[{lo},{hi})',numerator=sum(r['joint'] for r in rs),denominator=len(rs),worlds=len({r['world_id'] for r in rs}),status='ESTIMATED' if rs else 'NOT_ESTIMABLE_EMPTY_BIN'))
            for length in (1,2,3,5):
                for order in (0,1):
                    for inverse in ('forward','inverse'):
                        rs=[r for r in tracks if (r['seed'],r['method'],r['length'],r['order'],r['direction'])==(seed,method,length,order,inverse)]
                        assert len(rs)==123
                        direction.append(dict(seed=seed,method=method,length=length,order=order,direction=inverse,numerator=sum(r['success'] for r in rs),denominator=123))
    csv_write(ROOT/'results/amended_test_atomic_strata.csv',strata);csv_write(ROOT/'results/amended_test_trajectory_directions.csv',direction)
    trajectory_comparisons=[]
    for a,b in [('Mechanism-guided','Output-only'),('Mechanism-guided','Random-site')]:
        for length in (1,2,3,5):
            adapted=[dict(world_id=r['world_id'],seed=r['seed'],method=r['method'],source=source,joint=r['success']) for r in tracks if r['length']==length for source in ('natural','history')]
            trajectory_comparisons.append(dict(a=a,b=b,length=length,**paired_bootstrap(adapted,a,b),source_interpretation='natural-start only; two API labels are identical copies, not extra independent sources',scope='secondary trajectory analysis'))
    folder=Path(m['output_root'])/'bart_s42'
    readouts=[r for p in sorted(folder.glob('*_readouts.jsonl')) for r in rows(p)]
    causal=[r for p in sorted(folder.glob('*_causal.jsonl')) for r in rows(p)]
    curves=[r for p in sorted(folder.glob('*_curves.jsonl')) for r in rows(p)]
    bridges=[r for seed in (42,43,44) for p in sorted((Path(m['output_root'])/f'bart_s{seed}').glob('*_bridge.jsonl')) for r in rows(p)]
    prob=[]
    for pair in sorted({r['source_pair'] for r in readouts}):
        rs=[r for r in readouts if r['source_pair']==pair]
        prob.append(dict(source_pair=pair,worlds=len({r['world_id'] for r in rs}),token_denominator=len(rs),mean_JS=float(np.mean([r['JS'] for r in rs])),max_JS=max(r['JS'] for r in rs),p95_JS=float(np.quantile([r['JS'] for r in rs],.95)),max_abs_margin_change=max(abs(r['b_margin']-r['a_margin']) for r in rs),scope='amended123 confirmation' if len({r['world_id'] for r in rs})>=40 else 'exploratory below40'))
    cs=[]
    for key in sorted({(r['module'],r['scope'],r['condition']) for r in causal}):
        rs=[r for r in causal if (r['module'],r['scope'],r['condition'])==key];complete=[r for r in rs if 'free' in r]
        cs.append(dict(module=key[0],scope=key[1],condition=key[2],scanned_side_records=len(rs),intervened_side_records=len(complete),intervened_worlds=len({r['world_id'] for r in complete}),joint_numerator=sum(r['free']['score']['success'] for r in complete) if complete else None,content_numerator=sum(r['free']['score']['preserved'] for r in complete) if complete else None,target_numerator=sum(r['free']['score']['target'] for r in complete) if complete else None,content_margin_shift=float(np.mean([r['content_margin_shift'] for r in complete])) if complete else None,NA_records=len(rs)-len(complete),qualification='NOT_ESTIMABLE' if not complete else 'exploratory below40' if len({r['world_id'] for r in complete})<40 else 'amended123 confirmation'))
    curve_table=[]
    for key in sorted({(r['source_pair'],r['direction'],r['alpha']) for r in curves}):
        rs=[r for r in curves if (r['source_pair'],r['direction'],r['alpha'])==key]
        curve_table.append(dict(source_pair=key[0],direction=key[1],alpha=key[2],numerator=sum(r['tokens_preserved'] for r in rs),denominator=len(rs),worlds=len({r['world_id'] for r in rs}),mean_norm=float(np.mean([r['delta_norm'] for r in rs])),scope='fixed8 world subset, exploratory',per_token_energy_max_error=max(r['per_token_energy_max_error'] for r in rs)))
    matched=[]
    for chosen in read(ROOT/'configs/RANDOM_PRESERVATION_LOCK.json')['locked']:
        rs=[r for r in curves if r['source_pair']==chosen['source_pair'] and r['direction']==chosen['direction'] and r['alpha']==chosen['alpha']]
        matched.append(dict(**chosen,test_numerator=sum(r['tokens_preserved'] for r in rs),test_denominator=len(rs),amplitude_reselected_from_test=False,scope='fixed8 subset'))
    csv_write(ROOT/'results/amended_test_readout_summary.csv',prob);csv_write(ROOT/'results/amended_test_causal_summary.csv',cs);csv_write(ROOT/'results/amended_test_perturbation_curves.csv',curve_table)
    bridge_table=[]
    for seed in (42,43,44):
        for pair in sorted({r['source_pair'] for r in bridges}):
            for op in ('plus','minus'):
                rs=[r for r in bridges if (r['seed'],r['source_pair'],r['operation'])==(seed,pair,op)]
                bridge_table.append(dict(seed=seed,source_pair=pair,operation=op,panel_A_denominator=len(rs),panel_B_numerator=sum(r['panel_B'] for r in rs),legacy_accuracy_fork_numerator=sum(r['legacy_accuracy_fork'] for r in rs),worlds=len({r['world_id'] for r in rs})))
    csv_write(ROOT/'results/amended_test_bridge.csv',bridge_table)
    dump(ROOT/'results/AMENDED_TEST_NUMERICAL_AUDIT.json',dict(atomic=atoms,trajectories=chains,comparisons=comparisons,trajectory_comparisons=trajectory_comparisons,probability_summary=prob,causal_summary=cs,curve_summary=curve_table,matched_retention_random=matched,bridge=bridge_table,runs=run_audits,records=len(flat),amended_worlds=123,original_scan=128,original_endpoint='BLOCKED_TEST_INTEGRITY',amended_endpoint='AMENDED_UNEXPOSED123',authorization_sha256=sha(ROOT/'configs/S4_AMENDMENT_AUTHORIZATION.json')))
    status=read(ROOT/'results/main_method_status.json');status.update(confirmatory_family_executed=True,endpoint='AMENDED_UNEXPOSED123',comparisons=[r for r in comparisons if r['primary_family']])
    dump(ROOT/'results/main_method_status.json',status)
    print(json.dumps(comparisons,ensure_ascii=False))


if __name__=='__main__':summarize()
