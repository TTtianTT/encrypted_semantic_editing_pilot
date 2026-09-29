from common import *
import re

def main():
 local={};public={};flags=[]
 for p in sorted(ROOT.rglob('*')):
  if not p.is_file() or '__pycache__' in p.parts or p.name in ['artifact_manifest.json','PUBLICATION_MANIFEST.json']:continue
  name=str(p.relative_to(ROOT));entry={'sha256':digest(p),'bytes':p.stat().st_size};local[name]=entry
  if p.name!='latest.pt':
   assert p.stat().st_size<100_000_000,(name,p.stat().st_size);public[name]=entry
   if p.suffix in ['.py','.md','.json','.jsonl','.log','.slurm','.txt']:
    text=p.read_text()
    if re.search(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|gh[pousr]_[A-Za-z0-9]{30,}|hf_[A-Za-z0-9]{30,}',text):flags.append(name)
 assert not flags,flags
 dump('artifact_manifest.json',local);dump('PUBLICATION_MANIFEST.json',public)
 print('public files',len(public),'bytes',sum(x['bytes'] for x in public.values()),'largest',max(public,key=lambda k:public[k]['bytes']))
if __name__=='__main__':main()
