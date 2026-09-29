"""Train-only risk direction, dev thresholds, independent IID/OOD AUROC."""
import csv,json,math
from collections import defaultdict
from pathlib import Path

import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score,confusion_matrix
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from scipy.stats import rankdata

HERE=Path(__file__).resolve().parent
CFG=json.loads((HERE/'config.json').read_text())
FEATURES=['pooled_l2','pooled_cosine_distance','token_l2','token_cosine_distance','token_gram_rms','token_spread_log_ratio',
          'target_nll','target_worst_token_nll','output_entropy','output_top1_margin','output_min_top1_margin',
          'residual_norm','residual_previous_cosine','jvp_residual_gain']
GROUPS={
 'step_only':['step'],
 'pooled_geometry':['step','pooled_l2','pooled_cosine_distance'],
 'token_geometry':['step','token_l2','token_gram_rms','token_spread_log_ratio'],
 'decoder_scores':['step','target_nll','output_entropy','output_top1_margin'],
 'decoder_likelihood':['step','target_nll','target_worst_token_nll'],
 'dynamics':['step','residual_norm','residual_previous_cosine','jvp_residual_gain'],
 'all':['step','pooled_l2','token_l2','token_gram_rms','target_nll','output_entropy','output_top1_margin','residual_norm','residual_previous_cosine','jvp_residual_gain']}

def read(p):return [json.loads(s) for s in p.read_text().splitlines()]
def save_csv(name,rows):
 with (HERE/name).open('w',newline='') as f:
  wr=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');wr.writeheader();wr.writerows(rows)
def save_json(name,x):(HERE/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def matrix(rows,names):
 return np.array([[float(r[n]) if r[n] is not None and math.isfinite(float(r[n])) else np.nan for n in names] for r in rows],dtype=float)
def labels(rows):return np.array([int(r['next_failure']) for r in rows],dtype=int)
def auc(y,p):
 npos=int(np.sum(y));nneg=len(y)-npos
 return float((rankdata(p)[np.asarray(y)==1].sum()-npos*(npos+1)/2)/(npos*nneg)) if npos and nneg else float('nan')
def pct(x):return round(float(100*np.mean(x)),2) if len(x) else None
def threshold(y,s):
 assert len(set(y))==2
 values=np.unique(s)
 choices=np.r_[-np.inf,(values[1:]+values[:-1])/2,np.inf]
 best=None
 for v in choices:
  pred=(s>=v).astype(int);bal=balanced_accuracy_score(y,pred)
  # Conservative tie break: higher threshold and fewer false alarms.
  key=(bal,v)
  if best is None or key>best[0]:best=(key,v)
 return float(best[1])
def perf(y,s,t):
 pred=(s>=t).astype(int);tn,fp,fn,tp=confusion_matrix(y,pred,labels=[0,1]).ravel()
 return dict(threshold=float(t),sensitivity=float(tp/(tp+fn)) if tp+fn else None,specificity=float(tn/(tn+fp)) if tn+fp else None,
             precision=float(tp/(tp+fp)) if tp+fp else None,balanced_accuracy=float(balanced_accuracy_score(y,pred)) if len(set(y))==2 else None,
             true_positive=int(tp),false_positive=int(fp),true_negative=int(tn),false_negative=int(fn))
def bootstrap_auc(rows,scores,seed):
 y=labels(rows);worlds=np.array([r['world_id'] for r in rows]);ids=np.unique(worlds);rng=np.random.default_rng(seed)
 if len(set(y))<2:return None,None,0
 group={w:np.where(worlds==w)[0] for w in ids};out=[]
 for _ in range(CFG['bootstrap_replicates']):
  sample=rng.choice(ids,size=len(ids),replace=True);ii=np.concatenate([group[w] for w in sample])
  if len(set(y[ii]))==2:out.append(auc(y[ii],scores[ii]))
 return (round(float(np.quantile(out,.025)),4),round(float(np.quantile(out,.975)),4),len(out)) if out else (None,None,0)
def subset(rows,split):return [r for r in rows if r['split']==split] if split!='test_combined' else [r for r in rows if r['split'].startswith('test_')]
def summarize(rows,feature_names):
 out=[]
 for backbone in ('BART','T5Gemma'):
  for split in ('train','dev','test_iid','test_template_ood','test_combined'):
   for k in range(1,6):
    rr=[r for r in rows if r['backbone']==backbone and r['split']==split and r['step']==k]
    for state in ('all','current_correct','prefailure','next_stable'):
     z=[r for r in rr if state=='all' or (state=='current_correct' and r['current_success']) or (state=='prefailure' and r['current_success'] and r['next_failure']) or (state=='next_stable' and r['current_success'] and r['next_success'])]
     if not z:continue
     rec=dict(backbone=backbone,split=split,step=k,state=state,n=len(z),current_success_pct=pct([r['current_success'] for r in z]),next_failure_pct=pct([r['next_failure'] for r in z if r['next_failure'] is not None]))
     rec.update({f:round(float(np.nanmean(matrix(z,[f]))),6) for f in feature_names})
     out.append(rec)
 return out

def chart(name,curves,backbone):
 metrics=[('pooled_l2','Pooled normalized L2'),('token_l2','Aligned token normalized L2'),('target_nll','Gold target NLL'),('output_top1_margin','Generated top-1 logit margin')]
 W,H=960,660;xml=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">','<rect width="100%" height="100%" fill="white"/>',f'<text x="38" y="26" font-size="19" font-family="sans-serif">{backbone}: scores on currently correct test states</text>']
 palette={'next_stable':'#2074a5','prefailure':'#cf5d17'}
 for j,(key,title) in enumerate(metrics):
  x0=55+(j%2)*480;y0=60+(j//2)*300;L=x0;R=x0+370;U=y0+25;D=y0+245
  data=[r for r in curves if r['backbone']==backbone and r['split']=='test_combined' and r['state'] in palette and r['step']<5]
  upper=max([r[key] for r in data] or [1])*1.1;upper=max(upper,1e-6)
  X=lambda k:L+(k-1)*(R-L)/3
  Y=lambda v:D-v/upper*(D-U)
  xml.extend([f'<text x="{x0}" y="{y0+15}" font-size="14" font-family="sans-serif">{title}</text>',f'<path d="M {L} {U} V {D} H {R}" stroke="#444" fill="none"/>'])
  for k in range(1,5):xml.append(f'<text x="{X(k)-4:.1f}" y="{D+17}" font-size="11" font-family="sans-serif">{k}</text>')
  for state,color in palette.items():
   rr=sorted([r for r in data if r['state']==state],key=lambda r:r['step'])
   if rr:xml.append(f'<polyline points="{" ".join(f"{X(r["step"]):.1f},{Y(r[key]):.1f}" for r in rr)}" fill="none" stroke="{color}" stroke-width="2.5"/>')
   for r in rr:xml.append(f'<circle cx="{X(r["step"]):.1f}" cy="{Y(r[key]):.1f}" r="3" fill="{color}"/>')
  xml.append(f'<text x="{R+4}" y="{U+18}" font-size="10" fill="#555" font-family="sans-serif">max {upper:.2g}</text>')
 xml.extend(['<line x1="55" x2="79" y1="640" y2="640" stroke="#2074a5" stroke-width="3"/>','<text x="86" y="644" font-size="12" font-family="sans-serif">next step succeeds</text>','<line x1="240" x2="264" y1="640" y2="640" stroke="#cf5d17" stroke-width="3"/>','<text x="271" y="644" font-size="12" font-family="sans-serif">next step fails</text>','</svg>'])
 (HERE/name).write_text('\n'.join(xml)+'\n')

def main():
 rows=read(HERE/'features_bart.jsonl')+read(HERE/'features_t5gemma.jsonl')
 assert len(rows)==(160+27+53+53)*5*2
 keys={(r['backbone'],r['split'],r['world_id'],r['step']) for r in rows};assert len(keys)==len(rows)
 curves=summarize(rows,['pooled_l2','token_l2','token_gram_rms','target_nll','output_entropy','output_top1_margin','residual_norm','jvp_residual_gain'])
 # Add pooled test curves while preserving the two locked splits in the result table.
 combined=[dict(r,split='test_combined') for r in rows if r['split'].startswith('test_')]
 curves+=summarize(combined,['pooled_l2','token_l2','token_gram_rms','target_nll','output_entropy','output_top1_margin','residual_norm','jvp_residual_gain'])
 save_csv('stability_curves.csv',curves)
 for b in ('BART','T5Gemma'):chart(f'stability_curve_{b.lower()}.svg',curves,b)
 results=[];within=[];predictions=[];fits={}
 for bi,backbone in enumerate(('BART','T5Gemma')):
  valid=[r for r in rows if r['backbone']==backbone and r['step']<=4 and r['current_success']]
  train=subset(valid,'train');dev=subset(valid,'dev');assert len(set(labels(train)))==len(set(labels(dev)))==2
  for name,names in [(f'feature:{x}',[x]) for x in FEATURES]+[(f'model:{x}',v) for x,v in GROUPS.items()]:
   Xtr=matrix(train,names);Xdev=matrix(dev,names)
   if name.startswith('feature:'):
    med=float(np.nanmedian(Xtr[:,0]));Xtr=np.where(np.isfinite(Xtr),Xtr,med);Xdev=np.where(np.isfinite(Xdev),Xdev,med)
    direction=1 if auc(labels(train),Xtr[:,0])>=.5 else -1
    trscore=direction*Xtr[:,0];dvscore=direction*Xdev[:,0]
    def predict(rr):
     a=matrix(rr,names)[:,0];return direction*np.where(np.isfinite(a),a,med)
   else:
    model=make_pipeline(SimpleImputer(strategy='median',add_indicator=False),StandardScaler(),LogisticRegression(C=CFG['logistic_C'],class_weight='balanced',max_iter=2000,random_state=CFG['seed']))
    model.fit(Xtr,labels(train));trscore=model.predict_proba(Xtr)[:,1];dvscore=model.predict_proba(Xdev)[:,1]
    direction=None
    def predict(rr):return model.predict_proba(matrix(rr,names))[:,1]
   cut=threshold(labels(dev),dvscore)
   fits[backbone,name]=dict(direction=direction,threshold=cut,train_auc=auc(labels(train),trscore),dev_auc=auc(labels(dev),dvscore))
   for split in ('train','dev','test_iid','test_template_ood','test_combined'):
    rr=subset(valid,split);ys=labels(rr);ss=predict(rr)
    low,high,nboot=bootstrap_auc(rr,ss,CFG['bootstrap_seed']+bi*100+len(results)) if split.startswith('test_') else (None,None,0)
    report=dict(backbone=backbone,predictor=name,split=split,n=len(rr),n_worlds=len({r['world_id'] for r in rr}),next_failure_count=int(ys.sum()),next_failure_pct=pct(ys),train_direction=direction,
                auroc=round(auc(ys,ss),4) if len(set(ys))==2 else None,auroc_ci_low=low,auroc_ci_high=high,bootstrap_valid=nboot,**perf(ys,ss,cut))
    results.append(report)
    if split in ('test_iid','test_template_ood'):
     for r,s in zip(rr,ss):predictions.append(dict(backbone=backbone,predictor=name,split=split,world_id=r['world_id'],step=r['step'],next_failure=r['next_failure'],score=float(s),threshold=cut,predicted_failure=bool(s>=cut)))
   for split in ('test_iid','test_template_ood','test_combined'):
    for k in range(1,4):
     rr=[r for r in subset(valid,split) if r['step']==k]
     if not rr:continue
     ys=labels(rr);ss=predict(rr)
     within.append(dict(backbone=backbone,predictor=name,split=split,step=k,n=len(rr),next_failure_count=int(ys.sum()),auroc=round(auc(ys,ss),4) if len(set(ys))==2 else None,**perf(ys,ss,cut)))
 save_csv('predictor_comparison.csv',results);save_csv('within_step_auroc.csv',within);save_csv('test_predictions.csv',predictions)
 # Text-exact, currently correct states followed by failure: choose strongest NLL warnings with matched-step survivor references.
 examples=[]
 for backbone in ('BART','T5Gemma'):
  rr=[r for r in rows if r['backbone']==backbone and r['split'].startswith('test_')]
  idx={(r['split'],r['world_id'],r['step']):r for r in rr}
  candidates=[]
  for r in rr:
   if r['step']>3 or not r['current_success'] or not r['next_failure'] or r['decoded_text'].strip()!=r['gold_text']:continue
   peers=[x for x in rr if x['step']==r['step'] and x['current_success'] and x['next_success']]
   if not peers:continue
   med=float(np.median([x['target_nll'] for x in peers]));ratio=r['target_nll']/max(med,1e-8)
   candidates.append((ratio,r,med))
  for ratio,r,med in sorted(candidates,key=lambda z:z[0],reverse=True)[:3]:
   nxt=idx[r['split'],r['world_id'],r['step']+1]
   examples.append(dict(backbone=backbone,split=r['split'],world_id=r['world_id'],step=r['step'],current_text=r['decoded_text'],current_gold=r['gold_text'],next_text=nxt['decoded_text'],next_gold=nxt['gold_text'],current_success=True,next_success=False,
                        target_nll=r['target_nll'],matched_step_next_stable_nll_median=med,nll_ratio_to_stable_median=ratio,output_entropy=r['output_entropy'],output_top1_margin=r['output_top1_margin'],pooled_l2=r['pooled_l2'],token_l2=r['token_l2'],token_gram_rms=r['token_gram_rms'],residual_norm=r['residual_norm'],jvp_residual_gain=r['jvp_residual_gain']))
 save_json('pre_failure_examples.json',examples)
 save_json('analysis_summary.json',dict(config=CFG,predictor_rows=len(results),feature_rows=len(rows),examples=[dict(backbone=e['backbone'],split=e['split'],world_id=e['world_id'],step=e['step']) for e in examples]))

if __name__=='__main__':main()
