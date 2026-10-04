"""CPU-only progress watcher; never submits, cancels, loads a model or uses CUDA."""
import argparse, datetime, json, pathlib, subprocess, time

ROOT=pathlib.Path(__file__).resolve().parent

def snapshot():
    result={}
    for seed in (42,43,44):
        run=ROOT/f'runs/formal/s{seed}'
        trained=[p.parent.name for p in (ROOT/f'local/s{seed}').glob('*/training_status.json')
                 if json.loads(p.read_text())['completed_updates']==200]
        evaluated=[p.parent.name for p in run.glob('*/complete.json')]
        active={p.parent.name:len(list(p.glob('*.jsonl'))) for p in run.glob('*/trajectories')
                if not (p.parent/'complete.json').exists()}
        result[seed]={'trained':sorted(trained),'evaluated':sorted(evaluated),'trajectory_batches':active,
                      'complete':(run/'complete.json').exists(), 'failure':(run/'failure.json').exists()}
    return result

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--once',action='store_true');args=parser.parse_args()
    while True:
        state=snapshot()
        utc=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
        print(json.dumps({'utc':utc,'progress':state},ensure_ascii=False),flush=True)
        if args.once or all(s['complete'] for s in state.values()):return
        time.sleep(45)

if __name__=='__main__':main()
