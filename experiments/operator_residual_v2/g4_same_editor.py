"""Exp3b matched-checkpoint control for G4; S is refit on training worlds only.

P-editor S -> historical G3 is a cross-editor transfer test. This panel instead
uses the identical frozen G3 T_plus checkpoint that generated historical G4.
"""
from datetime import date,timedelta
from core import *
from fit import stats

@torch.no_grad()
def main():
    verify_protocol();eng,_=engine();eng.cap=96;eng.kw['max_new_tokens']=60
    v3=REPO/'experiments/reference_frame_pilot_v3';sys.path.insert(0,str(v3))
    from renderer_v1 import render
    from semantics_v1 import score
    from backend import Editor
    cp=v3/'checkpoints/G3/best.pt';state=load(cp);ed=Editor(768,16).cuda();ed.load_state_dict({k[len('T_plus.'):]:v for k,v in state.items() if k.startswith('T_plus.')});ed.eval().requires_grad_(False)
    alltrain=rows(v3/'data/train_worlds.jsonl')
    eligible=[w for w in alltrain if (date.fromisoformat(w['event_date'])-timedelta(days=1)).isoformat()>=w['record_date']]
    train=eligible[:96]
    assert len(train)==96
    def frame(w,off):return dict(view_date=(date.fromisoformat(w['event_date'])-timedelta(days=off)).isoformat(),perspective='first')
    def evaluate(h,m,ws,off):
        return [dict(**o,score=score(o['text'],frame(w,off),w,o['ended'])) for o,w in zip(eng.decode(h,m),ws)]
    residuals=[];qualification=[]
    for start in range(0,len(train),8):
        ws=train[start:start+8];h,m=eng.encode([render(w,frame(w,1)) for w in ws]);h=ed(ed(h,m),m)
        ref,rm=eng.encode([render(w,frame(w,-1)) for w in ws]);assert torch.equal(m,rm)
        cur=evaluate(h,m,ws,-1);cr=evaluate(ref,rm,ws,-1);nxt=evaluate(ed(h,m),m,ws,-2);nr=evaluate(ed(ref,rm),rm,ws,-2)
        for i,w in enumerate(ws):
            good=cur[i]['score']['joint_ok'] and cr[i]['score']['joint_ok'] and cur[i]['text']==cr[i]['text'] and nr[i]['score']['joint_ok'] and not nxt[i]['score']['joint_ok']
            qualification.append(dict(world_id=w['record_id'],eligible=good,current=cur[i],canonical=cr[i],next=nxt[i],canonical_next=nr[i]))
            if good:residuals.append((h[i]-ref[i])[m[i].bool()].cpu())
    assert len(residuals)>=20,'No test-based enlargement of the fixed training pool'
    x=torch.cat(residuals).double();xc=x-x.mean(0);vals,vec=torch.linalg.eigh(xc.T@xc/len(x));q=vec[:,-4:].flip(1).float()
    canonical=load(ROOT/'local/g4_canonical_pooled.pt')['pooled'];st=stats(canonical,q)
    random_q={seed:random_basis(768,4,seed) for seed in read(ROOT/'protocol.json')['random_seeds']};random_st={seed:stats(canonical,v) for seed,v in random_q.items()}
    archive=rows(REPO/'experiments/algebraic_generalization_v1/G3_trajectories.jsonl');vectors=load(REPO/'experiments/projection_hypothesis_v1/pooled_representations.pt')
    index={(r['split'],r['world_id'],r['path'],r['step']):r for r in archive};output=[]
    assert not(set(w['record_id'] for w in alltrain)&set(r['world_id'] for r in archive))
    for r in archive:
        key=(r['split'],r['world_id'],r['path'],r['step']+1)
        if r['path']!='plus_chain' or not r['endpoint_success'] or key not in index:continue
        z=vectors[f"pure/{r['split']}/{r['world_id']}/{r['step']}"];v=z['edited'];d=v@q-st['mean'];random=[]
        for seed,qq in random_q.items():
            delta=v@qq-random_st[seed]['mean'];random.append(float(delta@random_st[seed]['inverse']@delta))
        output.append(dict(dataset='G4_same_editor',basis_seed=42,world_id=r['world_id'],split=r['split'],step=r['step'],failure=not index[key]['endpoint_success'],
                           mahal=float(d@st['inverse']@d),random_mahal=float(np.mean(random)),reference_full_distance=float((z['edited']-z['gold']).norm()),no_reference=True))
    save('local/g4_same_editor_fit.pt',dict(q=q,stats=st,fit_worlds=[r['world_id'] for r in qualification if r['eligible']],checkpoint_hash=sha(cp)))
    write('results/g4_same_editor_qualification.jsonl',qualification);write('results/g4_same_editor_features.jsonl',output)
    dump('results/g4_same_editor_complete.json',dict(resources=eng.resources(),training_updates=0,fixed_training_worlds=96,qualified_training_worlds=len(residuals),
                                                  checkpoint_hash=sha(cp),code_sha256=sha(__file__),test_fitting=False))

if __name__=='__main__':main()
