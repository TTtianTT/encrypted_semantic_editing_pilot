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
            if not (folder/'RUN_STATUS.json').exists():continue
            key=str(folder);old=next((r for r in receipts if r['run']==key),None)
            if old and old['status']=='VERIFIED':continue
            assert command('git','branch','--show-current')==BRANCH
            if not old:
                command('git','add',str(ROOT.relative_to(WT)))
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
