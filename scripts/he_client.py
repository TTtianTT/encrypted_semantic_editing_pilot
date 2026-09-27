"""Trusted CPU client. Secret key stays in this process and is never serialized.
Streaming protocol sends no residuals or decrypted text back to server.
"""
import base64,json,time,subprocess,sys,os,platform,signal
from pathlib import Path
import numpy as np
import tenseal as ts
import tenseal.sealapi as sa
ROOT=Path(__file__).resolve().parents[1];trusted=ROOT/'he/trusted';public=ROOT/'he/public'
def dump(p,o):p.write_text(json.dumps(o,indent=2))
start=time.monotonic();signal.alarm(3*3600+25*60)
p=sa.EncryptionParameters(sa.SCHEME_TYPE.CKKS);p.set_poly_modulus_degree(8192);p.set_coeff_modulus(sa.CoeffModulus.Create(8192,[60,40,40,60]));sc=sa.SEALContext(p,True,sa.SEC_LEVEL_TYPE.TC128)
assert sc.parameters_set(),sc.parameters_error_message()
t=time.perf_counter();ctx=ts.context(ts.SCHEME_TYPE.CKKS,8192,coeff_mod_bit_sizes=[60,40,40,60],n_threads=4);ctx.global_scale=2**40;ctx.generate_galois_keys();keygen=time.perf_counter()-t
# Serialization explicitly excludes secret key and unnecessary relin key.
public_bytes=ctx.serialize(save_public_key=True,save_secret_key=False,save_galois_keys=True,save_relin_keys=False);(public/'context.bin').write_bytes(public_bytes)
base_bytes=ctx.serialize(save_public_key=True,save_secret_key=False,save_galois_keys=False,save_relin_keys=False)
server=subprocess.Popen([sys.executable,str(ROOT/'scripts/he_server.py'),'--public',str(public)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=(ROOT/'logs/he_server.stderr').open('w'),text=True,cwd=public)
ready=json.loads(server.stdout.readline());assert ready['ready'] and not ready['has_secret_key']
source=np.load(trusted/'inputs.npz');w=np.load(public/'editor.npz');samples=json.load(open(trusted/'samples.json'))
params={'tenseal':ts.__version__,'poly_modulus_degree':8192,'coeff_mod_bit_sizes':[60,40,40,60],'scale':2**40,'seal_tc128_parameters_set':sc.parameters_set(),'tc128_max_coeff_modulus_bits':sa.CoeffModulus.MaxBitCount(8192,sa.SEC_LEVEL_TYPE.TC128),'keygen_s':keygen,'public_context_bytes':len(public_bytes),'public_context_without_galois_bytes':len(base_bytes),'galois_increment_bytes':len(public_bytes)-len(base_bytes),'threads_per_active_process':4,'hostname':platform.node(),'cpu':platform.processor(),'secret_key_serialized':False,'server_separate_process':True,'server_has_secret_key':ready['has_secret_key'],'leakage':'public valid-token count/mask; only valid tokens encrypted; fixed96 memory at trusted endpoint; method public','security_limit':'SEAL tc128 parameter validation, not security audit; same Unix UID lacks access-control isolation','codec_timing':'TenSEAL API combines CKKS encoding+encryption and decryption+decoding; separately reporting these internals unavailable','packing':'one768-dimensional token per4096-slot ciphertext; factorized768x64 then64x768','initialization_s':time.monotonic()-start}
dump(trusted/'parameters.json',params)
completed=[]
try:
 for i,sample in enumerate(samples):
  path=trusted/f'sample_{i:02}.json'
  if path.exists():completed.append(json.load(open(path)));continue
  t0=time.perf_counter();z=source['z'][i];mask=source['mask'][i].astype(bool);zf=source['float_edit'][i];valid=z[mask].astype(float)
  scale=2**40;q=lambda a:np.round(a*scale)/scale
  t=time.perf_counter();zq=z.astype(float).copy();zq[mask]=q(q(valid)+q(q(q(valid)@q(w['v'].astype(float)))@q(w['u'].astype(float)))+q(w['b'].astype(float)));quant_s=time.perf_counter()-t
  t=time.perf_counter();cs=[ts.ckks_vector(ctx,row.tolist()) for row in valid];enc_s=time.perf_counter()-t
  t=time.perf_counter();blobs=[c.serialize() for c in cs];serialize_s=time.perf_counter()-t
  request={'request_id':i,'ciphertexts':[base64.b64encode(b).decode() for b in blobs]}
  t=time.perf_counter();server.stdin.write(json.dumps(request)+'\n');server.stdin.flush();reply=json.loads(server.stdout.readline());roundtrip=time.perf_counter()-t
  row={'source_id':sample['source_id'],'split':'test','task':'StylePTB_TFU','seed':42,'method':'CKKS_lowrank_affine','n_valid_tokens':int(mask.sum()),'plaintext_memory_bytes':int(z.nbytes),'ciphertext_input_bytes':sum(map(len,blobs)),'encode_encrypt_s':enc_s,'client_serialize_s':serialize_s,'server_roundtrip_s':roundtrip,'quantized_control_s':quant_s,'server_report':{k:v for k,v in reply.items() if k!='ciphertexts'},'failure':reply.get('error')}
  if not row['failure']:
   t=time.perf_counter();outs=[base64.b64decode(b) for b in reply['ciphertexts']];ys=[ts.ckks_vector_from(ctx,b) for b in outs];load_s=time.perf_counter()-t
   t=time.perf_counter();decrypted=np.array([c.decrypt() for c in ys]);dec_s=time.perf_counter()-t
   zh=z.astype(float).copy();zh[mask]=decrypted
   row.update(ciphertext_output_bytes=sum(map(len,outs)),client_deserialize_s=load_s,decrypt_decode_s=dec_s,he_vs_float_max_abs=float(abs(zh-zf).max()),he_vs_float_l2=float(np.linalg.norm(zh-zf)),he_vs_float_relative_l2=float(np.linalg.norm(zh-zf)/np.linalg.norm(zf)),quant_vs_float_max_abs=float(abs(zq-zf).max()),he_vs_quant_max_abs=float(abs(zh-zq).max()))
   np.savez(trusted/f'sample_{i:02}.npz',he=zh,quant=zq)
  row['total_request_s']=time.perf_counter()-t0;dump(path,row);completed.append(row);print(json.dumps(row),flush=True)
finally:
 server.stdin.close();server.wait(timeout=60)
 dump(trusted/'operator_summary.json',{'n_planned':len(samples),'n_completed':len(completed),'failures':sum(bool(r['failure']) for r in completed),'wall_s':time.monotonic()-start,'requests':completed})
print('HE_OPERATOR_COMPLETE',flush=True)
