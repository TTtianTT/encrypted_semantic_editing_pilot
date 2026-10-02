"""Only the originally budgeted P600 and dev gate; no test or supplement work."""
import argparse
from common import *
from backend import Backend
from train import train,load_editor
from evaluate import admission

def main():
    p=argparse.ArgumentParser();p.add_argument('--index',type=int,required=True);args=p.parse_args();t=read(ROOT/'atomic_preflight_tasks.json')[args.index];name=f"{t['model']}_{t['domain']}_s{t['seed']}";dest=ROOT/'atomic_preflight'/name;dest.mkdir(parents=True,exist_ok=True)
    if (dest/'complete.json').exists():return
    spec=read(ROOT/'atomic_preflight_lock.json')
    for r in spec['files']:assert digest(ROOT/r['path'])==r['sha256']
    eng=Backend(t['model']);folder=ROOT/'local/formal'/name;published=ROOT/'runs/formal'/name;published.mkdir(parents=True,exist_ok=True);d=t['domain'];worlds={w['world_id']:w for w in rows(ROOT/f'data/{d}/worlds.jsonl')};training=rows(ROOT/f'data/{d}/train_core.jsonl');dev=rows(ROOT/f'data/{d}/dev_core.jsonl')
    train(eng,folder/'P',training,dev,t['seed'],600);file=folder/'P/best.pt';P=load_editor(eng,file);gatepath=published/'dev/admission.json';gate=read(gatepath) if gatepath.exists() else admission(eng,P,dev,worlds,published/'dev');cp=dict(path=str(file),sha256=digest(file),selection=eng.cfg['selection'],seed=t['seed'])
    index=published/'checkpoint_index.json'
    if index.exists():assert read(index)['P']['sha256']==cp['sha256']
    else:dump(index,dict(P=cp))
    dump(dest/'complete.json',dict(task=t,status='atomic_admitted' if gate['passed'] else 'atomic_not_admitted',checkpoint=cp,admission=gate,resources=eng.resources(),no_test_access=True,no_extra_training_updates=True,original_formal_run=str(published)))
    print(json.dumps(dict(task=t,passed=gate['passed'],checkpoint_sha=cp['sha256'])))

if __name__=='__main__':main()
