"""Serial CPU publisher, one commit/push/remote verification per terminal run."""
import argparse
import fcntl
from .common import *

def publish(stage):
    CONTROL.mkdir(exist_ok=True)
    with (CONTROL/'publish.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        receipts=read(CONTROL/'publications.json') if (CONTROL/'publications.json').exists() else []
        for folder in sorted((ROOT/'reports').glob(stage+'_*')):
            if not all((folder/name).exists() for name in ('RUN_STATUS.json','REPORT.md','ARTIFACTS.json')):continue
            key=str(folder);old=next((r for r in receipts if r['run']==key),None)
            if old and old['status']=='VERIFIED':continue
            assert command('git','branch','--show-current')==BRANCH
            if not old:
                dump(folder/'PUBLICATION_RECORD.json',dict(run=key,terminal_status=read(folder/'RUN_STATUS.json')['status'],source_manifest=stage,verified_before_commit=True))
                # Stage only this terminal report and shared implementation/metadata.
                changed=command('git','diff','--name-only','HEAD').splitlines()+command('git','ls-files','--others','--exclude-standard').splitlines()
                base=str(ROOT.relative_to(WT))+'/'
                report_root=str((ROOT/'reports').relative_to(WT))
                paths=[p for p in changed if p.startswith(base) and ('/reports/' not in p or str(Path(p).parent)==report_root or p.startswith(str(folder.relative_to(WT))+'/'))]
                if paths:command('git','add','--',*paths)
                command('git','commit','-m','drie-v1: '+folder.name+' terminal results and limitations')
                old=dict(run=key,commit=command('git','rev-parse','HEAD'),status='PUSH_PENDING');receipts.append(old);dump(CONTROL/'publications.json',receipts)
            try:
                command('git','push','-u','origin',BRANCH)
                remote=command('git','ls-remote','origin','refs/heads/'+BRANCH).split()[0]
                assert remote==command('git','rev-parse','HEAD')
                old.update(status='VERIFIED',remote_sha=remote)
            except Exception as e:
                old.update(status='PUSH_BLOCKED',error=str(e));dump(CONTROL/'publications.json',receipts);raise
            dump(CONTROL/'publications.json',receipts);print(json.dumps(old))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--stage',required=True);a=p.parse_args();publish(a.stage)
