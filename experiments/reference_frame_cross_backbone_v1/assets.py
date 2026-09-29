"""CPU/network acquisition only. Never print credentials or auto-accept licenses."""
import time,platform,importlib.metadata,inspect,os
from huggingface_hub import HfApi,hf_hub_download,snapshot_download
from common import *
def main():
 api=HfApi();env={k:importlib.metadata.version(k) for k in ['torch','transformers','huggingface-hub','tokenizers','safetensors','numpy']};env['python']=platform.python_version();dump('environment.json',env)
 for name in MODELS:
  dest=ROOT/f'models/{name}.json'
  prior=json.loads(dest.read_text()) if dest.exists() else {}
  base=Path(os.environ.get('RF_MODEL_ROOT','/dataset1/zailong/models/reference-frame-cross-backbone'))/name
  if prior.get('status')=='downloaded' and str(base)==prior.get('directory') and all((base/f).is_file() and (base/f).stat().st_size==v['bytes'] for f,v in prior['files'].items()):continue
  start=time.monotonic();info=None
  try:
   # Published manifests retain the originally tested revision on a fresh checkout.
   if prior.get('revision'):rev=prior['revision']
   else:info=api.model_info('google/'+name);rev=info.sha
   # Establish actual access before attempting large weights.
   hf_hub_download('google/'+name,'config.json',revision=rev,local_dir=base)
   snapshot_download('google/'+name,revision=rev,local_dir=base,allow_patterns=['*.json','*.safetensors','*.model','*.txt','*.jinja','README.md'],ignore_patterns=['onnx/*','onnx/**'],max_workers=4)
   files={str(p.relative_to(base)):{'sha256':digest(p),'bytes':p.stat().st_size} for p in base.rglob('*') if p.is_file() and '.cache' not in p.parts}
   dump(f'models/{name}.json',dict(model_id='google/'+name,revision=rev,tokenizer_revision=rev,status='downloaded',directory=str(base),download_seconds=time.monotonic()-start,files=files))
   print(name,'downloaded',rev,flush=True)
  except Exception as e:
   # HF exceptions may contain request IDs but never include auth headers here.
   dump(f'models/{name}.json',dict(model_id='google/'+name,revision=prior.get('revision') or (info.sha if info else None),status='unavailable',exception=type(e).__name__,reason=str(e)[:1200],download_seconds=time.monotonic()-start));print(name,type(e).__name__,flush=True)
if __name__=='__main__':main()
