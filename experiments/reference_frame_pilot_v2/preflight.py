import torch,json,time
from common import *
from engine import Engine,new_editors,tensorhash

def main():
 eng=Engine();rows=read('data/calibration_views.jsonl');worlds={w['record_id']:w for w in read('data/calibration_worlds.jsonl')}
 # Check source/target lengths across all pre-generated views before any training or test lock.
 lengths=[]
 for p in (ROOT/'data').glob('*.jsonl'):
  if p.name.endswith('_worlds.jsonl') or p.name=='sample_schedule.jsonl':continue
  for row in read(p.relative_to(ROOT)):
   lengths.extend(len(eng.tok(t)['input_ids']) for t in [row['source_text'],row['target_text'],*row['gold_step_texts']])
 assert max(lengths)<=96 and max(lengths)<60
 eds=new_editors();h,mask,_=eng.encode([r['source_text'] for r in rows[:4]])
 h2,mask2,_=eng.encode([r['source_text'] for r in rows[:4]]);assert torch.equal(h,h2)
 assert all(torch.equal(eds[op](h,mask),h) for op in OPS)
 init_hash=tensorhash(eds.state_dict());torch.save(eds.state_dict(),ROOT/'checkpoints/initial.pt')
 dump('checkpoints/initial.json',{'tensor_hash':init_hash,'file_hash':digest(ROOT/'checkpoints/initial.pt'),'seed':42,'parameters':sum(p.numel() for p in eds.parameters())})
 batch=read('data/train_G1.jsonl')[:1]*4
 loss,_,_=eng.loss(eds,batch);loss.backward();assert eds['T_plus'].u.weight.grad.norm()>0 and eds['T_plus'].b.grad.norm()>0
 assert all(p.grad is None for p in eng.model.parameters())
 with torch.no_grad():
  eds['T_plus'].b.fill_(.1);out=eds['T_plus'](h,mask);assert torch.equal(out[mask==0],h[mask==0])
 dump('calibration/smoke.json',{'frozen_bart_no_grad':True,'editor_grad_nonzero':True,'model_eval':not eng.model.training,'repeat_encode_exact':True,'padding_preserved':True,'max_gold_tokens':max(lengths),'source_length':96,'max_new_tokens':60})
 eng.infer([r['source_text'] for r in rows[:4]])
 p=ROOT/'calibration/reconstruction.jsonl';existing=read('calibration/reconstruction.jsonl') if p.exists() else [];done={r['row_id'] for r in existing}
 todo=[r for r in rows if r['row_id'] not in done]
 for i in range(0,len(todo),16):
  rs=todo[i:i+16];results,timing,lens=eng.infer([r['source_text'] for r in rs])
  with p.open('a') as f:
   for r,steps,n in zip(rs,results,lens):
    x=steps[-1];row={**r,'output':x['output'],'score':score(x['output'],r['frames'][-1],worlds[r['record_id']],x['ended']),'source_tokens':n,'steps':steps,'timing':timing};existing.append(row);f.write(json.dumps(row)+'\n')
 passed=all(r['score']['joint_ok'] for r in existing) and len(existing)==len(rows)
 dump('calibration/gate.json',{'N':len(rows),'joint_successes':sum(r['score']['joint_ok'] for r in existing),'passed':passed,'exact_matches':sum(r['source_text']==r['output'] for r in existing),'requirement':'100% semantic reconstruction','human_review':False})
 if passed:
  dump('data/test_lock.json',{'locked_after_preflight':True,'calibration_gate_hash':digest(ROOT/'calibration/gate.json'),'files':{p.name:digest(p) for p in (ROOT/'data').glob('*') if p.is_file() and p.name!='test_lock.json'}})
 print('CALIBRATION',passed,len(existing),flush=True)
if __name__=='__main__':main()
