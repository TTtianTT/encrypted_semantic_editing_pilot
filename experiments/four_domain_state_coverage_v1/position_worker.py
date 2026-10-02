"""Slurm-only frozen-checkpoint evaluations of registered position diagnostics."""
import argparse,sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--study',required=True);p.add_argument('--domain',required=True);p.add_argument('--model',required=True);args=p.parse_args()
PARENT=Path(__file__).resolve().parent.parent;PRIMARY=PARENT/'four_domain_state_coverage_v1';sys.path.insert(0,str(PARENT/args.study))
from common import *
from backend import Backend
from train import load_editor
import evaluate,behavioral
from semantics import gold as original_gold,render as original_render
from evaluator import score as original_score
from position_spec import make_functions
gold,render,score=make_functions(original_gold,original_render,original_score)
# Redirect only this extension's local evaluation functions. Neither training
# modules nor files in either frozen primary study are changed.
evaluate.gold=gold;evaluate.render=render;evaluate.score=score
behavioral.gold=gold;behavioral.render=render;behavioral.score=score
import torch

@torch.no_grad()
def main():
    lock=read(PRIMARY/'position_lock.json')
    for item in lock['files']:assert digest(Path(item['path']))==item['sha256'],'Position specification changed'
    dest=ROOT/'position_foils'/f'{args.model}_{args.domain}';dest.mkdir(parents=True,exist_ok=True)
    if (dest/'complete.json').exists():return
    eng=Backend(args.model);data=ROOT/'position_foils/data'/args.domain;ws={w['world_id']:w for w in rows(data/'worlds.jsonl')};dev=rows(data/'dev.jsonl');test=rows(data/'test.jsonl');gates=[];checkpoints=[]
    for split,rs in [('dev',dev),('test',test)]:
        path=dest/f'{split}_reconstruction.jsonl'
        if not path.exists():evaluate.atomic(eng,None,rs,ws,path,True)
    rec=rows(dest/'dev_reconstruction.jsonl')
    for seed in (42,43,44):
        origin=ROOT/'runs/formal'/f'{args.model}_{args.domain}_s{seed}';cpfile=origin/'checkpoint_index.json'
        if not cpfile.exists():gates.append(dict(seed=seed,status='missing_atomic_checkpoint'));continue
        index=read(cpfile);out=dest/f's{seed}';out.mkdir(exist_ok=True)
        if 'P' not in index:gates.append(dict(seed=seed,status='missing_atomic_checkpoint'));continue
        for role,info in index.items():
            if role not in ('P','N_h0','S_h0','M_h0','N_h1','S_h1','M_h1'):continue
            cp=Path(info['path']);assert digest(cp)==info['sha256'];ed=load_editor(eng,cp);folder=out/role;folder.mkdir(exist_ok=True)
            path=folder/'test_atomic.jsonl'
            if not path.exists():evaluate.atomic(eng,ed,test,ws,path)
            checkpoints.append(dict(seed=seed,role=role,checkpoint=info,output=str(path.relative_to(ROOT)),sha256=digest(path)))
            if role!='P':continue
            ap=out/'dev_atomic.jsonl';np=out/'dev_gold_next.jsonl'
            if not ap.exists():evaluate.atomic(eng,ed,dev,ws,ap)
            if not np.exists():evaluate.gold_next(eng,ed,dev,ws,np)
            aa=rows(ap);nn=rows(np)
            for variant in sorted({r['template'] for r in dev}):
                ri=evaluate.rates([r for r in rec if r['template']==variant]);ar=evaluate.rates([r for r in aa if r['template']==variant]);nr=evaluate.rates([r for r in nn if r['template']==variant]);g=eng.cfg['gate'];passed=ri['rate']>=g['reconstruction'] and ar['rate']>=g['atomic'] and nr['rate']>=g['atomic'] and min(ar['min_cell'],nr['min_cell'])>=g['min_cell']
                gates.append(dict(seed=seed,variant=variant,status='admitted' if passed else 'not_admitted',reconstruction=ri,atomic=ar,gold_next=nr,thresholds=g));dump(dest/'gates.json',gates)
        for gate in [r for r in gates if r['seed']==seed and r.get('status')=='admitted']:
            for role,info in index.items():
                if role not in ('P','N_h0','S_h0','M_h0','N_h1','S_h1','M_h1'):continue
                cp=Path(info['path']);ed=load_editor(eng,cp);path=out/role/f"trajectory_v{gate['variant']}.jsonl"
                if not path.exists():behavioral.rollout(eng,ed,[w for w in ws.values() if w['split']=='test'],gate['variant'],path)
                checkpoints.append(dict(seed=seed,role=role,variant=gate['variant'],checkpoint=info,output=str(path.relative_to(ROOT)),sha256=digest(path)))
    dump(dest/'gates.json',gates);dump(dest/'checkpoint_index.json',checkpoints)
    dump(dest/'complete.json',dict(status='completed',study=args.study,model=args.model,domain=args.domain,resources=eng.resources(),specification_sha=digest(PRIMARY/'position_lock.json'),no_training_performed=True))

if __name__=='__main__':main()
