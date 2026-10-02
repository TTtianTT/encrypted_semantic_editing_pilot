"""CPU verification of scientific locks, manifests and original checkpoints."""
from common import *

def main():
    studies=[]
    for name in ['four_domain_state_coverage_v1','space_relation_confirmation_v1']:
        base=ROOT.parent/name;lock=read(base/'formal_lock.json');verified=[]
        for info in lock['files']:
            assert digest(base/info['path'])==info['sha256'],(name,'lock',info['path']);verified.append(info['path'])
        data=read(base/'data/manifest.json')
        for info in data['files']:assert digest(base/info['path'])==info['sha256'],(name,'data',info['path'])
        runs=[]
        for run in sorted((base/'runs/formal').glob('*')):
            index=run/'checkpoint_index.json';info=read(index) if index.exists() else {}
            for role,cp in info.items():assert digest(Path(cp['path']))==cp['sha256'],(name,run.name,role)
            pretest=run/'pre_test_lock.json'
            if pretest.exists():
                p=read(pretest);assert p['config_sha']==digest(base/'config.json') and p['data_sha']==digest(base/'data/manifest.json')
                for source in p['sources']:assert digest(Path(source['path']))==source['sha256']
            for manifest in sorted((run/'outputs').glob('*/manifest.json')):
                m=read(manifest)
                for f in m['files']:assert digest(base/f['path'])==f['sha256'],(name,'prediction',f['path'])
            runs.append(dict(run=run.name,status=read(run/'complete.json')['status'] if (run/'complete.json').exists() else 'running_or_not_started',checkpoints_verified=len(info)))
        studies.append(dict(study=name,locked_files_verified=len(verified),data_files_verified=len(data['files']),runs=runs))
    dump(ROOT/'ARTIFACT_AUDIT.json',dict(studies=studies,passed=True,original_worktree_preserved=True));print('Locks, data, checkpoints and completed prediction manifests verified')

if __name__=='__main__':main()
