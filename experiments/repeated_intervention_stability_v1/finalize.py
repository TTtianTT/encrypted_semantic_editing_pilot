"""Write the small-file G7 release manifest after analysis and audit."""
import hashlib
import importlib.metadata
import json
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path

HERE=Path(__file__).resolve().parent
FILES=(
 'REPORT.md','config.json','extract.py','extract_bart.slurm','extract_t5gemma.slurm',
 'analyze.py','cases.py','audit.py','finalize.py',
 'features_bart.jsonl','features_t5gemma.jsonl',
 'agreement_bart.json','agreement_t5gemma.json',
 'extraction_bart.json','extraction_t5gemma.json',
 'predictor_comparison.csv','within_step_auroc.csv','test_predictions.csv',
 'stability_curves.csv','stability_curve_bart.svg','stability_curve_t5gemma.svg',
 'pre_failure_examples.json','pre_failure_trajectories.json','analysis_summary.json','audit.json',
)

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=HERE,text=True).strip()

def main():
 files={name:dict(bytes=(HERE/name).stat().st_size,sha256=digest(HERE/name)) for name in FILES}
 versions={name:importlib.metadata.version(name) for name in ('torch','transformers','numpy','scipy','scikit-learn')}
 extract={name:json.loads((HERE/f'extraction_{name}.json').read_text()) for name in ('bart','t5gemma')}
 manifest=dict(experiment='G7 repeated intervention stability diagnosis',created_utc=datetime.now(timezone.utc).isoformat(),
               branch=git('branch','--show-current'),base_commit=git('rev-parse','HEAD'),python=platform.python_version(),packages=versions,
               slurm=dict(bart_job=1777,t5gemma_job=1778,gpus_per_job=1,max_concurrent_gpus=2),
               frozen_editor_sha256={name:extract[name]['editor_sha256'] for name in extract},
               frozen_base_reference='G3/G5 provenance and t5gemma_composition_v1/base_model_manifest.json',
               world_source_sha256={name:extract[name]['world_file_sha256'] for name in extract},
               files=files)
 (HERE/'run_complete.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
 print(len(files),'release files',sum(x['bytes'] for x in files.values()),'bytes')

if __name__=='__main__':main()
