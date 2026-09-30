"""Rescore G11 original manifests/outputs without changing historical artifacts."""
import collections
from common_g13 import *
def main():
    g11=ROOT.parent/'g11_semantic_history_v1'; manifest=json.loads((g11/'data/manifest.json').read_text()); cohort=json.loads((g11/'data/cohort_lock.json').read_text())
    for p,h in manifest['dependencies'].items(): assert digest(REPO/p)==h,p
    assert digest(g11/'data/worlds.jsonl')==manifest['worlds_sha256']
    for s in CFG['seeds']: assert digest(original(s))==cohort['checkpoint_hashes'][str(s)]
    worlds={w['record_id']:w for w in read(g11/'data/worlds.jsonl')}; counts=collections.defaultdict(lambda:dict(n=0,joint_k=0,exact_k=0,unresolved=0,date_error=0,fact_error=0)); checked=0
    for r in read(g11/'outputs/next_states.jsonl'):
        o=r['next'];sc=score(o['output'],o['frame'],worlds[r['record_id']],o['normal_end']); assert sc==o['score'];checked+=1
        if not r['strict_cohort']:continue
        c=counts[r['seed'],r['split'],r['anchor'],r['history']];c['n']+=1;c['joint_k']+=int(sc['joint_ok']);c['exact_k']+=int(o['exact']);c['unresolved']+=int(sc['parse_unresolved']);c['date_error']+=int(sc['parsed_date_error']);c['fact_error']+=int(sc['parsed_nondate_error'])
    expected={('iid',42):(80,50),('iid',43):(80,0),('iid',44):(80,0),('template_ood',42):(50,14),('template_ood',43):(60,0),('template_ood',44):(58,0)}
    for (split,s),(n,k) in expected.items(): assert counts[s,split,-1,2]['n']==n and counts[s,split,-1,2]['joint_k']==k
    dump(ROOT/'baseline/g11_archive_rescore.json',dict(passed=True,rows_rescored=checked,dependencies_and_checkpoint_hashes_match=True,key_rows=[dict(seed=k[0],split=k[1],anchor=k[2],history=k[3],**v) for k,v in counts.items()],main_report_key_rows_match=True,old_files_unchanged=True,code='audit_g11.py',G11_commit='0d9da457d8e8362064200ea1d53ecde5793134b9'))
    print('G11 archive scorer/checkpoint audit passed',checked,'rows',flush=True)
if __name__=='__main__': main()
