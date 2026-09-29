"""Small nonlinear fallback only after the linear temporal probe failed validation."""
import json,sys
from pathlib import Path
import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader,TensorDataset

HERE=Path(__file__).resolve().parent
V3=HERE.parent/'reference_frame_pilot_v3'
sys.path.insert(0,str(HERE));sys.path.insert(0,str(V3))
from calibrate_probe import cases,features,get_worlds,Engine,new_editors,SubspaceEditor,write_json,write_jsonl

class Reader(nn.Module):
    def __init__(self):
        super().__init__();self.net=nn.Sequential(nn.Linear(768,64),nn.ReLU(),nn.Linear(64,10))
    def forward(self,x):return self.net(x)

def main():
    torch.manual_seed(42);np.random.seed(42)
    eng=Engine();g3=new_editors();g3.load_state_dict(torch.load(V3/'checkpoints/G3/best.pt',weights_only=True))
    state=torch.load(HERE/'repair.pt',weights_only=True);R=state['T_plus.R'].cuda()
    repair=nn.ModuleDict({op:SubspaceEditor(R,g3[op]) for op in ['T_plus','T_minus']});repair.load_state_dict(state)
    tx,tm=features(eng,cases(get_worlds('train')),g3,repair)
    dx,dm=features(eng,cases(get_worlds('dev')),g3,repair)
    ti=np.array([i for i,z in enumerate(tm) if z['group']=='G3']);di=np.array([i for i,z in enumerate(dm) if z['group']=='G3'])
    center=tx[ti].mean(0);scale=tx[ti].std(0).clip(min=.05)
    train_x=torch.tensor((tx[ti]-center)/scale,dtype=torch.float32)
    dev_x=torch.tensor((dx[di]-center)/scale,dtype=torch.float32,device='cuda')
    train_y=torch.tensor([tm[i]['offset']+4 for i in ti],dtype=torch.long)
    dev_y=np.array([dm[i]['offset']+4 for i in di])
    train_steps=np.array([tm[i]['step'] for i in ti]);dev_steps=np.array([dm[i]['step'] for i in di])
    model=Reader().cuda();opt=torch.optim.AdamW(model.parameters(),lr=.001,weight_decay=.01)
    loader=DataLoader(TensorDataset(train_x,train_y),batch_size=256,shuffle=True,generator=torch.Generator().manual_seed(42))
    history=[];best=-1;best_epoch=0;best_state=None
    for epoch in range(1,31):
        model.train()
        for x,y in loader:
            x=x.cuda();y=y.cuda();opt.zero_grad(set_to_none=True)
            loss=nn.functional.cross_entropy(model(x),y);loss.backward();opt.step()
        model.eval()
        with torch.no_grad():p=model(dev_x).argmax(1).cpu().numpy()
        acc=[float(np.mean(p[dev_steps==k]==dev_y[dev_steps==k])) for k in range(3)]
        selected=sum(acc)/3
        history.append(dict(epoch=epoch,dev_accuracy_by_step=acc,mean_dev_accuracy=selected))
        if selected>best:
            best=selected;best_epoch=epoch;best_state={k:v.detach().cpu().clone() for k,v in model.state_dict().items()}
        if epoch-best_epoch>=5:break
    model.load_state_dict(best_state);model.eval()
    torch.save(dict(state=best_state,center=torch.tensor(center),scale=torch.tensor(scale),epoch=best_epoch),HERE/'mlp_probe.pt')
    write_json('mlp_probe_validation.json',dict(train_worlds=len(get_worlds('train')),dev_worlds=len(get_worlds('dev')),
                                                 train_examples=len(ti),dev_examples=len(di),hidden_width=64,epochs_run=len(history),
                                                 selected_epoch=best_epoch,selected_mean_dev_accuracy=best,history=history,
                                                 no_test_fit=True,max_trained_steps=2))
    data=torch.load(HERE/'G3_latents.pt',map_location='cpu',weights_only=False)
    keys=list(data);pred=[]
    for i in range(0,len(keys),256):
        kk=keys[i:i+256]
        xx=np.stack([(z['latent'].float()*z['mask'][:,None]).sum(0).numpy()/int(z['mask'].sum()) for z in (data[k] for k in kk)])
        x=torch.tensor((xx-center)/scale,dtype=torch.float32,device='cuda')
        with torch.no_grad():yy=(model(x).argmax(1)-4).cpu().tolist()
        pred.extend(dict(key=k,predicted_offset=y) for k,y in zip(kk,yy))
    write_jsonl('mlp_probe_predictions.jsonl',pred)
    print('MLP best dev',best_epoch,best,flush=True)

if __name__=='__main__':main()
