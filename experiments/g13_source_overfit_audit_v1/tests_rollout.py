"""CPU-only execution guards for the actual free-rollout state flow."""
import importlib.util
import unittest
from unittest.mock import patch
import torch
from common_g13 import ROOT, read, render, frame

spec=importlib.util.spec_from_file_location('g13_rollout_tests',ROOT/'run.py')
run=importlib.util.module_from_spec(spec); spec.loader.exec_module(run)

class RecordingEngine:
    def __init__(self): self.inputs=[]
    def check(self,_): pass
    def encode(self,texts):
        self.inputs.append(list(texts))
        value=1000+int(texts[0].rsplit('-',1)[1]) if texts[0].startswith('own-free-output-') else 0
        return torch.tensor([[[float(value)]]]),torch.ones((1,1),dtype=torch.long),None

class RolloutGuards(unittest.TestCase):
    def execute(self):
        w=read(ROOT/'data/iid_worlds.jsonl')[0]; e=RecordingEngine(); received=[]; counter=0
        def r(h,m): received.append(float(h.item())); return h+1
        def observed(engine,h,m,worlds,offset):
            nonlocal counter
            step=counter%5+1; counter+=1
            return [dict(output=f'own-free-output-{step}',normal_end=True,generated_tokens=1,
                         gold=f'future-gold-{step}',frame={},exact=False,
                         score={'joint_ok':step!=1})],0
        with patch.object(run,'observed',observed),patch.object(run,'editor',side_effect=AssertionError('frozen G/oracle editor invoked')):
            rows=run.rollout_eval(e,r,[w],42,'guard','iid','guard')
        return w,e,received,rows
    def test_latent_state_and_reencode_use_only_own_output(self):
        w,e,received,rows=self.execute()
        start=render(w,frame(w,1))
        self.assertEqual(e.inputs,[[start],[start]]+[[f'own-free-output-{k}'] for k in range(1,5)])
        self.assertEqual(received,[0,1,2,3,4,0,1001,1002,1003,1004])
        self.assertEqual(len(rows),10)
    def test_failure_remains_failure_after_later_endpoint_recovers(self):
        _,_,_,rows=self.execute()
        self.assertTrue(all(r['first_failure']==1 for r in rows))
        self.assertTrue(all(not r['trajectory_ok'] for r in rows))
        self.assertTrue(all(r['score']['joint_ok'] for r in rows if r['step']>1))

if __name__=='__main__': unittest.main()
