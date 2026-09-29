"""Merge disjoint completed T5Gemma worlds from two one-GPU Slurm runs."""
import json,shutil,sys
from pathlib import Path

HERE=Path(__file__).resolve().parent;G7=HERE.parent/'repeated_intervention_stability_v1';G5=HERE.parent/'projection_hypothesis_v1';V3=HERE.parent/'reference_frame_pilot_v3';T5=HERE.parent/'t5gemma_composition_v1'
sys.path.insert(0,str(V3))
from common import digest

def read(p):return [json.loads(s) for s in p.read_text().splitlines()]
def write(p,rows):p.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows))
def key(r):return r['backbone'],r['split'],r['world_id'],r['step']

def main():
 cfg=json.loads((HERE/'config.json').read_text())
 main_states=HERE/'states_t5gemma.jsonl';main_scan=HERE/'scan_t5gemma.jsonl'
 shard_states=HERE/'test_template_ood_states_t5gemma.jsonl';shard_scan=HERE/'test_template_ood_scan_t5gemma.jsonl'
 shard_prov=json.loads((HERE/'test_template_ood_extraction_t5gemma.json').read_text())
 assert shard_prov['only_split']=='test_template_ood' and shard_prov['config']==cfg
 shutil.copyfile(main_states,HERE/'premerge_states_t5gemma.jsonl')
 shutil.copyfile(main_scan,HERE/'premerge_scan_t5gemma.jsonl')
 before={p.name:digest(p) for p in (main_states,main_scan,shard_states,shard_scan)}
 early=[r for r in read(main_states) if r['split']!='test_template_ood']
 later=read(shard_states)
 early_scan=[r for r in read(main_scan) if r['split']!='test_template_ood']
 later_scan=read(shard_scan)
 assert {r['split'] for r in early}=={'train','dev','test_iid'}
 assert {r['split'] for r in later}=={'test_template_ood'}
 states=early+later;scan=early_scan+later_scan
 state_keys={key(r) for r in states};assert len(state_keys)==len(states)
 assert all(key(r) in state_keys for r in scan)
 g7p=json.loads((G7/'extraction_t5gemma.json').read_text())
 world_ids={'train':g7p['world_ids']['train'][:cfg['worlds']['train_recorded_plan_first']],
            'dev':g7p['world_ids']['dev'][:cfg['worlds']['dev_recorded_plan_first']],
            'test_iid':g7p['world_ids']['test_iid'],
            'test_template_ood':g7p['world_ids']['test_template_ood']}
 assert {r['world_id'] for r in later}<=set(world_ids['test_template_ood'])
 write(main_states,states);write(main_scan,scan)
 provenance=dict(backbone='T5Gemma',pilot=False,only_split=None,config=cfg,slurm_job_id='1798+1800',source_jobs=['1798','1800'],
                 merge_source_sha256=before,editor_sha256=digest(T5/'editor_best.pt'),
                 g7_features_sha256=digest(G7/'features_t5gemma.jsonl'),g5_provenance_sha256=digest(G5/'provenance.json'),
                 world_ids=world_ids,states=len(states),scan_rows=len(scan),
                 baseline_scope='included current-success states; original batch-8 baseline exactness retained per state',
                 baseline_checks=len(states),baseline_text_exact=sum(s['g7_current_text_exact'] for s in states),
                 baseline_success_same=len(states),excluded_baseline_failure=0,
                 alpha_one_next_state_exact=sum(s['alpha_one_match_g7'] for s in states),
                 alpha_one_next_semantic_same=sum(s['alpha_one_next_gold_success']==(not s['next_failure']) for s in states),
                 max_effective_norm_ratio_error=max(abs(r['effective_norm_ratio']-1) for r in scan),
                 states_sha256=digest(main_states),scan_sha256=digest(main_scan),base_training='none',editor_training='none')
 (HERE/'extraction_t5gemma.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+'\n')
 print('merged',len(states),'states',len(scan),'scan rows',provenance['alpha_one_next_state_exact'],'alpha=1 exact')

if __name__=='__main__':main()
