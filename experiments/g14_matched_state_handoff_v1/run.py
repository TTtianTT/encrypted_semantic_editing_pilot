"""Zero-training two-edit inference. GPU entry point requires sbatch and srun."""
import argparse, time
import torch
from common_g14 import *
G13run=load_module('g13_readonly_editor_definition',G13/'run.py')

def chunks(xs):
    for i in range(0,len(xs),CFG['batch_size']):yield xs[i:i+CFG['batch_size']]
def observe(e,state,ws,offset):
    texts,ends,lens,seconds=e.decode(state['memory'],state['mask'])
    return [dict(observe_text(t,end,w,offset),generated_tokens=int(n)) for t,end,n,w in zip(texts,ends,lens,ws)],seconds
def encoded(e,texts):
    h,m,_=e.encode(texts);ids=e.batch(texts).input_ids
    return dict(memory=h,mask=m,input_ids=ids)
def state_id(state):return statehash(state)
def row_state(state,j):return {k:v[j:j+1] for k,v in state.items()}
def state_fields(state,j):
    st=row_state(state,j)
    return dict(input_state_hash=state_id(st),input_memory_hash=statehash({'memory':st['memory']}),mask_hash=statehash({'mask':st['mask']}),input_ids_hash=statehash({'input_ids':st['input_ids']}),input_length=int(st['mask'].sum()),input_token_ids=st['input_ids'][0].detach().cpu().tolist(),attention_mask=st['mask'][0].detach().cpu().tolist())

def produce(e,editors,ws):
    start=encoded(e,[render(w,frame(w,1)) for w in ws]);initial=state_id(start)
    states={'start':start};current={};decode_seconds=0
    for name in ['G']+CFG['R_methods']:
        states[name]=dict(memory=editors[name](start['memory'],start['mask']),mask=start['mask'],input_ids=start['input_ids'])
        assert state_id(start)==initial,'Producer mutated shared h_start/m'
        current[name],dt=observe(e,states[name],ws,0);decode_seconds+=dt
    states['E']=encoded(e,[render(w,frame(w,0)) for w in ws]);current['E'],dt=observe(e,states['E'],ws,0);decode_seconds+=dt
    return states,current,decode_seconds

def cohort_rows(states,current,ws,s,method):
    rows=[]
    for j,w in enumerate(ws):
        eq=torch.equal(states['G']['mask'][j],states[method]['mask'][j]);gate=current_gate(current['G'][j],current[method][j],eq)
        rows.append(dict(seed=s,R_method=method,split=w['split'],world_id=w['record_id'],**gate,producer_masks_equal=eq,natural_mask_equal=torch.equal(states['E']['mask'][j],states['G']['mask'][j]),natural_current_exact=current['E'][j]['exact'],natural_current_joint=current['E'][j]['joint']))
    return rows

def receiver_pair(e,input_state,receivers,ws):
    before=state_id(input_state);out={}
    for name,receiver in receivers.items():
        edited=dict(input_state,memory=receiver(input_state['memory'],input_state['mask']))
        out[name],_=observe(e,edited,ws,-1)
        assert state_id(input_state)==before,'Receiver changed immutable producer cache'
    return out

def evaluate(e,states,current,editors,ws,s,method,gates,checkpoint_shas):
    """Main cells have no encode call; only explicitly named reset controls encode."""
    receivers={'G':editors['G'],'R':editors[method]};rows=[];all_before={k:state_id(v) for k,v in states.items()}
    def save(mode,P,st,nexts,cur,reset_equal=None):
        for j,w in enumerate(ws):
            for Q in ['G','R']:
                o=nexts[Q][j];a=cur[j];row=dict(split=w['split'],world_id=w['record_id'],seed=s,R_method=method,producer=P,receiver=Q,mode=mode,checkpoint_sha256=checkpoint_shas['G' if Q=='G' else method],producer_checkpoint_sha256=checkpoint_shas['G' if P=='G' else method] if P!='E' else getattr(e,'model_hash','CPU_fake_encoder'),current_output=a['output'],current_gold=a['gold'],current_exact=a['exact'],current_joint=a['joint'],current_normal_end=a['normal_end'],current_parsed_facts=a['parsed_facts'],current_error_type=a['error_type'],matched=gates[j]['matched'],match_failures=gates[j]['failures'],natural_mask_equal=gates[j]['natural_mask_equal'],natural_current_exact=current['E'][j]['exact'],natural_current_joint=current['E'][j]['joint'],next_output=o['output'],next_gold=o['gold'],next_exact=o['exact'],next_joint=o['joint'],next_normal_end=o['normal_end'],parsed_facts=o['parsed_facts'],next_score=o['score'],error_type=o['error_type'],predicted_relative_date=o['predicted_relative_date'],gold_relative_date=o['gold_relative_date'],relative_date_delta_days=o['relative_date_delta_days'],two_step_joint=a['joint'] and o['joint'],two_step_exact=a['exact'] and o['exact'],input_unchanged=True,**state_fields(st,j))
                if reset_equal is not None:row.update(reset_equals_natural=reset_equal[j])
                rows.append(row)
    # Both Q receive exactly the same state for this producer, including mask.
    for P,name in [('G','G'),('R',method)]:
        save('latent',P,states[name],receiver_pair(e,states[name],receivers,ws),current[name])
    save('natural','E',states['E'],receiver_pair(e,states['E'],receivers,ws),current['E'])
    for P,name in [('G','G'),('R',method)]:
        st=encoded(e,[o['output'] for o in current[name]]) # actual free text, never gold
        equals=[all(torch.equal(st[k][j],states['E'][k][j]) for k in st) for j in range(len(ws))]
        for j in range(len(ws)):
            if gates[j]['matched']:assert equals[j],'Identical matched current text did not reproduce natural IDs/mask/memory'
        save('reencode',P,st,receiver_pair(e,st,receivers,ws),current[name],equals)
    assert {k:state_id(v) for k,v in states.items()}==all_before
    return rows

def checkpoint_models():
    z=json.loads((ROOT/'checkpoints_manifest.json').read_text())['models'];return z
def frozen_models(s):
    eds={}
    for name,z in checkpoint_models()[str(s)].items():
        assert digest(z['path'])==z['sha256']
        ed=G13run.Editor().cuda().float().eval();ed.load_state_dict(torch.load(z['path'],map_location='cuda',weights_only=True))
        for p in ed.parameters():p.requires_grad_(False);p.grad=None
        eds[name]=ed
    return eds

@torch.no_grad()
def reproduce(e,eds,s):
    history=json.loads((ROOT/'data/history_batches.json').read_text())['worlds']
    expected={(r['split'],'G' if r['method']=='T0' else r['method'],r['record_id'],r['step']):r for r in read(ROOT/'data/history_expected.jsonl') if r['seed']==s};checks=[];mismatches=[]
    for split,ws in history.items():
        start=encoded(e,[render(w,frame(w,1)) for w in ws])
        for name in ['G','F2','F3']:
            st=start
            for step in [1,2]:
                st=dict(st,memory=eds[name](st['memory'],st['mask']));out,_=observe(e,st,ws,1-step)
                for j,(w,o) in enumerate(zip(ws,out)):
                    old=expected[split,name,w['record_id'],step]
                    ok=o['output']==old['output'] and o['normal_end']==old['normal_end'] and o['score']==old['score'] and o['exact']==old['exact'] and int(st['mask'][j].sum())==old['input_length']
                    row=dict(seed=s,split=split,model=name,world_id=w['record_id'],step=step,passed=ok,output=o['output'],expected_output=old['output'],normal_end=o['normal_end'],input_length=int(st['mask'][j].sum()),joint=o['joint']);checks.append(row)
                    if not ok:mismatches.append(row)
    dump(ROOT/f'history_reproduction_s{s}.json',dict(passed=not mismatches,worlds_per_split=16,checks=checks,mismatches=mismatches,settings=CFG,batch_order_preserved=True,new_confirmation_included=False))
    assert not mismatches,'Unexplained G13 reproduction mismatch: stop new inference'
    print('historical reproduction passed',s,len(checks),flush=True)

@torch.no_grad()
def build_caches(e,eds,s,worlds,phase):
    result={};decode_time=0;began=time.monotonic()
    for split in CFG['world_counts']:
        ws=[w for w in worlds if w['split']==split];pieces=[];obs={k:[] for k in ['G','F3','F2','E']}
        for bw in chunks(ws):
            e.check(90);states,current,dt=produce(e,eds,bw);decode_time+=dt
            pieces.append({name:{k:v.detach().cpu() for k,v in st.items()} for name,st in states.items()})
            for name in obs:obs[name]+=current[name]
        merged={name:{k:torch.cat([p[name][k] for p in pieces]) for k in pieces[0][name]} for name in pieces[0]}
        path=ROOT/f'local/{phase}_s{s}_{split}_states.pt';path.parent.mkdir(parents=True,exist_ok=True);torch.save(merged,path)
        state_meta=[dict(world_id=w['record_id'],source=name,**state_fields(st,j),current=obs[name][j] if name!='start' else None) for name,st in merged.items() for j,w in enumerate(ws)]
        gates={method:cohort_rows(merged,obs,ws,s,method) for method in CFG['R_methods']}
        meta=dict(seed=s,split=split,phase=phase,cache_path=str(path),cache_sha256=digest(path),dtype='float32',full_token_memory=True,source_encoded_once_for_all_producers=True,states=state_meta,cohorts=gates,locked_before_any_receiver=True,world_order=[w['record_id'] for w in ws])
        dump(ROOT/f'data/{phase}_s{s}_{split}_states.json',meta);result[split]=(ws,merged,obs,gates,meta)
        print('current gates',phase,s,split,{m:sum(g['matched'] for g in gs) for m,gs in gates.items()},flush=True)
    # Both splits' current cohorts now persisted, before any second-step output.
    dump(ROOT/f'data/{phase}_s{s}_cohort_lock.json',dict(current_only=True,next_outputs_available=False,files={f'{split}':digest(ROOT/f'data/{phase}_s{s}_{split}_states.json') for split in result}))
    return result,dict(cache_seconds=time.monotonic()-began,current_decode_seconds=decode_time)

@torch.no_grad()
def evaluate_caches(e,eds,s,caches,phase):
    rows=[];start=time.monotonic();shas={k:v['sha256'] for k,v in checkpoint_models()[str(s)].items()}
    for split,(ws,states,current,gates,meta) in caches.items():
        for method in CFG['R_methods']:
            sub=[]
            for i in range(0,len(ws),16):
                e.check(90);st={name:{k:v[i:i+16].cuda() for k,v in a.items()} for name,a in states.items()};cur={name:v[i:i+16] for name,v in current.items()}
                sub+=evaluate(e,st,cur,eds,ws[i:i+16],s,method,gates[method][i:i+16],shas)
            assert len(sub)==len(ws)*10
            assert digest(meta['cache_path'])==meta['cache_sha256']
            write(ROOT/f'outputs/{phase}_{method}_s{s}_{split}.jsonl',sub);rows+=sub
            print('two-step evaluation',phase,s,method,split,len(sub),flush=True)
    return rows,time.monotonic()-start

@torch.no_grad()
def run(e,s,smoke):
    verify_lock();eds=frozen_models(s)
    assert not e.model.training and all(not m.training for m in e.model.modules())
    assert all(not ed.training and all(not p.requires_grad for p in ed.parameters()) for ed in eds.values())
    assert all(not p.requires_grad for p in e.model.parameters())
    before=dict(backbone=statehash(e.model.state_dict()),editors={k:statehash(v.state_dict()) for k,v in eds.items()})
    reproduce(e,eds,s)
    if smoke:
        ws=[w for batch in json.loads((ROOT/'data/history_batches.json').read_text())['worlds'].values() for w in batch];phase='smoke'
    else:
        assert json.loads((ROOT/'smoke_test.json').read_text())['passed'];ws=read(ROOT/'data/worlds.jsonl');phase='confirm'
    caches,timing=build_caches(e,eds,s,ws,phase);rows,seconds=evaluate_caches(e,eds,s,caches,phase);timing['receiver_evaluation_seconds']=seconds
    after=dict(backbone=statehash(e.model.state_dict()),editors={k:statehash(v.state_dict()) for k,v in eds.items()});assert after==before
    assert all(p.grad is None for ed in eds.values() for p in ed.parameters()) and all(p.grad is None for p in e.model.parameters())
    for _,merged,_,_,meta in caches.values():
        loaded=torch.load(meta['cache_path'],map_location='cpu',weights_only=True)
        assert {k:state_id(v) for k,v in merged.items()}=={k:state_id(v) for k,v in loaded.items()}
    if smoke:
        # Exact repeated cross replay, using the same frozen complete state.
        split=next(iter(caches));worlds,states,current,gates,meta=caches[split];st={n:{k:v[:16].cuda() for k,v in a.items()} for n,a in states.items()};cur={n:a[:16] for n,a in current.items()};again=evaluate(e,st,cur,eds,worlds[:16],s,'F3',gates['F3'][:16],{k:v['sha256'] for k,v in checkpoint_models()[str(s)].items()})
        first=[r for r in rows if r['R_method']=='F3' and r['split']==split];assert again==first
    denominators=[]
    for split,(worlds,states,current,gates,meta) in caches.items():
        for method in CFG['R_methods']:
            C={g['world_id'] for g in gates[method] if g['matched']}
            for P in ['G','R']:
                for Q in ['G','R']:
                    cell=[r for r in rows if r['split']==split and r['R_method']==method and r['mode']=='latent' and r['producer']==P and r['receiver']==Q]
                    assert len(cell)==len(worlds) and {r['world_id'] for r in cell if r['matched']}==C
                    denominators.append(dict(split=split,R_method=method,producer=P,receiver=Q,matched_n=len(C),raw_N=len(worlds),matched_k=sum(r['next_joint'] for r in cell if r['matched'])))
    audit=dict(passed=True,denominators=denominators,seed=s,phase=phase,zero_training=True,optimizer_created=False,backward_executed=False,frozen_before=before,frozen_after=after,caches_unchanged=True,cache_save_load_equal=True,current_gate_independent_of_next=True,input_state_hashes_verified=True,matched_reset_equals_natural=True,rows=len(rows),timing=timing,elapsed_seconds=time.monotonic()-e.start,gpu=torch.cuda.get_device_name(),gpu_total_memory=torch.cuda.get_device_properties(0).total_memory,peak_cuda_bytes=torch.cuda.max_memory_allocated(),job_id=os.environ['SLURM_JOB_ID'],array_job_id=os.environ.get('SLURM_ARRAY_JOB_ID'),array_task_id=os.environ.get('SLURM_ARRAY_TASK_ID'),start_epoch=e.start_epoch,end_epoch=time.time(),historical_worlds=32,new_worlds=0 if smoke else 320,cache_replay_equal=True if smoke else 'smoke passed before array')
    dump(ROOT/('smoke_test.json' if smoke else f'seed_s{s}_complete.json'),audit)
    print('G14 COMPLETE',phase,s,flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--smoke',action='store_true');p.add_argument('--seed-index',type=int);a=p.parse_args()
    assert os.environ.get('SLURM_JOB_ID') and os.environ.get('SLURM_STEP_ID'),'sbatch plus srun required'
    from engine import Engine
    begin_epoch=time.time();e=Engine();e.start_epoch=begin_epoch;e.limit=float(os.environ['G14_WALL_SECONDS']);assert e.kw=={k:CFG[k] for k in ['max_new_tokens','do_sample','num_beams','forced_eos_token_id']}
    s=42 if a.smoke else json.loads((ROOT/'runs_manifest.json').read_text())['array_mapping'][a.seed_index]['seed']
    run(e,s,a.smoke)
