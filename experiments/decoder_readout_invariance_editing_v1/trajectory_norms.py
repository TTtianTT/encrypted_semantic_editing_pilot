"""Slurm-only latent replay for missing per-step magnitude diagnostics."""
import torch
from .common import *
from .engine import editors


@torch.no_grad()
def run(eng,folder):
    seed=eng.task['seed'];models={'Original':eng.ed}
    for item in read(ROOT/'configs/FINAL_METHOD_CHECKPOINT_LOCK.json')['checkpoints']:
        if item['seed']!=seed:continue
        assert sha(item['path'])==item['sha256']
        ed=editors(eng.d,seed);ed.load_state_dict(torch.load(item['path'],map_location='cuda',weights_only=False)['editor']);models[item['method']]=ed.eval()
    source=Path(read(ROOT/'manifests/S3_SELECTED_VALIDATION_TRAJECTORIES.json')['output_root'])/f'bart_s{seed}'
    assert read(source/'RUN_STATUS.json')['status']=='COMPLETED'
    artifact={r['path']:r['sha256'] for r in read(source/'RUN_STATUS.json')['artifacts']}
    cache=next(r for r in read(ROOT/'configs/S3_REUSE_LOCK.json')['entries'] if r['seed']==seed)['source_worlds']
    worlds=[w for w in rows(ROOT/'configs/worlds.jsonl') if w['split']=='validation'];records=[];checked=0
    for i,w in enumerate(worlds):
        path=source/(w['world_id']+'_trajectories.jsonl');assert sha(path)==artifact[str(path)]
        assert sha(cache[w['world_id']]['path'])==cache[w['world_id']]['sha256']
        src=torch.load(cache[w['world_id']]['path'],map_location='cpu',weights_only=False)[(w['world_id'],0,'natural')]
        h0=src['hidden'][None].cuda();mask=src['mask'][None].cuda()
        for track in rows(path):
            h=h0.clone();all_good=True
            for step in track['steps']:
                edited=models[track['method']][step['operation']](h,mask)
                if i==0:
                    actual=eng.evaluate(edited,mask,w,step['state']);assert actual==step['prediction'],'Replayed latent path does not reproduce stored prediction';checked+=1
                all_good=all_good and step['prediction']['score']['success']
                records.append(dict(world_id=w['world_id'],seed=seed,method=track['method'],order=track['order'],direction=track['direction'],step=step['step'],complete_to_step=all_good,update_norm=float((edited-h).float()[mask.bool()].norm()),relative_update_norm=float((edited-h).float()[mask.bool()].norm()/(h.float()[mask.bool()].norm()+1e-9)),cumulative_norm_from_natural=float((edited-h0).float()[mask.bool()].norm()),source_trajectory_sha256=artifact[str(path)],scope='POSTHOC_VALIDATION_MAGNITUDE_DIAGNOSTIC'))
                h=edited
        if (i+1)%8==0:jsonl(folder/'trajectory_norms.jsonl',records);print('trajectory magnitudes',seed,i+1,flush=True)
    jsonl(folder/'trajectory_norms.jsonl',records);assert len(records)==6400 and checked==100
    return dict(passed=True,worlds=64,seed=seed,records=6400,checked_stored_predictions=100,prediction_mismatches=0,all_padded_positions_excluded=True,algorithm_or_checkpoint_changed=False,test_accessed=0,scope='POSTHOC_VALIDATION_MAGNITUDE_DIAGNOSTIC',resources=eng.resources())
