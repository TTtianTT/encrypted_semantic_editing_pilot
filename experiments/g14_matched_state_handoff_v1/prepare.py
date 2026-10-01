"""CPU-only provenance, historical-batch extraction, new-world generation and lock."""
import collections, subprocess
from datetime import datetime, timezone
from common_g14 import *

def data_path(p):
    q=Path(p)
    return (p.endswith('.jsonl') and ('data' in q.parts or 'world' in q.name or 'manifest' in q.name) or p.endswith('.json') and ('world' in q.name or 'manifest' in q.name)) and not any(x in q.parts for x in ['outputs','local','latents','latents_archive','models','__pycache__']) and not p.startswith(str(ROOT.relative_to(REPO)))

def main():
    assert not (ROOT/'data/lock.json').exists(),'Never overwrite a locked run'
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip();assert head==CFG['baseline_commit']
    artifacts=json.loads((G13/'artifact_manifest.json').read_text())
    for x in artifacts['files']:assert digest(REPO/x['path'])==x['sha256'],x['path']
    original=json.loads((G13/'baseline_audit.json').read_text());checkpoints={}
    for s in CFG['seeds']:
        z=original['checkpoints'][str(s)]['T0']; rel='experiments/'+z['path'].split('/experiments/',1)[1];p=REPO/rel
        assert digest(p)==z['sha256']; checkpoints[str(s)]={'G':dict(path=str(p),repo_path=rel,sha256=z['sha256'],historical_path=z['path'],role='T0 from G13 baseline audit')}
        for method in CFG['R_methods']:
            meta=json.loads((G13/f'training/{method}_s{s}.json').read_text());assert meta['updates']==200
            p=G13/meta['final_path'];assert digest(p)==meta['final_sha256']
            entry=next(x for x in artifacts['files'] if x['path']==str(p.relative_to(REPO)));assert entry['sha256']==meta['final_sha256']
            checkpoints[str(s)][method]=dict(path=str(p),repo_path=str(p.relative_to(REPO)),sha256=meta['final_sha256'],step=200,role='final only')
    dump(ROOT/'checkpoints_manifest.json',dict(base_commit=head,models=checkpoints,backbone=original['model'],old_weights_read_only=True))
    # Available Git refs and original workspace data manifests are read-only.
    prep=load_module('g13_preparation_for_g14',G13/'prepare.py')
    refs=subprocess.check_output(['git','for-each-ref','--format=%(refname)','refs/heads','refs/remotes/origin'],cwd=REPO,text=True).splitlines()
    blobs={};sources=[];errors=[];old={};oldtexts=set()
    def ingest(raw,source):
        sha=hashlib.sha256(raw).hexdigest()
        if sha in blobs:return
        blobs[sha]=True;source=dict(source,sha256=sha,world_occurrences=0)
        try:
            content=raw.decode();rows=[json.loads(l) for l in content.splitlines() if l.strip()] if source['path'].endswith('.jsonl') else [json.loads(content)]
            for r in rows:
                for w in prep.extract_worlds(r):old[key(w)]=w;source['world_occurrences']+=1
                oldtexts.update(prep.text_fields(r))
        except Exception as e:errors.append(dict(source=source,error=str(e)))
        sources.append(source)
    for ref in refs:
        tree=subprocess.check_output(['git','ls-tree','-r',ref],cwd=REPO,text=True)
        for line in tree.splitlines():
            entry,p=line.split('\t',1)
            if not data_path(p):continue
            obj=entry.split()[2];raw=subprocess.check_output(['git','cat-file','blob',obj],cwd=REPO)
            ingest(raw,dict(ref=ref,path=p,git_blob=obj))
    original_workspace=Path('/dataset1/zailong/workspace/encrypted_semantic_editing_pilot')
    for folder in [original_workspace/'data',original_workspace/'experiments']:
        for p in sorted(folder.rglob('*')):
            if not p.is_file() or not data_path(str(p.relative_to(original_workspace))):continue
            ingest(p.read_bytes(),dict(ref='original-workspace-accessible-files',path=str(p.relative_to(original_workspace)),absolute_path=str(p)))
    assert not errors,'Historical parse/read errors require explicit resolution before locking'
    for w in old.values():
        if 'template_family' not in w:continue
        for d in range(-4,5):
            for p in ['first','third']:
                if valid(w,[frame(w,d,p)]):oldtexts.add(norm(render(w,frame(w,d,p))))
    historical={}
    for split in CFG['world_counts']:
        ws=[w for w in read(G13/f'data/{split}_worlds.jsonl') if w['record_status']=='recorded_plan'][:16]
        assert len(ws)==16;historical[split]=ws
    dump(ROOT/'data/history_batches.json',dict(selection='first complete16 recorded-plan worlds in each original G13 split order; no outcome selection',worlds=historical,record_ids={s:[w['record_id'] for w in ws] for s,ws in historical.items()}))
    targets={(s,sp,m,w['record_id'],k) for s in CFG['seeds'] for sp,ws in historical.items() for m in ['T0','F2','F3'] for w in ws for k in [1,2]};expected=[]
    with gzip.open(G13/'per_example.jsonl.gz','rt',encoding='utf-8') as f:
        for line in f:
            r=json.loads(line)
            if r['kind']=='rollout' and r['mode']=='latent' and r['checkpoint']=='final' and (r['seed'],r['split'],r['method'],r['record_id'],r['step']) in targets:
                expected.append({k:r[k] for k in ['seed','split','method','record_id','step','output','gold','normal_end','exact','score','input_length']})
    assert len(expected)==576
    write(ROOT/'data/history_expected.jsonl',expected)
    gen=load_module('g14_original_world_generator',V3/'prepare.py');used=set(old);oldkeys=set(old);newtexts=set();worlds=[];trace=[];rejections=[]
    for split,n in CFG['world_counts'].items():
        pool=[];quota=n//(4 if split=='template_ood' else 8)
        for round_i in range(100):
            name=f'worlds/{split}/round{round_i}';seed=sub_seed(name);trace.append(dict(split=split,name=name,seed=seed,candidates=n*3))
            for w in gen.build_worlds('test_template_ood' if split=='template_ood' else split,n*3,seed,used):
                if w['record_status']!='recorded_plan':continue
                if not eligible(w,['T_plus','T_plus'],1):rejections.append(dict(split=split,reason='illegal two-step semantics'));continue
                ts={norm(render(w,frame(w,d,p))) for d in range(-4,5) for p in ['first','third'] if valid(w,[frame(w,d,p)])}
                if key(w) in oldkeys or ts&(oldtexts|newtexts):
                    rejections.append(dict(split=split,fact_sha256=hashlib.sha256(key(w).encode()).hexdigest(),reason='fact or normalized-render overlap'));continue
                if sum(z['template_family']==w['template_family'] and z['polarity']==w['polarity'] for z in pool)>=quota:continue
                w=dict(w,record_id=f'g14_{split}_{len(pool):04d}',split=split);pool.append(w);newtexts.update(ts)
                assert advance(frame(w,1),'T_plus')==frame(w,0) and advance(frame(w,0),'T_plus')==frame(w,-1)
                if len(pool)==n:break
            if len(pool)==n:break
        assert len(pool)==n
        cells=collections.Counter((w['template_family'],w['polarity']) for w in pool);assert set(cells.values())=={quota}
        worlds+=pool;write(ROOT/f'data/{split}_worlds.jsonl',pool)
    assert len({key(w) for w in worlds})==320
    from transformers import AutoTokenizer
    tok=AutoTokenizer.from_pretrained(REPO/'models/bart-base',local_files_only=True)
    max_tokens=max(len(tok(render(w,frame(w,d)))['input_ids']) for w in worlds for d in [1,0,-1]);assert max_tokens<60
    train_templates={w['template_family'] for w in read(G13/'data/train_worlds.jsonl')};assert train_templates==set(range(8))
    assert {r['template_family'] for r in read(V3/'data/train_G1.jsonl')}==set(range(8))
    write(ROOT/'data/worlds.jsonl',worlds);dump(ROOT/'data/rejections.json',rejections)
    cases={str(s):{sp:[w['record_id'] for w in sorted([w for w in worlds if w['split']==sp],key=lambda w:hashlib.sha256(f'{CFG["data_seed"]}/case/{s}/{sp}/{w["record_id"]}'.encode()).hexdigest())[:2]] for sp in CFG['world_counts']} for s in CFG['seeds']}
    dump(ROOT/'data/case_ids.json',cases)
    dump(ROOT/'data/manifest.json',dict(data_seed=CFG['data_seed'],actual_named_substreams=trace,counts=CFG['world_counts'],worlds_sha256=digest(ROOT/'data/worlds.jsonl'),full_fact_identity_fields=FIELDS,old_unique_facts=len(old),normalized_historical_texts=len(oldtexts),historical_sources=sources,refs=refs,historical_errors=errors,confirmed_overlap=0,all_historical_data_claim=False,unaudited_scope='unavailable/deleted/private manifests and any files outside the enumerated Git refs and accessible data/world/manifest selection; no claim of complete historical coverage',quota='coupled template/polarity cells: IID8*20, OOD4*40',max_token_length=max_tokens,template_OOD_vs_G_and_R=True,history_rows=576))
    dump(ROOT/'baseline_audit.json',dict(base_commit=head,G13_artifact_manifest_all_hashes_verified=True,G13_rollout_expected_sha256=digest(G13/'per_example.jsonl.gz'),models=checkpoints,model=original['model'],settings=json.loads((G13/'configs/main.json').read_text()),AGENTS='No applicable repository/ancestor AGENTS.md found',zero_training=True,external_slurm_docs=['https://slurm.schedmd.com/job_array.html','https://slurm.schedmd.com/sbatch.html','https://slurm.schedmd.com/srun.html']))
    dependencies=[G13/n for n in ['PROTOCOL.md','REPORT.md','run.py','common_g13.py','core_rollout_table.csv','baseline_audit.json','artifact_manifest.json','per_example.jsonl.gz']]+[V3/n for n in ['engine.py','common.py','semantics_v1.py','renderer_v1.py','prepare.py','config.json','source_model_manifest.json']]+[V3.parent/'reference_frame_pilot_v2/prepare.py']+[REPO/z['repo_path'] for seed in checkpoints.values() for z in seed.values()]
    own=list(ROOT.glob('*.py'))+list((ROOT/'scripts').glob('*'))+list((ROOT/'configs').glob('*'))+list((ROOT/'data').glob('*'))+[ROOT/'PROTOCOL.md',ROOT/'checkpoints_manifest.json',ROOT/'baseline_audit.json']
    dump(ROOT/'data/lock.json',dict(locked_at_UTC=datetime.now(timezone.utc).isoformat(),before_new_model_inference=True,files={str(p.relative_to(REPO)):digest(p) for p in own+dependencies if p.is_file()}))
    dump(ROOT/'runs_manifest.json',dict(base_commit=head,branch=CFG['branch'],array_mapping=[dict(index=i,seed=s,methods=CFG['R_methods']) for i,s in enumerate(CFG['seeds'])],data_sha256=digest(ROOT/'data/worlds.jsonl'),lock_sha256=digest(ROOT/'data/lock.json'),budget_gpu_seconds=14400,max_gpus=2))
    print('locked320 new worlds; historical facts',len(old),'historical output rows576',flush=True)

if __name__=='__main__':main()
