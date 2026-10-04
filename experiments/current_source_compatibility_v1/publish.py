"""Deterministic prediction archives and small editor exports; large caches stay local."""
import gzip,io,shutil,torch
from study import *
def main():
    archives=[];checkpoints=[];sources=[]
    for seed in (42,43,44):
      for folder in [ROOT/f'runs/preflight/s{seed}/T0']+[ROOT/f'runs/formal/s{seed}/{m}_u{u}' for m in ('N','F','R') for u in (100,200)]:
        if not (folder/'complete.json').exists():continue
        members=sorted(folder.rglob('*.jsonl'));dest=folder/'predictions.jsonl.gz'
        with dest.open('wb') as raw,gzip.GzipFile(filename='',fileobj=raw,mode='wb',mtime=0) as gz,io.TextIOWrapper(gz,encoding='utf-8',newline='\n') as f:
          for path in members:
            for r in rows(path):f.write(json.dumps(dict(artifact=str(path.relative_to(folder)),row=r),ensure_ascii=False)+'\n')
        n=0;expected=((str(p.relative_to(folder)),r) for p in members for r in rows(p))
        with gzip.open(dest,'rt') as f:
          for line in f:
            r=json.loads(line);artifact,original=next(expected)
            assert r['artifact']==artifact and r['row']==original; n+=1
        assert next(expected,None) is None
        assert n==sum(len(rows(p)) for p in members)
        archives.append(dict(archive=str(dest.relative_to(ROOT)),sha256=digest(dest),rows=n,members=[dict(path=str(p.relative_to(folder)),sha256=digest(p),rows=len(rows(p))) for p in members]))
      for method in ('N','F','R'):
        folder=ROOT/f'local/s{seed}/{method}'
        if not (folder/'update200.pt').exists():continue
        public=ROOT/f'training/s{seed}/{method}';public.mkdir(parents=True,exist_ok=True)
        for name in ('training.jsonl','refreshes.json','training_status.json'):shutil.copyfile(folder/name,public/name)
        for u in (100,200):
          p=folder/f'update{u:03}.pt';state=torch.load(p,map_location='cpu',weights_only=True);dest=ROOT/f'checkpoints/s{seed}/{method}_u{u}.pt';dest.parent.mkdir(parents=True,exist_ok=True);torch.save(state,dest)
          check=torch.load(dest,map_location='cpu',weights_only=True);assert all(torch.equal(state['editor'][k],check['editor'][k]) for k in state['editor'])
          checkpoints.append(dict(seed=seed,condition=method,update=u,path=str(dest.relative_to(ROOT)),sha256=digest(dest),raw_checkpoint=str(p),raw_sha256=digest(p),initial_sha=digest(checkpoint(seed)),parameters=sum(v.numel() for v in state['editor'].values())))
        for refresh in read(folder/'refreshes.json'):
          cachefolder=folder/(f'cache_R/u{refresh["update"]:03}' if method=='R' else 'cache_'+method);info=read(cachefolder/'complete.json');quality=public/f'prefix_u{refresh["update"]:03}.jsonl.gz'
          with quality.open('wb') as raw,gzip.GzipFile(filename='',fileobj=raw,mode='wb',mtime=0) as gz:gz.write((cachefolder/'prefix_quality.jsonl').read_bytes())
          sources.append(dict(seed=seed,condition=method,refresh_update=refresh['update'],source_checkpoint_sha=refresh['source_sha'],prefix_quality_archive=str(quality.relative_to(ROOT)),prefix_quality_sha=digest(quality),cache_manifest=str(cachefolder/'complete.json'),cache_manifest_sha=digest(cachefolder/'complete.json'),cache=info))
    logs=[dict(path=str(p),sha256=digest(p),bytes=p.stat().st_size) for p in sorted((ROOT/'logs').glob('*')) if p.is_file()]
    dump(ROOT/'PREDICTION_INDEX.json',archives);dump(ROOT/'CHECKPOINT_INDEX.json',checkpoints);dump(ROOT/'SOURCE_LINEAGE_RESOLVED.json',dict(original=read(ROOT/'SOURCE_LINEAGE.json'),supplement_sources=sources));dump(ROOT/'LOG_INDEX.json',logs)
    assert not torch.cuda.is_initialized()
    dump(ROOT/'PUBLICATION_AUDIT.json',dict(passed=True,archives=len(archives),prediction_rows=sum(r['rows'] for r in archives),exact_editor_exports=len(checkpoints),supplement_source_manifests=len(sources),logs=len(logs),no_cuda_initialized=True,at_utc=now()));print('Published',len(archives),'prediction archives;',len(checkpoints),'editors;',len(sources),'source manifests')
if __name__=='__main__':main()
