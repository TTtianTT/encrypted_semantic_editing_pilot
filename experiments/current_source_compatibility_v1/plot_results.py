"""Standalone behavior plots from fixed200 results, CPU only."""
import csv,statistics,sys,os
from pathlib import Path
plot_root=Path(__file__).resolve().parent
sys.path.insert(0,str(plot_root/'local/plot_packages'))
os.environ['MPLCONFIGDIR']=str(plot_root/'local/mplconfig')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from study import *
def main():
    assert read(ROOT/'ANALYSIS_AUDIT.json')['all_seeds_complete']
    data=list(csv.DictReader((ROOT/'summary_by_seed.csv').open()))
    fig,axes=plt.subplots(2,2,figsize=(10,6),sharex=True,sharey=True,constrained_layout=True)
    colors={'T0':'#777777','N':'#222222','F':'#0072B2','R':'#D55E00'}
    values=[]
    for col,test in enumerate(('iid','ood')):
        for row,metric in enumerate(('full','endpoint')):
            ax=axes[row,col]
            for condition in ('T0','N','F','R'):
                group=[]
                for k in range(1,6):
                    rs=[r for r in data if r['source']=='latent' and r['cohort']=='long_paths' and r['condition']==condition and r['test']==test and r['metric']==f'{metric}{k}_all' and r['update']==('0' if condition=='T0' else '200')]
                    assert len(rs)==3 and {int(r['seed']) for r in rs}=={42,43,44}
                    rates=[float(r['rate'])*100 for r in rs];group.append(rates)
                    values.append(dict(condition=condition,test=test,metric=metric,step=k,seed_rates_pp=rates))
                means=[statistics.mean(v) for v in group];lower=[min(v) for v in group];upper=[max(v) for v in group]
                ax.plot(range(1,6),means,label=condition,color=colors[condition],marker='o',linestyle='--' if condition=='T0' else '-')
                ax.fill_between(range(1,6),lower,upper,color=colors[condition],alpha=.12)
            ax.set_ylim(-2,102);ax.set_xticks(range(1,6));ax.grid(alpha=.2)
            if col==0:ax.set_ylabel('Full trajectory (%)' if metric=='full' else 'Endpoint (%)')
            if row==0:ax.set_title('IID: template0' if test=='iid' else 'OOD: template2')
            if row==1:ax.set_xlabel('Legal latent editing steps')
    axes[0,0].legend(ncol=4,fontsize=8)
    fig.suptitle('T5Gemma time: fixed200; mean and range across seeds42/43/44\n256 five-step paths/template across32 shared test worlds',fontsize=11)
    folder=ROOT/'figures';folder.mkdir(exist_ok=True)
    for extension in ('png','pdf'):fig.savefig(folder/f'latent_length_transfer.{extension}',dpi=180)
    plt.close(fig)
    dump(ROOT/'FIGURE_AUDIT.json',dict(passed=True,input_sha256=digest(ROOT/'summary_by_seed.csv'),matplotlib_version=matplotlib.__version__,band='minimum/maximum across three training seeds, not confidence interval',two_step_denominator_note='length2 plotted on long-path set256, not exhaustive704 pairs',values=values,outputs={str(p.relative_to(ROOT)):digest(p) for p in sorted(folder.glob('*'))}))
    print('Standalone PNG/PDF behavior plots saved')
if __name__=='__main__':main()
