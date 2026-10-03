"""Archive identity/structure raw predictions and index all Slurm logs on CPU."""
import argparse,gzip,io
from common import *

def main(logs_only=False):
    archives=[];logs=[]
    for study in ('four_domain_state_coverage_v1','space_relation_confirmation_v1'):
        base=ROOT.parent/study
        directories=[] if logs_only else sorted((base/'language_controls').glob('*'))+sorted((base/'position_foils').glob('*'))+sorted((base/'runs/formal').glob('*/identity_probe'))
        for directory in directories:
            if not (directory/'complete.json').exists():continue
            members=sorted(directory.rglob('*.jsonl'))
            if not members:continue
            dest=directory/'predictions.jsonl.gz'
            with dest.open('wb') as raw, gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=0) as gz, io.TextIOWrapper(gz,encoding='utf-8',newline='\n') as f:
                for p in members:
                    for r in rows(p):f.write(json.dumps(dict(artifact=str(p.relative_to(base)),row=r),ensure_ascii=False)+'\n')
            archives.append(dict(study=study,archive=str(dest.relative_to(base)),sha256=digest(dest),members=[dict(path=str(p.relative_to(base)),sha256=digest(p),rows=len(rows(p))) for p in members]))
        for path in sorted((base/'logs').glob('*')):
            if path.is_file():logs.append(dict(study=study,path=str(path),sha256=digest(path),bytes=path.stat().st_size))
    if not logs_only:dump(ROOT/'ADDITIONAL_PREDICTION_ARCHIVES.json',archives)
    dump(ROOT/'LOG_INDEX.json',logs)
    if logs_only:print('Final log hashes refreshed:',len(logs))
    else:print('Extra prediction archives',len(archives),'; log files',len(logs))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--logs-only',action='store_true',help='Refresh final log hashes after the CPU finalize job exits; leave prediction archives intact.')
    main(parser.parse_args().logs_only)
