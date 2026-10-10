"""Interim read-only review of completed closure shards; not a final result table."""
from futils import *
from analyze_existing import grouped
def main():
 rr=[r for f in sorted((ROOT/'results/shards').glob('fresh_closure_*.jsonl')) for r in old.stream(f) if r['step'] in (10,20,50)];out=[]
 for key,rs in grouped(rr,['group','seed','template','path','step']).items():
  if len(rs)!=80:continue
  out.append(dict(group=key[0],seed=key[1],template=key[2],path=key[3],step=key[4],complete_worlds=len(rs),trajectory=old.rate([r['trajectory_success'] for r in rs]),token_mse=float(np.mean([r['token_mse'] for r in rs]))))
 dump('results/closure_interim_review.json',out)
 for r in out:print(r['group'],r['seed'],r['template'],r['path'],r['step'],r['trajectory']['rate'],r['token_mse'],flush=True)
if __name__=='__main__':main()
