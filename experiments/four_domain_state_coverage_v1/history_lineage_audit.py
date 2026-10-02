"""Read-only hash verification of archived G14–G17 parameter references."""
from common import *

def main():
    checks=[];cached={}
    def visit(value,label):
        if isinstance(value,dict):
            if isinstance(value.get('path'),str) and isinstance(value.get('sha256'),str):
                p=Path(value['path']);expected=value['sha256']
                if p.is_file():
                    if str(p) not in cached:cached[str(p)]=digest(p)
                    actual=cached[str(p)];status='verified' if actual==expected else 'mismatch'
                else:actual=None;status='missing; historical claim not verified here'
                checks.append(dict(manifest_position=label,path=str(p),expected_sha=expected,actual_sha=actual,status=status))
            for k,v in value.items():visit(v,label+'/'+str(k))
        elif isinstance(value,list):
            for i,v in enumerate(value):visit(v,label+'/'+str(i))
    for d in ['g14_matched_state_handoff_v1','g15_self_state_transfer_v1','g16_capability_preserving_transfer_v1','g17_state_source_transfer_v1']:
        p=ORIGINAL/'.g17-worktree'/'experiments'/d/'checkpoints_manifest.json'
        if p.exists():visit(read(p),d)
    dump(ROOT/'HISTORICAL_CHECKPOINT_AUDIT.json',dict(references=checks,unique_local_files_hashed=len(cached),verified=sum(r['status']=='verified' for r in checks),unconfirmed=[r for r in checks if r['status']!='verified'],old_weights_reused_for_new_training=False,limits='Verifies existing referenced weight bytes and roles, not a fresh GPU reproduction of historical neural results; Git ancestry is not parameter ancestry'))
    print('Historical references',len(checks),'verified',sum(r['status']=='verified' for r in checks))

if __name__=='__main__':main()
