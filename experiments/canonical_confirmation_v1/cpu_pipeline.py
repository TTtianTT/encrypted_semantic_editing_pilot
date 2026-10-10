"""Execute derived computation under an sbatch allocation with an srun step."""
from futils import *
import subprocess, py_compile, runpy
from datetime import datetime
def ledger():
 replay=read(ROOT/'results/cpu_replay_receipt.json')['job_id']
 cpu_receipts=[read(f) for f in (ROOT/'results').glob('cpu_*_receipt.json') if read(f)['job_id']!=int(os.environ['SLURM_JOB_ID'])]
 ids=[str(k) for k in range(3319,3326)]+sorted({str(r['job_id']) for r in cpu_receipts})
 for attempt in range(12):
  raw=subprocess.check_output(['sacct','-j',','.join(ids),'--noheader','--parsable2','--format=JobIDRaw,State,ExitCode,ElapsedRaw,Start,End,AllocTRES'],text=True)
  done=all(any(line.startswith(jid+'|COMPLETED|0:0|') for line in raw.splitlines()) and any(line.startswith(jid+'.0|COMPLETED|0:0|') for line in raw.splitlines()) for jid in ids)
  if done:break
  print('Waiting for completed allocation accounting',attempt,flush=True);time.sleep(2)
 assert done,raw
 jobs=[]
 for line in raw.splitlines():
  fields=line.split('|');jid,state,code,elapsed,start,end,tres=fields[:7]
  if jid not in ids:continue
  gpu=sum(int(v.split('=')[1]) for v in tres.split(',') if v.startswith('gres/gpu='))
  phase=dict(zip(range(3319,3326),['optimizer_controls','extract_fresh','train_final','eval_final','closure_final','mechanism_final','loss_old'])).get(int(jid))
  if phase is None:phase='cpu_'+next(r['phase'] for r in cpu_receipts if r['job_id']==int(jid))
  script='job.slurm' if gpu else 'job_cpu.slurm'
  jobs.append(dict(job_id=int(jid),phase=phase,state=state,exit_code=code,elapsed_seconds=int(elapsed),start=start,end=end,alloc_tres=tres,gpus=gpu,script=str((ROOT/script).relative_to(REPO)),command=f"sbatch --partition=B300q --export=ALL,{('FINAL_PHASE='+phase) if gpu else ('CPU_PHASE='+phase.removeprefix('cpu_'))} experiments/canonical_confirmation_v1/{script}",log=str((ROOT/f'logs/{jid}.out').relative_to(REPO))))
 assert len(jobs)==len(ids),(jobs,ids)
 events=[]
 for j in jobs:
  if j['gpus']:events.extend([(j['start'],j['gpus']),(j['end'],-j['gpus'])])
 running=peak=0
 for _,delta in sorted(events,key=lambda z:(z[0],z[1])):running+=delta;peak=max(peak,running)
 retries=subprocess.check_output(['sacct','-j','3326,3328,3333','--noheader','--parsable2','--format=JobIDRaw,State,ExitCode,ElapsedRaw,Start,End,AllocTRES'],text=True)
 dump('run_ledger.json',dict(jobs=jobs,allocation_seconds=sum(j['elapsed_seconds']*j['gpus'] for j in jobs),peak_gpus=peak,maximum_gpus=2,resource_amendment_sha256=sha(ROOT/'resource_amendment.json'),postprocessing_job_id=int(os.environ['SLURM_JOB_ID']),postprocessing_gpus=0,submission='All computations use sbatch allocations and srun steps; previous local derived analyses replayed in CPU allocation',sacct_raw=raw,superseded_cpu_attempts_sacct=retries,superseded_cpu_reason='3326/3328 lacked an explicit grouped-helper import; corrected and replayed. 3333 could not resolve the new review module via import lookup; switched the CPU driver to absolute script loading and replayed. No GPU or fresh model prediction affected.'))
def main():
 assert os.environ.get('SLURM_JOB_ID') and os.environ.get('SLURM_STEP_ID') is not None
 phase=sys.argv[1];receipt=dict(job_id=int(os.environ['SLURM_JOB_ID']),step_id=os.environ['SLURM_STEP_ID'],phase=phase,gpus=0,started=datetime.now().isoformat(),modules=[])
 for path in ROOT.glob('*.py'):py_compile.compile(str(path),doraise=True)
 modules={'replay':['analyze_existing','matched_context','context_figure','horizon_existing','summarize_controls'],'snapshot':['snapshot_final'],'review':['review_mechanism'],'closure_review':['preview_closure'],'single_review':['review_singles'],'finalize':['summarize_final','audit_final','report_final'],'refresh':['report_final']}[phase]
 if phase in ('finalize','refresh'):verify();verify('control_protocol.json');ledger()
 for name in modules:
  print('CPU phase',phase,name,flush=True);runpy.run_path(str(ROOT/f'{name}.py'))['main']();receipt['modules'].append(name)
 receipt['finished']=datetime.now().isoformat();dump(f'results/cpu_{phase}_receipt.json',receipt)
 if phase in ('finalize','refresh'):
  manifest={str(p.relative_to(ROOT)):sha(p) for p in sorted(ROOT.rglob('*')) if p.is_file() and not any(v in p.relative_to(ROOT).parts for v in ('local','logs','__pycache__','shards')) and p.name!='manifest.json' and p.suffix!='.tmp' and (p.suffix!='.jsonl' or 'data' in p.relative_to(ROOT).parts)}
  dump('manifest.json',dict(files=manifest,original_protocol_sha256=sha(ROOT/'protocol.json'),resource_amendment_sha256=sha(ROOT/'resource_amendment.json')))
  import re
  for label in re.findall(r'\]\(([^)]+)\)',(ROOT/'REPORT.md').read_text()):
   if label.startswith(('https://','http://')):continue
   assert (ROOT/label).is_file(),label
  assert all(sha(ROOT/name)==digest for name,digest in read(ROOT/'manifest.json')['files'].items())
  print('Manifest and local report links verified',flush=True)
if __name__=='__main__':main()
