"""CPU scientific plots reconstructed from complete stage records."""
import csv
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT.parent.parent))
from experiments.decoder_readout_invariance_editing_v1.common import read,rows,dump,sha
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

def rebuild():
    if (ROOT/'results/perturbation_curves.csv').exists():
        records=list(csv.DictReader((ROOT/'results/perturbation_curves.csv').open()))
        fig,axes=plt.subplots(1,3,figsize=(13,4),sharey=True)
        for ax,split in zip(axes,['discovery','validation','replay']):
            for pair in ['E_future_plus:N','E_future_plus:P']:
                for direction in ['real','isotropic','shared_rank4']:
                    rs=sorted([r for r in records if r.get('split')==split and r.get('source_pair')==pair and r.get('direction')==direction],key=lambda x:float(x['alpha']))
                    if rs:ax.plot([float(r['alpha']) for r in rs],[float(r['preservation']) for r in rs],marker='o',label=pair+' / '+direction)
            ax.set(title=split,xlabel='finite alpha',ylim=(-.05,1.05));ax.grid(alpha=.2)
        axes[0].set_ylabel('exact native token preservation');axes[-1].legend(fontsize=7,loc='lower left');fig.suptitle('Discovery / validation / old replay; independent test sealed')
        fig.tight_layout();fig.savefig(ROOT/'figures/01_readout_finite_paths.png',dpi=180);plt.close(fig)
    if (ROOT/'manifests/S1_NATIVE.json').exists():
        folder=Path(read(ROOT/'manifests/S1_NATIVE.json')['output_root'])/'bart_s42';path=folder/'propagation.jsonl'
        if path.exists():
            data=rows(path);names=sorted({r['module'] for r in data if r['module'].endswith(('encoder_attn','encoder_attn_layer_norm','fc2','final_layer_norm'))})
            fig,ax=plt.subplots(figsize=(12,5));values=[np.mean([r['relative_Frobenius'] for r in data if r['module']==n]) for n in names]
            ax.bar(range(len(names)),values);ax.set_xticks(range(len(names)),[n.replace('model.decoder.','') for n in names],rotation=75,ha='right',fontsize=7);ax.set_ylabel('within-module relative Frobenius difference');ax.set_title('Observed actual native outputs; not cross-module L2 shrinkage factors')
            fig.tight_layout();fig.savefig(ROOT/'figures/02_observed_propagation.png',dpi=180);plt.close(fig)
    plain=[]
    for p in (ROOT/'reports').glob('S3_PLAIN_*/SUMMARY.json'):
        r=read(p)
        if 'validation' in r:plain.append(r)
    if plain:
        fig,ax=plt.subplots(figsize=(6,4))
        for r in plain:ax.scatter(r['validation']['target'],r['validation']['content'],label='Plain seed'+str(r['seed']))
        ax.set(xlabel='validation target accuracy',ylabel='validation content preservation',title='Plain reference; Output-only / proposed / random pending')
        ax.legend();ax.grid(alpha=.2);fig.tight_layout();fig.savefig(ROOT/'figures/03_plain_reference_validation.png',dpi=180);plt.close(fig)
    dump(ROOT/'figures/FIGURE_INDEX.json',[dict(path=str(p),sha256=sha(p),rebuild='python experiments/decoder_readout_invariance_editing_v1/figures/rebuild.py',classification='observational / executed aggregate; no untested causal edges') for p in sorted((ROOT/'figures').glob('*.png'))])

if __name__=='__main__':rebuild()
