"""Read-only mechanism review; scientific choices remain frozen."""
from futils import *
from analyze_existing import grouped
def main():
 rr=rows(ROOT/'results/fresh_mechanism.jsonl');wm={w['world_id']:w for w in ws()};render=old.semantics()[0];out=[]
 for key,one in grouped(rr,['seed','template','kind','component']).items():
  rs=[r for r in one if r['eligible']];exact=[r for r in rs if r['current']['text']==render(wm[r['world_id']],0,r['template'])]
  out.append(dict(seed=key[0],template=key[1],kind=key[2],component=key[3],eligible=len(rs),paired_success=sum(r['current']['score']['success'] and r['next']['score']['success'] for r in rs),current_exact=len(exact),next_fail_given_exact=sum(not r['next']['score']['success'] for r in exact),KL_pre=float(np.mean([r['KL_pre_S_perp'] for r in rs])) if rs else None,KL_post=float(np.mean([r['KL_post_S_perp'] for r in rs])) if rs else None))
 dump('results/mechanism_review.json',out)
 for r in out:
  if r['component'] in ('S','S_R','S_perp'):print(r,flush=True)
if __name__=='__main__':main()
