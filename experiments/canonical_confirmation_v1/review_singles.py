"""Check canonical single-step prerequisites from completed predictions."""
from futils import *
from analyze_existing import grouped
def main():
 supported={d:{(s,op) for op,rr in items(d).items() for _,s,_ in rr} for d in ('time','person')}
 rs=[r for r in old.stream(ROOT/'results/fresh_single.jsonl') if (r['source_state'],r['operation']) in supported[r['domain']] and (r['group']!='C4' or r['checkpoint'] in (0,50))];out=[]
 for key,one in grouped(rs,['domain','group','seed','checkpoint','template']).items():
  worlds=grouped(one,['world_id']);a=dict(domain=key[0],group=key[1],seed=key[2],checkpoint=key[3],template=key[4],single_all_edges=old.rate([all(r['output']['score']['success'] for r in rr) for rr in worlds.values()]),single_mean=float(np.mean([r['output']['score']['success'] for r in one])),MSE=float(np.mean([r['token_mse'] for r in one if r['token_mse'] is not None])) if any(r['token_mse'] is not None for r in one) else None);out.append(a)
 dump('results/single_prerequisite_review.json',out)
 for r in out:print(r['domain'],r['group'],r['seed'],r['checkpoint'],r['template'],r['single_mean'],r['single_all_edges']['rate'],r['MSE'],flush=True)
if __name__=='__main__':main()
