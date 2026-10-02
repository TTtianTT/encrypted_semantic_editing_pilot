import argparse,traceback
from common import *
from backend import Backend
from train import train,load_editor
from evaluate import admission

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--phase',required=True);parser.add_argument('--index',type=int,required=True);args=parser.parse_args()
    tasks=[t for t in read(ROOT/'tasks.json') if t['phase']==args.phase];task=tasks[args.index]
    model,domain,seed=task['model'],task['domain'],task['seed'];folder=ROOT/'local'/args.phase/f'{model}_{domain}_s{seed}';published=ROOT/'runs'/args.phase/f'{model}_{domain}_s{seed}';published.mkdir(parents=True,exist_ok=True)
    if (published/'complete.json').exists():print('Immutable completed task, skipped');return
    eng=Backend(model);ws={w['world_id']:w for w in rows(ROOT/f'data/{domain}/worlds.jsonl')}
    kind='symbol' if args.phase=='symbol' else 'core';training=rows(ROOT/f'data/{domain}/train_{kind}.jsonl');dev=rows(ROOT/f'data/{domain}/dev_{kind}.jsonl')
    try:
        if args.phase=='interface':
            from evaluate import atomic,rates
            eng.instruction='Copy the following text exactly. Output only the copied text.\n\n'
            result=atomic(eng,None,dev,ws,published/'reconstruction.jsonl',True)
            dump(published/'complete.json',dict(task=task,reconstruction=rates(result),instruction=eng.instruction,resources=eng.resources()))
        elif args.phase=='engineering':
            train(eng,folder/'P',training,dev,seed,eng.cfg['engineering_steps']);ed=load_editor(eng,folder/'P/best.pt');gate=admission(eng,ed,dev,ws,published)
            dump(published/'complete.json',dict(task=task,admission=gate,resources=eng.resources(),phase='engineering-only; no test accessed'))
        else:
            from formal import run_formal
            run_formal(eng,task,folder,published,training,dev,ws)
    except Exception as ex:
        dump(published/'failure.json',dict(task=task,error=type(ex).__name__,message=str(ex),traceback=traceback.format_exc(),resources=eng.resources()));raise

if __name__=='__main__':main()
