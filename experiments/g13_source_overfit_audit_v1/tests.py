"""CPU invariants plus GPU integration assertions in run.py --smoke."""
import collections, unittest
import torch
from common_g13 import *
from run import Editor
class Invariants(unittest.TestCase):
    def test_decoder_gradient_and_independent_editors(self):
        torch.manual_seed(42); a=Editor(); b=Editor(); b.load_state_dict(a.state_dict()); before=statehash(b.state_dict())
        d=torch.nn.Linear(768,7)
        for p in d.parameters(): p.requires_grad_(False)
        h=torch.randn(2,4,768); m=torch.tensor([[1,1,0,0],[1,1,1,0]])
        opt=torch.optim.AdamW(a.parameters(),lr=.001)
        loss=d(a(h,m)).square().mean(); loss.backward()
        self.assertGreater(sum(float(p.grad.norm()) for p in a.parameters()),0)
        self.assertTrue(all(p.grad is None for p in d.parameters())); opt.step()
        self.assertEqual(statehash(b.state_dict()),before); self.assertNotEqual(statehash(a.state_dict()),before)
        self.assertTrue(torch.equal(a(h,m)[~m.bool()],h[~m.bool()]))
        self.assertTrue(all(x.data_ptr()!=y.data_ptr() for x,y in zip(a.parameters(),b.parameters())))
    def test_schedule_budget_and_rotations(self):
        schedule=read(ROOT/'data/sample_schedule.jsonl'); self.assertEqual(len(schedule),200)
        src=collections.Counter(k for r in schedule for k in r['mixed_sources']); self.assertLessEqual(max(src.values())-min(src.values()),1)
        replay=collections.Counter((r['offset'],r['perspective']) for b in schedule for r in b['replay']); self.assertEqual(sum(replay.values()),3200)
        ws={w['record_id']:w for w in read(ROOT/'data/train_worlds.jsonl')}; cells=collections.Counter((ws[r['record_id']]['record_status'],r['offset'],r['perspective']) for b in schedule for r in b['replay']); self.assertEqual(len(cells),40); self.assertEqual(set(cells.values()),{80})
        self.assertTrue(all(len(b['anchor_positions'])==len(b['replay'])==16 for b in schedule))
    def test_identity_split_and_legal_five_step(self):
        ws=read(ROOT/'data/worlds.jsonl'); self.assertEqual(len(ws),2880); self.assertEqual(len({key(w) for w in ws}),len(ws))
        for w in ws:
            for d,p in atomic_specs(w): self.assertTrue(score(render(w,frame(w,d-1,p)),frame(w,d-1,p),w)['joint_ok'])
            if w['record_status']=='recorded_plan': self.assertTrue(valid(w,[frame(w,d) for d in CFG['rollout_offsets']]))
    def test_unresolved_not_confirmed_error(self):
        w=read(ROOT/'data/worlds.jsonl')[0]; s=score('unparseable',frame(w,-2),w)
        self.assertTrue(s['parse_unresolved']); self.assertFalse(s['joint_ok']); self.assertFalse(s['parsed_date_error']); self.assertFalse(s['parsed_nondate_error'])
    def test_no_free_run_gold_reset(self):
        import ast, inspect
        from run import rollout_eval
        src=inspect.getsource(rollout_eval); self.assertIn("e.encode([o['output'] for o in obs])",src)
        self.assertNotIn('load_editor',src); self.assertNotIn('stopgrad',src)
        tree=ast.parse(src); calls=[n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='encode']; self.assertEqual(len(calls),2)
if __name__=='__main__': unittest.main()
