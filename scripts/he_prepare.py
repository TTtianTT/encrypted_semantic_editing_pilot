import json,time,os
import numpy as np,torch
from pilot import ROOT,Runner,Editor,rows,dump
r=Runner();sd=42;rank=json.load(open(ROOT/'results/frozen_configuration.json'))['chosen_rank']
ed=Editor('lowrank_affine',r=rank).cuda();ed.load_state_dict(torch.load(ROOT/f'checkpoints/lowrank_affine_r{rank}_s42/best.pt',weights_only=True))
trusted=ROOT/'he/trusted';public=ROOT/'he/public';trusted.mkdir(parents=True,exist_ok=True);public.mkdir(parents=True,exist_ok=True);os.chmod(trusted,0o700)
rs=sorted(rows('test'),key=lambda x:x['source_id'])[:16]
torch.cuda.synchronize();t=time.perf_counter()
with torch.no_grad():
 x,_=r.batch(rs);z=r.model.get_encoder()(**x).last_hidden_state;ze=ed(z,x.attention_mask)
torch.cuda.synchronize();elapsed=time.perf_counter()-t
np.savez(trusted/'inputs.npz',z=z.cpu().numpy(),float_edit=ze.cpu().numpy(),mask=x.attention_mask.cpu().numpy())
np.savez(public/'editor.npz',v=ed.v.weight.detach().cpu().numpy().T,u=ed.u.weight.detach().cpu().numpy().T,b=ed.b.detach().cpu().numpy())
dump(trusted/'samples.json',rs);dump(trusted/'prepare.json',{'n':16,'shape':list(z.shape),'encode_edit_seconds':elapsed,'selection':'first16 sorted source_id test; includes all failures','parameters':sum(p.numel() for p in ed.parameters()),'float_dtype':'float32','job':os.environ.get('SLURM_JOB_ID')})
print('HE_INPUTS_READY',flush=True)
