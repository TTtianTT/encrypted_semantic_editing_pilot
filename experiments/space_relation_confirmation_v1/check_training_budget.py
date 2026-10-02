"""Verify matched S/M update, semantic-label and replay budgets on CPU."""
from common import *

def main():
    verified=[]
    for run in sorted((ROOT/'local/formal').glob('*')):
        for h in (0,1):
            s=run/f'S_h{h}/training.jsonl';m=run/f'M_h{h}/training.jsonl'
            if not s.exists() or not m.exists():continue
            sr,mr=rows(s),rows(m);assert len(sr)==len(mr)==200
            for a,b in zip(sr,mr):
                assert a['step']==b['step'] and a['operation']==b['operation']
                assert a['supervised_semantic_units']==b['supervised_semantic_units']==8
                assert a['world_ids'][:4]==b['world_ids'][:4] and a['states'][:4]==b['states'][:4]
                assert a['world_ids'][6:]==b['world_ids'][6:] and a['states'][6:]==b['states'][6:]
            verified.append(dict(run=run.name,holdout_split=h,updates=200,natural_units=800,focus_units=400,old_source_units=400,S_target_tokens=sum(r['target_tokens'] for r in sr),M_target_tokens=sum(r['target_tokens'] for r in mr),S_focus_states=sorted({state for r in sr for state in r['states'][4:6]}),M_focus_states=sorted({state for r in mr for state in r['states'][4:6]}),general_and_old_draws_byte_matched=True,equal_target_tokens=False,equal_semantic_units=True))
    dump(ROOT/'matched_training_budget_audit.json',dict(verified=verified,interpretation='Per-example token-mean CE fixes equal endpoint supervision units, not equal target tokens or FLOPs'))
    print('Verified matched S/M budgets',len(verified))

if __name__=='__main__':main()
