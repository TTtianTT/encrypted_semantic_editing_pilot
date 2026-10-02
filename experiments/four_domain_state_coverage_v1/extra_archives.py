"""Archive identity/structure raw predictions and index all Slurm logs on CPU."""
import gzip
from common import *

def main():
    archives=[];logs=[]
    for study in ('four_domain_state_coverage_v1','space_relation_confirmation_v1'):
        base=ROOT.parent/study
        for directory in sorted((base/'language_controls').glob('*'))+sorted((base/'position_foils').glob('*'))+sorted((base/'runs/formal').glob('*/identity_probe')):
            if not (directory/'complete.json').exists():continue
            members=sorted(directory.rglob('*.jsonl'))
            if not members:continue
            dest=directory/'predictions.jsonl.gz'
            with gzip.open(dest,'wt',encoding='utf-8') as f:
                for p in members:
                    for r in rows(p):f.write(json.dumps(dict(artifact=str(p.relative_to(base)),row=r),ensure_ascii=False)+'\n')
            archives.append(dict(study=study,archive=str(dest.relative_to(base)),sha256=digest(dest),members=[dict(path=str(p.relative_to(base)),sha256=digest(p),rows=len(rows(p))) for p in members]))
        for path in sorted((base/'logs').glob('*')):
            if path.is_file():logs.append(dict(study=study,path=str(path),sha256=digest(path),bytes=path.stat().st_size))
    dump(ROOT/'ADDITIONAL_PREDICTION_ARCHIVES.json',archives);dump(ROOT/'LOG_INDEX.json',logs)
    print('Extra prediction archives',len(archives),'; log files',len(logs))

if __name__=='__main__':main()
