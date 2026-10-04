"""Discovery/validation and locked once-only t0 repair rollouts."""
import os
import re
import time
from collections import defaultdict
import torch
from .common import *
from .adapter import render,gold,advance
from .pairs import primary_pairs
from .state_patching import basis,patch,matched_random,reverse
from .operator_analysis import analyze

RANDOM_SEEDS=list(range(61001,61009))
SEQUENCES=dict(primary=['plus','minus','plus','minus','plus'],reordered=['plus','plus','minus','minus','plus'])

def load_pairs(eng):
    p=ROOT/f'local/scan_{eng.name}/{eng.name}_s{eng.task["editor_seed"]}/pairs.jsonl'
    return rows(p)

def load_state(pair):
    ck=torch.load(pair['state_path'],map_location='cpu',weights_only=True)
    return ck['bad'].cuda(),ck['good'].cuda(),ck['mask'].cuda()

def token_positions(eng,pair):
    def positions(history):
        text=history.get('input_text',render(pair['world'],history['start'],pair['template']));text=eng.wrap(text)
        found=list(re.finditer(r'(?:dated|event is) ([^.]+)\.',text));assert found
        span=found[0].span(1)
        tok=eng.tok(text,add_special_tokens=not eng.chat,return_offsets_mapping=True)
        return [i for i,(a,b) in enumerate(tok['offset_mapping']) if b>a and a<span[1] and b>span[0]]
    recipient=positions(pair['recipient_history']);donor=positions(pair['donor_history'])
    if recipient!=donor: return None
    return recipient

@torch.no_grad()
def fit_pca(pairs,path):
    n=0;total=moment=None
    for r in pairs:
        bad,good,m=load_state(r);x=(good.float()-bad.float())[m.bool()]
        if total is None:total=torch.zeros(x.shape[1],device=x.device);moment=torch.zeros(x.shape[1],x.shape[1],device=x.device)
        total+=x.sum(0);moment+=x.T@x;n+=len(x)
    if n<2:raise RuntimeError('Insufficient discovery pair tokens for PCA')
    cov=(moment-total[:,None]*total[None,:]/n)/(n-1)
    vals,vec=torch.linalg.eigh(cov);q=vec[:,-16:].flip(1).cpu()
    path.parent.mkdir(parents=True,exist_ok=True);torch.save(dict(q=q,values=vals[-16:].flip(0).cpu(),mean=(total/n).cpu(),worlds=[r['world_id'] for r in pairs],tokens=n),path)

def candidate_specs():
    return [dict(method=m,rank=k,alpha=a,name=f'{m}_k{k}_a{a}') for m in ('read','write','pca') for k in (1,4,8,16) for a in (.25,.5,1.0)] + [dict(method='token',alpha=a,name=f'token_a{a}') for a in (.25,.5,1.0)]

def get_patch(eng,pair,bad,good,mask,spec,pca):
    q=None;s=dict(spec)
    if s['method']=='read':q=basis(eng.ed[pair['operation']].v.weight,s['rank'])
    if s['method']=='write':q=basis(eng.ed[pair['operation']].u.weight.T,s['rank'])
    if s['method']=='pca':q=pca[:,:s['rank']].to(bad.device)
    if s['method']=='token':
        s['positions']=token_positions(eng,pair)
        if s['positions'] is None:raise RuntimeError('No reliable common semantic memory span')
    h,component,meta=patch(bad,good,mask,s,q)
    return h,component,s,meta

def random_component(pair,delta,mask,component,spec,seed):
    if spec['method']=='token':
        g=torch.Generator().manual_seed(seed+int(objsha(pair['world_id'])[:8],16));valid=mask[0].nonzero().flatten().cpu()
        positions=valid[torch.randperm(len(valid),generator=g)[:len(spec['positions'])]].tolist()
        candidate=torch.zeros_like(delta);candidate[:,positions]=delta[:,positions];n=candidate.norm()
        if float(n)<1e-7:raise RuntimeError('Random token position difference norm too small')
        return candidate*(component.norm()/n),dict(random_seed=seed,random_positions=positions,resamples=0)
    return matched_random(delta,mask,spec['rank'],component.norm(),seed)

@torch.no_grad()
def evaluate_condition(eng,pair,h,mask,name,spec,component,sequence_name,operations):
    started=time.monotonic();w=pair['world'];current=pair['current_state'];template=pair['template']
    c=eng.evaluate(h,mask,w,current,template);conf=eng.confidence(h,mask,render(w,current,template));step_success=[];sc=[];outputs=[];gold_states=[];state=h;target_score=None
    other=None
    if sequence_name=='primary' and len(operations)>=3:
        other_op='minus' if pair['operation']=='plus' else 'plus'
        other=eng.evaluate(eng.ed[other_op](h,mask),mask,w,advance('time',pair['current_state'],other_op),template)
    for op in operations:
        current=advance('time',current,op);gold_states.append(gold(w,current,template));state=eng.ed[op](state,mask)
        pred=eng.evaluate(state,mask,w,current,template);step_success.append(pred['success']);sc.append(pred['score']);outputs.append(pred['text'])
        if len(step_success)==1:target_score=eng.confidence(state,mask,render(w,current,template),competitor=render(w,pair['current_state'],template))
    result={k:v for k,v in pair.items() if k not in ('world','state_path','donor_next','recipient_next')}
    result.update(method_name=name,sequence_name=sequence_name,operation_sequence=operations,gold_states=gold_states,intervention_spec=spec,alpha=spec.get('alpha',1),effective_rank=spec.get('rank'),patched_positions=spec.get('positions','all_valid'),patch_norm=float(component.norm()),relative_patch_norm=float(component.norm()/(h.float()*mask[...,None]).norm().clamp_min(1e-12)),relative_patch_norm_denominator='patched valid-memory representation',C0=c['success'],exact_preservation=c['text']==pair['current_text'],step_successes=step_success,step_scores=sc,step_texts=outputs,current_prediction=c['text'],R1=bool(c['success'] and all(step_success[:1])),R3=bool(c['success'] and all(step_success[:3])) if len(operations)>=3 else None,R5=bool(c['success'] and all(step_success[:5])) if len(operations)>=5 else None,first_failure=0 if not c['success'] else next((i+1 for i,v in enumerate(step_success) if not v),None),current_target_score=conf,target_score=target_score,failure_reason=None if c['success'] and all(step_success) else 'parse/semantic/grammar/EOS failure; see step_scores',job_id=os.environ['SLURM_JOB_ID'],walltime=time.monotonic()-started)
    result.update(patched_position_count=len(spec['positions']) if 'positions' in spec else int(mask.sum()),feature_dimension=h.shape[-1],other_operation_success=other['success'] if other else None,other_operation_text=other['text'] if other else None)
    result['current_score']=c['score']
    return result

def criterion(xs):
    return (sum(r['R1'] for r in xs)/len(xs),sum(r['C0'] for r in xs)/len(xs),-sum(r['relative_patch_norm'] for r in xs)/len(xs))

@torch.no_grad()
def run(eng,config,folder):
    allpairs=load_pairs(eng);stage=config['stage'];mode=config['mode']
    pcafile=ROOT/f'local/pca/{eng.name}_s{eng.task["editor_seed"]}.pt'
    discovery=primary_pairs(allpairs,'discovery',80)
    if mode=='fit':
        if not pcafile.exists():fit_pca(discovery,pcafile)
        return dict(mode=mode,discovery_worlds=len(discovery),PCA_path=str(pcafile),PCA_sha256=sha(pcafile),no_test_interventions=True,resources=eng.resources())
    if mode=='discovery':
        fit_pca(discovery,pcafile);pairs=discovery[:16];specs=candidate_specs()
    elif mode=='validation':
        pairs=primary_pairs(allpairs,'validation',40);specs=read(ROOT/f'results/{eng.name}_discovery_shortlist.json')['methods']
    elif mode=='test':
        pairs=primary_pairs([r for r in allpairs if r['original_split']=='new'],'test',80);specs=read(ROOT/f'results/{eng.name}_method_lock.json')['methods']
    else:raise ValueError(mode)
    if not pcafile.exists():fit_pca(discovery,pcafile)
    pca=torch.load(pcafile,map_location='cpu',weights_only=True)['q']
    records=[];operators=[]
    for pi,pair in enumerate(pairs):
        pp=folder/'worlds'/pair['world_id'];done=pp/'complete.json'
        if done.exists():
            assert read(done)['task_hash']==eng.task['task_hash'];records.extend(rows(pp/'results.jsonl'));operators.extend(rows(pp/'operator.jsonl'));continue
        bad,good,mask=load_state(pair);delta=(good.float()-bad.float())*mask[...,None];outputs=[]
        controls=[dict(method=m,name=m,alpha=1) for m in ('bad','good','full','noop','self')]+[dict(method='global',alpha=a,name=f'global_a{a}') for a in (0,.25,.5,1.0)]
        conditions=[]
        for s in controls:
            h,component,actual,meta=get_patch(eng,pair,bad,good,mask,s,pca);conditions.append((h,component,actual,s['name']))
        for s in specs:
            h,component,actual,meta=get_patch(eng,pair,bad,good,mask,s,pca);conditions.append((h,component,actual,s['name']))
            if mode!='discovery':
                conditions.append((reverse(good,component,mask),-component,dict(actual,reverse=True),'reverse_'+s['name']))
                for seed in RANDOM_SEEDS:
                    rc,rm=random_component(pair,delta,mask,component,actual,seed)
                    rh=torch.where(mask.bool()[...,None],(bad.float()+rc).to(bad.dtype),bad)
                    conditions.append((rh,rc,dict(actual,random_control=True,**rm),f'random_{s["name"]}_{seed}'))
        for h,component,s,name in conditions:
            sequences=SEQUENCES if mode=='test' and (name in ('bad','good','full') or name==specs[0]['name'] or name.startswith('random_'+specs[0]['name']+'_') or name=='global_a0.5') else dict(primary=[pair['operation']])
            for sequence_name,ops in sequences.items():outputs.append(evaluate_condition(eng,pair,h,mask,name,s,component,sequence_name,ops))
        baseline={r['method_name']:r for r in outputs if r['sequence_name']=='primary'}
        assert baseline['bad']['C0'] and not baseline['bad']['R1'],'Qualification reproduction drift'
        assert baseline['full']['R1'] and baseline['good']['R1'],'Full donor sanity failed'
        assert baseline['full']['step_texts']==baseline['good']['step_texts'],'Full donor trajectory mismatch'
        for name in ('noop','self','global_a0'):
            assert baseline[name]['C0']==baseline['bad']['C0'] and baseline[name]['R1']==baseline['bad']['R1'] and baseline[name]['current_prediction']==baseline['bad']['current_prediction']
        opdata=dict(world_id=pair['world_id'],pair_id=pair['pair_id'],split=pair['split'],editor_seed=eng.task['editor_seed'],model=eng.name,**analyze(eng.ed,bad,good,mask,pair['operation']))
        jsonl(pp/'results.jsonl',outputs);jsonl(pp/'operator.jsonl',[opdata]);dump(done,dict(task_hash=eng.task['task_hash']))
        records.extend(outputs);operators.append(opdata)
        print(f'{mode} {pi+1}/{len(pairs)} records={len(outputs)}',flush=True)
    jsonl(folder/'results.jsonl',records);jsonl(folder/'operator.jsonl',operators)
    if mode in ('discovery','validation'):
        by=defaultdict(list)
        for r in records:by[r['method_name']].append(r)
        ordered=sorted(specs,key=lambda s:(tuple(-v for v in criterion(by[s['name']])) if by[s['name']] else (999,999,999),s.get('rank',0),s['name']))
        best=[]
        for s in ordered:
            if s['method'] not in [v['method'] for v in best]:best.append(s)
            if len(best)==2:break
        path=ROOT/f'results/{eng.name}_{"discovery_shortlist" if mode=="discovery" else "method_lock"}.json'
        report=dict(methods=best,selection_split=mode,n_worlds=len(pairs),seed=eng.task['editor_seed'],selection_rule='R1,C0,smaller relative norm,rank,name',PCA_path=str(pcafile),PCA_sha256=sha(pcafile),scores={name:dict(n=len(rs),R1=sum(r['R1'] for r in rs)/len(rs),C0=sum(r['C0'] for r in rs)/len(rs)) for name,rs in by.items()})
        if mode=='validation':
            main=best[0];local=by[main['name']];rand=[r for name,rs in by.items() if name.startswith('random_'+main['name']+'_') for r in rs]
            gain=sum(r['R1'] for r in local)/max(1,len(local))-sum(r['R1'] for r in rand)/max(1,len(rand))
            report.update(gate_passed=len(pairs)>=20 and sum(r['C0'] for r in local)/max(1,len(local))>=.95 and gain>=.1 and sum(r['R1'] for r in local)>=2,validation_R1_random_difference=gain,test_intervention_unread=True)
        dump(path,report)
    return dict(mode=mode,n_worlds=len(pairs),records=len(records),resources=eng.resources())
