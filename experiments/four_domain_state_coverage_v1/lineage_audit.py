"""CPU audit of selection, initialization and the actual P/Q chronology."""
import torch
from common import *

def main():
    output=[];checked=0
    for study in ('four_domain_state_coverage_v1','space_relation_confirmation_v1'):
        base=ROOT.parent/study
        for run in sorted((base/'runs/formal').glob('*')):
            cpfile=run/'checkpoint_index.json'
            if not cpfile.exists():continue
            model,domain,se=run.name.split('_');seed=int(se[1:]);index=read(cpfile);cache={}
            for role,info in index.items():
                path=Path(info['path']);assert digest(path)==info['sha256'];cache[role]=torch.load(path,map_location='cpu',weights_only=False);checked+=1
            for role in ('P','U'):
                if role not in cache:continue
                local=Path(index[role]['path']).parent;trainlog=rows(local/'training.jsonl');candidates=[r for r in trainlog if 'dev_nll' in r];best=min(candidates,key=lambda r:(r['dev_nll'],r['step']));assert cache[role]['step']==best['step'],(study,run.name,role,'selection mismatch');assert read(local/'complete.json')['step']==600
            for role,info in index.items():
                if role in ('P','U'):
                    lineage=dict(initialization='new identity editor',optimization_seed=seed if role=='P' else seed+10000,atomic_updates_executed=600,selected_dev_step=cache[role]['step'],selection='earliest minimum full-core-dev token-mean NLL over100/200/300/400/500/600')
                elif role=='Q':
                    assert cache[role]['step']==300
                    lineage=dict(atomic_optimization_run=str(Path(index['P']['path']).parent),optimization_seed=seed,trajectory_snapshot_step=300,selected_P_step=cache['P']['step'],selected_P_sha=index['P']['sha256'],relationship='same optimization trajectory; Qstep300 is not a child initialized from selected P. Legacy raw parent field identifies the associated P run only.')
                else:
                    assert cache[role]['step']==200 and info['parent_P_sha']==index['P']['sha256']
                    lineage=dict(initialization_exact_P_sha=index['P']['sha256'],initialization_P_step=cache['P']['step'],supplement_updates=200,selection='final200, no test selection',condition=info['condition'],heldout_current_state=info['heldout'],edited_focus_states=info['edited_focus_states'] if role.startswith(('S','M')) else [],natural_control_states=info['edited_focus_states'] if role.startswith('N') else [],optimization_seed=seed+20000+int(role[-1]))
                output.append(dict(study=study,run=run.name,role=role,raw_path=info['path'],raw_sha256=info['sha256'],step=cache[role]['step'],resolved_lineage=lineage,formal_task_complete=(run/'complete.json').exists()))
    assert not torch.cuda.is_initialized()
    dump(ROOT/'SOURCE_LINEAGE_RESOLVED.json',dict(checkpoints=output,raw_checkpoints_verified=checked,legacy_metadata_preserved=True,historical_editor_weights_used=False,no_cuda_initialized=True));print('Lineage/selection checked',checked,'checkpoints')

if __name__=='__main__':main()
