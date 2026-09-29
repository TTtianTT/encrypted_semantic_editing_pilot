import hashlib,json,sys
from pathlib import Path
import torch

HERE=Path(__file__).resolve().parent
V3=HERE.parent/'reference_frame_pilot_v3'
sys.path.insert(0,str(V3))
from common import score

def load(name):return [json.loads(s) for s in (HERE/name).read_text().splitlines()]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    p=json.loads((HERE/'probe_split.json').read_text())
    train=set(p['train_world_ids']);dev=set(p['dev_world_ids']);test=set(p['test_world_ids'])
    assert not(train&dev or train&test or dev&test)
    assert json.loads((HERE/'repair_training.json').read_text())['count']=={'T_plus':200,'T_minus':200}
    assert json.loads((HERE/'mlp_probe_validation.json').read_text())['max_trained_steps']==2
    worlds={w['record_id']:w for split in ['test_iid','test_template_ood'] for w in [json.loads(s) for s in (V3/f'data/{split}_worlds.jsonl').read_text().splitlines()]}
    report={};source=torch.load(HERE/'source_latents.pt',map_location='cpu',weights_only=False)
    assert len(source)==106
    for group in ['G3','repair']:
        rr=load(f'{group}_trajectories.jsonl');latent=torch.load(HERE/f'{group}_latents.pt',map_location='cpu',weights_only=False)
        assert len(rr)==len(latent)==1696
        ids=set()
        for r in rr:
            key=f"{r['split']}/{r['world_id']}/{r['path']}/{r['step']}"
            assert key in latent and key not in ids;ids.add(key)
            w=worlds[r['world_id']]
            gold=score(r['decoded_text'],r['gold_frame'],w,r['normal_end'])
            assert gold['joint_ok']==r['endpoint_success'] and gold['nondate_facts_ok']==r['fact_preservation']
            v=latent[key];assert v['latent'].shape==(96,768) and v['mask'].shape==(96,)
            assert torch.isfinite(v['latent'].float()).all()
        for split in ['test_iid','test_template_ood']:
            for world in [r['world_id'] for r in rr if r['split']==split and r['path']=='plus_chain' and r['step']==1]:
                for k in [1,2]:
                    a=latent[f'{split}/{world}/plus_chain/{k}']['latent'];b=latent[f'{split}/{world}/plus_plus_person/{k}']['latent']
                    assert torch.equal(a,b)
        report[group]=dict(stages=len(rr),latents=len(latent),unique_keys=len(ids),recomputed_scores=True,shared_prefix_identical=True)
    artifact_names=['config.json','run.py','calibrate_probe.py','mlp_probe.py','analyze.py','analyze_calibrated.py','analyze_mlp.py',
                    'analyze_dynamics.py','repair.pt','mlp_probe.pt','calibrated_probe_weights.npz','G3_latents.pt','repair_latents.pt',
                    'source_latents.pt','G3_trajectories.jsonl','repair_trajectories.jsonl','length_generalization.csv',
                    'representation_distance.csv','algebraic_consistency.csv','failure_taxonomy.csv','mlp_failure_taxonomy.csv']
    hashes={name:sha(HERE/name) for name in artifact_names}
    (HERE/'audit.json').write_text(json.dumps(dict(disjoint_world_splits=True,training_max_chain_length=2,
                                                results=report,artifact_sha256=hashes),indent=2)+'\n')
    print('G4 audit passed',report)

if __name__=='__main__':main()
