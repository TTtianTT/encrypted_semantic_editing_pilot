"""CPU preparation and exact provenance audit. Never calls a GPU or views new outputs."""
import collections, importlib.util, random, subprocess
from common_g13 import *

def sub_seed(name): return int.from_bytes(hashlib.sha256(f'{CFG["data_seed"]}/{name}'.encode()).digest()[:8], 'big')
def extract_worlds(x):
    if isinstance(x, dict):
        if all(k in x for k in FIELDS): yield x
        for v in x.values(): yield from extract_worlds(v)
    elif isinstance(x, list):
        for v in x: yield from extract_worlds(v)
def text_fields(x):
    if isinstance(x, dict):
        for k, v in x.items():
            if k in ['source_text', 'target_text', 'gold_step_texts', 'texts', 'current_gold', 'next_target']:
                if isinstance(v, str): yield norm(v)
                elif isinstance(v, list):
                    for t in v:
                        if isinstance(t, str): yield norm(t)
            elif isinstance(v, (list, dict)): yield from text_fields(v)
    elif isinstance(x, list):
        for v in x: yield from text_fields(v)
def stratified(ws, n, name):
    cells = collections.defaultdict(list)
    for w in ws: cells[w['template_family'], w['polarity']].append(w)
    rng = random.Random(sub_seed(name))
    for v in cells.values(): rng.shuffle(v)
    out = []
    while len(out) < min(n, len(ws)):
        for k in sorted(cells):
            if cells[k] and len(out) < n: out.append(cells[k].pop())
    return out
def main():
    assert not (ROOT / 'data/lock.json').exists(), 'Do not overwrite locked experiment'
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(REPO / 'models/bart-base', local_files_only=True)
    paths = sorted(set(list((REPO / 'data').glob('*.jsonl')) + [p for p in (REPO / 'experiments').rglob('*.jsonl') if ROOT not in p.parents and ('data' in p.parts or 'world' in p.name or 'manifest' in p.name) and not any(q in p.parts for q in ['outputs', 'local', 'latents', 'latents_archive'])]))
    old = {}; oldtexts = set(); provenance = {}
    for p in paths:
        rows = read(p); n = 0
        for r in rows:
            for w in extract_worlds(r): old[key(w)] = w; n += 1
            oldtexts.update(text_fields(r))
        provenance[str(p.relative_to(REPO))] = dict(sha256=digest(p), world_occurrences=n)
    for w in old.values():
        if 'template_family' not in w: continue
        for d in range(-4, 5):
            for pers in ['first', 'third']:
                if valid(w, [frame(w, d, pers)]): oldtexts.add(norm(render(w, frame(w, d, pers))))
    spec = importlib.util.spec_from_file_location('worldgen', V3 / 'prepare.py'); gen = importlib.util.module_from_spec(spec); spec.loader.exec_module(gen)
    used = set(old); oldkeys = used.copy(); newtexts = set(); worlds = []; rejects = []; streams = {}
    for split, n in CFG['plan_world_counts'].items():
        streams[split] = sub_seed('worlds/' + split)
        for status in gen.STATUSES:
            pool = []
            for round_i in range(100):
                candidates = gen.build_worlds('test_template_ood' if split == 'template_ood' else split, n * 3, sub_seed(f'worlds/{split}/{status}/{round_i}'), used)
                for w in candidates:
                    if w['record_status'] != status: continue
                    ts = {norm(render(w, frame(w, d, p))) for d in range(-4, 5) for p in ['first', 'third'] if valid(w, [frame(w, d, p)])}
                    if ts & (oldtexts | newtexts):
                        rejects.append(dict(split=split, status=status, fact_hash=hashlib.sha256(key(w).encode()).hexdigest(), reason='normalized-render collision')); continue
                    # Fixed cell quotas; rejection cannot change template/polarity balance.
                    # Historical generator couples template parity to polarity.
                    # Preserve that actual support (4 OOD / 8 IID cells), not
                    # an unattainable Cartesian template x polarity quota.
                    quota = n // (4 if split == 'template_ood' else 8)
                    if sum(z['template_family'] == w['template_family'] and z['polarity'] == w['polarity'] for z in pool) >= quota: continue
                    w = dict(w, record_id=f'g13_{split}_{status}_{len(pool):04d}', split=split)
                    assert key(w) not in oldkeys
                    pool.append(w); newtexts.update(ts)
                    if len(pool) == n: break
                if len(pool) == n: break
            assert len(pool) == n, (split, status, len(pool), n)
            worlds += pool
    assert len({key(w) for w in worlds}) == len(worlds)
    for split in CFG['plan_world_counts']: write(ROOT / f'data/{split}_worlds.jsonl', [w for w in worlds if w['split'] == split])
    write(ROOT / 'data/worlds.jsonl', worlds)
    dump(ROOT / 'data/collision_rejections.json', rejects)
    train = [w for w in worlds if w['split'] == 'train']; plans = [w for w in train if w['record_status'] == 'recorded_plan']
    anchor_order = list(range(len(plans))); rng = random.Random(sub_seed('schedule/anchor')); rng.shuffle(anchor_order)
    narrow_order = list(range(len(plans))); random.Random(sub_seed('schedule/narrow')).shuffle(narrow_order)
    cells = collections.defaultdict(list)
    for w in train:
        for d, p in atomic_specs(w): cells[w['record_status'], d, p].append(dict(record_id=w['record_id'], offset=d, perspective=p))
    assert len(cells) == 40
    rng = random.Random(sub_seed('schedule/replay')); cell_keys = sorted(cells)
    for rows in cells.values(): rng.shuffle(rows)
    schedule = []
    for u in range(CFG['updates']):
        replay = [cells[cell_keys[(u*16+j)%40]][((u*16+j)//40)%len(cells[cell_keys[(u*16+j)%40]])] for j in range(16)]
        schedule.append(dict(update=u+1, anchor_positions=[(u*16+j)%512 for j in range(16)], narrow_positions=[(u*16+j)%512 for j in range(16)], mixed_sources=[(u*16+j)%3 for j in range(16)], replay=replay))
    write(ROOT / 'data/sample_schedule.jsonl', schedule)
    dump(ROOT / 'data/anchor_order.json', dict(anchor_worlds=[plans[i]['record_id'] for i in anchor_order], narrow_worlds=[plans[i]['record_id'] for i in narrow_order], projection='filter once onto each seed train C, cycle positions modulo |C|'))
    diag = {}
    for split in ['train', 'dev']:
        ws = [w for w in worlds if w['split'] == split]
        diag[split] = dict(anchor=[w['record_id'] for w in stratified([w for w in ws if w['record_status']=='recorded_plan'], 80 if split=='train' else 128, 'diag/'+split)], atomic=[w['record_id'] for status in gen.STATUSES for w in stratified([w for w in ws if w['record_status']==status],16,'diag/'+split+'/'+status)])
    dump(ROOT / 'data/diagnostic_ids.json', diag)
    oldpaths = read(G12 / 'data/train_paths.jsonl'); selected = stratified([r['world'] for r in oldpaths],80,'old_g12_train')
    dump(ROOT / 'data/old_train_diagnostic.json', dict(g12_worlds=[w['record_id'] for w in selected]))
    alltexts = [render(w, frame(w,d,p)) for w in worlds for d,p in atomic_specs(w)]
    maxlen = max(map(len, tok(alltexts)['input_ids'])); assert maxlen < 60
    initial = {}
    for s in CFG['seeds']:
        initial[str(s)] = dict(T0=dict(path=str(original(s)), sha256=digest(original(s))), **{a:dict(path=str(G12/f'checkpoints/{a}_seed{s}.pt'),sha256=digest(G12/f'checkpoints/{a}_seed{s}.pt')) for a in ['A','B']})
        for a in ['A','B']:
            assert initial[str(s)][a]['sha256'] == json.loads((G12/f'training/{a}_seed{s}.json').read_text())['checkpoint_sha256']
        assert initial[str(s)]['T0']['sha256'] == json.loads((G10/f'checkpoints/rank16/rank16_seed{s}.json').read_text())['checkpoint_sha256']
    trainrows=read(V3/'data/train_G1.jsonl'); assert {r['template_family'] for r in trainrows}==set(range(8))
    assert {r['world']['template_family'] for r in oldpaths}==set(range(8))
    dump(ROOT/'baseline_audit.json',dict(checkpoints=initial, model=json.loads((V3/'source_model_manifest.json').read_text()), G10_train_sha=digest(V3/'data/train_G1.jsonl'), G10_schedule_sha=digest(V3/'data/sample_schedule.jsonl'), G12_train_sha=digest(G12/'data/train_paths.jsonl'), G10_supervised_lengths=[1,2], G12_supervised_lengths=[1,2,3], G12_B_third='stopgrad own current h2; not fixed old state', old_data_files=provenance, old_unique_facts=len(old), normalized_historical_texts=len(oldtexts), scope='All accessible CPU data/world manifests listed; excludes unavailable manifests and free model outputs. No universal all-history claim.', no_AGENTS_found=True))
    dump(ROOT / 'data/manifest.json',dict(data_seed=CFG['data_seed'],named_substreams=streams,counts={s:dict(collections.Counter(w['record_status'] for w in worlds if w['split']==s)) for s in CFG['plan_world_counts']},fact_overlap=0,normalized_render_overlap=0,new_split_text_overlap=0,old_files=provenance,legal_atomic_cells=list(map(list,cell_keys)),max_gold_tokens=maxlen,template_ood_valid_vs_T0_and_G12=True,old_train_templates=list(range(8)),ood_templates=list(range(8,12)),full_identity_fields=FIELDS))
    deps=[V3/p for p in ['engine.py','common.py','semantics_v1.py','renderer_v1.py','config.json','source_model_manifest.json','data/train_G1.jsonl','data/sample_schedule.jsonl','checkpoints/G3/editor_best.pt'] if (V3/p).exists()]+[original(s) for s in CFG['seeds']]+[G12/f'checkpoints/{a}_seed{s}.pt' for a in ['A','B'] for s in CFG['seeds']]
    files=list(ROOT.glob('*.py'))+list((ROOT/'scripts').glob('*'))+list((ROOT/'configs').glob('*'))+list((ROOT/'data').glob('*'))+[ROOT/'PROTOCOL.md',ROOT/'BASELINE_AUDIT.md']+deps
    dump(ROOT/'data/lock.json',dict(before_new_training=True,files={str(p.relative_to(REPO)):digest(p) for p in files if p.exists()}))
    dump(ROOT/'runs_manifest.json',dict(branch='experiment/g13-source-overfit-audit-v1',baseline=CFG['baseline'],array_mapping=[dict(index=i,seed=s,groups=CFG['methods']) for i,s in enumerate(CFG['seeds'])],data_sha256=digest(ROOT/'data/worlds.jsonl'),schedule_sha256=digest(ROOT/'data/sample_schedule.jsonl'),protocol_sha256=digest(ROOT/'PROTOCOL.md'),max_gpus=2,budget_gpu_seconds=43200))
    print('locked',len(worlds),'worlds; historical facts',len(old),'cells',len(cells),flush=True)
if __name__=='__main__': main()
