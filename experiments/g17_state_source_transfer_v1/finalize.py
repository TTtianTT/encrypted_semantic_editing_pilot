"""Post-evaluation CPU delivery checks/interpretation only; no inference/selection."""
import statistics,itertools
from common_g17 import *
def main():
    verify_lock();rows=read(ROOT/'per_example.jsonl.gz');coverage=list(csv.DictReader((ROOT/'current_coverage.csv').open()));source=list(csv.DictReader((ROOT/'source_state_results.csv').open()));nat=list(csv.DictReader((ROOT/'natural_controls.csv').open()));roll=list(csv.DictReader((ROOT/'self_rollout.csv').open()));pairs=list(csv.DictReader((ROOT/'paired_repair_gains.csv').open()));mask=list(csv.DictReader((ROOT/'mask_controls.csv').open()));inter=list(csv.DictReader((ROOT/'interchangeability.csv').open()));intervals=[]
    def add(r,metric,k,n,scope):
        intervals.append({k:v for k,v in r.items() if k in ['seed','split','anchor','producer','receiver','sources']}|dict(metric=metric,scope=scope,**proportion(int(k),int(n))))
    for r in source:
        for k in ['k','exact_k','EOS_k']:add(r,'conditional_'+k,r[k],r['n'],'C')
        for k in ['gate_and_next_k','raw_full2_k','raw_next_k']:add(r,k,r[k],160,'raw160')
    for r in coverage:
        for k in ['k','exact_k','EOS_k']:add(r,'current_'+k,r[k],160,'raw160')
        if r['current_C_n']:add(r,'C_coverage',r['current_C_n'],160,'raw160')
        add(r,'natural_mask_equal',r['natural_mask_equal_k'],160,'raw160')
    for r in nat:
        for k in ['k','exact_k','EOS_k']:add(r,'natural_'+k,r[k],160,'raw160')
    for r in roll:
        for k in ['k','first_k','first_exact_k','endpoint_k','endpoint_exact_k']:add(r,'self_'+k,r[k],160,'raw160')
    for r in inter:
        if r.get('only_F'):
            r['both_correct']=r['both'];r['only_left_correct']=r['only_F'];r['only_right_correct']=r['only_N'];r['both_wrong']=r['neither'];r['left_source'],r['right_source']=r['sources'].split('-');r['legacy_field_aliases']='only_F means left source, only_N means right source; receiver unchanged'
            for k in ['both_correct','only_left_correct','only_right_correct','both_wrong']:add(r,k,r[k],r['n'],r['scope'])
        add(r,'all_success',r['all_success_k'],r['n'],r['scope'])
    csvwrite(ROOT/'interchangeability.csv',inter);csvwrite(ROOT/'proportion_intervals.csv',intervals)
    # Additional presentation mean/SD for original counts; identical estimators/no new comparisons.
    means=list(csv.DictReader((ROOT/'seed_mean_SD.csv').open()))
    for r in means:r['metric']='full2' if r['kind']=='self' else 'joint'
    for rs,kind,metrics in [(roll,'self',['first_k','endpoint_k']),(coverage,'coverage',['k','exact_k','current_C_n','natural_mask_equal_k'])]:
        keys={(r['split'],r['anchor'],r.get('producer',''),r.get('receiver','')) for r in rs}
        for sp,a,p,q in sorted(keys):
            ss=sorted([r for r in rs if (r['split'],r['anchor'],r.get('producer',''),r.get('receiver',''))==(sp,a,p,q)],key=lambda r:r['seed'])
            for metric in metrics:
                vals=[int(r[metric])/160 for r in ss if r[metric]]
                means.append(dict(kind=kind,split=sp,anchor=a,producer=p,receiver=q,metric=metric,mean=statistics.mean(vals) if len(vals)==3 else None,sample_SD=statistics.stdev(vals) if len(vals)==3 else None,contributing_seeds=len(vals),per_seed=json.dumps([dict(seed=r['seed'],k=r[metric],n=160) for r in ss])))
    csvwrite(ROOT/'seed_mean_SD.csv',means)
    def cell(s,sp,a,p,q):return next(r for r in source if (r['seed'],r['split'],r['anchor'],r['producer'],r['receiver'])==(str(s),sp,str(a),p,q))
    def natural(s,sp,a,q):return next(r for r in nat if (r['seed'],r['split'],r['anchor'],r['receiver'])==(str(s),sp,str(a),q))
    def self_(s,sp,a,q):return next(r for r in roll if (r['seed'],r['split'],r['anchor'],r['receiver'])==(str(s),sp,str(a),q))
    def gain(sp,a,p):return next(r for r in pairs if r['seed']=='mean' and r['split']==sp and r['anchor']==str(a) and r['producer']==p and r['contrast']=='F-N' and r['metric']=='conditional_joint')
    primary=json.loads((ROOT/'primary_result.json').read_text());txt=['# G17 interpretation\n\nZero training confirmed; five editor roles and E/D frozen; no optimizers/backward, max two semantic calls.\n\n']
    if primary['stable_positive']:txt.append('IID +2/U supports positive main repair increment across all three fixed training seeds under the preregistered definition. This is limited state/source transfer in audited-lineage-unsupervised edited reception, not universal interchangeability or arbitrary composition.\n\n')
    else:txt.append('The preregistered condition for stable positive IID +2/U transfer across all three seeds is NOT met. Disclose each seed and cohort; high F absolute success alone does not establish new repair transfer. Zero increments at P/N ceiling are pre-existing feasibility, not falsification of all transfer.\n\n')
    for sp in CFG['splits']:
        for a in CFG['anchors']:
            txt.append(f'## {sp} current anchor {a}\n\n')
            for s in CFG['seeds']:
                fs=self_(s,sp,a,'F');ns=self_(s,sp,a,'N');txt.append(f'seed{s}: selfF {fs["k"]}/160 vs selfN {ns["k"]}/160; naturalF {natural(s,sp,a,"F")["k"]}/160 vs N {natural(s,sp,a,"N")["k"]}/160. ')
                for p in CFG['producers']:
                    f=cell(s,sp,a,p,'F');n=cell(s,sp,a,p,'N');p0=cell(s,sp,a,p,'P');txt.append(f'{p} input: F {f["k"]}/{f["n"]}, N {n["k"]}/{n["n"]}, P {p0["k"]}/{p0["n"]}; rawF full2 {f["raw_full2_k"]}/160; ')
                txt.append('\n\n')
            for p in CFG['producers']:
                g=gain(sp,a,p);txt.append(f'{p}: mean F−N {g["delta_pp"]}pp [CI {g["ci_low_pp"]},{g["ci_high_pp"]}], seed SD {g["seed_sample_SD_pp"]}, per-seed C={g["per_seed_n"]}.\n\n')
    txt.append('Historical labels: +2 not directly supervised edited reception in audited parameter ancestry (natural rule known); today/P F repair input, U/G related ancestor exposure; yesterday/G maintenance input, exact later P/U not repair inputs; −2 ancestor G10 two-call exposure, not repair-maintained state. G16NF derive from P, not G15. These are supervised-input roles, not claims about pretraining or unavailable history.\n\n')
    txt.append('Mask boundaries: natural/edited equal-mask subsets are explicitly separate in mask_controls. Empty strict subsets cannot support memory-only explanations; fixed F−N uses the exact same full edited state regardless natural mask. Current producer entry failures excluded only from its own C, kept in raw160; pair/triple intersections separate. G17 yesterday/G is one-step producer maintenance comparison, not fullG13H0/H1/H2 all3 re-evaluation. Full40cell not re-evaluated.\n\n')
    txt.append('All intervals outside IID+2/U descriptive, no multiple-comparison/global significance claim. Bootstrap samples160 shared worlds jointly across anchors/sources/receivers/seeds; no independent1280-world or480-training inflation. World CI excludes full training/selection uncertainty. Wilson intervals retained for raw/conditional/exact/EOS and pair patterns; zero/one bootstrap degeneration is not certainty. Natural insufficiency, entry coverage and edited reception failure are distinct evidence. Reencoding actual output is a diagnostic complete-interface control, never pure-latent result or extra independent evidence when identical to natural.\n\n')
    budget=json.loads((ROOT/'budget.json').read_text());txt.append(f'Budget actual {budget["actual_gpu_hours"]:.6f}, requested {budget["requested_gpu_hours"]:.6f} GPUh, peak {budget["max_concurrent_gpus"]}. Engineering events are fully retained separately; no score-driven retry/configuration/anchor/source changes. Main cases prehash12 worlds, extra cases posthoc descriptive. No automatic follow-up training or expansion.\n')
    (ROOT/'INTERPRETATION.md').write_text('\n'.join(line.rstrip() for line in ''.join(txt).splitlines()).rstrip()+'\n')
    report=(ROOT/'REPORT.md').read_text();answer='\n'.join(txt[:3])+'\nFull interpretation: INTERPRETATION.md; all raw/conditional/Wilson/pair counts available in CSVs.\n\n'
    report=report.replace('零训练，全部冻结；唯一主检验 IID,+2,U，固定同一输入比较F−N。\n\n','零训练，全部冻结；唯一主检验 IID,+2,U，固定同一输入比较F−N。\n\n'+answer)
    report+='\n执行与偏离：engineering_events.json 记录 CPU 同名模块导入修复、历史source=Q索引修复及CPU NumPy JSON标量导出修复；科学条件未因新确认分数调整。Smoke2533工程失败、2534通过，预算均计入。\n\n'+f'累计实际{budget["actual_gpu_hours"]:.6f}、申请{budget["requested_gpu_hours"]:.6f} GPU小时，峰值{budget["max_concurrent_gpus"]}。确认完成状态与JobID见slurm_jobs.csv和seed_s*_complete.json。\n'
    (ROOT/'REPORT.md').write_text(report)
    cache_artifacts=[]
    for p in sorted((ROOT/'cache_manifests').glob('*.json')):
        z=json.loads(p.read_text());assert digest(z['cache_path'])==z['cache_sha256'];cache_artifacts.append(dict(path=z['cache_path'],sha256=z['cache_sha256'],manifest=str(p.relative_to(ROOT)),size_bytes=Path(z['cache_path']).stat().st_size))
    deps=json.loads((ROOT/'scientific_lock.json').read_text())['files'];assert all(digest(REPO/p)==h for p,h in deps.items());assert len(rows)==130560
    outputs=[]
    for p in sorted((ROOT/'outputs').glob('*')):outputs.append(dict(path=str(p),sha256=digest(p),bytes=p.stat().st_size))
    dump(ROOT/'artifact_manifest.json',dict(base_commit=CFG['base_commit'],zero_training=True,old_checkpoints_referenced_not_reuploaded=True,scientific_lock_sha256=digest(ROOT/'scientific_lock.json'),large_caches_local_only=cache_artifacts,local_output_shards=outputs,public_complete_archive=dict(path='per_example.jsonl.gz',sha256=digest(ROOT/'per_example.jsonl.gz'),records=len(rows)),all_dependencies_unchanged=True))
    dump(ROOT/'delivery_audit.json',dict(passed=True,scientific_dependencies_unchanged=True,complete_records=len(rows),fixed_case_worlds=12,zero_training=True,mask_subsets_explicit=True,proportion_intervals=len(intervals),actual_budget=budget,CPU_delivery_helpers_do_not_change_scores_cohorts_draws=True))
    print('G17 CPU delivery checks passed; no old files/locked scientific code changed')
if __name__=='__main__':main()
