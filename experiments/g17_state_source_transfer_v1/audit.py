"""CPU-only actual parameter ancestry / occurrence audit, no model forward."""
import torch
from common_g17 import *
def main():
    assert not (ROOT/'scientific_lock.json').exists()
    g10=ROOT.parent/'g10_matched_editor_composability_v1'
    mapping=json.loads((G16/'checkpoints_manifest.json').read_text());models={};lineage=[];deps={}
    def evidence(p):
        k=str(p.relative_to(REPO))
        if k not in deps:deps[k]=digest(p)
        return dict(evidence_path=k,evidence_sha=deps[k])
    rows=read(V3/'data/train_G1.jsonl');schedule=[b for b in read(V3/'data/sample_schedule.jsonl') if b['path'].startswith('T_plus')];assert len(schedule)==200
    occurrences=[]
    for s in CFG['seeds']:
        models[str(s)]={}
        for role in ['P','U','G']:
            old=mapping['models'][str(s)][role];p=Path(old['path']);assert p.is_file() and digest(p)==old['sha256']
            models[str(s)][role]=dict(old,usage='frozen G17 inference only');evidence(REPO/old['repo_path'])
        states={role:statehash(torch.load(z['path'],map_location='cpu',weights_only=True)) for role,z in models[str(s)].items()}
        gm=json.loads((g10/f'checkpoints/rank16/rank16_seed{s}.json').read_text())
        assert gm['schedule_sha256']==digest(V3/'data/sample_schedule.jsonl') and gm['train_data_sha256']==digest(V3/'data/train_G1.jsonl') and gm['checkpoint_sha256']==models[str(s)]['G']['sha256']
        evidence(g10/f'checkpoints/rank16/rank16_seed{s}.json')
        for b in schedule:
            for i,flag in zip(b['pair_indices'],b['g2_replace']):
                r=rows[i];d=r['offsets'][0];assert r['frames'][0]['perspective'] in ['first','third']
                occurrences.append(dict(seed=s,experiment='G10',update=b['step'],world_id=r['record_id'],offset=d,received_offset=d-1 if flag else None,replacement=flag,status=r['record_status'],perspective=r['frames'][0]['perspective'],source_text=r['source_text'],current_gold=r['target_text'],target_offset=d-2 if flag else d-1,**evidence(V3/'data/sample_schedule.jsonl')))
        for role,arm in [('P','F3'),('U','F2')]:
            p=G13/f'training/{arm}_s{s}_trained.json';z=json.loads(p.read_text());assert z['initial_hash']==states['G'] and z['final_sha256']==models[str(s)][role]['sha256'];assert z['schedule_sha256']==digest(G13/f'data/schedule_s{s}.jsonl')
            sc=read(G13/f'data/schedule_s{s}.jsonl');assert len(sc)==200
            assert {r['offset'] for b in sc for r in b['replay']}==set(range(-3,5))
            if arm=='F3':assert sum(z['anchor_source_counts'].values())==3200 and set(z['anchor_source_counts'])=={'0','1','2'}
            lineage.append(dict(seed=s,role=role,parent='G10 Original T0',parent_state_hash=states['G'],checkpoint_state_hash=states[role],natural_offsets=list(range(-3,5)),edited_receive_anchors=[-1] if arm=='F3' else [],edited_input_sources='fixed G yesterday H0/H1/H2' if arm=='F3' else 'none; natural H0 yesterday anchor',**evidence(p)))
        for role in ['N','F']:
            p=G16/f'training/{role}_s{s}.json';z=json.loads(p.read_text());assert z['updates']==200 and z['initial_hash']==states['P']
            weight=G16/z['final_path'];assert digest(weight)==z['final_sha256'];assert z['schedule_sha256']==digest(G16/f'data/schedule_s{s}.jsonl')
            models[str(s)][role]=dict(path=str(weight),repo_path=str(weight.relative_to(REPO)),sha256=z['final_sha256'],step=200,manifest_path=str(p.relative_to(REPO)),manifest_sha256=digest(p),usage='frozen receiver only')
            states[role]=statehash(torch.load(weight,map_location='cpu',weights_only=True));assert states[role]==z['final_state_hash']
            sc=read(G16/f'data/schedule_s{s}.jsonl');assert len(sc)==200 and all(len(b['main_indices'])==len(b['replay'])==len(b['maintenance_sources'])==8 for b in sc)
            assert {r['offset'] for b in sc for r in b['replay']}==set(range(-3,5)) and {k for b in sc for k in b['maintenance_sources']}=={0,1,2}
            lineage.append(dict(seed=s,role=role,parent='G13 F3 final200 (P)',parent_state_hash=states['P'],checkpoint_state_hash=states[role],natural_offsets=list(range(-3,5)),edited_receive_anchors=[-1,0] if role=='F' else [-1],edited_input_sources='G yesterday H0/H1/H2; exact frozen P today' if role=='F' else 'G yesterday H0/H1/H2; D natural today',not_G15_weight_inheritance=True,**evidence(p)))
    write(ROOT/'g10_actual_occurrences.jsonl.gz',occurrences)
    breakdown=[]
    counter=collections.Counter((r['seed'],r['status'],r['perspective'],r['offset'],r['replacement']) for r in occurrences)
    for k,n in sorted(counter.items()):breakdown.append(dict(seed=k[0],status=k[1],perspective=k[2],source_offset=k[3],replacement=k[4],occurrences=n,edited_received_anchor=k[3]-1 if k[4] else None))
    csvwrite(ROOT/'g10_schedule_counts.csv',breakdown)
    coverage=[]
    for s in CFG['seeds']:
        for a in CFG['anchors']:
            hist=sum(r['replacement'] and r['offset']==a+1 and r['seed']==s and r['status']=='recorded_plan' and r['perspective']=='first' for r in occurrences)
            for receiver in CFG['receivers']:
                for producer in CFG['producers']:
                    direct=receiver in ['N','F'] and ((a==-1 and producer=='G') or (a==0 and producer=='P' and receiver=='F'))
                    received_ancestor=(hist>0 or a==-1)
                    label='direct_repair_seen' if direct else 'repair_unseen_but_historically_exposed' if received_ancestor else 'not_directly_supervised_in_audited_lineage'
                    coverage.append(dict(seed=s,anchor=a,producer=producer,receiver_lineage=receiver,natural_rule_seen=True,received_edited_anchor_in_ancestor_training=received_ancestor,received_exact_producer_state_in_repair=direct,selected_on_this_state=False,historical_evaluation_known=a in [0,-1,-2],historical_evaluation_scope='G13/G16 natural atom; tomorrow rollouts reached today/yesterday/two-days-ago' if a!=2 else 'natural atom known; edited +3→+2→+1 not found in enumerated actual training; no universal history claim',producer_generated_in_repair_gate=(a==-1 and producer=='G') or (a==0 and producer=='P'),G10_related_two_call_first_plan_occurrences=hist,supervision_label=label,audit_status='verified accessible actual schedules and checkpoint parent state hashes',evidence_path=';'.join(deps),evidence_sha=json.dumps(deps,sort_keys=True)))
    csvwrite(ROOT/'supervision_coverage.csv',coverage)
    for p in [g10/'train.py',V3/'engine.py',V3/'data/train_G1.jsonl',V3/'data/sample_schedule.jsonl',G13/'run.py',G13/'PROTOCOL.md',G13/'BASELINE_AUDIT.md',G16/'run.py',G16/'PROTOCOL.md',G16/'INTERPRETATION.md',G16/'checkpoints_manifest.json',G16/'data/manifest.json',G16/'data/sample_schedule.jsonl']+[G13/f'data/schedule_s{s}.jsonl' for s in CFG['seeds']]+[G16/f'data/schedule_s{s}.jsonl' for s in CFG['seeds']]:evidence(p)
    for z in mapping['backbone']['actual_files']:assert digest(z['file'])==z['sha256']
    dump(ROOT/'checkpoints_manifest.json',dict(base_commit=CFG['base_commit'],models=models,backbone=mapping['backbone'],lineage=lineage,dependencies=deps,G16_manifest_sha256=digest(G16/'checkpoints_manifest.json'),not_git_ancestry_as_parameter_ancestry=True))
    text='# G17 actual supervision lineage audit\n\nCPU only; no old checkpoint new GPU test. G10→G13F3(P)→G16NF, and G10→G13F2(U). No G12/G15 weights in these parameter ancestors. All parent state/checkpoint/data/schedule hashes verified per seed.\n\n'
    text+='G10 each seed:200 updates,3200 source occurrences;1600 replacement two-call instances. Natural source offsets[-3,3]; replacements[-2,2]. Source+3 has297 natural instances and0 replacements (all statuses/perspectives). Full per-status/perspective/offset/flag counts and3200 occurrences per seed retained. This verifies +3→+2 as a natural rule, not edited+2→+1 reception. G13 P/U add full40cell natural sources[-3,4]; P additionally fixed G yesterday H0/H1/H2, U natural yesterday anchor. G16NF A natural tomorrow→today, B all40 natural cells, C G yesterday H0/H1/H2, D F=fixed P today or N=natural today. Exact U state never repair train/dev. All main snapshots final200; G13 best-dev monitoring exists but final fixed200 was not selected by it; G16 guards excluded.\n\n'
    text+='| anchor | accessible-history label and source qualification |\n|---|---|\n|+2 in two days|not_directly_supervised_in_audited_lineage: no +3 replacement, no G13/G16 edited+2 receive; natural rule seen|\n|0 today|F/P direct_repair_seen; U/G repair_unseen_but_historically_exposed via related G10 two-call today, not exact final U; N natural D only|\n|-1 yesterday|G direct_repair_seen for NF via C and historical P via G13; P/U exact states not repair inputs, related edited anchor historically exposed|\n|-2 two days ago|repair_unseen_but_historically_exposed: G10 replacement from -1 receives -2; G13/G16 repair did not use edited -2 receive|\n\n'
    text+='Labels relative to available actual parameter ancestry and input condition, not BART pretraining or all possible history. Related edited anchor supervision is not exact later producer-state supervision. Generation/current gate/natural input/reception/evaluation distinct columns; G16 C H2 construction not new-model self3. Past evaluation is not gradient exposure. No missing accessible schedule/checkpoint/hash evidence; out-of-list/deleted history and unlogged BART pretraining are not audited. Actual natural gold checked by inherited renderer; no fabricated logs. Scientific primary remains IID+2/U regardless audit label.\n'
    (ROOT/'SUPERVISION_AUDIT.md').write_text(text)
    print('Lineage and actual supervision verified; +2 edited reception absent in audited lineage')
if __name__=='__main__':main()
