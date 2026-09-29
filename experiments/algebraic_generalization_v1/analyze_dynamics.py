import csv,json
from collections import defaultdict
from pathlib import Path
import numpy as np
import torch

HERE=Path(__file__).resolve().parent
V3=HERE.parent/'reference_frame_pilot_v3'

def save(name,rs):
    with (HERE/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rs[0]),lineterminator='\n');w.writeheader();w.writerows(rs)

def main():
    source=torch.load(HERE/'source_latents.pt',map_location='cpu',weights_only=False)
    out=[];world_res={}
    for group in ['G3','repair']:
        data=torch.load(HERE/f'{group}_latents.pt',map_location='cpu',weights_only=False)
        for split in ['test_iid','test_template_ood']:
            ws=sorted({k.split('/')[1] for k in data if k.startswith(split+'/') and '/plus_chain/' in k})
            for w in ws:
                h0=source[f'{split}/{w}'];m=h0['mask'].bool()
                prev=h0['latent'].float()
                rs=[]
                for k in range(1,6):
                    h=data[f'{split}/{w}/plus_chain/{k}']['latent'].float()
                    rs.append((h-prev)[m].mean(0));prev=h
                world_res[group,split,w]=torch.stack(rs).numpy()
            for k in range(5):
                rr=np.stack([world_res[group,split,w][k] for w in ws])
                norms=np.linalg.norm(rr,axis=1)
                base=np.stack([world_res[group,split,w][0] for w in ws])
                align=np.sum(rr*base,axis=1)/(np.linalg.norm(rr,axis=1)*np.linalg.norm(base,axis=1))
                meanvec=rr.mean(0)
                between=float(np.mean(np.sum(rr*meanvec,axis=1)/(np.linalg.norm(rr,axis=1)*np.linalg.norm(meanvec))))
                out.append(dict(group=group,split=split,step=k+1,n=len(ws),mean_pooled_residual_norm=float(norms.mean()),
                                mean_cosine_to_first_residual=float(align.mean()),mean_cosine_to_group_direction=between,
                                residual_norm_ratio_to_first=float(norms.mean()/np.mean([np.linalg.norm(world_res[group,split,w][0]) for w in ws]))))
    save('residual_dynamics.csv',out)
    g3=torch.load(V3/'checkpoints/G3/best.pt',map_location='cpu',weights_only=True)
    repair=torch.load(HERE/'repair.pt',map_location='cpu',weights_only=True)
    spectrum=[]
    for group in ['G3','repair']:
        for op in ['T_plus','T_minus']:
            if group=='G3':
                U=g3[f'{op}.u.weight'].numpy();V=g3[f'{op}.v.weight'].numpy();J=np.eye(768)+U@V
            else:
                R=repair[f'{op}.R'].numpy();A=repair[f'{op}.A'].numpy();J=np.eye(768)+R.T@A@R
            sv=np.linalg.svd(J,compute_uv=False)
            eig=np.linalg.eigvals(J)
            spectrum.append(dict(group=group,operator=op,min_singular=float(sv.min()),max_singular=float(sv.max()),
                                 spectral_radius=float(abs(eig).max()),condition_number=float(sv.max()/sv.min()),
                                 singular_above_1_01=int((sv>1.01).sum()),singular_below_0_99=int((sv<.99).sum())))
    save('jacobian_spectrum.csv',spectrum)

if __name__=='__main__':main()
