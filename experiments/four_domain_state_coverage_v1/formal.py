import copy
import torch
from common import *
from train import train,load_editor
from evaluate import admission,atomic
from sources import source_cache,supplement_pool,covered_states
from semantics import states

def run_formal(eng,task,folder,published,training,dev,worlds):
    d=task['domain'];seed=task['seed'];phase=task['phase']
    train(eng,folder/'P',training,dev,seed,600)
    pfile=folder/'P/best.pt';P=load_editor(eng,pfile)
    gate_path=published/'dev'
    if (gate_path/'admission.json').exists():gate=read(gate_path/'admission.json')
    else:gate=admission(eng,P,dev,worlds,gate_path)
    index={'P':dict(path=str(pfile),sha256=digest(pfile),selection=eng.cfg['selection'],seed=seed)}
    symbol=phase=='symbol'
    if symbol or not gate['passed']:
        kind='symbol' if symbol else 'core';test=rows(ROOT/f'data/{d}/test_{kind}.jsonl')
        atomic(eng,P,test,worlds,published/'test_atomic.jsonl');atomic(eng,P,test,worlds,published/'test_reconstruction.jsonl',True)
        dump(published/'checkpoint_index.json',index)
        dump(published/'complete.json',dict(task=task,status='symbol_diagnostic' if symbol else 'not_admitted',admission=gate,resources=eng.resources(),supplement_executed=False));return
    train(eng,folder/'U',training,dev,seed+10000,600)
    ufile=folder/'U/best.pt';qfile=folder/'P/step300.pt';U=load_editor(eng,ufile);Q=load_editor(eng,qfile)
    for role,file in [('Q',qfile),('U',ufile)]:index[role]=dict(path=str(file),sha256=digest(file),parent=index['P'] if role=='Q' else 'independent identity initialization, seed+10000')
    dump(published/'checkpoint_index.json',index)
    ws=[w for w in worlds.values() if w['split']=='train'][:32]
    all_train_states=sorted(set(s for h in eng.cfg['holdouts'][d] for s in covered_states(d,h)[1]))
    pc=source_cache(eng,P,ws,all_train_states,0,folder/'sources/P_train.pt',pfile)
    single=covered_states(d,eng.cfg['holdouts'][d][0])[0]
    qc=source_cache(eng,Q,ws,[single],0,folder/'sources/Q_train.pt',qfile)
    old,oldcoverage=supplement_pool(qc,worlds,[single]);conditions={};coverage_report=[]
    for split_index,heldout in enumerate(eng.cfg['holdouts'][d]):
        single,multi=covered_states(d,heldout);sp,sc=supplement_pool(pc,worlds,[single]);mp,mc=supplement_pool(pc,worlds,multi)
        coverage_report.append(dict(split_index=split_index,heldout=heldout,S=sc,M=mc,old=oldcoverage))
        if not (sc['feasible'] and mc['feasible'] and oldcoverage['feasible']):
            conditions[f'h{split_index}']=dict(status='source_training_infeasible',coverage=coverage_report[-1]);continue
        for condition,pool in [('N',mp),('S',sp),('M',mp)]:
            name=f'{condition}_h{split_index}';run=folder/name
            # Seed and general/old draws matched across N/S/M. Independent
            # optimizer runs all initialize from exact selected P tensor state.
            train(eng,run,training,dev,seed+20000+split_index,200,initial=pfile,pools=dict(focus=pool,old=old),condition=condition)
            cp=run/'final.pt';index[name]=dict(path=str(cp),sha256=digest(cp),parent_P_sha=index['P']['sha256'],heldout=heldout,edited_focus_states=[single] if condition=='S' else multi,condition=condition,updates=200)
        conditions[f'h{split_index}']=dict(status='trained',heldout=heldout)
    dump(published/'source_train_coverage.json',coverage_report);dump(published/'checkpoint_index.json',index)
    # Fixed parameters, budgets and source hashes all saved before first test.
    dump(published/'pre_test_lock.json',dict(checkpoints=index,config_sha=digest(ROOT/'config.json'),data_sha=digest(ROOT/'data/manifest.json'),sources=[dict(path=str(p),sha256=digest(p)) for p in sorted((folder/'sources').glob('*.pt'))]))
    from behavioral import evaluate_all
    evaluate_all(eng,task,folder,published,worlds,index,conditions)
    dump(published/'complete.json',dict(task=task,status='completed' if all(v['status']=='trained' for v in conditions.values()) else 'source_training_infeasible',admission=gate,conditions=conditions,resources=eng.resources(),supplement_executed=any(v['status']=='trained' for v in conditions.values())))
