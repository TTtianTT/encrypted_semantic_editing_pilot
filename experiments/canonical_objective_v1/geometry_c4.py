"""Post-hoc CPU geometry of saved C4 maps; no new training or decoding."""
from cutil import *

def main():
    p=read(ROOT/'protocol.json');a=canonical('eval',0,1);b=canonical('eval',0,0);h=a['h'];m=a['m'];d=(b['h']-h)*m[...,None];out=[]
    for seed in SEEDS:
      for k in p['training']['evaluation_C4_checkpoints']:
        ck=load(ROOT/f'local/C4_s{seed}_{k:04d}.pt')['editor'];z=h+(h@ck['plus.v.weight'].T@ck['plus.u.weight'].T+ck['plus.b'])*m[...,None];e=(z-b['h'])*m[...,None];co=(e*d).sum((1,2))/d.square().sum((1,2));orth=e-co[:,None,None]*d
        frac=orth.square().sum((1,2))/e.square().sum((1,2));mse=e.square().sum((1,2))/(m.sum(1)*768)
        out.append(dict(seed=seed,update=k,template=0,source_state=1,target_state=0,worlds=80,mean_coefficient=float(co.mean()),coefficient_ci95_world_bootstrap=old.bootstrap_mean(co.numpy()),positive_count=int((co>0).sum()),token_mse=float(mse.mean()),mean_orthogonal_energy_fraction=float(frac.mean()),post_hoc=True))
    dump('results/c4_geometry.json',out)

if __name__=='__main__':main()
