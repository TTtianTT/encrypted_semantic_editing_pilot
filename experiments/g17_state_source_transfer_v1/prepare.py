"""CPU data, full fact/render dedup, history batch and scientific lock."""
import subprocess
from datetime import datetime,timezone
from common_g17 import *
def main():
    assert not (ROOT/'scientific_lock.json').exists(),'Do not overwrite G17 lock'
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip()==CFG['base_commit']
    oldprep=load_module('g17_g16_readonly_history',G16/'prepare.py');old,texts,sources,missing=oldprep.history()
    for path in [G16/'data/worlds.jsonl']:
        ws=read(path)
        for w in ws:old[key(w)]=w;texts.update(oldprep.legal_texts(w))
        sources.append(dict(path=str(path.relative_to(REPO)),absolute_path=str(path),sha256=digest(path),world_occurrences=len(ws),supplement='G16 all train/dev/IID/OOD facts'))
    oldkeys=set(old);used=set(old);newtexts=set();worlds=[];rejections=[]
    gen=load_module('g17_readonly_generator',V3/'prepare.py')
    for split in CFG['splits']:
        pool=[];counts=collections.Counter();quota=160//(4 if split=='template_ood' else 8)
        for rnd in range(100):
            seed=sub_seed(f'worlds/{split}/round{rnd}')
            for w in gen.build_worlds('test_template_ood' if split=='template_ood' else 'iid',480,seed,used):
                if w['record_status']!='recorded_plan':continue
                ts=oldprep.legal_texts(w);cell=w['template_family'],w['polarity'];reason=None
                if not all(eligible(w,['T_plus','T_plus'],a+1,'first') for a in CFG['anchors']):reason='CPU reference legality'
                elif key(w) in oldkeys or ts & (texts|newtexts):reason='historical/new fact or normalized legal rendering overlap'
                if reason:rejections.append(dict(split=split,fact_sha256=hashlib.sha256(key(w).encode()).hexdigest(),reason=reason));continue
                if counts[cell]>=quota:continue
                w=dict(w,record_id=f'g17_{split}_{len(pool):04d}',split=split)
                for a in CFG['anchors']:
                    fs=[frame(w,d,'first') for d in [a+1,a,a-1]]
                    assert valid(w,fs) and advance(fs[0],'T_plus')==fs[1] and advance(fs[1],'T_plus')==fs[2]
                    for f in fs:assert score(render(w,f),f,w,True)['joint_ok']
                pool.append(w);counts[cell]+=1;newtexts.update(ts)
                if len(pool)==160:break
            if len(pool)==160:break
        assert len(pool)==160 and set(counts.values())=={quota};worlds+=pool
        write(ROOT/f'data/{split}_worlds.jsonl',pool)
    assert len({key(w) for w in worlds})==320
    from transformers import AutoTokenizer
    tok=AutoTokenizer.from_pretrained(REPO/'models/bart-base',local_files_only=True)
    lengths=[len(tok(render(w,frame(w,d)))['input_ids']) for w in worlds for a in CFG['anchors'] for d in [a+1,a,a-1]]
    assert max(lengths)<=96 and max(lengths)<60,'Structural max length failure; do not increase caps'
    write(ROOT/'data/worlds.jsonl',worlds);dump(ROOT/'data/rejections.json',rejections)
    cases={str(s):{sp:[w['record_id'] for w in sorted([w for w in worlds if w['split']==sp],key=lambda w:hashlib.sha256(f'g17/case/{s}/{sp}/{w["record_id"]}'.encode()).hexdigest())[:2]] for sp in CFG['splits']} for s in CFG['seeds']}
    dump(ROOT/'data/case_ids.json',cases);sub_seed('analysis/shared_world');[sub_seed('analysis/shared_world/'+sp) for sp in CFG['splits']];dump(ROOT/'data/leaf_seeds.json',LEAF_SEEDS)
    dump(ROOT/'data/manifest.json',dict(data_seed=CFG['data_seed'],namespace='g17',named_leaf_seeds=LEAF_SEEDS,counts={sp:160 for sp in CFG['splits']},total_worlds=320,anchors_are_related_not_independent_worlds=True,full_identity_fields=FIELDS,historical_sources=sources,unavailable=missing,old_unique_facts=len(old),old_normalized_texts=len(texts),fact_overlap=0,render_overlap=0,scope='inherited accessible G16/G15 audited list plus all G16 worlds; no inaccessible/all-history claim',all_frames_legal=True,max_tokens=max(lengths),templates={'iid':list(range(8)),'template_ood':list(range(8,12))},template_polarity_joint_support='same generator parity coupling',shared_vocab=True))
    # Original complete16-world batch/order, not error-picked. History only for smoke.
    hist={sp:read(G16/f'data/{sp}_worlds.jsonl') for sp in CFG['splits']}
    hist={sp:[w for w in ws if w['record_status']=='recorded_plan'][:16] for sp,ws in hist.items()};ids={w['record_id'] for ws in hist.values() for w in ws};expected=[]
    for r in read(G16/'per_example_s42.jsonl.gz'):
        if r['world_id'] in ids and r['method'] in ['P','N-final','F-final'] and r['kind'] in ['self_first','self_second','fixed'] and (r['kind']!='fixed' or r['source'] in ['P','G','U','E']):expected.append(r)
    assert len(expected)==32*3*6
    dump(ROOT/'data/history_batches.json',hist);write(ROOT/'data/history_expected.jsonl.gz',expected)
    deps=json.loads((ROOT/'checkpoints_manifest.json').read_text())['dependencies']
    for p in [G15/'run.py',G15/'common_g15.py',G13/'run.py',G13/'common_g13.py',G16/'common_g16.py',G16/'prepare.py',G16/'data/worlds.jsonl',G16/'data/manifest.json',V3/'common.py',V3/'renderer_v1.py',V3/'semantics_v1.py',V3/'engine.py',V3/'config.json',V3/'source_model_manifest.json',ROOT.parent/'reference_frame_pilot_v2/prepare.py']:
        deps[str(p.relative_to(REPO))]=digest(p)
    deps.update({s['path']:s['sha256'] for s in sources if s.get('absolute_path') and (REPO/s['path']).is_file()})
    own=list(ROOT.glob('*.py'))+list((ROOT/'configs').glob('*'))+list((ROOT/'scripts').glob('*'))+list((ROOT/'data').glob('*'))+[ROOT/'PROTOCOL.md',ROOT/'SUPERVISION_AUDIT.md',ROOT/'supervision_coverage.csv',ROOT/'g10_schedule_counts.csv',ROOT/'g10_actual_occurrences.jsonl.gz',ROOT/'checkpoints_manifest.json']
    dump(ROOT/'scientific_lock.json',dict(locked_at_UTC=datetime.now(timezone.utc).isoformat(),before_any_G17_model_forward=True,files={**deps,**{str(p.relative_to(REPO)):digest(p) for p in own if p.is_file()}}))
    dump(ROOT/'runs_manifest.json',dict(base_commit=CFG['base_commit'],branch=CFG['branch'],array_mapping=[dict(index=i,seed=s) for i,s in enumerate(CFG['seeds'])],data_sha256=digest(ROOT/'data/worlds.jsonl'),scientific_lock_sha256=digest(ROOT/'scientific_lock.json'),gpu_budget_seconds=7200,zero_training=True))
    print('Locked320 new worlds; historical facts',len(old),'max tokens',max(lengths))
if __name__=='__main__':main()
