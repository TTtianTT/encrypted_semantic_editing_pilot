"""Server protocol endpoint: public context, public affine weights, ciphertext only.
No torch, decoder, private key, source text or plaintext latent is loaded here.
Same-UID host is not an OS security boundary; deploy under separate hosts/users.
"""
import argparse,base64,json,sys,time
from pathlib import Path
import numpy as np
import tenseal as ts
p=argparse.ArgumentParser();p.add_argument('--public',type=Path,required=True);a=p.parse_args()
ctx=ts.context_from((a.public/'context.bin').read_bytes(),n_threads=4)
assert ctx.is_public() and not ctx.has_secret_key()
w=np.load(a.public/'editor.npz');v=w['v'].astype(float).tolist();u=w['u'].astype(float).tolist();b=w['b'].astype(float).tolist()
print(json.dumps({'ready':True,'has_secret_key':ctx.has_secret_key(),'tenseal':ts.__version__}),flush=True)
for line in sys.stdin:
 request=json.loads(line);out=[];elapsed=0.;deserialize=0.;serialize=0.
 try:
  for blob in request['ciphertexts']:
   t=time.perf_counter();z=ts.ckks_vector_from(ctx,base64.b64decode(blob));deserialize+=time.perf_counter()-t
   t=time.perf_counter();delta=z.matmul(v).matmul(u);edited=delta+z+b;elapsed+=time.perf_counter()-t
   t=time.perf_counter();out.append(base64.b64encode(edited.serialize()).decode());serialize+=time.perf_counter()-t
  print(json.dumps({'request_id':request['request_id'],'ciphertexts':out,'eval_s':elapsed,'deserialize_s':deserialize,'serialize_s':serialize,'n_tokens':len(out),'matrix_multiply_calls':2*len(out),'ciphertext_multiplications':0,'depth_plain_multiplications':2}),flush=True)
 except Exception as e:
  print(json.dumps({'request_id':request['request_id'],'error':type(e).__name__+': '+str(e),'eval_s':elapsed}),flush=True)
