"""One real-batch interface/gradient/mask check; no optimizer update."""
import sys,os,torch,json
from g10_common import *
sys.path.insert(0,str(G7));sys.path.insert(0,str(V3));sys.path.insert(0,str(ROOT))
from extract import Backbone,readjsonl
sys.path.insert(0,str(ROOT))
from train import LowRank
from common import score

def main():
 assert os.environ.get('SLURM_JOB_ID'),'Run the BART preflight on a Slurm GPU allocation'
 torch.manual_seed(42);base=Backbone('BART');base.model.eval();schedule=[b for b in read(V3/'data/sample_schedule.jsonl') if b['path'].startswith('T_plus')]
 b=next(x for x in schedule if any(x['g2_replace']));rows=read(V3/'data/train_G1.jsonl');batch=[rows[k] for k in b['pair_indices']]
 world={w['record_id']:w for w in read(V3/'data/train_worlds.jsonl')};ed=LowRank(base.U.shape[0],8).cuda().eval()
 for p in base.model.parameters():p.grad=None;assert not p.requires_grad
 source=[r['source_text'] for r in batch];h,m=base.encode(source);identity=ed(h,m)
 assert torch.equal(identity,h) and torch.equal(identity[~m.bool()],h[~m.bool()])
 direct=base.eng.decode(h,m)[0];via=base.eng.decode(identity,m)[0];assert direct==via
 loss,stats=base.eng.stage_loss(torch.nn.ModuleDict({'T_plus':ed}),batch,b['g2_replace'],world,.5,.5)
 assert torch.isfinite(loss);loss.backward()
 assert all(p.grad is None for p in base.model.parameters())
 active=sum(p.grad is not None and bool(torch.isfinite(p.grad).all()) and bool(p.grad.abs().sum()>0) for p in ed.parameters())
 assert active>=2
 result=dict(passed=True,job_id=os.environ['SLURM_JOB_ID'],batch_size=len(batch),replacement_count=sum(b['g2_replace']),
  loss=float(loss.detach()),stats=stats,active_nonzero_gradient_tensors=active,backbone_gradients_absent=True,
  backbone_requires_grad_false=True,zero_editor_identity_exact=True,padding_identity_exact=True,
  identity_direct_generate_equal=True,dtype=str(h.dtype),input_tokens=int(m.sum()),encoder_length=int(m.shape[1]))
 dump('calibration/preflight.json',result);print('G10 preflight passed',json.dumps(result),flush=True)
if __name__=='__main__':main()
