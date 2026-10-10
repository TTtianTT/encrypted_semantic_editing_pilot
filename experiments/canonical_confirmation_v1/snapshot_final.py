"""Read-only progress snapshot from completed fresh evaluation predictions."""
from futils import *
from analyze_existing import grouped
def main():
 rs=[r for r in old.stream(ROOT/'results/fresh_chain.jsonl') if r['path'] in ('aligned_from_plus_one','person_forward') and (r['group']!='C4' or r['checkpoint'] in (0,10,25,50))]
 out=[]
 for key,one in grouped(rs,['domain','group','seed','checkpoint','template']).items():
  out.append(dict(domain=key[0],group=key[1],seed=key[2],checkpoint=key[3],template=key[4],R1_to_R5=[old.rate([r['trajectory_success'] for r in one if r['step']==k]) for k in range(1,6)]))
 dump('results/fresh_progress_snapshot.json',out)
 for r in out:print(r['domain'],r['group'],r['seed'],r['checkpoint'],r['template'],[v['rate'] for v in r['R1_to_R5']],flush=True)
if __name__=='__main__':main()
