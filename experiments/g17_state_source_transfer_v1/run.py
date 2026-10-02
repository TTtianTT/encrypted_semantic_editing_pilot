"""Zero-training Slurm-only frozen full-state evaluation; no optimizer/backward."""
import argparse,time
import torch
from common_g17 import *
# Reuse unchanged historical full-state and scoring interfaces; old globals/files read-only.
base=load_module('g17_readonly_g15_runtime',G15/'run.py')
Editor=base.Editor;encode=base.encode;observe=base.observe;edit=base.edit;chunks=base.chunks;state_fields=base.state_fields
engmod=load_module('g17_unchanged_bart_engine',V3/'engine.py')
def require_allocation():
    assert os.environ.get('SLURM_JOB_ID') and os.environ.get('SLURM_STEP_ID'),'sbatch allocation + srun step required'
def load_models(seed):
    mapping=json.loads((ROOT/'checkpoints_manifest.json').read_text())['models'][str(seed)];eds={}
    for role,z in mapping.items():
        assert digest(z['path'])==z['sha256'],role
        ed=Editor().cuda().float().eval();ed.load_state_dict(torch.load(z['path'],map_location='cuda',weights_only=True))
        for p in ed.parameters():p.requires_grad_(False);p.grad=None
        eds[role]=ed
    assert all(not ed.training and all(not p.requires_grad for p in ed.parameters()) for ed in eds.values())
    assert len({p.data_ptr() for ed in eds.values() for p in ed.parameters()})==15
    return eds,mapping
def frozen_hashes(e,eds):return dict(ED=statehash(e.model.state_dict()),**{k:statehash(v.state_dict()) for k,v in eds.items()})
def immutable_apply(ed,st):
    before=statehash(st);out=edit(ed,st);assert statehash(st)==before
    assert out['mask'] is st['mask'] and out['input_ids'] is st['input_ids']
    return out

def make_cache(e,eds,ws,seed,split,a,tag):
    path=ROOT/f'local/{tag}_s{seed}_{split}_a{a}.pt';mp=ROOT/f'cache_manifests/{tag}_s{seed}_{split}_a{a}.json'
    if mp.exists():
        meta=json.loads(mp.read_text());assert digest(path)==meta['cache_sha256'];assert meta['world_ids']==[w['record_id'] for w in ws];assert meta['scientific_lock_sha256']==digest(ROOT/'scientific_lock.json')
        return torch.load(path,map_location='cpu',weights_only=False),meta
    began=time.monotonic();pieces=[];obs=collections.defaultdict(list);gates=[];metadata=collections.defaultdict(list);timing=collections.Counter()
    for bw in chunks(ws,16):
        e.check(60);t=time.monotonic();start=encode(e,[render(w,frame(w,a+1)) for w in bw]);nat=encode(e,[render(w,frame(w,a)) for w in bw]);timing['encode']+=time.monotonic()-t
        st=dict(start=start,E=nat);t=time.monotonic();natural,_=observe(e,nat,bw,a);obs['E']+=natural;timing['current_decode']+=time.monotonic()-t
        for name in CFG['producers']:
            t=time.monotonic();st[name]=immutable_apply(eds[name],start);current,_=observe(e,st[name],bw,a);obs[name]+=current;timing['produce_and_decode']+=time.monotonic()-t
        for j,w in enumerate(bw):
            eq=all(torch.equal(st[n]['mask'][j],start['mask'][j]) for n in CFG['producers']);assert eq
            gt={name:current_gate(obs[name][-len(bw)+j],natural[j]) for name in CFG['producers']}
            gates.append(dict(world_id=w['record_id'],cohorts=gt,producer_masks_equal=eq,natural_mask_equal=torch.equal(nat['mask'][j],start['mask'][j]),natural_length=int(nat['mask'][j].sum()),edited_length=int(start['mask'][j].sum())))
        for name,v in st.items():metadata[name]+=[state_fields(v,j) for j in range(len(bw))]
        pieces.append({n:{k:v.detach().cpu() for k,v in s.items()} for n,s in st.items()})
    states={n:{k:torch.cat([p[n][k] for p in pieces]) for k in pieces[0][n]} for n in pieces[0]}
    assert all(v['memory'].dtype==torch.float32 for v in states.values())
    payload=dict(states=states,current=dict(obs),gates=gates,metadata=dict(metadata),world_ids=[w['record_id'] for w in ws])
    path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_suffix('.tmp');torch.save(payload,tmp);tmp.replace(path)
    meta=dict(seed=seed,split=split,anchor=a,world_ids=payload['world_ids'],cache_path=str(path),cache_sha256=digest(path),tensor_hashes={k:statehash(v) for k,v in states.items()},source_checkpoint_hashes={n:statehash(eds[n].state_dict()) for n in CFG['producers']},scientific_lock_sha256=digest(ROOT/'scientific_lock.json'),complete_FP32_memory_mask_ids=True,cohort_before_any_receiver_next=True,cohorts={n:[g['world_id'] for g in gates if g['cohorts'][n]['matched']] for n in CFG['producers']},gates=gates,cache_seconds=time.monotonic()-began,timing_seconds=dict(timing))
    dump(mp,meta);print('CACHE',seed,split,a,{k:len(v) for k,v in meta['cohorts'].items()},flush=True)
    return payload,meta

def record(seed,split,a,w,kind,producer,receiver,o,current=None,matched=False,fields=None,mapping=None,**extra):
    z=dict(seed=seed,split=split,world_id=w['record_id'],anchor=a,status=w['record_status'],perspective='first',kind=kind,mode=kind,producer=producer,receiver=receiver,matched=matched,raw_world_denominator=160,**o,**(fields or {}),**extra)
    if current is not None:z.update(current=current,current_output=current['output'],current_gold=current['gold'],current_exact=current['exact'],current_joint=current['joint'],current_EOS=current['normal_end'])
    if kind not in ['current','self_first']:z.update(next_output=o['output'],next_gold=o['gold'],next_joint=o['joint'],next_exact=o['exact'],next_EOS=o['normal_end'])
    if mapping:z['checkpoint_sha256']={n:mapping[n]['sha256'] for n in {producer,receiver} if n in mapping}
    return z

def evaluate(e,eds,mapping,payload,ws,seed,split,a):
    began=time.monotonic();rows=[];timing=collections.Counter();states=payload['states'];gates=payload['gates'];cur=payload['current'];md=payload['metadata']
    for ix in chunks(list(range(len(ws))),16):
        e.check(60);bw=[ws[i] for i in ix];st={n:{k:v[ix].cuda() for k,v in s.items()} for n,s in states.items()};before={n:statehash(s) for n,s in st.items()}
        for n in ['E']+CFG['producers']:
            for j,i in enumerate(ix):rows.append(record(seed,split,a,ws[i],'current',n,'',cur[n][i],cur[n][i],gates[i]['cohorts'].get(n,{}).get('matched',False),md[n][i],mapping,natural_mask_equal=gates[i]['natural_mask_equal'],producer_masks_equal=True))
        natural={};cross={}
        for q in CFG['natural_receivers']:
            t=time.monotonic();out=immutable_apply(eds[q],st['E']);os_,_=observe(e,out,bw,a-1);timing['natural']+=time.monotonic()-t;natural[q]=os_
            for j,i in enumerate(ix):rows.append(record(seed,split,a,ws[i],'natural','E',q,os_[j],cur['E'][i],False,md['E'][i],mapping))
        for s in CFG['producers']:
            for q in CFG['receivers']:
                t=time.monotonic();out=immutable_apply(eds[q],st[s]);os_,_=observe(e,out,bw,a-1);timing['handoff']+=time.monotonic()-t;cross[s,q]=os_
                for j,i in enumerate(ix):rows.append(record(seed,split,a,ws[i],'handoff',s,q,os_[j],cur[s][i],gates[i]['cohorts'][s]['matched'],md[s][i],mapping,full2=full_success(cur[s][i],os_[j]),gate_and_next=gates[i]['cohorts'][s]['matched'] and os_[j]['joint'],cohort_failures=gates[i]['cohorts'][s]['failures'],natural_mask_equal=gates[i]['natural_mask_equal'],natural_joint=natural[q][j]['joint']))
        for s in CFG['producers']:
            texts=[cur[s][i]['output'] for i in ix];all_same=texts==[render(w,frame(w,a)) for w in bw];t=time.monotonic()
            reset=st['E'] if all_same else encode(e,texts)
            reset_md=md['E'] if all_same else [state_fields(reset,j) for j in range(len(ix))]
            for j,i in enumerate(ix):
                if gates[i]['cohorts'][s]['matched']:
                    assert all(torch.equal(reset[k][j],st['E'][k][j]) for k in ['memory','mask','input_ids'])
            for q in CFG['receivers']:
                os_=natural[q] if all_same else observe(e,immutable_apply(eds[q],reset),bw,a-1)[0]
                for j,i in enumerate(ix):rows.append(record(seed,split,a,ws[i],'reset',s,q,os_[j],cur[s][i],gates[i]['cohorts'][s]['matched'],md['E'][i] if all_same else reset_md[j],mapping,full2=full_success(cur[s][i],os_[j]),reset_uses_actual_output=True,duplicate_natural_control=all_same,reset_natural_equal_on_C=gates[i]['cohorts'][s]['matched'],original_edited_mask_sha256=md[s][i]['mask_sha256'],natural_mask_equal=gates[i]['natural_mask_equal']))
            timing['reset']+=time.monotonic()-t
        for q in CFG['natural_receivers']:
            t=time.monotonic()
            if q in ['P','G']:first=[cur[q][i] for i in ix];h1=st[q];first_md=[md[q][i] for i in ix]
            else:
                h1=immutable_apply(eds[q],st['start']);first,_=observe(e,h1,bw,a);first_md=[state_fields(h1,j) for j in range(len(ix))]
            second=cross['P','P'] if q=='P' else observe(e,immutable_apply(eds[q],h1),bw,a-1)[0]
            timing['self']+=time.monotonic()-t
            for j,i in enumerate(ix):
                rows.append(record(seed,split,a,ws[i],'self_first',q,q,first[j],first[j],False,md['start'][i],mapping))
                full=full_success(first[j],second[j]);fail=1 if not first[j]['joint'] else 2 if not second[j]['joint'] else None
                rows.append(record(seed,split,a,ws[i],'self_second',q,q,second[j],first[j],False,first_md[j],mapping,full2=full,first_failure=fail))
        assert before=={n:statehash(s) for n,s in st.items()},'generation/editor modified complete cache input'
    return rows,dict(total_seconds=time.monotonic()-began,phase_seconds=dict(timing),all_cached_inputs_unchanged=True,reset_on_C_identical_to_natural=True)

@torch.no_grad()
def smoke(e,eds,mapping):
    histories=json.loads((ROOT/'data/history_batches.json').read_text());expected=read(ROOT/'data/history_expected.jsonl.gz');checks=[];through=[]
    by={(r['world_id'],r['method'],r['kind'],r.get('source')):r for r in expected}
    for sp,ws in histories.items():
        payload,meta=make_cache(e,eds,ws,42,sp,0,'smoke_v2');rows,metrics=evaluate(e,eds,mapping,payload,ws,42,sp,0)
        for r in rows:
            if r['kind'] not in ['self_first','self_second','handoff','natural'] or r['receiver'] not in ['P','N','F']:continue
            method={'P':'P','N':'N-final','F':'F-final'}[r['receiver']]
            kind='fixed' if r['kind'] in ['handoff','natural'] else r['kind'];source=r['producer'] if kind=='fixed' else 'Q'
            old=by[r['world_id'],method,kind,source]
            for k in ['output','normal_end','score','exact','joint']:assert r[k]==old[k],(r['world_id'],method,kind,source,k)
            checks.append(dict(world_id=r['world_id'],split=sp,method=method,kind=kind,source=source,passed=True))
        # Same FP32 state, fixed decoder settings, complete input unchanged before/after replay.
        bs={k:v[:16].cuda() for k,v in payload['states']['P'].items()};h=statehash(bs)
        o1=observe(e,immutable_apply(eds['F'],bs),ws[:16],-1)[0];o2=observe(e,immutable_apply(eds['F'],bs),ws[:16],-1)[0];assert o1==o2 and statehash(bs)==h
        write(ROOT/f'smoke_{sp}.jsonl.gz',rows);through.append(dict(split=sp,worlds=len(ws),cache_seconds=meta['cache_seconds'],**metrics))
    assert len(checks)==len(expected)==576
    dump(ROOT/'smoke_test.json',dict(passed=True,seed=42,new_confirmation_worlds_not_accessed=True,history_checks=checks,throughput=through,frozen_models=True,cache_replay_equal=True,actual_reset_control_checked=True,gpu=torch.cuda.get_device_name(),peak_cuda_bytes=torch.cuda.max_memory_allocated(),elapsed_seconds=time.monotonic()-e.start))
    print('G17 SMOKE PASS',len(checks),through,flush=True)

@torch.no_grad()
def main_eval(e,eds,mapping,seed):
    assert json.loads((ROOT/'smoke_test.json').read_text())['passed'];done=ROOT/f'seed_s{seed}_complete.json'
    if done.exists():
        z=json.loads(done.read_text());assert all(digest(ROOT/p)==h for p,h in z['output_sha256'].items());return
    outputs={};metrics=[];worlds=read(ROOT/'data/worlds.jsonl')
    for sp in CFG['splits']:
        ws=[w for w in worlds if w['split']==sp]
        for a in CFG['anchors']:
            path=ROOT/f'outputs/s{seed}_{sp}_a{a}.jsonl.gz';mp=path.with_suffix('.meta.json')
            if path.exists() and mp.exists():
                z=json.loads(mp.read_text());assert digest(path)==z['sha256'] and z['scientific_lock_sha256']==digest(ROOT/'scientific_lock.json');outputs[str(path.relative_to(ROOT))]=z['sha256'];continue
            payload,meta=make_cache(e,eds,ws,seed,sp,a,'confirm');rows,m=evaluate(e,eds,mapping,payload,ws,seed,sp,a)
            assert digest(meta['cache_path'])==meta['cache_sha256']
            assert len(rows)==160*34 #4 current+4natural+9handoff+9reset+8self
            write(path,rows);sha=digest(path);dump(mp,dict(sha256=sha,scientific_lock_sha256=digest(ROOT/'scientific_lock.json'),seed=seed,split=sp,anchor=a,records=len(rows),cache_sha256=meta['cache_sha256'],**m))
            outputs[str(path.relative_to(ROOT))]=sha;metrics.append(dict(split=sp,anchor=a,**m));print('EVALUATED',seed,sp,a,m['total_seconds'],flush=True)
    dump(done,dict(passed=True,zero_training=True,seed=seed,output_sha256=outputs,metrics=metrics,job_id=os.environ['SLURM_JOB_ID'],array_job_id=os.environ.get('SLURM_ARRAY_JOB_ID'),array_task_id=os.environ.get('SLURM_ARRAY_TASK_ID'),gpu=torch.cuda.get_device_name(),peak_cuda_bytes=torch.cuda.max_memory_allocated(),elapsed_seconds=time.monotonic()-e.start))

def main():
    p=argparse.ArgumentParser();p.add_argument('--smoke',action='store_true');p.add_argument('--seed-index',type=int);args=p.parse_args();require_allocation();verify_lock()
    seed=42 if args.smoke else CFG['seeds'][args.seed_index];base.seed_all(seed)
    e=engmod.Engine();assert all(not p.requires_grad for p in e.model.parameters()) and not e.model.training
    eds,mapping=load_models(seed);before=frozen_hashes(e,eds)
    with torch.no_grad():
        if args.smoke:smoke(e,eds,mapping)
        else:main_eval(e,eds,mapping,seed)
    after=frozen_hashes(e,eds);assert before==after
    assert all(p.grad is None for ed in [e.model]+list(eds.values()) for p in ed.parameters())
    dump(ROOT/f'frozen_{"smoke" if args.smoke else "s"+str(seed)}.json',dict(passed=True,before=before,after=after,all_eval=True,all_requires_grad_false=True,no_gradient_or_optimizer=True,job_id=os.environ['SLURM_JOB_ID'],step_id=os.environ['SLURM_STEP_ID']))
if __name__=='__main__':main()
