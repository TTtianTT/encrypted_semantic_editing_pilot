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
        axes[0].set_ylabel('exact native token preservation');axes[-1].legend(fontsize=7,loc='lower left');fig.suptitle('Exploratory discovery / validation / old replay; full test endpoint BLOCKED')
        fig.tight_layout();fig.savefig(ROOT/'figures/01_readout_finite_paths.png',dpi=180);plt.close(fig)
    if (ROOT/'manifests/S1_NATIVE.json').exists():
        folder=Path(read(ROOT/'manifests/S1_NATIVE.json')['output_root'])/'bart_s42';path=folder/'propagation.jsonl'
        if path.exists():
            data=rows(path);names=sorted({r['module'] for r in data if r['module'].endswith(('encoder_attn','encoder_attn_layer_norm','fc2','final_layer_norm'))})
            fig,ax=plt.subplots(figsize=(12,5));values=[np.mean([r['relative_Frobenius'] for r in data if r['module']==n]) for n in names]
            ax.bar(range(len(names)),values);ax.set_xticks(range(len(names)),[n.replace('model.decoder.','') for n in names],rotation=75,ha='right',fontsize=7);ax.set_ylabel('within-module relative Frobenius difference');ax.set_title('Observed actual native outputs; not cross-module L2 shrinkage factors')
            fig.tight_layout();fig.savefig(ROOT/'figures/02_observed_propagation.png',dpi=180);plt.close(fig)
    if (ROOT/'results/VALIDATION_NUMERICAL_AUDIT.json').exists():
        data=read(ROOT/'results/VALIDATION_NUMERICAL_AUDIT.json')
        fig,axes=plt.subplots(1,2,figsize=(11,4))
        for source,ax in zip(['natural','history'],axes):
            for method,marker in [('Original','x'),('Plain','o')]:
                for r in data['atomic']:
                    if r['grouping']=='source' and r['source']==source and r['method']==method:
                        ax.scatter(r['target_rate'],r['content_rate'],marker=marker,s=70,label=method+' seed'+str(r['seed']))
            ax.set(xlabel='target accuracy',ylabel='non-target content preservation',title=source+' / 768 operations per seed',xlim=(-.04,1.08),ylim=(-.04,1.08));ax.grid(alpha=.2)
        axes[-1].legend(fontsize=7);fig.suptitle('64 validation worlds: Output-only / Mechanism / Random-site = NA (not trained)')
        fig.tight_layout();fig.savefig(ROOT/'figures/03_plain_reference_validation.png',dpi=180);plt.close(fig)
        fig,axes=plt.subplots(1,3,figsize=(12,4),sharey=True)
        for seed,ax in zip([42,43,44],axes):
            for method in ['Original','Plain']:
                rs=[r for r in data['trajectories'] if r['seed']==seed and r['method']==method]
                ax.plot([r['length'] for r in rs],[r['rate'] for r in rs],marker='o',label=method)
                if method=='Plain':
                    for r in rs:ax.annotate(str(r['complete_numerator'])+'/256',(r['length'],r['rate']),xytext=(0,8),textcoords='offset points',fontsize=8,ha='center')
            ax.set(title='seed'+str(seed),xlabel='trajectory length (all steps correct)',xticks=[1,2,3,5],ylim=(-.05,1.12));ax.grid(alpha=.2)
        axes[0].set_ylabel('complete trajectory success');axes[-1].legend();fig.suptitle('Own latent states; 64 validation worlds x 4 orders/directions; IID test blocked, OOD unavailable')
        fig.tight_layout();fig.savefig(ROOT/'figures/04_pure_latent_trajectories.png',dpi=180);plt.close(fig)
    if (ROOT/'results/causal_conditions_summary.csv').exists():
        records=list(csv.DictReader((ROOT/'results/causal_conditions_summary.csv').open()))
        fig,axes=plt.subplots(1,2,figsize=(11,4),sharey=True)
        for i,layer in enumerate([5,0]):
            labels=['AA','BA','AB','BB'];rs=[next(r for r in records if r['split']=='validation' and r['module']==f'model.decoder.layers.{layer}.encoder_attn' and r['scope']=='layer' and r['condition']==c) for c in labels]
            x=np.arange(4);axes[0].bar(x+(i-.5)*.34,[int(r['joint_numerator'])/int(r['free_generation_denominator']) for r in rs],width=.34,label='layer'+str(layer))
        axes[0].set(xticks=np.arange(4),xticklabels=['AA','BA','AB','BB'],title='K/V replacement: 32 worlds / 64 sides');axes[0].legend()
        qm=read(ROOT/'manifests/S2_QUERY_BRIDGE.json');qs=read(Path(qm['output_root'])/'bart_s42/SUMMARY.json')['conditions'];qs=[r for r in qs if r['split']=='validation']
        axes[1].bar(np.arange(len(qs)),[r['joint_numerator']/r['side_denominator'] for r in qs]);axes[1].set(xticks=np.arange(len(qs)),xticklabels=[r['condition'] for r in qs],title='Online query: 16 worlds / 32 sides')
        for ax in axes:ax.set_ylim(0,1.1);ax.set_xlabel('exact native intervention');ax.grid(axis='y',alpha=.2)
        axes[0].set_ylabel('joint current semantic success');fig.suptitle('Exploratory local causal evidence; donor + extra forward used in query diagnostics')
        fig.tight_layout();fig.savefig(ROOT/'figures/05_native_causal_interventions.png',dpi=180);plt.close(fig)
    dump(ROOT/'figures/FIGURE_INDEX.json',[dict(path=str(p),sha256=sha(p),rebuild='python experiments/decoder_readout_invariance_editing_v1/figures/rebuild.py',classification='observational / executed aggregate; no untested causal edges') for p in sorted((ROOT/'figures').glob('*.png'))])

if __name__=='__main__':rebuild()
