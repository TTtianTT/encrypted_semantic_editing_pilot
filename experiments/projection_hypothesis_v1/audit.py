"""Verify frozen inputs, matched paths, scores and saved pooled geometry."""
import hashlib,json,math,sys
from collections import defaultdict
from pathlib import Path
import torch
import torch.nn.functional as F

HERE=Path(__file__).resolve().parent
G4=HERE.parent/'algebraic_generalization_v1'
V3=HERE.parent/'reference_frame_pilot_v3'
sys.path.insert(0,str(V3))
from common import score,digest

def read(name):return [json.loads(x) for x in (HERE/name).read_text().splitlines()]
def write(name,x):(HERE/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')

def main():
    cfg=json.loads((HERE/'config.json').read_text())
    provenance=json.loads((HERE/'provenance.json').read_text())
    complete=json.loads((HERE/'run_complete.json').read_text())
    assert cfg['editor_training']=='none' and cfg['new_projector_training']=='none'
    assert provenance['checkpoint_sha256']==digest(V3/'checkpoints/G3/best.pt')
    assert provenance['g4_pure_latents_sha256']==digest(G4/'G3_latents.pt')
    assert provenance['g4_probe_sha256']==digest(G4/'mlp_probe.pt')
    assert complete['pure_output_sha256']==digest(HERE/'pure_reset_controls.jsonl')
    assert complete['decode_reencode_output_sha256']==digest(HERE/'decode_reencode_trajectories.jsonl')
    assert complete['pooled_representations_sha256']==digest(HERE/'pooled_representations.pt')
    pure=read('pure_reset_controls.jsonl');dre=read('decode_reencode_trajectories.jsonl')
    assert len(pure)==len(dre)==530
    g4={ (r['split'],r['world_id'],r['step']):r for r in [json.loads(x) for x in (G4/'G3_trajectories.jsonl').read_text().splitlines()] if r['path']=='plus_chain'}
    worlds={w['record_id']:w for split in ['test_iid','test_template_ood'] for w in [json.loads(x) for x in (V3/f'data/{split}_worlds.jsonl').read_text().splitlines()]}
    keys=set(g4)
    assert keys=={(r['split'],r['world_id'],r['step']) for r in pure}=={(r['split'],r['world_id'],r['step']) for r in dre}
    vectors=torch.load(HERE/'pooled_representations.pt',map_location='cpu',weights_only=False)
    assert len(vectors)==1060
    gold_probe=json.loads((HERE/'gold_probe_validation.json').read_text())
    assert gold_probe['no_g5_chain_fit'] and gold_probe['training']=='gold train worlds only'
    predictions=[json.loads(x) for x in (HERE/'gold_probe_predictions.jsonl').read_text().splitlines()]
    assert len(predictions)==1060 and {p['key'] for p in predictions}==set(vectors)
    drmap={(r['split'],r['world_id'],r['step']):r for r in dre}
    first_match=0;recomputed=0;maximum_distance_error=0.
    for path,rows in [('pure',pure),('decode_reencode',dre)]:
        for r in rows:
            key=(r['split'],r['world_id'],r['step']);ref=g4[key];world=worlds[r['world_id']]
            assert r['gold_text']==ref['gold_text'] and r['gold_frame']==ref['gold_frame']
            if path=='pure':
                assert r['decoded_text']==ref['decoded_text'] and r['edited']['success']==ref['endpoint_success']
            elif r['step']==1:
                first_match+=int(r['decoded_text']==ref['decoded_text'])
            else:
                assert r['input_text']==drmap[r['split'],r['world_id'],r['step']-1]['decoded_text']
            for field,text,end in [('edited',r['decoded_text'],r['edited']['normal_end']),('reset',r['reset_text'],r['reset']['normal_end'])]:
                s=score(text,r['gold_frame'],world,end)
                assert r[field]['success']==s['joint_ok']
                assert r[field]['fact_preservation']==s['nondate_facts_ok']
                assert r[field]['parse_unresolved']==s['parse_unresolved']
                recomputed+=1
            vec=vectors[f'{path}/{r["split"]}/{r["world_id"]}/{r["step"]}']
            assert all(v.shape==(768,) and torch.isfinite(v).all() for v in vec.values())
            for name,field in [('edited','edited_distance'),('reset','reset_distance')]:
                d=float((vec[name]-vec['gold']).norm()/vec['gold'].norm())
                c=float(1-F.cosine_similarity(vec[name][None],vec['gold'][None]).item())
                maximum_distance_error=max(maximum_distance_error,abs(d-r[field]['normalized_l2']),abs(c-r[field]['cosine']))
                assert abs(d-r[field]['normalized_l2'])<2e-5 and abs(c-r[field]['cosine'])<2e-5
    ids=provenance['world_ids']
    assert len(ids['test_iid'])==len(ids['test_template_ood'])==53
    summary=dict(passed=True,worlds_per_split=53,steps_per_path=530,recomputed_scores=recomputed,
                 first_step_decode_matches_g4=f'{first_match}/106',max_distance_recompute_error=maximum_distance_error,
                 frozen_checkpoint_sha256=provenance['checkpoint_sha256'],
                 no_editor_or_projector_training=True,
                 gold_probe_dev_accuracy=gold_probe['dev_accuracy'],gold_probe_test_gold_accuracy=gold_probe['test_gold_accuracy'],
                 output_sha256={name:digest(HERE/name) for name in ['config.json','run.py','analyze.py','gold_probe.py',
                     'gold_probe_validation.json','gold_probe_weights.npz','gold_probe_predictions.jsonl','gold_probe_trajectory.csv',
                     'pure_reset_controls.jsonl','decode_reencode_trajectories.jsonl','pooled_representations.pt',
                     'length_generalization.csv','representation_reset.csv','paired_effects.csv']})
    write('audit.json',summary)
    print('G5 audit passed',summary['first_step_decode_matches_g4'],maximum_distance_error)

if __name__=='__main__':main()
