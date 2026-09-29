"""CPU invariant check with nonzero residuals, complementing real-batch GPU checks."""
import torch
from common import *
from backend import Editor
results=[]
for path in (ROOT/'models').glob('*_interface.json'):
 c=json.loads(path.read_text());d=c.get('encoder_output_dimension')
 if d is None:continue
 torch.manual_seed(42);ed=Editor(d);h=torch.randn(2,9,d);mask=torch.tensor([[1,1,1,1,1,0,0,0,0],[1,1,1,1,1,1,1,0,0]])
 with torch.no_grad():ed.b.fill_(.01);ed.u.weight.normal_(std=.01);edited=ed(h,mask)
 assert torch.equal(edited[mask==0],h[mask==0]);assert not torch.equal(edited[mask==1],h[mask==1]);assert sum(p.numel() for p in ed.parameters())==33*d
 results.append(dict(model=path.name.removesuffix('_interface.json'),d=d,padding_exactly_unchanged=True,active_tokens_changed=True,parameters=33*d,input='synthetic CPU tensor using observed d; no model outputs or editor training'))
dump('calibration/nonzero_mask_invariant.json',results);print('nonzero mask checks',len(results))
