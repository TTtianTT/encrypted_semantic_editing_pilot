import time
from engine import *
def main():
 assert_lock();be=Backend(NAME);ws=worlds();rows=read('data/test_iid_joint.jsonl')+read('data/test_template_ood_joint.jsonl');old=old_editors(be)
 paths={f'Joint{r}':ROOT/f'checkpoints/Joint{r}/best.pt' for r in [16,32]}
 for r in [16,32]:assert json.loads((ROOT/f'checkpoints/Joint{r}/complete.json').read_text())['updates']==600
 provenance=dict(joints={k:digest(p) for k,p in paths.items()},old_G1_hash=digest(CROSS/f'checkpoints/{NAME}/G1/best.pt'),interface_hash=digest(ROOT/f'models/{NAME}_interface.json'),data_lock_hash=digest(ROOT/'data/lock.json'))
 lock=ROOT/'evaluation/checkpoint_lock.json'
 if lock.exists():assert json.loads(lock.read_text())==provenance
 else:dump('evaluation/checkpoint_lock.json',provenance)
 started=time.monotonic();outdir=ROOT/'outputs';outdir.mkdir(exist_ok=True)
 # Original and endpoint oracle reconstruction, same frozen wrapper and decoder.
 controls=[]
 if not (outdir/'controls.jsonl').exists():
  for role in ['source','target']:
   for i in range(0,len(rows),16):
    batch=rows[i:i+16];ss,timing,lens=be.infer([r[f'{role}_text'] for r in batch],None,[])
    for r,st,n in zip(batch,ss,lens):
     s=st[0];s['score']=metric(s['output'],r[f'{role}_frame'],ws[r['record_id']],s['ended']);controls.append(dict(record_id=r['record_id'],split=r['split'],role=role,source_text=r[f'{role}_text'],frame=r[f'{role}_frame'],result=s,timing=timing,source_tokens=n))
  write('outputs/controls.jsonl',controls)
 rules=[]
 for r in rows:
  results={}
  for order,o in r['orders'].items():
   text=r['source_text'];steps=[]
   for c0,c1 in zip(o['frames'],o['frames'][1:]):text,e=text_rule(text,c0,c1);steps.append(dict(output=text,rule_error=e,score=metric(text,c1,ws[r['record_id']],True)))
   results[order]=steps
  rules.append(dict(row_id=r['row_id'],record_id=r['record_id'],split=r['split'],orders=results))
 write('outputs/rules.jsonl',rules)
 models={}
 for rank in [16,32]:
  ed=new_joint(be.d,rank);ed.load_state_dict(torch.load(paths[f'Joint{rank}'],weights_only=True));models[f'Joint{rank}']=(nn.ModuleDict({'J':ed}),['J'],None)
 for order,ops in ORDERS.items():
  models['Sequential_'+order]=(old,ops,order);folded=fold(old[ops[0]],old[ops[1]],be.d);torch.save(folded.state_dict(),ROOT/f'checkpoints/Folded_{order}.pt');models['Folded_'+order]=(nn.ModuleDict({'J':folded}),['J'],order)
 for method,(eds,ops,order) in models.items():
  editor_hash=provenance['joints'][method] if method.startswith('Joint') else provenance['old_G1_hash'] if method.startswith('Sequential') else digest(ROOT/f'checkpoints/{method}.pt')
  file=outdir/f'{method}.jsonl';seen={r['record_id'] for r in read(file)} if file.exists() else set();todo=[r for r in rows if r['record_id'] not in seen]
  for i in range(0,len(todo),16):
   batch=todo[i:i+16];ss,timing,lens=be.infer([r['source_text'] for r in batch],eds,ops)
   with file.open('a') as f:
    for r,st,n in zip(batch,ss,lens):
     frames=r['orders'][order]['frames'][1:] if method.startswith('Sequential') else [r['target_frame']]
     for s,c in zip(st,frames):s['frame']=c;s['score']=metric(s['output'],c,ws[r['record_id']],s['ended'])
     v=dict(**r,method=method,seed=42,steps=st,output=st[-1]['output'],score=st[-1]['score'],endpoint_joint=st[-1]['score']['joint_ok'],trajectory_joint=all(s['score']['joint_ok'] for s in st) if method.startswith('Sequential') else None,source_tokens=n,wrapped_source=be.wrap(r['source_text']),timing=timing,model_revision=be.manifest['revision'],editor_hash=editor_hash,provenance=provenance)
     f.write(json.dumps(v)+'\n')
  print('evaluated',method,flush=True)
 # Numerical checks have their own resume keys; a completed generation is never repeated for them.
 numericfile=outdir/'fold_numerical.jsonl';seen={(r['record_id'],r['order']) for r in read(numericfile)} if numericfile.exists() else set()
 with torch.no_grad():
  for order,(a,b) in ORDERS.items():
   todo=[r for r in rows if (r['record_id'],order) not in seen];ed=models['Folded_'+order][0]['J']
   for i in range(0,len(todo),16):
    be.check();batch=todo[i:i+16];h,m,_=be.encode([r['source_text'] for r in batch]);seq=old[b](old[a](h,m),m);one=ed(h,m)
    with numericfile.open('a') as f:
     for r,s,folded,mask in zip(batch,seq,one,m):
      d=(s-folded)[mask.bool()];f.write(json.dumps(dict(record_id=r['record_id'],split=r['split'],order=order,max_abs=float(d.abs().max()),relative_l2=float(d.norm()/s[mask.bool()].norm()),padding_equal=bool(torch.equal(s[~mask.bool()],folded[~mask.bool()]))))+'\n')
 dump('evaluation/complete.json',dict(completed=True,methods=list(models),rows_per_method=160,wall_seconds=time.monotonic()-started,peak_cuda_bytes=torch.cuda.max_memory_allocated(),provenance=provenance))
if __name__=='__main__':main()
