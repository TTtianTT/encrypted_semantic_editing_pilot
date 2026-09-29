"""Audit and hash this experiment's Git-visible delivery; never include base weights."""
import subprocess
from common import *
def main():
 names=subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','--','experiments/reference_frame_cross_backbone_v1'],cwd=REPO,text=True).splitlines()
 result={}
 for name in sorted(set(names)):
  p=REPO/name
  if p.name=='PUBLICATION_MANIFEST.json':continue
  assert not p.is_symlink() and p.is_file()
  assert p.name!='latest.pt' and p.suffix!='.safetensors'
  assert not any(s in p.parts for s in ['.models','.hf_cache','__pycache__'])
  n=p.stat().st_size;assert n<100_000_000,(name,n)
  result[str(p.relative_to(ROOT))]=dict(bytes=n,sha256=digest(p))
 dump('PUBLICATION_MANIFEST.json',dict(files=result,file_count=len(result),bytes=sum(r['bytes'] for r in result.values()),base_models_included=False,optimizer_recovery_included=False))
 print('publication files',len(result),'bytes',sum(r['bytes'] for r in result.values()))
if __name__=='__main__':main()
