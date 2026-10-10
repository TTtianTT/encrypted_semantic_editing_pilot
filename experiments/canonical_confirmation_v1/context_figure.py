"""A fixed state/operation counterexample to universal scalar residual thresholds."""
from futils import *
def main():
 import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
 rs=read(ROOT/'results/risk_matched_context.json');fig,axs=plt.subplots(2,2,figsize=(10,7),sharey=True)
 for i,metric in enumerate(('entering_token_mse','entering_S_mse')):
  for j,t in enumerate((0,3)):
   ax=axs[i,j]
   for label,marker,color in [('C1','o','C0'),('C4','D','C3'),('C5','s','C4')]:
    rr=[r for r in rs if r['template']==t and r['condition']==label];x=[r[metric] for r in rr];y=[r['next_success']['rate'] for r in rr];ax.scatter(x,y,label=label,marker=marker,color=color,s=28,alpha=.7)
   ax.set_xscale('log');ax.set_ylim(-.05,1.05);ax.set_title(f'Template{t}: state0, next plus');ax.set_xlabel(metric);ax.set_ylabel('Next success | current correct');ax.legend()
 fig.tight_layout();fig.savefig(ROOT/'results/matched_context_risk.svg');fig.savefig(ROOT/'results/matched_context_risk.png',dpi=160)
if __name__=='__main__':main()
