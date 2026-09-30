"""Reconstruct only locked worlds on CPU; preserve data and expose actual leaf RNG seeds."""
import importlib.util
from common_g13 import *
def main():
    spec=importlib.util.spec_from_file_location('g13_data_builder',ROOT/'prepare.py'); prep=importlib.util.module_from_spec(spec); spec.loader.exec_module(prep)
    original_manifest=json.loads((ROOT/'data/manifest.json').read_text()); old={}; oldtexts=set()
    for name,z in original_manifest['old_files'].items():
        p=REPO/name; assert digest(p)==z['sha256'],name
        for r in read(p):
            for w in prep.extract_worlds(r): old[key(w)]=w
            oldtexts.update(prep.text_fields(r))
    for w in old.values():
        if 'template_family' not in w: continue
        for d in range(-4,5):
            for p in ['first','third']:
                if valid(w,[frame(w,d,p)]): oldtexts.add(norm(render(w,frame(w,d,p))))
    spec=importlib.util.spec_from_file_location('v3_data_builder_for_audit',V3/'prepare.py'); gen=importlib.util.module_from_spec(spec); spec.loader.exec_module(gen)
    used=set(old); newtexts=set(); reconstructed=[]; trace=[]
    for split,n in CFG['plan_world_counts'].items():
        for status in gen.STATUSES:
            pool=[]
            for round_i in range(100):
                name=f'worlds/{split}/{status}/{round_i}'; seed=prep.sub_seed(name); candidates=gen.build_worlds('test_template_ood' if split=='template_ood' else split,n*3,seed,used)
                trace.append(dict(split=split,status=status,round=round_i,name=name,seed=seed,candidates=n*3))
                for w in candidates:
                    if w['record_status']!=status: continue
                    ts={norm(render(w,frame(w,d,p))) for d in range(-4,5) for p in ['first','third'] if valid(w,[frame(w,d,p)])}
                    if ts & (oldtexts|newtexts): continue
                    quota=n//(4 if split=='template_ood' else 8)
                    if sum(z['template_family']==w['template_family'] and z['polarity']==w['polarity'] for z in pool)>=quota: continue
                    pool.append(dict(w,record_id=f'g13_{split}_{status}_{len(pool):04d}',split=split)); newtexts.update(ts)
                    if len(pool)==n: break
                if len(pool)==n: break
            assert len(pool)==n
            reconstructed+=pool
    assert reconstructed==read(ROOT/'data/worlds.jsonl'),'Locked world reconstruction mismatch; never replace data'
    dump(ROOT/'data_rng_provenance.json',dict(data_seed=CFG['data_seed'],derivation='first8 bytes SHA256(f"{data_seed}/{name}"), big-endian integer, Python random.Random at each leaf',actual_world_substreams=trace,schedule_seeds={name:prep.sub_seed('schedule/'+name) for name in ['anchor','narrow','replay']},diagnostic_and_old_audit='sub_seed names in prepare.py; data/model seeds separate',locked_worlds_exactly_reproduced=True,worlds_sha256=digest(ROOT/'data/worlds.jsonl'),scope_note='Initial manifest split-level named_substreams values identify namespaces, not the actual status/round generator calls; this sidecar records actual leaf seeds without changing locked data.',verified_after_lock=True))
    print('Exact CPU world reconstruction passed; leaf RNG calls',len(trace),flush=True)
if __name__=='__main__': main()
