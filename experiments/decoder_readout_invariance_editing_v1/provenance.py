"""CPU data lineage gates and idempotent exposure reconstruction."""
from .common import *

def control_core_allowed(candidate,recipient_split):
    # Metadata only. Never consult model outputs to select a different donor.
    worlds=rows(ROOT/'configs/worlds.jsonl');key=core(candidate)
    reserved={core(w) for w in worlds if w['split'] in ('test_iid','reserved_iid')}
    if key in reserved:return False
    same_split={core(w) for w in worlds if w['split']==recipient_split}
    historical_path=ROOT/'configs/historical_exposure_registry.jsonl'
    historical={tuple(r['core_content']) for r in rows(historical_path)} if historical_path.exists() else set()
    return key in same_split or key in historical

def update_registry():
    historical=ROOT/'configs/historical_exposure_registry.jsonl';records=rows(historical);by={tuple(r['core_content']):r for r in records}
    worlds=rows(ROOT/'configs/worlds.jsonl');lookup={w['world_id']:w for w in worlds+rows(ROOT/'configs/replay_worlds.jsonl')}
    for manifest in sorted((ROOT/'manifests').glob('*_registration.json')):
        reg=read(manifest);m=read(reg['manifest'])
        for task in m['tasks']:
            folder=Path(m['output_root'])/f"{task['model']}_s{task['seed']}";status=folder/'RUN_STATUS.json'
            if not status.exists():continue
            proof={p.stem.removesuffix('_qualification'):p for p in folder.glob('*_qualification.jsonl')}
            proof.update({p.stem:p for p in (folder/'source_worlds').glob('*.pt')})
            if task['stage']=='S0' and (folder/'SUMMARY.json').exists():
                proof.update({w['world_id']:status for w in worlds if w['split']=='train' and w in [x for x in worlds if x['split']=='train'][:8]})
            for wid,path in sorted(proof.items()):
                w=lookup[wid];key=core(w);rec=by.setdefault(key,dict(core_content=list(key),core_hash=objsha(key),history_and_checkpoint_provenance='immutable stage/run manifests; hashed actual artifacts',exposures=[]))
                rec['exposures'].append(dict(experiment='decoder_readout_invariance_editing_v1',stage=task['stage'],model=task['model'],seed=task['seed'],world_id=wid,declared_split=w['split'],template=0,exposure='neural state/qualification artifact exists',proof_path=str(path),proof_sha256=sha(path),manifest_sha256=sha(reg['manifest']),checkpoint_hash=task['checkpoint_hash']))
            if task['stage'] in ('S1_NATIVE','S2_NATIVE'):
                output=folder/('source_prefix_controls.jsonl' if task['stage']=='S1_NATIVE' else 'causal_conditions.jsonl')
                if not output.exists():continue
                entries=[r for r in rows(output) if task['stage']=='S1_NATIVE' or r['condition']=='NORMAL_COLOR_VALUE_RESAMPLE' and r.get('same_shape_mask')]
                for wid in sorted({r['world_id'] for r in entries}):
                    w=lookup[wid];changed=dict(w,color='red' if w['color']!='red' else 'blue');key=core(changed)
                    rec=by.setdefault(key,dict(core_content=list(key),core_hash=objsha(key),history_and_checkpoint_provenance='counterfactual color donor, retained exposure correction',exposures=[]))
                    rec['exposures'].append(dict(experiment='decoder_readout_invariance_editing_v1',stage=task['stage'],model=task['model'],seed=task['seed'],recipient_world_id=wid,recipient_split=w['split'],template=0,exposure='neural encoder/value projection control',proof_path=str(output),proof_sha256=sha(output),manifest_sha256=sha(reg['manifest']),checkpoint_hash=task['checkpoint_hash'],counterfactual_core=True))
    for name in ('PREDICTED_CORE_EXPOSURE_AUDIT.json','HISTORICAL_OUTPUT_EXPOSURE_AUDIT.json'):
        audit_path=ROOT/'results'/name
        if not audit_path.exists():continue
        digest=sha(audit_path);grouped={}
        for hit in read(audit_path)['hits']:
            key=tuple(hit['core_content']);grouped.setdefault(key,[]).append(hit)
        for key,hits in grouped.items():
            hit=hits[0]
            rec=by.setdefault(key,dict(core_content=list(key),core_hash=objsha(key),history_and_checkpoint_provenance='actual output text conservatively counted as core exposure',exposures=[]))
            entry=dict(experiment='decoder_readout_invariance_editing_v1' if name.startswith('PREDICTED') else 'historical_output_audit',world_id=hit['world_id'],declared_split=hit['split'],exposure='complete core appears in actual stored output; includes malformed grammar conservatively',proof_path=str(audit_path),proof_sha256=digest,matching_output_records=len(hits),representative_output_source=hit.get('source',hit.get('file')),representative_output_field=hit['field'])
            if entry not in rec['exposures']:rec['exposures'].append(entry)
    jsonl(ROOT/'world_exposure_registry.jsonl',[rec for key,rec in sorted(by.items())])
    return dict(core_records=len(by),historical_core_records=len(records),source='actual qualification/source-cache/terminal artifacts; no inference on metadata CPU')

if __name__=='__main__':print(update_registry())
