"""Only run after admission passes; benchmark without optimizer updates and reserve evaluation."""
import argparse,time,torch,shutil
from common import *
from backend import Backend,new_editors

def main(name):
 a=json.loads((ROOT/f'calibration/{name}/admission.json').read_text());assert a['passed'];be=Backend(name);eds=new_editors(be.d);rows=read('data/train_G1.jsonl');b=next(b for b in read('data/sample_schedule.jsonl') if b['path']=='T_plus_first');rs=[rows[k] for k in b['pair_indices']];worlds={w['record_id']:w for w in read('data/train_worlds.jsonl')};est={}
 for g in ['G1','G3']:
  terminal=[render(worlds[r['record_id']],advance(r['frames'][-1],'T_plus')) if g=='G3' and f else r['target_text'] for r,f in zip(rs,b['g2_replace'])];den=sum(map(len,be.label_ids(terminal)));eds.zero_grad(set_to_none=True);torch.cuda.synchronize();t=time.monotonic()
  for i in range(0,16,4):l,stats=be.objective(eds,rs[i:i+4],b['g2_replace'][i:i+4],worlds,g,den);l.backward()
  torch.cuda.synchronize();est[g]=(time.monotonic()-t)*600*1.5 # include dev overhead, conservative temporal/chain batch
  assert all(p.grad is None for p in be.model.parameters())
 timing=json.loads((ROOT/f"calibration/{name}/timing_{a['selected_wrapper']}.json").read_text())
 # One fixed inference-throughput check, not a prompt/rank/learning-rate search.
 reference=read(f"calibration/{name}/{a['selected_wrapper']}_unique_outputs.jsonl")[:32];gen_seconds=0.;same=True
 for i in range(0,32,16):
  rr=reference[i:i+16];t=time.monotonic();out,_,_=be.infer([r['source_text'] for r in rr],None,[]);gen_seconds+=time.monotonic()-t;same &= all(ss[0]['output']==r['output'] and ss[0]['ended']==r['ended'] for r,ss in zip(rr,out))
 evaluation=gen_seconds/32*26000 if same else timing['estimated_full_evaluation_seconds']
 if same:
  interface=ROOT/f'models/{name}_interface.json';shutil.copyfile(interface,ROOT/f'models/{name}_interface_before_batch_lock.json');be.cfg['generation_batch_size']=16;dump(f'models/{name}_interface.json',be.cfg)
 dump(f'calibration/{name}/inference_batch_check.json',dict(N=32,archived_batch_size=4,checked_batch_size=16,exact_outputs_and_endings=same,chosen_inference_batch=16 if same else 4,seconds=gen_seconds,criterion='all 32 exact, otherwise retain 4; no other batch search'))
 budget=json.loads((ROOT/'budget.json').read_text());need=sum(est.values())+1.5*evaluation
 decision=dict(training_estimate_seconds=est,evaluation_estimate_seconds=evaluation,evaluation_reserve_seconds=1.5*evaluation,total_required_estimate_seconds=need,remaining_at_decision=budget['remaining_gpu_seconds'],run_training=need<budget['remaining_gpu_seconds']-120,actual_benchmark_seconds=time.monotonic()-be.started,optimizer_updates=0,reason='predefined 1.5x evaluation reserve and measured training cost')
 dump(f'checkpoints/{name}/budget_gate.json',decision);print(decision)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('model');main(p.parse_args().model)
