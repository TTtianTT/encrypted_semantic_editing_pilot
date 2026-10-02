"""CPU-only creation of a separately frozen observable-relation holdout study."""
import shutil
from common import *

def main():
    target=ROOT.parent/'space_relation_confirmation_v1'
    assert not target.exists(),'Do not overwrite an existing confirmation study'
    target.mkdir()
    modules=['backend.py','train.py','evaluate.py','formal.py','sources.py','behavioral.py','probe.py','run.py','evaluator.py','semantics.py','prepare.py','tests.py','check_data.py','analyze.py','publish.py','restore_archives.py','check_training_budget.py']
    for name in modules:shutil.copyfile(ROOT/name,target/name)
    code=(ROOT/'common.py').read_text().replace("DOMAINS = ['time', 'space', 'emotion', 'person']","DOMAINS = ['space']")
    (target/'common.py').write_text(code)
    code=(target/'semantics.py').read_text()
    code=code.replace("    elif domain == 'emotion':\n", "    elif domain == 'space':\n        result = (current - delta) % 4  # CW facing rotation reduces relative bearing\n    elif domain == 'emotion':\n")
    code=code.replace("        out.update(relation=relation(world,current), heading=current,", "        dx=world['object_xy'][0]-world['observer_xy'][0]\n        dy=world['object_xy'][1]-world['observer_xy'][1]\n        ray_heading=0 if dy>0 else 2 if dy<0 else 1 if dx>0 else 3\n        heading=(ray_heading-current)%4\n        bearing=['front','right','back','left'][current]\n        assert relation(world,heading)==bearing\n        out.update(relation=bearing, heading=heading,")
    code=code.replace("heading={current}; relation=", "heading={g['heading']}; relation=")
    (target/'semantics.py').write_text(code)
    # Worlds and all their split assignments stay identical. Natural atomic text
    # pair sets must be exactly equal; only state stratification/order changes.
    shutil.copyfile(ROOT/'model_manifest.json',target/'model_manifest.json')
    (target/'data/space').mkdir(parents=True)
    shutil.copyfile(ROOT/'data/space/worlds.jsonl',target/'data/space/worlds.jsonl')
    old_status=[dict(run=p.parent.parent.name,gate=read(p)) for p in sorted((ROOT/'runs/formal').glob('*_space_*/dev/admission.json'))]
    dump(target/'prior_evidence.json',dict(original_gate_evidence=old_status,reason='Absolute facing index varied independently of object world ray; original edited holdout did not exclude visible relative relations.',old_outputs_preserved=True,unchanged_original_lock_sha=digest(ROOT/'formal_lock.json'),original_semantics_sha=digest(ROOT/'semantics.py'),aborted_in_place_attempt='Guard failed before any data/config/lock mutation; temporary space-only semantics edit restored byte-for-byte.'))
    cfg=read(ROOT/'config.json');cfg.pop('scientific_plan_sha');cfg.pop('data_spec_sha');cfg.pop('data_manifest_sha');cfg.pop('pre_formal_amendment_sha')
    cfg['study']='space_relation_confirmation_v1';cfg['state_definition']='relative bearing: 0 front,1 right,2 back,3 left; physical heading=(object cardinal world ray - state) mod4; plus turns physical heading CW90 and decrements bearing state'
    dump(target/'config.json',cfg)
    tasks=[dict(phase='formal',model=m,domain='space',seed=s,index=i) for i,(m,s) in enumerate((m,s) for m in MODELS for s in (42,43,44))]
    dump(target/'tasks.json',tasks)
    (target/'logs').mkdir()
    (target/'job.slurm').write_text((ROOT/'job.slurm').read_text().replace('fdsc-v1','fdsc-space-confirm-v1').replace('four_domain_state_coverage_v1','space_relation_confirmation_v1'))
    (target/'.gitignore').write_text((ROOT/'.gitignore').read_text())
    dump(target/'SOURCE_LINEAGE.json',dict(base_model_manifest_sha=digest(target/'model_manifest.json'),historical_editor_weights_used=False,original_study_editor_weights_used=False,P='fresh rank16 atomic editor from identity,600steps,dev NLL selection',Q='its frozen step300 checkpoint',U='fresh independent seed+10000 producer',N_S_M='identical selected P initialization,200updates each, two relative-relation holdout partitions',differences='space current-state stratification only; same content-world splits and exact natural source/target text pair sets; no model, parser, loss, decoding or budget change'))
    print(target)

if __name__=='__main__':main()
