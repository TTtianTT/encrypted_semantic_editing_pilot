"""Standalone scientific figures with per-seed panels and uncertainty."""
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/operator_residual_v2_mpl')
import ast
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from core import *

def table(name):return list(csv.DictReader((ROOT/f'results/{name}.csv').open()))
def export(fig,name):
    fig.savefig(ROOT/f'results/{name}.svg',bbox_inches='tight')
    fig.savefig(ROOT/f'results/{name}.png',bbox_inches='tight',dpi=180)
    plt.close(fig)

def main():
    colors={'S':'#20639b','S_R':'#d95f02','S_perp':'#249b80'}
    rows_a=table('attribution_summary')
    fig,axes=plt.subplots(2,3,figsize=(12,7),sharex=True,sharey=True)
    for row,direction in enumerate(('repair','injection')):
        metric='repair_joint' if direction=='repair' else 'preserved_current_next_failure'
        for col,seed in enumerate(SEEDS):
            ax=axes[row,col]
            for component,color in colors.items():
                for control in ('real','random'):
                    rs=sorted((r for r in rows_a if int(r['seed'])==seed and r['direction']==direction and r['component']==component and r['control']==control),key=lambda r:float(r['alpha']))
                    x=[float(r['alpha']) for r in rs];y=[float(r[metric]) for r in rs]
                    ci=np.array([ast.literal_eval(r[metric+'_ci95']) for r in rs])
                    ax.plot(x,y,'o-' if control=='real' else '--',color=color,label=component+(' random' if control=='random' else ''))
                    if control=='real':ax.fill_between(x,ci[:,0],ci[:,1],color=color,alpha=.10)
            ax.set_title(f'{direction.capitalize()}, seed {seed}');ax.set_ylim(-.03,1.03);ax.set_xticks(ALPHAS if 'ALPHAS' in globals() else [.25,.5,.75,1]);ax.grid(alpha=.2)
            if col==0:ax.set_ylabel('Current exact and next correct' if row==0 else 'Current exact and next failed')
            if row==1:ax.set_xlabel('Dose alpha')
    axes[0,0].legend(fontsize=8,ncol=2);fig.tight_layout();export(fig,'causal_dose')
    rs=table('visibility_summary');fig,axes=plt.subplots(1,3,figsize=(12,3.6),sharey=True)
    for ax,seed in zip(axes,SEEDS):
        for control,color in [('real','#20639b'),('random','#888888')]:
            vs=sorted((r for r in rs if int(r['seed'])==seed and r['control']==control),key=lambda r:float(r['alpha']))
            for context,style in [('pre','o--'),('post','o-')]:
                ax.plot([float(r['alpha']) for r in vs],[float(r['KL_'+context]) for r in vs],style,color=color,label=control+' '+context)
        ax.set_yscale('log');ax.set_title(f'Seed {seed}');ax.set_xlabel('Dose alpha');ax.grid(alpha=.2)
    axes[0].set_ylabel('Teacher forced KL per valid token');axes[0].legend(fontsize=8);fig.tight_layout();export(fig,'visibility')
    rs=table('decoder_summary');fig,axes=plt.subplots(3,3,figsize=(12,9),sharex=True,sharey=True)
    groups=['all','edited','entity_quantity','other']
    for row,seed in enumerate(SEEDS):
        for col,condition in enumerate(('K','V','KV')):
            ax=axes[row,col];values=np.zeros((6,4))
            for r in rs:
                if int(r['seed'])==seed and r['condition']==condition and r['layer']!='all':values[int(r['layer']),groups.index(r['group'])]=float(r['rate'])
            im=ax.imshow(values,vmin=0,vmax=1,cmap='Blues',aspect='auto')
            for i in range(6):
                for j in range(4):ax.text(j,i,f'{values[i,j]*100:.0f}',ha='center',va='center',fontsize=8,color='white' if values[i,j]>.55 else 'black')
            ax.set_title(f'Seed {seed}, {condition}');ax.set_xticks(range(4),['all','edited','entity/qty','other'],rotation=20);ax.set_yticks(range(6),range(1,7))
            if col==0:ax.set_ylabel('Decoder layer')
    fig.subplots_adjust(right=.9,hspace=.4);fig.colorbar(im,ax=axes.ravel().tolist(),fraction=.025,pad=.03,label='Next-step success');export(fig,'decoder_localization')
    rs=table('decoder_cumulative_summary');fig,axes=plt.subplots(1,3,figsize=(12,3.6),sharey=True)
    for ax,seed in zip(axes,SEEDS):
        for condition,color in [('K','#20639b'),('V','#d95f02'),('KV','#249b80')]:
            for direction,style in [('prefix','o-'),('suffix','x--')]:
                vs=sorted((r for r in rs if int(r['seed'])==seed and r['condition']==condition and r['direction']==direction),key=lambda r:int(r['layer_count']))
                ax.plot([int(r['layer_count']) for r in vs],[float(r['rate']) for r in vs],style,color=color,label=condition+' '+direction)
        ax.set_title(f'Seed {seed}');ax.set_xlabel('Number of replaced decoder layers');ax.set_xticks(range(1,7));ax.set_ylim(-.03,1.03);ax.grid(alpha=.2)
    axes[0].set_ylabel('Next-step success');axes[0].legend(fontsize=8,ncol=2);fig.tight_layout();export(fig,'decoder_cumulative')
    rs=table('projection_summary');fig,axes=plt.subplots(3,3,figsize=(12,8),sharex=True,sharey=True)
    palette=dict(none='#444444',mean='#d95f02',ridge='#20639b',random_ridge='#aaaaaa',reencode='#249b80')
    for row,template in enumerate((0,2,3)):
        for col,seed in enumerate(SEEDS):
            ax=axes[row,col]
            for r in rs:
                if int(r['seed'])!=seed or int(r['template'])!=template or r['sequence']!='primary':continue
                ax.plot(range(1,6),[float(r[f'R{k}']) for k in range(1,6)],'o--' if r['method']=='random_ridge' else 'o-',color=palette[r['method']],label=r['method'])
            ax.set_title(f'Template {template}, seed {seed}');ax.set_ylim(-.04,1.04);ax.set_xticks(range(1,6));ax.grid(alpha=.2)
            if col==0:ax.set_ylabel('Full trajectory success')
            if row==2:ax.set_xlabel('Chain length')
    axes[0,0].legend(fontsize=8,ncol=2);fig.tight_layout();export(fig,'projection_chains')
    print('Standalone SVG and PNG figures saved.')

if __name__=='__main__':main()
