"""CPU state-flow guards exercise the actual production handoff functions."""
import collections, inspect, unittest
from types import SimpleNamespace
import torch
from common_g14 import *
run=load_module('g14_actual_state_flow',ROOT/'run.py')

class FakeEngine:
    def __init__(self,w):self.w=w;self.inputs=[]
    def encode(self,texts):
        self.inputs.append(list(texts)); natural=texts[0]==render(self.w,frame(self.w,0))
        h=torch.tensor([[[99. if natural else 0.]]]);m=torch.ones((1,4 if natural else 3),dtype=torch.long)
        return h,m,0
    def batch(self,texts):
        natural=texts[0]==render(self.w,frame(self.w,0))
        return SimpleNamespace(input_ids=torch.full((1,4 if natural else 3),99 if natural else 0,dtype=torch.long))
    def decode(self,h,m):return [f'own-state-{int(h.item())}'],[True],[1],0

class FlowTests(unittest.TestCase):
    def setUp(self):
        self.w=next(w for w in read(G13/'data/iid_worlds.jsonl') if w['record_status']=='recorded_plan');self.e=FakeEngine(self.w)
        self.eds={'G':lambda h,m:h+1,'F3':lambda h,m:h+10,'F2':lambda h,m:h+100}
        self.states,self.cur,_=run.produce(self.e,self.eds,[self.w]);self.gates=run.cohort_rows(self.states,self.cur,[self.w],42,'F3')
    def evaluate(self):return run.evaluate(self.e,self.states,self.cur,self.eds,[self.w],42,'F3',self.gates,{'G':'g','F3':'r','F2':'f2'})
    def test_source_is_encoded_once_and_shared(self):
        self.assertEqual(len(self.e.inputs),2);self.assertEqual(self.states['G']['memory'].item(),1);self.assertEqual(self.states['F3']['memory'].item(),10)
        self.assertIs(self.states['G']['mask'],self.states['F3']['mask']);self.assertEqual(self.states['start']['memory'].item(),0)
    def test_cross_recipients_and_no_second_latent_encoding(self):
        rows=self.evaluate();lat=[r for r in rows if r['mode']=='latent']
        self.assertEqual([(r['producer'],r['receiver'],r['next_output']) for r in lat],[('G','G','own-state-2'),('G','R','own-state-11'),('R','G','own-state-11'),('R','R','own-state-20')])
        self.assertEqual(len(self.e.inputs),4) # source, natural, and only two actual reset controls
    def test_reset_uses_actual_free_text_never_gold(self):
        self.evaluate();self.assertEqual(self.e.inputs[-2:],[[self.cur['G'][0]['output']],[self.cur['F3'][0]['output']]])
        self.assertNotEqual(self.e.inputs[-1],[self.cur['F3'][0]['gold']]);self.assertNotIn([render(self.w,frame(self.w,-1))],self.e.inputs)
    def test_current_gate_cannot_depend_on_next_output(self):
        a=observe_text(render(self.w,frame(self.w,0)),True,self.w,0)
        self.cur={name:[a.copy()] for name in self.cur};g=run.cohort_rows(self.states,self.cur,[self.w],42,'F3')
        self.assertTrue(g[0]['matched']);self.assertFalse(g[0]['natural_mask_equal'])
        self.gates=g;rows=self.evaluate();self.assertTrue(all(r['matched'] for r in rows));self.assertTrue(all(not r['next_joint'] for r in rows))
        self.assertEqual(list(inspect.signature(current_gate).parameters),['g','r','mask_equal'])
    def test_equal_wrong_currents_do_not_match(self):
        wrong=observe_text(render(self.w,frame(self.w,-1)),True,self.w,0)
        self.assertFalse(current_gate(wrong,wrong,True)['matched'])
    def test_actual_masks_and_cache_are_preserved(self):
        hashes={k:run.state_id(v) for k,v in self.states.items()};rows=self.evaluate()
        self.assertEqual(hashes,{k:run.state_id(v) for k,v in self.states.items()})
        self.assertTrue(all(r['input_length']==3 for r in rows if r['mode']=='latent'))
        self.assertTrue(all(r['input_length']==4 for r in rows if r['mode']=='natural'))
    def test_reference_advances_without_fact_change(self):
        c=advance(frame(self.w,1),'T_plus');self.assertEqual(c,frame(self.w,0))
        p=score(render(self.w,c),c,self.w)['parsed'];self.assertTrue(all(p[k]==self.w[k] for k in FIELDS))
    def test_zero_training_entry(self):
        import ast
        tree=ast.parse((ROOT/'run.py').read_text())
        calls=[n.func.attr if isinstance(n.func,ast.Attribute) else n.func.id if isinstance(n.func,ast.Name) else '' for n in ast.walk(tree) if isinstance(n,ast.Call)]
        self.assertNotIn('backward',calls);self.assertFalse(any('Adam' in x or 'SGD' in x for x in calls))

class DataTests(unittest.TestCase):
    def test_locked_data_and_prespecified_cases(self):
        verify_lock();ws=read(ROOT/'data/worlds.jsonl');self.assertEqual(len(ws),320);self.assertEqual(len({key(w) for w in ws}),320)
        for split,n in CFG['world_counts'].items():
            sub=[w for w in ws if w['split']==split];self.assertEqual(len(sub),160)
            self.assertTrue(all(eligible(w,['T_plus','T_plus'],1) and w['record_status']=='recorded_plan' for w in sub))
            cs=collections.Counter((w['template_family'],w['polarity']) for w in sub);self.assertEqual(set(cs.values()),{40 if split=='template_ood' else 20})
        selected=json.loads((ROOT/'data/case_ids.json').read_text());self.assertEqual(sum(len(v) for s in selected.values() for v in s.values()),12)

class StatisticsTests(unittest.TestCase):
    def test_pairing_and_extreme_binary_uncertainty(self):
        a=load_module('g14_statistics_test',ROOT/'analyze.py')
        self.assertEqual(a.pair_counts([1,1,0,0],[1,0,1,0]),dict(both_success=1,old_only=1,new_only=1,both_fail=1))
        self.assertGreater(a.wilson(0,160)[1],.02);self.assertLess(a.wilson(160,160)[0],.98)
    def test_empty_cohort_and_empty_resample_are_not_zero(self):
        a=load_module('g14_empty_statistics_test',ROOT/'analyze.py')
        r=a.shared_bootstrap([1,0],[0,1],[False,False],[[0,0],[1,1]])
        self.assertIsNone(r['delta']);self.assertEqual(r['ci'],(None,None));self.assertEqual(r['empty_draws'],2)
        r=a.shared_bootstrap([1,0],[0,1],[True,False],[[0,0],[1,1]])
        self.assertEqual(r['delta'],1);self.assertEqual(r['empty_draws'],1);self.assertEqual(r['ci'],(1,1))

if __name__=='__main__':unittest.main()
