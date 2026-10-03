"""Reuse Slurm predictions only for byte-identical inference, with fresh scoring."""
from common import *
from semantics import gold as base_gold,render as base_render,states
from position_spec import make_functions
from evaluator import score as base_score

def main():
    pgold,prender,pscore=make_functions(base_gold,base_render,base_score)
    domain='emotion';model='t5gemma';variant=0;template=4
    worlds={w['world_id']:w for w in rows(ROOT/f'position_foils/data/{domain}/worlds.jsonl')}
    original={w['world_id']:w for w in rows(ROOT/f'data/{domain}/worlds.jsonl')}
    assert worlds=={key:original[key] for key in worlds}
    assert [key for key,w in worlds.items() if w['split']=='test']==[key for key,w in original.items() if w['split']=='test']
    source_rows=rows(ROOT/f'data/{domain}/test_challenge.jsonl')
    target_rows=rows(ROOT/f'position_foils/data/{domain}/test.jsonl')
    source_pairs={(r['world_id'],r['state'],r['operation']):(r['source'],r['target']) for r in source_rows if r['template']==template}
    target_pairs={(r['world_id'],r['state'],r['operation']):(r['source'],r['target']) for r in target_rows if r['template']==variant}
    assert source_pairs==target_pairs and len(source_pairs)==256
    for w in worlds.values():
        for state in states(domain):
            assert base_render(w,state,template)==prender(w,state,variant)
            expected=pgold(w,state,variant);assert {k:v for k,v in expected.items() if k!='foil_variant'}==base_gold(w,state,template)
    destination=ROOT/'position_foils'/f'{model}_{domain}'
    manifest=[]
    for seed in (42,43,44):
        index=read(ROOT/'runs/formal'/f'{model}_{domain}_s{seed}'/'checkpoint_index.json')
        for role in ('P','N_h0','S_h0','M_h0','N_h1','S_h1','M_h1'):
            source=ROOT/'language_controls'/f'{model}_{domain}'/f's{seed}'/role/f'trajectory_t{template}.jsonl'
            if not source.exists():continue
            target=destination/f's{seed}'/role/f'trajectory_v{variant}.jsonl'
            if (destination/'dev_reconstruction.jsonl').exists() and not target.exists():
                # Never introduce a new cache shard once this model/domain starts.
                continue
            cp=index[role];assert digest(Path(cp['path']))==cp['sha256']
            converted=[];previous={};full={}
            for r in rows(source):
                assert r['template']==template
                r=dict(r,template=variant)
                key=(r['world_id'],r['trajectory'],r['mode']);step=r['step']
                if step==1:previous[key]=True;full[key]=True
                assert key in previous
                if r['gold'] is not None:
                    g=pgold(worlds[r['world_id']],r['state'],variant)
                    assert {k:v for k,v in g.items() if k!='foil_variant'}==r['gold']
                    r['gold']=g;r['score']=pscore(r['prediction'],g,worlds[r['world_id']],r['score']['ended'])
                r['previous_correct']=previous[key];full[key]=full[key] and r['score']['success'];r['full_success']=full[key];previous[key]=r['score']['success'];converted.append(r)
            assert len(converted)==1248
            if target.exists():assert rows(target)==converted
            else:target.parent.mkdir(parents=True,exist_ok=True);jsonl(target,converted)
            manifest.append(dict(seed=seed,condition=role,source=str(source.relative_to(ROOT)),source_sha256=digest(source),source_slurm_array_task='2587_6',target=str(target.relative_to(ROOT)),target_sha256=digest(target),rows=len(converted),checkpoint=cp,model_inputs_and_signed_operations_identical=True,all_current_states_render_identically=True,raw_predictions_and_masks_unchanged=True,new_scores_and_history_flags_recomputed_on_cpu=True,position_specification_sha256=digest(ROOT/'position_lock.json')))
    dump(ROOT/'POSITION_EXACT_REUSE_AUDIT.json',dict(reused_shards=len(manifest),files=manifest,atomic_input_target_pairs_checked=256,all_content_worlds_and_states_checked=True,test_world_batch_order_identical=True,selection_independent_of_scores=True,new_gpu_inference=False,original_gpu_inference_via_slurm=True))
    print('Exactly equivalent position trajectory shards:',len(manifest))

if __name__=='__main__':main()
