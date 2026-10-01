"""Synthetic CPU denominator/paired-statistics fixture; never experimental data."""
import numpy as np
from common_g15 import *
a=load_module('g15_aggregation_fixture',ROOT/'analyze.py')

def main():
    worlds=read(ROOT/'data/worlds.jsonl');rows=[]
    for method in ['P','N','F','O']:
        for split in ['iid','template_ood']:
            sw=[w for w in worlds if w['split']==split];plans=[w for w in sw if w['record_status']=='recorded_plan']
            def row(kind,w,success=True,source=None,**extras):
                z=dict(kind=kind,world_id=w['record_id'],seed=42,method=method,split=split,joint=bool(success),exact=bool(success),error_type='success' if success else 'date_error',predicted_relative_date=-1 if success else -2,relative_date_delta_days=0 if success else -1)
                if source is not None:z['source']=source
                z.update(extras);rows.append(z)
            for w in sw:
                for d,p in atomic_specs(w):row('atomic',w,status=w['record_status'],offset=d,perspective=p)
            for i,w in enumerate(plans):
                matched=i<80
                edited=(i<40 if method=='F' else i<80 if method=='O' else False)
                for source in ['E','P','G','U']:row('fixed',w,True if source=='E' else edited,source,matched=matched,full=True if source=='E' else edited)
                for source in ['H0','H1','H2']:row('old',w,source=source,matched=i<120)
                for source in ['P','G','U']:row('reset_fixed',w,source=source,matched=matched,full=True,reset_equals_natural=True)
                first=i<80 if method=='F' else i<120 if method=='O' else True
                second=method in ['F','O'];full=bool(first and second)
                row('self_first',w,first,'Q')
                row('self_second',w,second,'Q',matched=matched,full=full,full_exact=full,first_failure=1 if not first else 2 if not second else None)
                row('reset_self',w,source='Q',matched=matched,full=first,reset_equals_natural=first)
    z=a.analyze([42],rows,{w['record_id']:w for w in worlds});differences=a.contrasts([42],z)
    F=next(r for r in z['core'] if r['method']=='F' and r['split']=='iid')
    O=next(r for r in z['core'] if r['method']=='O' and r['split']=='iid')
    assert F['n']==O['n']==80 and F['old_n']==120
    assert F['U_k']==40 and O['U_k']==80
    assert F['endpoint2_k']==O['endpoint2_k']==160 and F['full2_k']==80 and O['full2_k']==120
    counts=next(r for r in z['pairs'] if r['method']=='F' and r['split']=='iid' and r['source']=='U')
    assert (counts['both'],counts['natural_only'],counts['edited_only'],counts['neither'])==(40,40,0,0)
    contrast=next(r for r in differences if r['seed']==42 and r['split']=='iid' and r['contrast']=='O-F' and r['metric']=='U')
    assert contrast['delta_pp']==50 and contrast['ci_lo_pp']<50<contrast['ci_hi_pp']
    full=next(r for r in differences if r['seed']==42 and r['split']=='iid' and r['contrast']=='O-F' and r['metric']=='self_full')
    assert full['delta_pp']==25
    delta,draws=a.paired_boot(np.ones(160),np.zeros(160),np.zeros(160,bool),np.zeros((2000,160),int))
    assert delta is None and not np.isfinite(draws).any()
    dump(ROOT/'aggregation_test.json',dict(passed=True,synthetic_CPU_only=True,not_scientific_evidence=True,rows=len(rows),conditional_n=80,old_n=120,endpoint_vs_full_checked=True,shared_world_bootstrap_checked=True,empty_cohort_NA_checked=True,science_files_not_changed=True,created_after_science_lock=True))
    print('CPU synthetic aggregation verified',len(rows),'rows; conditional/old/raw denominators80/120/160')

if __name__=='__main__':main()
