"""Counts-only earliest qualifying development selector and immutable barriers."""
from fractions import Fraction
from common_g16 import *

ALLOWED={'seed','step','split','method','atomic_cells','old_k','old_n','A_k','A_n','D_k','D_n','checkpoint_sha256','checkpoint_state_hash','checkpoint_path'}

def qualify(candidate):
    reasons=[]
    extra=set(candidate)-ALLOWED
    if extra:reasons.append('unapproved fields: '+','.join(sorted(extra)))
    needed={'seed','step','split','method','atomic_cells','old_k','old_n','A_k','A_n','D_k','D_n'}
    if not needed<=set(candidate):return dict(qualified=False,reasons=reasons+['missing required values'])
    if candidate['method']!='F' or candidate['split']!='dev' or candidate['step'] not in CFG['candidates']:reasons.append('not F dev candidate25..200')
    cs=candidate['atomic_cells']
    if not isinstance(cs,list) or any(not isinstance(c,dict) or set(c)!={'status','offset','perspective','k','n'} for c in cs):return dict(qualified=False,reasons=reasons+['missing/invalid atomic values'])
    identities={(c.get('status'),c.get('offset'),c.get('perspective')) for c in cs}
    expected={(s,d,p) for s in ['recorded_plan','reported_cancelled','reported_completed'] for d in range(-3,5) for p in ['first','third'] if s!='reported_completed' or d<=0}
    if len(cs)!=40 or identities!=expected or any(c.get('n')!=128 or not isinstance(c.get('k'),int) or not 0<=c['k']<=128 for c in cs):
        return dict(qualified=False,reasons=reasons+['missing/invalid full40-cell dev counts'])
    macro=sum(Fraction(c['k'],c['n']) for c in cs)/40
    if macro<Fraction(98,100):reasons.append('atomic_macro_below98')
    if any(c['k']*10<9*c['n'] for c in cs):reasons.append('atomic_cell_below90')
    for label in ['old','A','D']:
        k,n=candidate[label+'_k'],candidate[label+'_n']
        if not isinstance(k,int) or not isinstance(n,int) or not 0<=k<=n or n<=0:reasons.append(label+'_missing_counts');continue
        if label in ['old','D'] and n<64:reasons.append(label+'_coverage_below64')
        if label=='A' and n!=128:reasons.append('A_not_full128')
        if k*10<9*n:reasons.append(label+'_below90')
    return dict(qualified=not reasons,reasons=reasons,atomic_macro=float(macro),min_cell=min(c['k']/c['n'] for c in cs))

def write_once(path,value):
    """Publish atomically without replacing an existing selection."""
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():assert json.loads(path.read_text())==value,'Immutable record differs';return
    tmp=path.with_name(path.name+'.'+str(os.getpid())+'.tmp');tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
    try:os.link(tmp,path)
    except FileExistsError:assert json.loads(path.read_text())==value,'Concurrent immutable record differs'
    finally:tmp.unlink()

def decision(candidates):
    ok=[c for c in candidates if qualify(c)['qualified']]
    return min(ok,key=lambda c:c['step']) if ok else None

def check_selection_lock():
    path=ROOT/'selection_lock.json';assert path.exists(),'U/confirmation forbidden before all6 final and3 selections are locked'
    lock=json.loads(path.read_text());assert lock['all6_complete'] and lock['all3_selections_locked']
    for p,sha in lock['files'].items():assert digest(ROOT/p)==sha,p
    return lock

def lock_all():
    verify_lock();files={};summary=[]
    for seed in CFG['seeds']:
        proof=json.loads((ROOT/f'seed_s{seed}_train_complete.json').read_text());assert proof['passed'] and proof['frozen_before']==proof['frozen_after']
        for method in CFG['methods']:
            meta=json.loads((ROOT/f'training/{method}_s{seed}.json').read_text());assert meta['updates']==200 and meta['counts']['instances']==6400
            p=ROOT/meta['final_path'];assert digest(p)==meta['final_sha256']
            for q in [p,ROOT/f'training/{method}_s{seed}.json']:files[str(q.relative_to(ROOT))]=digest(q)
        sp=ROOT/f'selection_s{seed}.json';selected=json.loads(sp.read_text())
        candidates=json.loads((ROOT/f'training/F_s{seed}_candidates.json').read_text());assert [c['step'] for c in candidates]==CFG['candidates']
        earliest=decision(candidates);assert selected['selected_step']==(earliest['step'] if earliest else None)
        if earliest:
            p=ROOT/selected['checkpoint_path'];assert digest(p)==selected['checkpoint_sha256']==earliest['checkpoint_sha256'];files[str(p.relative_to(ROOT))]=digest(p)
        files[str(sp.relative_to(ROOT))]=digest(sp);files[f'training/F_s{seed}_candidates.json']=digest(ROOT/f'training/F_s{seed}_candidates.json')
        summary.append(dict(seed=seed,selected_step=selected['selected_step'],guard_sha256=selected.get('checkpoint_sha256'),selection_failed=earliest is None,final_step=200))
    write_once(ROOT/'selection_lock.json',dict(all6_complete=True,all3_selections_locked=True,U_used=False,files=files,summary=summary))
    csvwrite(ROOT/'selected_models.csv',summary);print('G16 selections locked',summary,flush=True)

if __name__=='__main__':lock_all()
