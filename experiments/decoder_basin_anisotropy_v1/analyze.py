"""Paired, world-clustered G8 directional-radius analysis on locked tests."""
import csv,json,math
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import binomtest,rankdata

HERE=Path(__file__).resolve().parent
CFG=json.loads((HERE/'config.json').read_text())
DIRS=CFG['directions']
COLORS=dict(editor_forward='#bb3d2b',editor_reverse='#7768ae',radial_orthogonal_random='#418cbe',toward_gold='#3d9b67',editor_orthogonal_random='#d6952a')

def read(path):return [json.loads(s) for s in path.read_text().splitlines()]
def savecsv(name,rows):
 assert rows
 with (HERE/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
def savejson(name,x):(HERE/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def state_key(r):return r['backbone'],r['split'],r['world_id'],r['step']
def pct(x):return float(100*np.mean(x)) if len(x) else None
def auc(y,s):
 y=np.asarray(y,dtype=int);s=np.asarray(s,dtype=float);pos=int(y.sum());neg=len(y)-pos
 return float((rankdata(s)[y==1].sum()-pos*(pos+1)/2)/(pos*neg)) if pos and neg else None

def radii(states,scan):
 scans=defaultdict(list)
 for r in scan:scans[state_key(r),r['direction']].append(r)
 out=[]
 for s in states:
  for d in DIRS:
   rr=scans[state_key(s),d];assert len(rr)>=len(CFG['coarse_alpha'])
   coarse=sorted((x for x in rr if x['alpha'] in CFG['coarse_alpha']),key=lambda x:x['alpha'])
   assert [x['alpha'] for x in coarse]==CFG['coarse_alpha']
   failed=sorted(x['alpha'] for x in rr if not x['corridor_success'])
   upper=failed[0] if failed else None
   lower=max((x['alpha'] for x in rr if x['corridor_success'] and (upper is None or x['alpha']<upper)),default=0.)
   if upper is None:lower=CFG['radius_cap']
   nonmono=upper is not None and any(x['alpha']>upper and x['corridor_success'] for x in coarse)
   first_content=next((x['alpha'] for x in coarse if not x['content_compatible']),None)
   content_nonmono=first_content is not None and any(x['alpha']>first_content and x['content_compatible'] for x in coarse)
   out.append(dict(backbone=s['backbone'],split=s['split'],world_id=s['world_id'],step=s['step'],next_failure=s['next_failure'],
                   direction=d,radius_lower=lower,radius_upper=upper,radius_capped=upper if upper is not None else CFG['radius_cap'],
                   censored=upper is None,nonmonotonic_coarse=nonmono,content_radius_coarse=first_content,
                   content_nonmonotonic_coarse=content_nonmono,
                   content_radius_capped=first_content if first_content is not None else CFG['radius_cap'],
                   content_fail_by_one=first_content is not None and first_content<=1,
                   corridor_fail_by_half=upper is not None and upper<=.5,corridor_fail_by_one=upper is not None and upper<=1,
                   alpha_one_corridor_success=next(x['corridor_success'] for x in coarse if x['alpha']==1),
                   alpha_one_next_gold_success=next(x['next_gold_success'] for x in coarse if x['alpha']==1),
                   samples=len(rr)))
 return out

def curves(scan):
 out=[]
 for backbone in ('BART','T5Gemma'):
  for split in ('train','dev','test_iid','test_template_ood','test_combined'):
   rows=[r for r in scan if r['backbone']==backbone and (r['split']==split or split=='test_combined' and r['split'].startswith('test_'))]
   for d in DIRS:
    for alpha in CFG['coarse_alpha']:
     rr=[r for r in rows if r['direction']==d and r['alpha']==alpha]
     if not rr:continue
     out.append(dict(backbone=backbone,split=split,direction=d,alpha=alpha,n=len(rr),
                     corridor_success_pct=pct([r['corridor_success'] for r in rr]),
                     current_gold_success_pct=pct([r['current_gold_success'] for r in rr]),
                     next_gold_success_pct=pct([r['next_gold_success'] for r in rr]),
                     content_compatible_pct=pct([r['content_compatible'] for r in rr]),
                     fact_preservation_pct=pct([r['fact_preservation'] for r in rr]),
                     mean_nll_best=float(np.mean([r['target_nll_best'] for r in rr])),
                     median_nll_best=float(np.median([r['target_nll_best'] for r in rr])),
                     mean_output_entropy=float(np.mean([r['output_entropy'] for r in rr])),
                     mean_top1_margin=float(np.mean([r['output_top1_margin'] for r in rr])),
                     mean_effective_norm_ratio=float(np.mean([r['effective_norm_ratio'] for r in rr]))))
 return out

def radius_summary(radius):
 out=[]
 for backbone in ('BART','T5Gemma'):
  for split in ('test_iid','test_template_ood','test_combined'):
   for step in ('all',1,2,3):
    for group in ('all','next_failure','next_stable'):
     for direction in DIRS:
      rr=[r for r in radius if r['backbone']==backbone and r['direction']==direction and
          (r['split']==split or split=='test_combined' and r['split'].startswith('test_')) and
          (step=='all' or r['step']==step) and
          (group=='all' or group=='next_failure' and r['next_failure'] or group=='next_stable' and not r['next_failure'])]
      if not rr:continue
      out.append(dict(backbone=backbone,split=split,step=step,group=group,direction=direction,n=len(rr),
                      corridor_mean_capped=float(np.mean([r['radius_capped'] for r in rr])),
                      corridor_median_capped=float(np.median([r['radius_capped'] for r in rr])),
                      corridor_censored_pct=pct([r['censored'] for r in rr]),
                      corridor_fail_by_one_pct=pct([r['corridor_fail_by_one'] for r in rr]),
                      content_mean_capped=float(np.mean([r['content_radius_capped'] for r in rr])),
                      content_median_capped=float(np.median([r['content_radius_capped'] for r in rr])),
                      content_censored_pct=pct([r['content_radius_coarse'] is None for r in rr]),
                      content_fail_by_one_pct=pct([r['content_fail_by_one'] for r in rr]),
                      corridor_nonmonotonic_pct=pct([r['nonmonotonic_coarse'] for r in rr]),
                      content_nonmonotonic_pct=pct([r['content_nonmonotonic_coarse'] for r in rr])))
 return out

def paired_bootstrap(diff,world_ids,seed):
 ids=np.unique(world_ids);groups={i:np.where(world_ids==i)[0] for i in ids};rng=np.random.default_rng(seed)
 boot=[]
 for _ in range(CFG['bootstrap_replicates']):
  draw=rng.choice(ids,size=len(ids),replace=True);ix=np.concatenate([groups[i] for i in draw])
  boot.append(float(np.mean(diff[ix])))
 return float(np.quantile(boot,.025)),float(np.quantile(boot,.975))

def paired_contrasts(radii_rows):
 index={(state_key(r),r['direction']):r for r in radii_rows};out=[]
 for backbone in ('BART','T5Gemma'):
  for split in ('test_iid','test_template_ood','test_combined'):
   states=sorted({state_key(r) for r in radii_rows if r['backbone']==backbone and (r['split']==split or split=='test_combined' and r['split'].startswith('test_'))})
   if not states:continue
   for endpoint,field,fail_field in [('semantic_corridor','radius_capped','corridor_fail_by_one'),('content_structure','content_radius_capped','content_fail_by_one')]:
    for ci,control in enumerate(DIRS[1:]):
     edit=np.array([index[k,'editor_forward'][field] for k in states]);other=np.array([index[k,control][field] for k in states]);diff=edit-other
     worlds=np.array([k[2] for k in states]);low,high=paired_bootstrap(diff,worlds,CFG['bootstrap_seed']+ci+101*len(out))
     smaller=int((diff<0).sum());larger=int((diff>0).sum());ties=int((diff==0).sum())
     out.append(dict(backbone=backbone,split=split,endpoint=endpoint,control=control,n_states=len(states),n_worlds=len(set(worlds)),
                     edit_mean_capped=float(edit.mean()),control_mean_capped=float(other.mean()),
                     mean_edit_minus_control=float(diff.mean()),ci_low=low,ci_high=high,
                     edit_smaller=smaller,edit_larger=larger,ties=ties,
                     paired_sign_p=float(binomtest(smaller,smaller+larger,.5).pvalue) if smaller+larger else 1.,
                     edit_fail_by_one=int(sum(index[k,'editor_forward'][fail_field] for k in states)),
                     control_fail_by_one=int(sum(index[k,control][fail_field] for k in states))))
 return out

def early_warning(states,scan,radius):
 states_index={state_key(s):s for s in states}
 at_half={(state_key(r),r['direction']):r for r in scan if r['alpha']==.5}
 radii_index={(state_key(r),r['direction']):r for r in radius}
 out=[]
 for backbone in ('BART','T5Gemma'):
  for split in ('test_iid','test_template_ood','test_combined'):
   for step in (1,2,3):
    keys=[k for k,s in states_index.items() if k[0]==backbone and k[3]==step and (k[1]==split or split=='test_combined' and k[1].startswith('test_'))]
    if not keys:continue
    for label_source in ('g7_original','local_alpha_one'):
     labels=[states_index[k]['next_failure'] if label_source=='g7_original' else not states_index[k]['alpha_one_next_gold_success'] for k in keys]
     for measure in ('radius_capped','content_radius_capped','half_step_failure','half_step_content_failure','half_step_nll_best','half_step_entropy','half_step_entropy_change'):
      values=[]
      for k in keys:
       s=states_index[k];half=at_half[k,'editor_forward'];rad=radii_index[k,'editor_forward']
       values.append({'radius_capped':-rad['radius_capped'],
                      'content_radius_capped':-rad['content_radius_capped'],
                      'half_step_failure':int(not half['corridor_success']),
                      'half_step_content_failure':int(not half['content_compatible']),
                      'half_step_nll_best':half['target_nll_best'],
                      'half_step_entropy':half['output_entropy'],
                      'half_step_entropy_change':half['output_entropy']-s['current_output_entropy']}[measure])
      out.append(dict(backbone=backbone,split=split,step=step,label_source=label_source,measure=measure,n=len(keys),next_failures=int(sum(labels)),
                      auroc=auc(labels,values),failure_group_mean=float(np.mean([v for v,y in zip(values,labels) if y])) if any(labels) else None,
                      stable_group_mean=float(np.mean([v for v,y in zip(values,labels) if not y])) if not all(labels) else None))
 return out

def svg(name,curves,backbone):
 series=[r for r in curves if r['backbone']==backbone and r['split']=='test_combined']
 W,H=920,570;xml=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">','<rect width="100%" height="100%" fill="white"/>',
 f'<text x="45" y="35" font-size="21" font-family="sans-serif">{backbone}: directional decoder basin, locked tests</text>']
 panels=[('corridor_success_pct','Current-or-next semantic success (%)',0.,100.),('mean_output_entropy','Generated-token entropy',0.,max(r['mean_output_entropy'] for r in series)*1.1)]
 for j,(metric,title,ymin,ymax) in enumerate(panels):
  x0=55+j*450;top=85;bottom=420;right=x0+365
  xml.extend([f'<text x="{x0}" y="68" font-size="15" font-family="sans-serif">{title}</text>',f'<path d="M{x0} {top} V{bottom} H{right}" stroke="#444" fill="none"/>'])
  X=lambda a:x0+(a/2)*(right-x0)
  Y=lambda v:bottom-(v-ymin)/(ymax-ymin if ymax>ymin else 1)*(bottom-top)
  for tick in (0,.5,1,1.5,2):xml.append(f'<text x="{X(tick)-7:.1f}" y="{bottom+19}" font-size="11" font-family="sans-serif">{tick:g}</text>')
  for d in DIRS:
   rr=sorted([r for r in series if r['direction']==d],key=lambda r:r['alpha'])
   pts=' '.join(f'{X(r["alpha"]):.1f},{Y(r[metric]):.1f}' for r in rr)
   xml.append(f'<polyline points="{pts}" stroke="{COLORS[d]}" stroke-width="2.4" fill="none"/>')
 xml.append('<text x="412" y="468" font-size="13" font-family="sans-serif">α × actual editor residual norm</text>')
 for i,d in enumerate(DIRS):
  x=55+(i%3)*280;y=500+(i//3)*25
  xml.extend([f'<line x1="{x}" x2="{x+25}" y1="{y}" y2="{y}" stroke="{COLORS[d]}" stroke-width="3"/>',f'<text x="{x+32}" y="{y+4}" font-size="12" font-family="sans-serif">{d}</text>'])
 xml.append('</svg>');(HERE/name).write_text('\n'.join(xml)+'\n')

def examples(states,scan,radius):
 bykey={(state_key(r),r['direction']):r for r in radius};scanby=defaultdict(list)
 for r in scan:scanby[state_key(r)].append(r)
 output=[]
 for backbone in ('BART','T5Gemma'):
  options=[s for s in states if s['backbone']==backbone and s['split'].startswith('test_') and s['next_failure'] and s['alpha_one_match_g7'] and s['current_decoded_text'].strip()==s['current_gold']]
  def gap(s):
   k=state_key(s);e=bykey[k,'editor_forward']['radius_capped'];c=bykey[k,'editor_orthogonal_random']['radius_capped']
   return c-e
  for s in sorted(options,key=gap,reverse=True)[:2]:
   k=state_key(s);rr=sorted(scanby[k],key=lambda x:(DIRS.index(x['direction']),x['alpha']))
   output.append(dict(backbone=backbone,split=s['split'],world_id=s['world_id'],step=s['step'],next_failure=True,
                      current_text=s['current_decoded_text'],current_gold=s['current_gold'],next_gold=s['next_gold'],
                      radius={d:bykey[k,d]['radius_capped'] for d in DIRS},samples=rr))
  # Also retain a case where the next edit fails but the corridor remains readable at alpha=1.
  other=[s for s in options if bykey[state_key(s),'editor_forward']['alpha_one_corridor_success']]
  if other:
   s=sorted(other,key=lambda z:(z['step'],z['world_id']))[0];k=state_key(s)
   output.append(dict(backbone=backbone,split=s['split'],world_id=s['world_id'],step=s['step'],next_failure=True,
                      subtype='semantic_failure_inside_corridor',current_text=s['current_decoded_text'],
                      current_gold=s['current_gold'],next_gold=s['next_gold'],
                      radius={d:bykey[k,d]['radius_capped'] for d in DIRS},
                      samples=sorted(scanby[k],key=lambda x:(DIRS.index(x['direction']),x['alpha']))))
  mismatches=[s for s in states if s['backbone']==backbone and s['split'].startswith('test_') and not s['alpha_one_match_g7']]
  if mismatches:
   s=sorted(mismatches,key=lambda z:(z['split'],z['world_id'],z['step']))[0];k=state_key(s)
   output.append(dict(backbone=backbone,split=s['split'],world_id=s['world_id'],step=s['step'],subtype='decoder_batch_sensitivity',
                      current_text=s['current_decoded_text'],current_gold=s['current_gold'],next_gold=s['next_gold'],
                      g7_next_text=s['next_original_decoded_text'],scan_next_text=s['alpha_one_decoded_text'],
                      radius={d:bykey[k,d]['radius_capped'] for d in DIRS},
                      samples=sorted(scanby[k],key=lambda x:(DIRS.index(x['direction']),x['alpha']))))
 return output

def main():
 states=read(HERE/'states_bart.jsonl')+read(HERE/'states_t5gemma.jsonl')
 scan=read(HERE/'scan_bart.jsonl')+read(HERE/'scan_t5gemma.jsonl')
 assert len({state_key(s) for s in states})==len(states)
 rad=radii(states,scan);curve=curves(scan);radius_table=radius_summary(rad);contrast=paired_contrasts(rad);warning=early_warning(states,scan,rad)
 savecsv('directional_radii.csv',rad);savecsv('radius_summary.csv',radius_table);savecsv('direction_curves.csv',curve);savecsv('paired_bootstrap.csv',contrast);savecsv('early_warning.csv',warning)
 savejson('pre_failure_cases.json',examples(states,scan,rad))
 for backbone in ('BART','T5Gemma'):svg(f'curve_{backbone.lower()}.svg',curve,backbone)
 nonmonotonic={b:{d:dict(semantic_corridor=sum(r['nonmonotonic_coarse'] for r in rad if r['backbone']==b and r['direction']==d and r['split'].startswith('test_')),
                            content_structure=sum(r['content_nonmonotonic_coarse'] for r in rad if r['backbone']==b and r['direction']==d and r['split'].startswith('test_'))) for d in DIRS} for b in ('BART','T5Gemma')}
 agreement={b:dict(states=sum(s['backbone']==b for s in states),
                   alpha_one_text_exact=sum(s['backbone']==b and s['alpha_one_match_g7'] for s in states),
                   alpha_one_semantic_same=sum(s['backbone']==b and (s['alpha_one_next_gold_success']==(not s['next_failure'])) for s in states)) for b in ('BART','T5Gemma')}
 savejson('analysis_summary.json',dict(config=CFG,state_count=len(states),scan_count=len(scan),radii_count=len(rad),radius_summary_rows=len(radius_table),curve_rows=len(curve),paired_rows=len(contrast),warning_rows=len(warning),nonmonotonic_test_counts=nonmonotonic,batch_agreement=agreement))
 print('states',len(states),'scan',len(scan),'paired',len(contrast))

if __name__=='__main__':main()
