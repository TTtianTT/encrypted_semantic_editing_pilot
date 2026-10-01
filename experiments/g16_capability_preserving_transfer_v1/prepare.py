"""CPU-only preparation reusing G14's enumerated history; never infers a model."""
import subprocess
from datetime import datetime, timezone
from common_g16 import *

def legal_texts(w):
    return {norm(render(w,frame(w,d,p))) for d in range(-4,5) for p in ['first','third'] if valid(w,[frame(w,d,p)])}

def history():
    audit = json.loads((G15/'data/manifest.json').read_text())
    prep = load_module('g13_history_extract_readonly',G13/'prepare.py')
    old = {}; texts = set(); sources = []; unavailable = []
    for src in audit['historical_sources']:
        try:
            raw = subprocess.check_output(['git','cat-file','blob',src['git_blob']],cwd=REPO) if 'git_blob' in src else Path(src['absolute_path']).read_bytes()
            assert hashlib.sha256(raw).hexdigest() == src['sha256']
        except (OSError,subprocess.CalledProcessError) as exc:
            unavailable.append(dict(source=src,error=str(exc))); continue
        rs = [json.loads(l) for l in raw.decode().splitlines() if l.strip()] if src['path'].endswith('.jsonl') else [json.loads(raw)]
        for r in rs:
            for w in prep.extract_worlds(r): old[key(w)] = w
            texts.update(prep.text_fields(r))
        sources.append(src)
    for path in [G13/'data/worlds.jsonl',G14/'data/worlds.jsonl',G15/'data/worlds.jsonl']:
        rs=read(path)
        for w in rs: old[key(w)]=w
        sources.append(dict(path=str(path.relative_to(REPO)),absolute_path=str(path),sha256=digest(path),world_occurrences=len(rs),supplement='G13/G14/G15 explicit worlds'))
    for w in old.values():
        if 'template_family' in w: texts.update(legal_texts(w))
    return old,texts,sources,unavailable

def main():
    assert json.loads((ROOT/'g15_audit.json').read_text())['passed']
    assert not (ROOT/'data/lock.json').exists(),'Never overwrite a locked G16 experiment'
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip()
    assert head==CFG['baseline_commit']
    oldcfg=json.loads((G15/'configs/main.json').read_text())
    for k in ['optimizer','learning_rate','weight_decay','gradient_clip','gradient_accumulation','source_length','max_new_tokens','do_sample','num_beams','forced_eos_token_id','dtype','tf32','rank']:
        assert CFG[k]==oldcfg[k],k
    oldmap=json.loads((G15/'checkpoints_manifest.json').read_text())
    for z in oldmap['backbone']['actual_files']: assert digest(z['file'])==z['sha256']
    models={}
    for s in CFG['seeds']:
        models[str(s)]={}
        for role,oldrole in [('P','P'),('G','G'),('U','U')]:
            z=oldmap['models'][str(s)][oldrole]; p=REPO/z['repo_path']; assert digest(p)==z['sha256']
            models[str(s)][role]=dict(path=str(p),repo_path=z['repo_path'],sha256=z['sha256'],G15_mapping_sha256=digest(G15/'checkpoints_manifest.json'),step=200 if role!='G' else 'original',usage='final confirmation only' if role=='U' else 'frozen training producer/initialization')
    dump(ROOT/'checkpoints_manifest.json',dict(base_commit=head,models=models,backbone=oldmap['backbone'],selection='earliest all-thresholds dev candidate for F only',independent_T_initialization='exact P copy per arm',U_representation_not_used_before_final=True))
    old,texts,sources,unavailable=history(); oldkeys=set(old); used=set(old); newtexts=set(); worlds=[]; streams=[]; rejected=[]
    gen=load_module('g16_same_v3_generator',V3/'prepare.py')
    for split,n in CFG['plan_world_counts'].items():
        for status in gen.STATUSES:
            pool=[];quota=n//(4 if split=='template_ood' else 8); counts=collections.Counter()
            for rnd in range(100):
                name=f'worlds/{split}/{status}/round{rnd}'; seed=sub_seed(name); streams.append(dict(name=name,seed=seed,candidates=n*3))
                for w in gen.build_worlds('test_template_ood' if split=='template_ood' else split,n*3,seed,used):
                    if w['record_status']!=status: continue
                    k=key(w); ts=legal_texts(w); cell=w['template_family'],w['polarity']
                    if k in oldkeys or ts & (texts|newtexts):
                        rejected.append(dict(split=split,status=status,fact_sha256=hashlib.sha256(k.encode()).hexdigest(),reason='old fact or normalized legal rendering overlap'));continue
                    if counts[cell]>=quota: continue
                    w=dict(w,record_id=f'g16_{split}_{status}_{len(pool):04d}',split=split)
                    if status=='recorded_plan':
                        assert eligible(w,['T_plus','T_plus'],1)
                        assert advance(frame(w,1),'T_plus')==frame(w,0) and advance(frame(w,0),'T_plus')==frame(w,-1)
                    assert len(atomic_specs(w))==(8 if status=='reported_completed' else 16)
                    pool.append(w);counts[cell]+=1;newtexts.update(ts)
                    if len(pool)==n:break
                if len(pool)==n:break
            assert len(pool)==n and set(counts.values())=={quota},(split,status,len(pool))
            worlds+=pool
        write(ROOT/f'data/{split}_worlds.jsonl',[w for w in worlds if w['split']==split])
    assert len({key(w) for w in worlds})==len(worlds)==2880
    write(ROOT/'data/worlds.jsonl',worlds); dump(ROOT/'data/rejections.json',rejected)
    cells=collections.defaultdict(list)
    for w in worlds:
        if w['split']!='train':continue
        for d,p in atomic_specs(w): cells[w['record_status'],d,p].append(dict(record_id=w['record_id'],offset=d,perspective=p))
    assert len(cells)==40; ck=sorted(cells)
    for cell,rows in cells.items(): random.Random(sub_seed('replay/'+str(cell))).shuffle(rows)
    orders={}
    for name in ['main','maintenance']:
        order=[w['record_id'] for w in worlds if w['split']=='train' and w['record_status']=='recorded_plan']
        random.Random(sub_seed('schedule/'+name)).shuffle(order);orders[name]=order
    schedule=[]
    for u in range(200):
        replay=[cells[ck[(u*8+j)%40]][((u*8+j)//40)%512] for j in range(8)]
        schedule.append(dict(update=u+1,main_positions=[u*8+j for j in range(8)],maintenance_positions=[u*8+j for j in range(8)],maintenance_sources=[(u*8+j)%3 for j in range(8)],replay=replay))
    byid={w['record_id']:w for w in worlds}
    cc=collections.Counter((byid[r['record_id']]['record_status'],r['offset'],r['perspective']) for b in schedule for r in b['replay'])
    assert len(cc)==40 and set(cc.values())=={40}
    write(ROOT/'data/sample_schedule.jsonl',schedule);dump(ROOT/'data/world_order.json',orders)
    diag={}
    for split in ['train','dev']:
        sw=[w for w in worlds if w['split']==split];rank=lambda w:hashlib.sha256(f'g16/diag/{split}/{w["record_id"]}'.encode()).hexdigest()
        diag[split]=dict(main=[w['record_id'] for w in sorted([w for w in sw if w['record_status']=='recorded_plan'],key=rank)[:32]],atomic=[w['record_id'] for status in gen.STATUSES for w in sorted([w for w in sw if w['record_status']==status],key=rank)[:16]])
    dump(ROOT/'data/diagnostic_ids.json',diag)
    cases={str(s):{sp:[w['record_id'] for w in sorted([w for w in worlds if w['split']==sp and w['record_status']=='recorded_plan'],key=lambda w:hashlib.sha256(f'g16/case/{s}/{sp}/{w["record_id"]}'.encode()).hexdigest())[:2]] for sp in ['iid','template_ood']} for s in CFG['seeds']}
    dump(ROOT/'data/case_ids.json',cases)
    from transformers import AutoTokenizer
    tok=AutoTokenizer.from_pretrained(REPO/'models/bart-base',local_files_only=True)
    lengths=[len(tok(render(w,frame(w,d,p)))['input_ids']) for w in worlds for d,p in atomic_specs(w)]
    assert max(lengths)<60
    dump(ROOT/'data/manifest.json',dict(data_seed=CFG['data_seed'],namespace='g16',named_substreams=streams,counts={sp:dict(collections.Counter(w['record_status'] for w in worlds if w['split']==sp)) for sp in CFG['plan_world_counts']},total_worlds=len(worlds),train_worlds=1536,main_confirmation_worlds_per_split=160,full_identity_fields=FIELDS,old_unique_facts=len(old),normalized_old_texts=len(texts),reused_G15_history_manifest_sha256=digest(G15/'data/manifest.json'),all_named_leaf_seeds=LEAF_SEEDS,historical_sources=sources,unavailable_sources=unavailable,scope='exact G15 enumerated available history plus G13/G14/G15 explicit worlds; no branch resurvey, no inaccessible/deleted/outside-list all-history claim',fact_overlap=0,normalized_render_overlap=0,legal_atomic_cells=list(map(list,ck)),max_gold_tokens=max(lengths),IID_templates=list(range(8)),OOD_templates=list(range(8,12)),shared_vocab=True))
    sub_seed('bootstrap')
    dump(ROOT/'data/leaf_seeds.json',LEAF_SEEDS)
    # Engineering reproduction: first complete16-world batch per G15 split, not error-selected.
    hw={sp:[w for w in read(G15/f'data/{sp}_worlds.jsonl') if w['record_status']=='recorded_plan'][:16] for sp in ['iid','template_ood']}
    hids={w['record_id'] for ws in hw.values() for w in ws};expected=[]
    import gzip
    with gzip.open(G15/'per_example.jsonl.gz','rt') as f:
        for line in f:
            r=json.loads(line)
            if r['seed']==42 and r['method']=='P' and r['kind'] in ['self_first','self_second'] and r['world_id'] in hids: expected.append(r)
    assert len(expected)==64
    dump(ROOT/'data/history_worlds.json',hw);write(ROOT/'data/history_expected.jsonl',expected)
    deps=[G15/n for n in ['PROTOCOL.md','README.md','INTERPRETATION.md','REPORT.md','run.py','common_g15.py','prepare.py','configs/main.json','checkpoints_manifest.json','data/manifest.json','data/worlds.jsonl']]+[G13/n for n in ['PROTOCOL.md','README.md','configs/main.json','run.py','common_g13.py','baseline_audit.json','artifact_manifest.json']]+[G14/n for n in ['PROTOCOL.md','README.md','INTERPRETATION.md','checkpoints_manifest.json','common_g14.py','data/manifest.json','data/worlds.jsonl','data/history_batches.json','data/history_expected.jsonl']]+[V3/n for n in ['engine.py','common.py','semantics_v1.py','renderer_v1.py','prepare.py','config.json','source_model_manifest.json']]+[V3.parent/'reference_frame_pilot_v2/prepare.py']+[REPO/z['repo_path'] for m in models.values() for z in m.values()]
    dump(ROOT/'baseline_audit.json',dict(G15_base_commit=head,AGENTS='none found in repository/ancestors',exact_dependencies={str(p.relative_to(REPO)):digest(p) for p in deps},settings_from_G15=oldcfg,models=models,ancestry_limits='G13 yesterday anchors already supervised; G-today historically supervised; U/P share ancestry; exact U final200 today state held out only from this repair train/dev',U_excluded_from_training_and_dev=True))
    own=list(ROOT.glob('*.py'))+list((ROOT/'scripts').glob('*'))+list((ROOT/'configs').glob('*'))+list((ROOT/'data').glob('*'))+[ROOT/'PROTOCOL.md',ROOT/'checkpoints_manifest.json',ROOT/'baseline_audit.json',ROOT/'g15_audit.json']+list(ROOT.glob('g15_*.csv'))
    dump(ROOT/'data/lock.json',dict(locked_at_UTC=datetime.now(timezone.utc).isoformat(),before_any_G16_model_inference=True,files={str(p.relative_to(REPO)):digest(p) for p in own+deps if p.is_file()}))
    dump(ROOT/'runs_manifest.json',dict(base_commit=head,branch=CFG['branch'],array_mapping=[dict(index=i,seed=s,methods=CFG['methods']) for i,s in enumerate(CFG['seeds'])],data_sha256=digest(ROOT/'data/worlds.jsonl'),base_schedule_sha256=digest(ROOT/'data/sample_schedule.jsonl'),lock_sha256=digest(ROOT/'data/lock.json'),gpu_budget_seconds=14400,max_concurrent_gpus=2))
    print('G16 locked',len(worlds),'new worlds; old fact exclusions',len(old),'40 atomic cells',flush=True)

if __name__=='__main__':main()
