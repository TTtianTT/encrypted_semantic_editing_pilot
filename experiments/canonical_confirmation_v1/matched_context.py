"""A reproducible fixed current-state/next-operation comparison from old records."""
from futils import *
from analyze_existing import grouped
def main():
 rs=[r for r in old.stream(ROOT/'results/lagged_continuation.jsonl') if r['path']=='aligned_from_plus_one' and r['next_step']==2]
 out=[]
 for key,one in grouped(rs,['condition','setting','seed','template']).items():
  out.append(dict(condition=key[0],setting=key[1],seed=key[2],template=key[3],state=0,next_operation='plus',n=len(one),entering_token_mse=float(np.mean([r['entering_token_mse'] for r in one])),entering_S_mse=float(np.mean([r['entering_S_mse'] for r in one])),next_success=old.rate([r['next_success'] for r in one])))
 dump('results/risk_matched_context.json',out)
if __name__=='__main__':main()
