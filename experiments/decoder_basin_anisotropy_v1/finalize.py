"""Hash the small G8 release set without uploading frozen base checkpoints."""
import hashlib,importlib.metadata,json,platform,subprocess
from datetime import datetime,timezone
from pathlib import Path

HERE=Path(__file__).resolve().parent
FILES=(
 'REPORT.md','config.json','extract.py','analyze.py','audit.py','finalize.py','merge_t5.py','run.slurm',
 'states_bart.jsonl','states_t5gemma.jsonl','scan_bart.jsonl','scan_t5gemma.jsonl',
 'premerge_states_t5gemma.jsonl','premerge_scan_t5gemma.jsonl',
 'test_template_ood_states_t5gemma.jsonl','test_template_ood_scan_t5gemma.jsonl',
 'test_template_ood_extraction_t5gemma.json',
 'extraction_bart.json','extraction_t5gemma.json','directional_radii.csv','radius_summary.csv','direction_curves.csv',
 'paired_bootstrap.csv','early_warning.csv','curve_bart.svg','curve_t5gemma.svg',
 'pre_failure_cases.json','analysis_summary.json','audit.json',
)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=HERE,text=True).strip()
def main():
 files={n:dict(bytes=(HERE/n).stat().st_size,sha256=sha(HERE/n)) for n in FILES}
 versions={n:importlib.metadata.version(n) for n in ('torch','transformers','numpy','scipy','scikit-learn')}
 ext={b:json.loads((HERE/f'extraction_{b}.json').read_text()) for b in ('bart','t5gemma')}
 manifest=dict(experiment='G8 Decoder Basin Anisotropy',created_utc=datetime.now(timezone.utc).isoformat(),
               branch=git('branch','--show-current'),base_commit=git('rev-parse','HEAD'),python=platform.python_version(),packages=versions,
               jobs={b:ext[b]['slurm_job_id'] for b in ext},max_concurrent_gpus=2,
               frozen_editor_sha256={b:ext[b]['editor_sha256'] for b in ext},
               g7_feature_sha256={b:ext[b]['g7_features_sha256'] for b in ext},files=files)
 (HERE/'run_complete.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
 print(len(files),'files',sum(x['bytes'] for x in files.values()),'bytes')
if __name__=='__main__':main()
