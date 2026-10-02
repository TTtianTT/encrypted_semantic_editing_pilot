"""Archive finished shards and selected editor parameters on CPU only."""
import gzip,torch,argparse,io
from common import *

def main():
    assert not torch.cuda.is_initialized(),'Publication must not initialize CUDA'
    cpindex=[];sources=[];archives=[]
    for phase in ('engineering','interface','formal','symbol'):
        for run in sorted((ROOT/'runs'/phase).glob('*')):
            if not (run/'complete.json').exists():continue
            archive=run/'predictions.jsonl.gz';members=[]
            for p in sorted(run.rglob('*.jsonl')):
                if 'outputs' in p.parts or p.parent==run or p.parent.name=='dev':members.append(p)
            with archive.open('wb') as raw, gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=0) as gz, io.TextIOWrapper(gz,encoding='utf-8',newline='\n') as out:
                for p in members:
                    for r in rows(p):out.write(json.dumps(dict(artifact=str(p.relative_to(ROOT)),row=r),ensure_ascii=False)+'\n')
            archives.append(dict(run=str(run.relative_to(ROOT)),archive=str(archive.relative_to(ROOT)),sha256=digest(archive),members=[dict(path=str(p.relative_to(ROOT)),sha256=digest(p),rows=len(rows(p))) for p in members]))
            ip=run/'checkpoint_index.json'
            if ip.exists():
                index=read(ip)
                for role,info in index.items():
                    original=Path(info['path']);assert digest(original)==info['sha256']
                    ck=torch.load(original,map_location='cpu',weights_only=False);target=ROOT/'checkpoints'/phase/run.name/(role+'.pt');target.parent.mkdir(parents=True,exist_ok=True)
                    torch.save(dict(editor=ck['editor'],step=ck['step'],raw_checkpoint_sha=info['sha256'],lineage=info),target)
                    cpindex.append(dict(phase=phase,run=run.name,role=role,**info,published_editor=str(target.relative_to(ROOT)),published_sha=digest(target),step=ck['step']))
            local=ROOT/'local'/phase/run.name
            for p in sorted(local.glob('sources/*.json')):
                manifest=read(p);manifest['run']=run.name;manifest['phase']=phase;sources.append(manifest)
            # Correct and rejected training-source decoded states are retained.
            if (local/'sources').exists():
                target=run/'source_decodes.jsonl.gz'
                with target.open('wb') as raw, gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=0) as gz, io.TextIOWrapper(gz,encoding='utf-8',newline='\n') as out:
                    for p in sorted((local/'sources').glob('*.jsonl')):
                        for r in rows(p):out.write(json.dumps(dict(source_artifact=str(p),row=r),ensure_ascii=False)+'\n')
            # Training budgets/schedules are small; expose all semantic-unit draws.
            for p in sorted(local.glob('*/training.jsonl')):
                target=run/'training'/p.parent.name/'training.jsonl';target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(p.read_bytes())
    dump(ROOT/'prediction_archives.json',archives);dump(ROOT/'checkpoints_index.json',cpindex);dump(ROOT/'source_cache_manifests.json',sources)
    lineage=read(ROOT/'SOURCE_LINEAGE.json');lineage['run_checkpoints']=cpindex;lineage['source_cache_manifest_sha']=digest(ROOT/'source_cache_manifests.json');dump(ROOT/'SOURCE_LINEAGE_COMPLETE.json',lineage)
    print('Published',len(cpindex),'editor checkpoints,',len(archives),'complete prediction archives')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--study',choices=['four_domain_state_coverage_v1','space_relation_confirmation_v1'],default='four_domain_state_coverage_v1');args=parser.parse_args()
    ROOT=ROOT.parent/args.study
    main()
