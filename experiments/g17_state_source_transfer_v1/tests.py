"""CPU state-flow, semantic, cohort and statistics tests; never GPU forward."""
import unittest,ast
import torch
from common_g17 import *
runtime=load_module('g17_explicit_cpu_runtime',ROOT/'run.py')
class Checks(unittest.TestCase):
    def world(self):return read(G16/'data/iid_worlds.jsonl')[0]
    def test_four_reference_paths(self):
        w=self.world();identity=key(w)
        for a in CFG['anchors']:
            fs=[frame(w,d) for d in [a+1,a,a-1]];self.assertTrue(valid(w,fs))
            self.assertEqual(advance(fs[0],'T_plus'),fs[1]);self.assertEqual(advance(fs[1],'T_plus'),fs[2]);self.assertEqual(key(w),identity)
            for f in fs:self.assertTrue(score(render(w,f),f,w,True)['joint_ok'])
    def test_identical_complete_handoff(self):
        st=dict(memory=torch.arange(12.).reshape(1,3,4),mask=torch.tensor([[1,1,0]]),input_ids=torch.tensor([[1,2,0]]));h=statehash(st);calls=[]
        class Receiver:
            def __init__(self,x):self.x=x
            def __call__(self,m,mask):calls.append((id(m),id(mask)));return m+self.x*mask[...,None]
        f=runtime.immutable_apply(Receiver(2),st);n=runtime.immutable_apply(Receiver(3),st)
        self.assertEqual(calls[0],calls[1]);self.assertEqual(statehash(st),h);self.assertIs(f['mask'],st['mask']);self.assertIs(n['input_ids'],st['input_ids']);self.assertFalse(torch.equal(f['memory'],n['memory']))
    def test_mutation_rejected(self):
        st=dict(memory=torch.zeros(1,2,2),mask=torch.ones(1,2),input_ids=torch.ones(1,2))
        def bad(m,mask):m.add_(1);return m
        with self.assertRaises(AssertionError):runtime.immutable_apply(bad,st)
    def test_current_only_gate(self):
        good=dict(exact=True,normal_end=True,joint=True,next_joint=False);self.assertTrue(current_gate(good,good)['matched']);good['next_joint']=True;self.assertTrue(current_gate(good,good)['matched'])
        self.assertFalse(current_gate(dict(good,exact=False),good)['matched']);self.assertFalse(current_gate(dict(good,joint=False),good)['matched'])
    def test_cohorts_not_substitutable(self):
        c=dict(P={1,2,3},U={2,3,4},G={3,4});self.assertEqual(intersection(c,['P','U']),{2,3});self.assertEqual(intersection(c,['P','U','G']),{3});self.assertEqual(len(c['P']),3)
        strict=c['P']&{2};self.assertNotEqual(strict,c['P']);self.assertEqual(len(set(range(160))),160)
    def test_raw_full_and_paired(self):
        self.assertFalse(full_success(dict(joint=False),dict(joint=True)));self.assertTrue(full_success(dict(joint=True),dict(joint=True)))
        self.assertEqual(paired_counts([1,1,0,0],[1,0,1,0]),dict(both=1,only_F=1,only_N=1,neither=1))
    def test_wilson_zero_one_empty(self):
        self.assertEqual(wilson(0,0),[None,None]);self.assertGreater(wilson(0,160)[1],0);self.assertLess(wilson(160,160)[0],1);self.assertTrue(proportion(1,10)['exploratory']);self.assertIsNone(proportion(0,0)['rate'])
    def test_runtime_static_flow(self):
        source=(ROOT/'run.py').read_text();tree=ast.parse(source)
        self.assertNotIn('backward(',source);self.assertNotIn('torch.optim',source)
        self.assertIn("out=immutable_apply(eds[q],st[s])",source);self.assertIn("texts=[cur[s][i]['output'] for i in ix]",source);self.assertIn('else encode(e,texts)',source)
        self.assertIn("h1=immutable_apply(eds[q],st['start'])",source);self.assertIn('immutable_apply(eds[q],h1)',source)
        self.assertIn('before==after',source);self.assertIn('requires_grad_(False)',source);self.assertIn('SLURM_STEP_ID',source)
        self.assertNotIn("encode(e,[render(w,frame(w,a-1))",source)
    def test_actual_bootstrap_and_JSON_scalar(self):
        import numpy as np
        a=load_module('g17_actual_CPU_analysis_test',ROOT/'analyze.py')
        row=a.plain_row(paired_counts(np.array([1,0],bool),np.array([0,1],bool)))
        json.dumps(row);self.assertTrue(all(type(v) is int for v in row.values()))
        draw=np.zeros((2000,160),dtype=int);mask=np.zeros(160,dtype=bool);mask[-1]=True
        stats,b=a.paired_boot(np.ones(160),mask,draw);self.assertEqual(stats['empty_draws'],2000);self.assertIsNone(stats['ci_low_pp'])
        empty,b=a.paired_boot(np.ones(160),np.zeros(160,bool),draw);self.assertIsNone(empty['delta_pp'])
    def test_history_source_key(self):
        rs=read(ROOT/'data/history_expected.jsonl.gz')
        self.assertEqual({r['source'] for r in rs if r['kind'] in ['self_first','self_second']},{'Q'})
        self.assertIn("source=r['producer'] if kind=='fixed' else 'Q'",(ROOT/'run.py').read_text())
    def test_shared_world_sampling(self):
        import numpy as np
        rng=np.random.default_rng(12);draw=rng.integers(0,160,(2000,160));world=np.arange(160);cube=np.stack([world]*12);sample=cube[:,draw[0]]
        self.assertTrue(np.all(sample==sample[0]));self.assertEqual(draw.shape,(2000,160));cohort=world<40;self.assertTrue(np.array_equal(cohort[draw],(world[draw]<40)))
    def test_checkpoint_and_world_lock_if_prepared(self):
        if not (ROOT/'scientific_lock.json').exists():return
        verify_lock();ws=read(ROOT/'data/worlds.jsonl');self.assertEqual(len(ws),320);self.assertEqual(len({key(w) for w in ws}),320)
        for w in ws:
            self.assertEqual(w['record_status'],'recorded_plan')
            for a in CFG['anchors']:self.assertTrue(eligible(w,['T_plus','T_plus'],a+1))
        z=json.loads((ROOT/'checkpoints_manifest.json').read_text());self.assertEqual(set(z['models']['42']),{'P','U','G','N','F'})
        for m in z['models'].values():
            for role,s in m.items():self.assertEqual(digest(s['path']),s['sha256'])
if __name__=='__main__':unittest.main(verbosity=2)
