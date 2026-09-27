"""Pinned public BART files, idempotent. No credentials used."""
import subprocess
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'models/bart-base'; p.mkdir(exist_ok=True)
for f in ['config.json','tokenizer.json','vocab.json','merges.txt','README.md','model.safetensors']:
 if (p/f).exists() and (p/f).stat().st_size>100: continue
 subprocess.run(['curl','--fail','--location','--max-time','300','https://huggingface.co/facebook/bart-base/resolve/aadd2ab0ae0c8268c7c9693540e9904811f36177/'+f,'-o',str(p/f)],check=True)
