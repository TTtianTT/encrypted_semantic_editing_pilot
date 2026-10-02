"""Record the fixed cases already read by the supervising Codex assistant."""
from common import *

def main():
    reasons={
        ('time',42,'forward'):'Expected tomorrow; output says two days ago and drops status, color and quantity.',
        ('time',42,'reverse'):'Expected yesterday; keeps two days ago and changes quantity3 to2.',
        ('time',42,'inverse'):'Expected today with completed status and fixed facts; repeats incompatible dated/status fragments and does not end.',
        ('time',43,'forward'):'Expected tomorrow; says two days ago with a comma and omits required facts.',
        ('time',43,'reverse'):'Expected yesterday; output remains two days ago while fixed facts survive.',
        ('time',43,'inverse'):'Expected today and completed status; leaves yesterday and invents incompatible status clauses.',
        ('time',44,'forward'):'Expected tomorrow; switches to two days ago while fixed facts survive.',
        ('time',44,'reverse'):'Expected yesterday; remains two days ago while fixed facts survive.',
        ('time',44,'inverse'):'Expected today; remains yesterday while fixed facts survive.',
        ('space',42,'forward'):'Expected right; remains behind and emits an incomplete extra fragment, omitting color/quantity.',
        ('space',42,'reverse'):'Expected right with observer David; output calls the parcel the observer and omits the relation/facts.',
        ('space',42,'inverse'):'Expected left; repeats front and omits fixed facts without ending.'}
    cases=[];reviews=[]
    for (d,seed,trajectory),reason in reasons.items():
        path=ROOT/'runs/formal'/f't5gemma_{d}_s{seed}'/'outputs/P/trajectory_t0.jsonl';rr=rows(path);world=min(r['world_id'] for r in rr);group=[r for r in rr if r['world_id']==world and r['trajectory']==trajectory];current=next(r for r in group if r['mode']=='latent' and r['step']==1);nxt=next(r for r in group if r['mode']=='latent' and r['step']==2);control=next(r for r in group if r['mode']=='gold_reencode' and r['step']==2)
        assert current['score']['success'] and control['score']['success'] and not nxt['score']['success']
        key=f't5gemma/{d}/s{seed}/{world}/{trajectory}'
        cases.append(dict(case_id=key,domain=d,seed=seed,world_id=world,trajectory=trajectory,current=current,next=nxt,gold_reencode_control=control,artifact=str(path.relative_to(ROOT)),artifact_sha256=digest(path)))
        reviews.append(dict(case_id=key,domain=d,seed=seed,clear_failure=True,reason=reason,reviewer='supervising Codex assistant',independent_human_label=False))
    jsonl(ROOT/'t5_continuation_review_set.jsonl',cases);dump(ROOT/'T5_CONTINUATION_AGENT_REVIEW.json',dict(selection='Lexically first test world, P/core, step1→2 for forward/reverse/inverse. All available time seeds42/43/44 and original-facing space seed42. Fixed world/trajectory selection without ranking outcomes. Space cases are not corrected relation-confirmation evidence.',cases=reviews,reviewed_after_actual_predictions=True,case_set_sha256=digest(ROOT/'t5_continuation_review_set.jsonl'),limitation='Existence examples, not population annotation or causal mechanism; not proof all unresolved outputs are wrong. Formal evaluations for time42/44 and space42 still incomplete at this review.'))
    print('Recorded12 directly reviewed T5 continuation cases')

if __name__=='__main__':main()
