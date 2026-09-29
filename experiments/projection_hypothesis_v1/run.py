"""G5: fixed G3 editor; compare pure latent and decode/re-encode through five steps."""
import hashlib,json,sys,time
from collections import defaultdict
from pathlib import Path

import torch
import torch.nn.functional as F

HERE=Path(__file__).resolve().parent
G4=HERE.parent/'algebraic_generalization_v1'
V3=HERE.parent/'reference_frame_pilot_v3'
REPO=HERE.parents[1]
sys.path.insert(0,str(V3))
from common import frame,render,score,digest
from engine import Engine,new_editors

CFG=json.loads((HERE/'config.json').read_text())

def readjsonl(p):return [json.loads(s) for s in p.read_text().splitlines()]
def writejsonl(p,rs):
    with p.open('w') as f:
        for r in rs:f.write(json.dumps(r,ensure_ascii=False)+'\n')
def writejson(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def pooled(h,m):return (h.float()*m[...,None]).sum(1)/m.sum(1).clamp(min=1)[:,None]
def distances(x,g):
    return dict(cosine=float(1-F.cosine_similarity(x[None],g[None]).item()),
                normalized_l2=float((x-g).norm().item()/g.norm().item()))

class TimeProbe(torch.nn.Module):
    def __init__(self):
        super().__init__();self.net=torch.nn.Sequential(torch.nn.Linear(768,64),torch.nn.ReLU(),torch.nn.Linear(64,10))
        payload=torch.load(G4/'mlp_probe.pt',map_location='cpu',weights_only=True)
        self.net.load_state_dict({k.removeprefix('net.'):v for k,v in payload['state'].items()});self.net.cuda().eval()
        self.register_buffer('center',payload['center'].cuda());self.register_buffer('scale',payload['scale'].cuda())
    @torch.no_grad()
    def predict(self,h,m):
        z=(pooled(h,m)-self.center)/self.scale
        return (self.net(z).argmax(1)-4).tolist()

def score_record(text,f,w,ended):
    s=score(text,f,w,ended)
    return dict(success=bool(s['joint_ok']),fact_preservation=bool(s['nondate_facts_ok']),
                parse_unresolved=bool(s['parse_unresolved']),decoded_semantic_state=s['parsed'],normal_end=bool(ended))

@torch.no_grad()
def main():
    lock=json.loads((V3/'checkpoints/locked.json').read_text())
    assert digest(V3/'checkpoints/G3/best.pt')==lock['groups']['G3']
    g4run=json.loads((G4/'run_complete.json').read_text())
    assert digest(G4/'G3_latents.pt')==g4run['baseline_latents_sha256']
    pure=[r for r in readjsonl(G4/'G3_trajectories.jsonl') if r['path']=='plus_chain']
    assert len(pure)==530
    pure_idx={(r['split'],r['world_id'],r['step']):r for r in pure}
    latent=torch.load(G4/'G3_latents.pt',map_location='cpu',weights_only=False)
    worlds={w['record_id']:w for split in ['test_iid','test_template_ood'] for w in readjsonl(V3/f'data/{split}_worlds.jsonl')}
    selected={split:sorted({r['world_id'] for r in pure if r['split']==split}) for split in ['test_iid','test_template_ood']}
    assert all(len(v)==CFG['worlds_per_split'] for v in selected.values())
    g4split=json.loads((G4/'probe_split.json').read_text())
    assert set(selected['test_iid']+selected['test_template_ood'])==set(g4split['test_world_ids'])
    eng=Engine();eds=new_editors();eds.load_state_dict(torch.load(V3/'checkpoints/G3/best.pt',weights_only=True));eds.eval()
    probe=TimeProbe();assert all(not p.requires_grad for p in eng.model.parameters())
    gold={};vectors={};pureout=[];dreout=[];started=time.time()
    for split,ids in selected.items():
        # Encode all gold stages once, with the same frozen encoder as both paths.
        for step in range(1,6):
            for start in range(0,len(ids),16):
                sub=ids[start:start+16]
                texts=[pure_idx[split,w,step]['gold_text'] for w in sub]
                gh,gm,_=eng.encode(texts)
                for i,w in enumerate(sub):gold[split,w,step]=pooled(gh[i:i+1],gm[i:i+1])[0].detach()
        for start in range(0,len(ids),8):
            sub=ids[start:start+8]
            # Independent reset control applied to every frozen G4 pure-latent stage.
            for step in range(1,6):
                base=[pure_idx[split,w,step] for w in sub]
                hh=torch.stack([latent[f'{split}/{w}/plus_chain/{step}']['latent'] for w in sub]).cuda()
                mm=torch.stack([latent[f'{split}/{w}/plus_chain/{step}']['mask'] for w in sub]).cuda()
                texts=[r['decoded_text'] for r in base]
                reset,rm,_=eng.encode(texts)
                reset_text,reset_end,_,_=eng.decode(reset,rm)
                bp=probe.predict(hh,mm);rp=probe.predict(reset,rm)
                ep=pooled(hh,mm);pp=pooled(reset,rm)
                for i,w in enumerate(sub):
                    g=gold[split,w,step];r=base[i];f=r['gold_frame'];world=worlds[w]
                    key=f'{split}/{w}/{step}'
                    rec=dict(path='pure_latent',split=split,world_id=w,step=step,source_text=r['source_text'],
                             decoded_text=texts[i],gold_text=r['gold_text'],gold_frame=f,gold_semantic_state=r['gold_semantic_state'],
                             edited=score_record(texts[i],f,world,r['normal_end']),edited_probe_offset=bp[i],
                             edited_distance=distances(ep[i],g),residual_norm=r['residual_norm'],edited_mask_length=int(mm[i].sum()),
                             reset_text=reset_text[i],reset=score_record(reset_text[i],f,world,reset_end[i]),
                             reset_probe_offset=rp[i],reset_distance=distances(pp[i],g),reset_mask_length=int(rm[i].sum()))
                    pureout.append(rec)
                    vectors['pure/'+key]=dict(edited=ep[i].cpu(),reset=pp[i].cpu(),gold=g.cpu())
            # Decode-reencode has its own evolving text and mask; no gold fed into the chain.
            source=[pure_idx[split,w,1]['source_text'] for w in sub]
            current,cm,_=eng.encode(source)
            for step in range(1,6):
                edit=eds['T_plus'](current,cm)
                residual=(edit-current)*cm[...,None]
                texts,ended,_,_=eng.decode(edit,cm)
                reset,rm,_=eng.encode(texts)
                reset_text,reset_end,_,_=eng.decode(reset,rm)
                ep=pooled(edit,cm);pp=pooled(reset,rm)
                bp=probe.predict(edit,cm);rp=probe.predict(reset,rm)
                for i,w in enumerate(sub):
                    r=pure_idx[split,w,step];g=gold[split,w,step];f=r['gold_frame'];world=worlds[w]
                    key=f'{split}/{w}/{step}'
                    active=cm[i].bool();rn=float(residual[i][active].float().norm()/active.sum().sqrt())
                    rec=dict(path='decode_reencode',split=split,world_id=w,step=step,source_text=source[i],
                             input_text=source[i] if step==1 else previous_text[i],decoded_text=texts[i],
                             gold_text=r['gold_text'],gold_frame=f,gold_semantic_state=r['gold_semantic_state'],
                             edited=score_record(texts[i],f,world,ended[i]),edited_probe_offset=bp[i],
                             edited_distance=distances(ep[i],g),residual_norm=rn,edited_mask_length=int(cm[i].sum()),
                             reset_text=reset_text[i],reset=score_record(reset_text[i],f,world,reset_end[i]),
                             reset_probe_offset=rp[i],reset_distance=distances(pp[i],g),reset_mask_length=int(rm[i].sum()))
                    dreout.append(rec)
                    vectors['decode_reencode/'+key]=dict(edited=ep[i].cpu(),reset=pp[i].cpu(),gold=g.cpu())
                previous_text=texts
                current,cm=reset,rm
            print('complete',split,start+len(sub),'/',len(ids),flush=True)
    writejsonl(HERE/'pure_reset_controls.jsonl',pureout)
    writejsonl(HERE/'decode_reencode_trajectories.jsonl',dreout)
    torch.save(vectors,HERE/'pooled_representations.pt')
    writejson(HERE/'provenance.json',dict(config=CFG,checkpoint_sha256=digest(V3/'checkpoints/G3/best.pt'),
                                          bart_sha256=digest(REPO/'models/bart-base/model.safetensors'),
                                          g4_pure_trajectories_sha256=digest(G4/'G3_trajectories.jsonl'),
                                          g4_pure_latents_sha256=digest(G4/'G3_latents.pt'),
                                          g4_probe_sha256=digest(G4/'mlp_probe.pt'),
                                          g4_split_sha256=digest(G4/'probe_split.json'),
                                          world_file_sha256={split:digest(V3/f'data/{split}_worlds.jsonl') for split in selected},
                                          world_ids=selected,editor_training='none',new_projector_training='none'))
    writejson(HERE/'run_complete.json',dict(completed=True,steps_per_path=len(pureout),
                                            pure_output_sha256=digest(HERE/'pure_reset_controls.jsonl'),
                                            decode_reencode_output_sha256=digest(HERE/'decode_reencode_trajectories.jsonl'),
                                            pooled_representations_sha256=digest(HERE/'pooled_representations.pt'),
                                            elapsed_seconds=time.time()-started,peak_cuda_bytes=torch.cuda.max_memory_allocated()))

if __name__=='__main__':main()
