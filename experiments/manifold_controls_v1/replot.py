"""No new predictions: absolute likelihood and paired canonical advantage."""
from mutil import *
def main():
 require_slurm();rr=read(CONF/'results/control_summary.json');variants=['adam_1e3','adam_1e4','sgd_1','sgd_10'];import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
 curves=defaultdict(list)
 for r in rr:curves[r['variant'],r['seed']].append(r)
 fig,ax=plt.subplots(2,3,figsize=(13,7),sharex='col')
 for j,seed in enumerate(SEEDS):
  canonical=curves['adam_1e3',seed][0]['canonical_nll']['mean']
  for i,v in enumerate(variants):
   rs=sorted(curves[v,seed],key=lambda r:r['checkpoint']);x=[r['nll']['mean'] for r in rs]
   for row,metric in [(0,'token_mse'),(1,'R5')]:
    y=[r[metric]['mean' if row==0 else 'rate'] for r in rs];a=ax[row,j];a.plot(x,y,'-o',ms=3,color=f'C{i}',label=v)
    for k in ((0,10,15,20,25,100) if i==0 else ()):
     q=next(r for r in rs if r['checkpoint']==k);offset=(4,-16) if row==1 and k in (10,15) else (4,5)
     a.annotate(str(k),(q['nll']['mean'],q[metric]['mean' if row==0 else 'rate']),xytext=offset,textcoords='offset points',fontsize=7,color=f'C{i}')
    ci=[r[metric]['ci95_world_bootstrap' if row==0 else 'ci95'] for r in rs];a.fill_between(x,[c[0] for c in ci],[c[1] for c in ci],alpha=.10,color=f'C{i}');a.axvline(canonical,color='k',ls=':',lw=.8);a.set_xscale('log')
   ax[0,j].set_yscale('log')
  # Explicit limits once per shared column: likelihood improves left-to-right.
  ax[1,j].set_xlim(canonical*1.2,min(r['nll']['mean'] for v in variants for r in curves[v,seed])*.8);ax[1,j].set_ylim(-.03,1.04);ax[0,j].set_title(f'Seed {seed}');ax[1,j].set_xlabel('Measured CE (nats / target token; decreases ->)')
 ax[0,0].set_ylabel('Aligned token MSE');ax[1,0].set_ylabel('Aligned +1 complete R5');ax[0,0].legend(fontsize=8);fig.suptitle('Dotted line: canonical CE; labels: AdamW 1e-3 update count',fontsize=11);fig.tight_layout()
 for suffix in ('svg','png','pdf'):fig.savefig(ROOT/f'results/optimizer_absolute_ce.{suffix}',dpi=180)
 fig,ax=plt.subplots(1,3,figsize=(13,3.8));gaps=[]
 for j,seed in enumerate(SEEDS):
  for i,v in enumerate(variants):
   rs=sorted(curves[v,seed],key=lambda r:r['checkpoint']);gap=[r['nll']['mean']-r['canonical_nll']['mean'] for r in rs];ax[j].plot([r['checkpoint'] for r in rs],gap,'-o',color=f'C{i}',ms=3,label=v)
  ax[j].axhline(0,color='k',ls=':');ax[j].set_title(f'Seed {seed}');ax[j].set_xlabel('Update');ax[j].ticklabel_format(axis='y',style='sci',scilimits=(0,0))
 ax[0].set_ylabel('Edited CE - canonical CE (nats/token)');ax[0].legend(fontsize=8);fig.tight_layout()
 for suffix in ('svg','png','pdf'):fig.savefig(ROOT/f'results/optimizer_canonical_gap.{suffix}',dpi=180)
 # World-paired uncertainty, no independence assumption between eight edges.
 path=CONF/'results/control_panel.jsonl.gz';groups=defaultdict(lambda:defaultdict(list))
 with gzip.open(path,'rt') as fo:
  for line in fo:
   r=json.loads(line);groups[r['variant'],r['seed'],r['checkpoint']][r['world_id']].append(r['nll']-r['canonical_nll'])
 for (v,s,k),ww in sorted(groups.items()):
  vals=[float(np.mean(a)) for a in ww.values()];gaps.append(dict(variant=v,seed=s,checkpoint=k,edited_minus_canonical_ce_mean=float(np.mean(vals)),ci95_world_bootstrap=old.bootstrap_mean(vals),worlds=len(vals)))
 dump('results/canonical_ce_gap.json',gaps)
 geometry=read(CONF/'results/write_geometry_summary.json');dump('results/write_geometry.json',geometry)
 lines=['# 主张表补充：规范 CE 与写入几何','','|主张|直接证据|边界|','|---|---|---|','|规范编码不是当前输出 CE 的最优点|同 world / 同目标 teacher forcing 下，RRR 初始化及微调状态的 CE 可低于 E(y)；绝对收益与配对 world bootstrap 区间见 canonical_ce_gap.json|这是有限受控目标上存在更低 CE 状态的证据；不主张找到了全局最优点|','|历史 CE 编辑几乎不沿规范方向写入|三 seed IID：cos(w,d)=-0.0119 至 -0.0052，||w||/||d||=3.31–3.40；结构 OOD=3.69–3.80；沿 d 的系数略负|历史编辑器与对齐转换；相对理想写入较大，不等于相对完整表示较大。Decoder shortcut 是解释，不是形式化攻击|','|CE 能奖励偏离规范的写法；组合破坏依赖优化路径|所有四优化器存在可测 CE 下降；AdamW1e-3 R5 掉到0%，小 lr/SGD 保留更多 R5|不能写成任意 CE 优化器必然破坏组合性；图中每点是实测检查点，连线不代表实测中间模型|','','新图：optimizer_absolute_ce.svg（绝对 CE、规范基线、更新标签、置信区间）；optimizer_canonical_gap.svg（相对规范 CE 差值）。没有新增训练或模型预测。']
 (ROOT/'CLAIMS.md').write_text(('\n'.join(lines)+'\n').replace('||w||/||d||','写入与规范写入的范数比'));dump('results/replot_complete.json',dict(job_id=os.environ['SLURM_JOB_ID'],gpus=0,new_predictions=0,source_sha256=sha(CONF/'results/control_summary.json')))
if __name__=='__main__':main()
