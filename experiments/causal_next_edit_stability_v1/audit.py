"""CPU resource/data audit, deterministic new worlds, and Slurm smoke acceptance."""
import argparse
import itertools
import platform
import random
import subprocess
import sys
from datetime import date,timedelta
from .common import *

def prepare():
    import torch,transformers,yaml
    sys.path.insert(0,str(SOURCE))
    from semantics import render,states
    old=rows(SOURCE/'data/time/worlds.jsonl'); signatures={render(w,s,0) for w in old for s in states('time')}
    candidate=[dict(w,original_split=w['split'],mechanism_split=split(w['world_id']),new_generated=False) for w in old if w['split']!='train']
    slots=list(itertools.product(['book','lamp','ticket','parcel','sensor','cup','box','key'],['blue','red','green','white','black'],range(1,10),['planned','completed','cancelled']))
    rng=random.Random(2026100401);rng.shuffle(slots)
    for obj,col,quantity,status in slots:
        w=dict(old[0],object=obj,color=col,quantity=quantity,status=status,world_id=f'new_time_{len(candidate)-56:04d}',split='new')
        if render(w,0,0) in signatures:continue
        w.update(original_split='new',mechanism_split=split(w['world_id']),new_generated=True)
        candidate.append(w)
        if len(candidate)==256:break
    assert len(candidate)==256 and len({render(w,0,0) for w in candidate})==256
    assert not ({render(w,0,0) for w in candidate if w['new_generated']} & signatures)
    jsonl(ROOT/'configs/worlds.jsonl',candidate)
    models=read(SOURCE/'model_manifest.json');checks=[]
    for model in ('bart','t5gemma'):
        for name,info in models[model]['files'].items():
            p=Path(models[model]['directory'])/name
            checks.append(dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size,expected_sha256=info['sha256']))
            assert checks[-1]['sha256']==info['sha256']
    editors=[]
    for model in ('bart','t5gemma'):
        for seed in (42,43,44):
            idx=read(SOURCE/f'runs/formal/{model}_time_s{seed}/checkpoint_index.json')['P']
            p=Path(idx['path']);assert sha(p)==idx['sha256']
            editors.append(dict(model=model,seed=seed,condition='P',path=str(p),sha256=sha(p),metadata=idx))
    manifest=dict(run_id=RUN_ID,base_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),reference='0b73738',
        original_branch=subprocess.check_output(['git','-C',str(ORIGINAL),'branch','--show-current'],text=True).strip(),
        original_status=subprocess.check_output(['git','-C',str(ORIGINAL),'status','--short'],text=True),
        branches=subprocess.check_output(['git','for-each-ref','--format=%(refname:short) %(objectname) %(subject)','refs/remotes/origin'],text=True),
        python=sys.version,python_executable=sys.executable,torch=torch.__version__,transformers=transformers.__version__,cuda_build=torch.version.cuda,
        dependencies=subprocess.check_output([sys.executable,'-m','pip','freeze'],text=True).splitlines(),models={k:models[k] for k in ('bart','t5gemma')},verified_backbone_files=checks,editors=editors,
        data_sha=sha(ROOT/'configs/worlds.jsonl'),candidate_worlds=256,new_generated_worlds=200,training_worlds_excluded=96,
        split_counts={s:sum(w['mechanism_split']==s for w in candidate) for s in ('discovery','validation','test')},
        source_root=str(SOURCE),artifact_root=str(ARTIFACT),source_backend_sha=sha(SOURCE/'backend.py'),source_parser_sha=sha(SOURCE/'evaluator.py'),
        slurm=dict(partition='B300q',gres='gpu:1',account=None,qos='normal',environment=str(ORIGINAL/'.venv'),source_script=str(SOURCE/'job.slurm'),global_limit=2,budget=40),
        related_newer_branch='experiment/current-source-compatibility-v1 at aea8310: source reconstruction/repair training, not localized pre-edit causal patching',
        condition_selection='P/time: all seeds admitted and current-correct next failures in latest coverage; fixed before intervention results')
    dump(ROOT/'run_manifest.json',manifest)
    text='''# Artifact audit\n\nBase: 0b73738cf552e1ec29aa7a5db1eb1ee703804b66. Branch: experiment/causal-next-edit-stability-v1. Original dirty files and worktrees are retained (exact snapshot in run_manifest.json). Fetched origin; no newer causal/patching branch found. Newer current-source compatibility branch aea8310 is audited separately; it retrains receiver editors and is not this localized intervention.\n\nRead source README, RESULTS, DATA_SPEC, backend, evaluator, train, checkpoints_index, config, job/submit scripts; source paths/hashes and all actual backbone/editor file checks are in run_manifest.json. Frozen facebook/bart-base FP32 and original google/t5gemma-2b-2b-ul2-it BF16, HF SDPA, eval, max_new_tokens160, deterministic greedy, original tokenizer/chat wrapper/caps192/256. No backbone/editor training. Historical P checkpoint is the full-core-dev NLL selected original atomic editor (600 updates, seeds42/43/44); 96 train worlds, 24 old dev, 32 old test. All training world content excluded; 200 new worlds use same slots/rendering and disjoint core content. Old test exposure during discovery is disclosed through original_split and never relabelled template OOD.\n\nNatural N is E(render(world,state)); edited E is a deterministic recorded operation history over the original source-position memory and mask. R is exactly one E(Decode(edited)) and labelled reencode, never an encoder-internal history. All histories stay grouped by world across seeds. Time legal states−3..3, plus decrements relative day and minus increments it; illegal boundaries stop gold construction. Original independent parser defines success as parsed target+preservation+scope+grammar+normal EOS. Other domains retain source semantics and parser, but are outside the selected time condition.\n\nEditor: z=h.float(); delta=b+u(v(z)); output=(z+delta*mask[...,None]).to(h.dtype). v.weight rank×d, u.weight d×rank, no activation, normalization, clipping or token mixing in inference; identity residual, scale1, bias at each valid token, padding identity. Training clipping is not inference clipping. Difference propagation is affine in FP32 but BF16 casts produce rounding, which must be measured rather than called exact. Read subspace row(v), write subspace col(u). Bias cancels analytically in differences, but not in absolute state/margin.\n\nExisting environment Python3.12.3, torch2.11.0+cu128, transformers5.16.1; no upgrades. CUDA/GPU runtime inspected only inside Slurm. B300q/gpu:1, blank account/default normal QoS verified from historical sacct; script uses existing .venv and srun. New data/configs/small results in Git; large CPU state caches, logs and complete per-example results under ignored local/.\n\nS0 runtime acceptance and peak GPU memory will be linked in results; missing/unexecuted checks are not assumed passed.\n'''
    atomic_text(ROOT/'ARTIFACT_AUDIT.md',text)
    print(manifest['split_counts'])

def smoke(eng,worlds):
    import torch
    from .adapter import render,gold,native_hook
    from .state_patching import patch
    output=[]
    for w in worlds[:16]:
        good,m=eng.encode([render(w,0,0)]);base,mb=eng.encode([render(w,1,0)]);bad=eng.ed['plus'](base,mb)
        assert torch.equal(m,mb),'Smoke local pair mask mismatch'
        for name,h in [('current',bad),('next',eng.ed['plus'](bad,m))]:
            original_generate=eng.model.generate;captured=[]
            def capture(*args,**kwargs):
                ids=original_generate(*args,**kwargs);captured.append(ids);return ids
            eng.model.generate=capture
            try: orig=eng.decode(h,m)
            finally: eng.model.generate=original_generate
            ids=eng.ids(h,m);assert torch.equal(ids,captured[0])
            new=eng.tok.batch_decode(ids,skip_special_tokens=True,clean_up_tokenization_spaces=False)[0]
            assert orig[0]['text']==new
            logits,_=eng.logits(h,m,render(w,0 if name=='current' else -1,0))
            hook_before=len(eng.model.get_decoder()._forward_hooks)
            with native_hook(eng.model.get_decoder(),lambda module,args,out:out):
                hooked,_=eng.logits(h,m,render(w,0 if name=='current' else -1,0)); hooked_ids=eng.ids(h,m)
            assert len(eng.model.get_decoder()._forward_hooks)==hook_before
            assert torch.equal(ids,hooked_ids)
            for spec in (dict(method='self'),dict(method='editor',alpha=0),dict(method='noop')):
                hp,delta,_=patch(h,h,m,spec); lp,_=eng.logits(hp,m,render(w,0 if name=='current' else -1,0))
                assert torch.equal(eng.ids(hp,m),ids) and torch.equal(lp,logits)
            diff=(logits-hooked).abs(); assert torch.equal(logits,hooked)
            output.append(dict(world_id=w['world_id'],position=name,greedy_tokens_equal=True,semantic_judgment_equal=True,logit_max=float(diff.max()),logit_mean=float(diff.mean()),dtype=str(h.dtype),tolerance=0,hook_removed=True))
        calls=[]
        with native_hook(eng.model.get_encoder(),lambda *args:calls.append(1)):
            eng.ids(bad,m);eng.logits(bad,m,render(w,0,0))
        assert not calls
        full,delta,_=patch(bad,good,m,dict(method='full'))
        assert torch.equal(full[m.bool()],good[m.bool()])
        assert torch.equal(full[~m.bool()],bad[~m.bool()])
        assert torch.equal(eng.ids(eng.ed['plus'](full,m),m),eng.ids(eng.ed['plus'](good,m),m))
    return dict(passed=True,worlds=len(worlds[:16]),checks=output,encoder_forward_calls=0,full_donor_next_tokens_equal=True,padding_excluded=True,diagnostic_use_cache=False,resources=eng.resources())

def make_stage(stage,model_seeds,walltime,extra=None):
    if any((ROOT/f'configs/{stage}{suffix}.json').exists() for suffix in ('','_tasks')):
        raise FileExistsError('Historical stage namespace exists; choose a fresh stage name')
    c=dict(stage=stage,partition='B300q',gpus=1,walltime=walltime,walltime_hours=sum(int(v)*f for v,f in zip(walltime.split(':'),(1,1/60,1/3600))),**(extra or {}))
    cp=ROOT/f'configs/{stage}.json';dump(cp,c)
    aud=read(ROOT/'run_manifest.json');tasks=[]
    for model,seed in model_seeds:
        ck=next(e for e in aud['editors'] if e['model']==model and e['seed']==seed)
        t=dict(stage=stage,model=model,model_id=aud['models'][model]['model_id'],editor_seed=seed,editor_condition='P',checkpoint=ck['path'],checkpoint_hash=ck['sha256'],world_shard='all',method='grouped',config_hash=sha(cp),data_hash=sha(ROOT/'configs/worlds.jsonl'),output_path=f'local/{stage}/{model}_s{seed}')
        t['task_hash']=objsha(dict(t,code_hash=code_hash()));tasks.append(t)
    mp=ROOT/f'configs/{stage}_tasks.json';dump(mp,dict(stage=stage,config_hash=sha(cp),code_hash=code_hash(),tasks=tasks))
    print(str(cp),str(mp))

def qualification_diagnostics(eng,worlds,folder):
    import torch
    from .adapter import reconstruct,render,advance
    from .pairs import HISTORIES
    from .operator_analysis import analyze
    output=[];algebra=[]
    for w in [w for w in worlds if w['mechanism_split']=='discovery'][:16]:
        states={}
        for hist in HISTORIES:
            h,m=reconstruct(eng,w,hist,0);states[hist['id']]=(h,m,eng.evaluate(h,m,w,0,0))
        hn,mn=eng.encode([render(w,0,0)]);states['N_current']=(hn,mn,eng.evaluate(hn,mn,w,0,0))
        first=states[HISTORIES[0]['id']][2]
        hr,mr=eng.encode([first['text']]);states['R_once']=(hr,mr,eng.evaluate(hr,mr,w,0,0))
        natural=states['N_current'][2]['text']
        for name,(h,m,pred) in states.items():
            nxt={op:eng.evaluate(eng.ed[op](h,m),m,w,advance('time',0,op),0) for op in ('plus','minus')}
            output.append(dict(world_id=w['world_id'],split='discovery',history=name,current=pred,current_confidence=eng.confidence(h,m,render(w,0,0),competitor=render(w,1,0)),next=nxt,mask_length=int(m.sum()),mask_hash=objsha(m.cpu().tolist()),raw_equal_to_natural=pred['text']==natural,strip_equal_to_natural_diagnostic_only=pred['text'].strip()==natural.strip(),strip_used_for_qualification=False))
        hb,mb,_=states[HISTORIES[0]['id']]
        if torch.equal(mb,mn):algebra.append(dict(world_id=w['world_id'],model=eng.name,editor_seed=eng.task['editor_seed'],analysis_source='qualification-only, raw-text-unmatched states; excluded from primary intervention statistics',**analyze(eng.ed,hb,hn,mb,'plus')))
    jsonl(folder/'qualification_diagnostics.jsonl',output);jsonl(folder/'operator_diagnostic.jsonl',algebra)
    return dict(worlds=16,records=len(output),no_interventions=True,resources=eng.resources())

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--prepare',action='store_true');p.add_argument('--stage');p.add_argument('--models',default='bart:42');p.add_argument('--walltime',default='00:15:00');a=p.parse_args()
    if a.prepare:prepare()
    if a.stage:make_stage(a.stage,[(m,int(s)) for m,s in (v.split(':') for v in a.models.split(','))],a.walltime)
