"""Additional generation/structure controls; frozen checkpoints, no updates."""
import argparse,sys
from pathlib import Path
parser=argparse.ArgumentParser();parser.add_argument('--study',required=True);parser.add_argument('--model',required=True);parser.add_argument('--domain',required=True);args=parser.parse_args()
PARENT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(PARENT/args.study))
from common import *
from backend import Backend
from train import load_editor
from evaluate import atomic,gold_next,rates
from behavioral import rollout
from semantics import gold
from evaluator import score
import torch

@torch.no_grad()
def reconstruction(eng,records,worlds,path):
    if path.exists():return rows(path)
    unique={ (r['world_id'],r['state'],r['template']):r for r in records };rr=list(unique.values());output=[]
    for i in range(0,len(rr),8):
        batch=rr[i:i+8];h,m=eng.cached([r['source'] for r in batch]);pred=eng.decode(h,m)
        for r,out,mask in zip(batch,pred,m):
            w=worlds[r['world_id']];g=gold(w,r['state'],r['template']);output.append(dict(world_id=r['world_id'],template=r['template'],state=r['state'],operation=r['operation'],source=r['source'],gold=g,prediction=out['text'],score=score(out['text'],g,w,out['ended']),exact=out['text'].strip()==r['source'].strip(),mask_length=int(mask.sum()),kind='structure_reconstruction'))
    jsonl(path,output);return output

def main():
    dest=ROOT/'language_controls'/f'{args.model}_{args.domain}';dest.mkdir(parents=True,exist_ok=True)
    if (dest/'complete.json').exists():return
    eng=Backend(args.model);ws={w['world_id']:w for w in rows(ROOT/f'data/{args.domain}/worlds.jsonl')}
    dev=rows(ROOT/f'data/{args.domain}/dev_expression.jsonl')+rows(ROOT/f'data/{args.domain}/dev_challenge.jsonl');test=rows(ROOT/f'data/{args.domain}/test_expression.jsonl')+rows(ROOT/f'data/{args.domain}/test_challenge.jsonl')
    rec=reconstruction(eng,dev,ws,dest/'dev_reconstruction.jsonl');reconstruction(eng,test,ws,dest/'test_reconstruction.jsonl');templates=sorted({r['template'] for r in dev});gates=[];checkpoint_info=[]
    for seed in (42,43,44):
        origin=ROOT/'runs/formal'/f'{args.model}_{args.domain}_s{seed}';status=read(origin/'complete.json') if (origin/'complete.json').exists() else None
        if status is None or not status.get('admission',{}).get('passed'):
            gates.append(dict(seed=seed,status='not_executed_core_not_admitted_or_incomplete'));continue
        index=read(origin/'checkpoint_index.json');P=load_editor(eng,Path(index['P']['path']));out=dest/f's{seed}';out.mkdir(exist_ok=True)
        cp=index['P'];assert digest(Path(cp['path']))==cp['sha256']
        ap=out/'dev_atomic.jsonl';np=out/'dev_gold_next.jsonl';atomic_rows=rows(ap) if ap.exists() else atomic(eng,P,dev,ws,ap);next_rows=rows(np) if np.exists() else gold_next(eng,P,dev,ws,np)
        for template in templates:
            identity=rates([r for r in rec if r['template']==template]);ar=rates([r for r in atomic_rows if r['template']==template]);nr=rates([r for r in next_rows if r['template']==template]);gate=eng.cfg['gate'];passed=identity['rate']>=gate['reconstruction'] and ar['rate']>=gate['atomic'] and ar['min_cell']>=gate['min_cell'] and nr['rate']>=gate['atomic'] and nr['min_cell']>=gate['min_cell']
            gates.append(dict(seed=seed,template=template,status='admitted_structure' if passed else 'not_admitted_structure',reconstruction=identity,atomic=ar,gold_next=nr,thresholds=gate,P=cp))
            dump(dest/'gates.json',gates)
            if not passed:continue
            for role,info in index.items():
                if role not in ('P','N_h0','S_h0','M_h0','N_h1','S_h1','M_h1'):continue
                ed=load_editor(eng,Path(info['path']));path=out/role/f'trajectory_t{template}.jsonl';path.parent.mkdir(parents=True,exist_ok=True)
                if not path.exists():rollout(eng,ed,[w for w in ws.values() if w['split']=='test'],template,path)
                checkpoint_info.append(dict(seed=seed,role=role,template=template,checkpoint=info,output=str(path.relative_to(ROOT)),output_sha=digest(path)))
    dump(dest/'gates.json',gates);dump(dest/'checkpoint_index.json',checkpoint_info)
    dump(dest/'complete.json',dict(status='completed',study=args.study,model=args.model,domain=args.domain,resources=eng.resources(),config_sha=digest(ROOT/'config.json'),data_manifest_sha=digest(ROOT/'data/manifest.json'),extension_plan_sha=digest(PARENT/'four_domain_state_coverage_v1/LINGUISTIC_CONTROLS_PLAN.md'),no_training_performed=True))

if __name__=='__main__':main()
