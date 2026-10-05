"""Structured numerator/denominator calculations; no endpoint-as-full substitution."""
import collections
import csv
import io
import numpy as np
from .common import *

def csv_write(path,records):
    columns=list(dict.fromkeys(k for r in records for k in r));s=io.StringIO();w=csv.DictWriter(s,fieldnames=columns,lineterminator='\n');w.writeheader();w.writerows(records);text(path,s.getvalue())
def ratio(rs,key):
    n=sum(bool(r.get(key,False)) for r in rs);return dict(numerator=n,denominator=len(rs),rate=n/len(rs) if rs else None)
def summarize_records(records):
    groups=collections.defaultdict(list)
    for r in records:
        kind=r['kind']
        keys={'atomic':['receiver','state','operation'],'second':['b','condition'],'matrix':['producer','receiver'],'depth':['producer','receiver','sequence_id','depth','condition'],'long':['producer','sequence_id','depth']}[kind]
        tag=tuple((k,r[k]) for k in keys)
        groups[(kind,tag,'all')].append(r)
        if kind=='matrix':
            for subset,passed in [('shared_first',r['shared_first_correct']),('shared_raw_exact',r['shared_first_correct'] and r['raw_exact']),('shared_trailing_ASCII',r['shared_first_correct'] and r['trailing_ASCII_equal']),('shared_parser_semantic',r['shared_first_correct'] and r['parser_semantic_equal'])]:
                groups[(kind,tag,subset)] # preserve zero-denominator NA
                if passed:groups[(kind,tag,subset)].append(r)
        if kind=='depth':
            groups[(kind,tag,'correct_prefix')]
            if r['Cprefix']:groups[(kind,tag,'correct_prefix')].append(r)
    out=[]
    for (kind,tag,subset),rs in sorted(groups.items()):
        for metric in ['C0','C1','Cprefix','Cbridge','C2','Full','bridge_exact']:
            if rs and not any(metric in r for r in rs):continue
            # For empty slices only Full is defined; other absent fields not invented.
            if not rs and metric!='Full':continue
            out.append(dict(kind=kind,**dict(tag),subset=subset,metric=metric,worlds=len({r['world_id'] for r in rs}),**ratio(rs,metric)))
    return out
def failure_partition(records):
    group=collections.defaultdict(dict)
    for r in records:
        if r['kind']=='second':group[(r['world_id'],r['b'])][r['condition']]=r
    out=[]
    categories={(False,True,True):'SOURCE_INTERFACE_COMPATIBLE',(False,False,True):'CANONICAL_ONLY',(False,False,False):'NATURAL_ATOMIC_GAP',(False,True,False):'EXPRESSION_DEPENDENT'}
    for (world,op),g in sorted(group.items()):
        if set(g)!={'PURE','ACTUAL_REENCODE','GOLD_CANONICAL'}:category='MISSING_CONDITION'
        elif not(g['PURE']['C0'] and g['PURE']['C1']):category='INITIAL_OR_FIRST_FAILURE'
        elif not g['ACTUAL_REENCODE']['Cbridge']:category='BRIDGE_CHANGED_CURRENT'
        elif not g['GOLD_CANONICAL']['Cbridge']:category='CANONICAL_RECONSTRUCTION_FAILURE'
        else:
            flags=tuple(g[k]['C2'] for k in ['PURE','ACTUAL_REENCODE','GOLD_CANONICAL'])
            category='PURE_ALREADY_SUCCESS' if flags[0] else categories[flags]
        out.append(dict(world_id=world,b=op,category=category,**{k+'_C2':g[k]['C2'] for k in g}))
    return out
def primary(records):
    if any(r['kind']=='second' for r in records):
        groups=collections.defaultdict(dict)
        for r in records:
            if r['kind']=='second':groups[(r['world_id'],r['b'])][r['condition']]=r['Full']
        diffs=[int(g['ACTUAL_REENCODE'])-int(g['PURE']) for g in groups.values() if 'ACTUAL_REENCODE' in g and 'PURE' in g]
        return dict(name='Full2_actual_reencode_minus_pure',estimate=float(np.mean(diffs)) if diffs else None,paired_path_denominator=len(diffs))
    if any(r['kind']=='matrix' for r in records):
        vals={}
        for p,q in [('F','F'),('F','R'),('R','F'),('R','R')]:
            rs=[r for r in records if r['kind']=='matrix' and r['producer']==p and r['receiver']==q];vals[p+q]=ratio(rs,'Full')
        if len({v['denominator'] for v in vals.values()})!=1:estimate=None
        else:estimate=vals['FF']['rate']+vals['RR']['rate']-vals['FR']['rate']-vals['RF']['rate']
        return dict(name='producer_receiver_interaction_I',estimate=estimate,matrix=vals)
    return dict(name='depth_diagnosis',estimate=None)
def bootstrap_primary(records,kind):
    clusters=collections.defaultdict(list)
    if kind=='R01':
        g=collections.defaultdict(dict)
        for r in records:
            if r['kind']=='second':g[(r['world_id'],r['seed'],r['b'])][r['condition']]=r['Full']
        for (w,s,b),v in g.items():
            if set(v)=={'PURE','ACTUAL_REENCODE','GOLD_CANONICAL'}:clusters[w].append((s,int(v['ACTUAL_REENCODE'])-int(v['PURE'])))
    else:
        g=collections.defaultdict(dict)
        for r in records:
            if r['kind']=='matrix':g[(r['world_id'],r['seed'],r['initial_state'],r['a'],r['b'])][r['producer']+r['receiver']]=r['Full']
        for (w,s,*_),v in g.items():
            if set(v)=={'FF','FR','RF','RR'}:clusters[w].append((s,int(v['FF'])+int(v['RR'])-int(v['FR'])-int(v['RF'])))
    seeds=sorted({s for a in clusters.values() for s,v in a});worlds=sorted(clusters)
    x=np.array([[np.mean([v for s,v in clusters[w] if s==seed]) for seed in seeds] for w in worlds])
    assert np.isfinite(x).all()
    rng=np.random.default_rng(2026100502);dist=np.empty(5000)
    for i in range(5000):dist[i]=x[rng.integers(0,len(worlds),len(worlds))].mean(axis=0).mean()
    return dict(estimate=float(x.mean()),ci95=np.quantile(dist,[.025,.975]).tolist(),worlds=len(worlds),seeds=seeds,bootstrap_draws=5000,unit='world cluster; all seeds and legal operation cells together; equal seed and cell weights',degenerate=bool(dist.max()==dist.min()),limitations='Fixed-checkpoint world sampling; not training randomness. Saturated intervals do not imply population certainty.')
