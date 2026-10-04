"""Allocation-only accounting, including failed attempts and account-wide peak."""
import subprocess,csv,io,re,datetime,os
from study import *
def gpus(tres):
    m=re.search(r'(?:^|,)gres/gpu=(\d+)',tres)
    if m:return int(m[1])
    m=re.search(r'(?:^|,)gres/gpu:[^=,]+=(\d+)',tres);return int(m[1]) if m else 0
def timevalue(s):
    try:return datetime.datetime.fromisoformat(s)
    except (ValueError,TypeError):return None
def main():
    ledger=read(ROOT/'submissions.json');ids=','.join(v['job_id'] for v in ledger);start=(datetime.datetime.fromisoformat(ledger[0]['created_utc'])-datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    columns='JobIDRaw,JobID,JobName,State,ExitCode,Start,End,ElapsedRaw,AllocTRES,ReqTRES,Partition,NodeList'
    raw=subprocess.check_output(['sacct','-X','--duplicates','-j',ids,'-S',start,'--format='+columns,'-P'],text=True)
    (ROOT/'slurm_accounting.psv').write_text(raw);records=list(csv.DictReader(io.StringIO(raw),delimiter='|'));events=[];total=0
    for r in records:
      n=gpus(r['AllocTRES']);sec=int(r['ElapsedRaw'] or 0);total+=n*sec/3600;s=timevalue(r['Start']);e=timevalue(r['End']) or (s+datetime.timedelta(seconds=sec) if s else None)
      if s and e and n:events.extend([(s,n),(e,-n)])
    def peak(events):
      value=maximum=0
      for _,delta in sorted(events,key=lambda x:(x[0],x[1])):value+=delta;maximum=max(maximum,value)
      return maximum
    ar=subprocess.check_output(['sacct','-X','--duplicates','-u',os.environ.get('USER','zailong'),'-S',start,'--format='+columns,'-P'],text=True);(ROOT/'account_all_jobs.psv').write_text(ar)
    account_events=[];earliest=min((t for t,d in events if d>0),default=None)
    for r in csv.DictReader(io.StringIO(ar),delimiter='|'):
      n=gpus(r['AllocTRES']);s=timevalue(r['Start']);e=timevalue(r['End']) or (s+datetime.timedelta(seconds=int(r['ElapsedRaw'] or 0)) if s else None)
      if n and s and e and earliest and e>earliest:account_events.extend([(max(s,earliest),n),(e,-n)])
    assert peak(events)<=2 and peak(account_events)<=2,'Hard account GPU limit violated'
    report=dict(at_utc=now(),gpu_hours=total,peak_project_gpus=peak(events),peak_account_gpus_since_first_allocation=peak(account_events),allocation_attempts=len(records),records=records,failures=[r for r in records if r['State'] not in ('COMPLETED','RUNNING','PENDING')])
    dump(ROOT/'resource_usage.json',report);print(json.dumps({k:v for k,v in report.items() if k not in ('records','failures')}))
if __name__=='__main__':main()
