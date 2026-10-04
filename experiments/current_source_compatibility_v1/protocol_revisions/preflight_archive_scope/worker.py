import argparse,traceback,time,collections
from engine import *
from evaluation import natural,evaluate

def admission(eng,seed):
    folder=ROOT/f'runs/preflight/s{seed}';folder.mkdir(parents=True,exist_ok=True)
    ed=load(eng,checkpoint(seed));ws=worldmap();dev=rows(ROOT/'data/dev_core.jsonl')
    rec=natural(eng,ed,dev,folder/'reconstruction.jsonl',True);atom=natural(eng,ed,dev,folder/'atomic.jsonl')
    from evaluate import gold_next,rates
    if (folder/'gold_next.jsonl').exists():gn=rows(folder/'gold_next.jsonl')
    else:gn=gold_next(eng,ed,dev,ws,folder/'gold_next.jsonl')
    def rate(rs):
      v=collections.defaultdict(list)
      for r in rs:v[(r['state'],r['operation'])].append(r['score']['success'])
      return dict(rate=sum(r['score']['success'] for r in rs)/len(rs),min_cell=min(sum(x)/len(x) for x in v.values()),n=len(rs))
    stats={'reconstruction':rate(rec),'atomic':rate(atom),'gold_next':rate(gn)}
    passed=stats['reconstruction']['rate']>=.95 and all(stats[k]['rate']>=.85 and stats[k]['min_cell']>=.75 for k in ('atomic','gold_next'))
    dump(folder/'admission.json',dict(passed=passed,**stats));assert passed,'T0 admission failed: investigate before formal training'
    evaluate(eng,seed,ed,checkpoint(seed),folder/'T0',True)
    # Verify the unchanged old natural successes by row ID, not aggregate only.
    import gzip
    old=BASE/f'runs/formal/t5gemma_time_s{seed}/predictions.jsonl.gz'
    expected={}
    with gzip.open(old,'rt') as f:
     for line in f:
      x=json.loads(line);r=x.get('row',x)
      if r.get('kind')=='atomic' and r.get('template') in (0,1) and r.get('state') is not None:
       expected[f"{r['world_id']}_t{r['template']}_s{r['state']}_{r['operation']}"]=r['score']['success']
    actual=rows(folder/'T0/old_natural.jsonl');assert len(expected)==len(actual)==768
    assert all(expected[r['id']]==r['score']['success'] for r in actual),'Old natural admission not reproduced'
    dump(folder/'complete.json',dict(seed=seed,passed=True,old_natural_predictions_reproduced=768,resources=eng.resources(),at_utc=now()))

def smoke(eng):
    folder=ROOT/'local/smoke';folder.mkdir(parents=True,exist_ok=True)
    before=tensorhash(dict(eng.model.named_parameters()))
    for method in ('N','F'):train_condition(eng,42,method,stop=2,folder=folder/method,smoke=True)
    direct,_,_,dr=train_condition(eng,42,'R',stop=22,folder=folder/'R_direct',smoke=True)
    train_condition(eng,42,'R',stop=11,folder=folder/'R_resume',smoke=True)
    resumed,_,_,rr=train_condition(eng,42,'R',stop=22,folder=folder/'R_resume',smoke=True)
    assert tensorhash(direct.state_dict())==tensorhash(resumed.state_dict()),'Resume changed editor'
    da=torch.load(folder/'R_direct/latest.pt',map_location='cpu',weights_only=False);ra=torch.load(folder/'R_resume/latest.pt',map_location='cpu',weights_only=False)
    for k in da['optimizer']['state']:
      for name,value in da['optimizer']['state'][k].items():
       assert torch.equal(value,ra['optimizer']['state'][k][name]) if isinstance(value,torch.Tensor) else value==ra['optimizer']['state'][k][name]
    assert dr[0]['source_sha']!=dr[1]['source_sha'] and [x['update'] for x in rr]==[0,20]
    assert before==tensorhash(dict(eng.model.named_parameters())),'Backbone changed'
    assert all(p.grad is None for p in eng.model.parameters())
    from evaluation import long_paths
    w=next(w for w in worldmap().values() if w['split']=='train');ops=['plus','minus','plus','minus','plus'];s=0;ss=[]
    for op in ops:s=advance('time',s,op);ss.append(s)
    smoke_path=dict(id='smoke_train_path',world_id=w['world_id'],template=0,initial_state=0,operations=ops,states=ss,family='smoke_alternating',original_text=render(w,0,0))
    long_paths(eng,direct,[smoke_path],'latent',folder/'latent')
    dump(ROOT/'SMOKE_AUDIT.json',dict(passed=True,frozen_backbone=True,detached_prefix=True,F_T0_immutable=True,R_refreshed=True,exact_resumed_editor_and_optimizer=True,refresh_positions=[0,20],latent_no_reencode=True,resources=eng.resources(),at_utc=now()))

def formal(eng,seed):
    assert read(ROOT/'SMOKE_AUDIT.json')['passed']
    for s in (42,43,44):assert read(ROOT/f'runs/preflight/s{s}/complete.json')['passed']
    out=ROOT/f'runs/formal/s{seed}';out.mkdir(parents=True,exist_ok=True)
    for method in ('N','F','R'):
      if (out/f'{method}_complete.json').exists():continue
      training=ROOT/f'local/s{seed}/{method}'
      if not (training/'update200.pt').exists():train_condition(eng,seed,method)
      for u in (100,200):
       cp=training/f'update{u:03}.pt';ed=load(eng,cp);evaluate(eng,seed,ed,cp,out/f'{method}_u{u}');del ed
      dump(out/f'{method}_complete.json',dict(seed=seed,method=method,updates=200,checkpoint100_sha=digest(training/'update100.pt'),checkpoint200_sha=digest(training/'update200.pt')))
    dump(out/'complete.json',dict(seed=seed,methods=['N','F','R'],passed=True,resources=eng.resources(),at_utc=now()))

def main():
    p=argparse.ArgumentParser();p.add_argument('--phase',choices=['smoke','preflight','formal'],required=True);p.add_argument('--index',type=int,default=0);a=p.parse_args();guard();verify_lock()
    seed=(42,43,44)[a.index] if a.phase!='smoke' else 42
    eng=Backend('t5gemma');encode=eng.encode;eng.encode_calls=0
    def counted(texts):eng.encode_calls+=1;return encode(texts)
    eng.encode=counted
    dest=ROOT/f'runs/{a.phase}/s{seed}';dest.mkdir(parents=True,exist_ok=True)
    try:
      if a.phase=='smoke':smoke(eng)
      elif a.phase=='preflight':admission(eng,seed)
      else:formal(eng,seed)
    except Exception as e:dump(dest/'failure.json',dict(phase=a.phase,seed=seed,error=type(e).__name__,message=str(e),traceback=traceback.format_exc(),at_utc=now(),resources=eng.resources()));raise
if __name__=='__main__':main()
