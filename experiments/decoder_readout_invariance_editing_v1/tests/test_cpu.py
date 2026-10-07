import json
import tempfile
import unittest
from pathlib import Path
from ..common import ROOT,rows,core,dump,read,atomic
from ..metrics import effective_ids,proportion,joint,masked_squared_norm,wilson
from ..resources import gpu_count

class CPUChecks(unittest.TestCase):
    def test_world_grouping(self):
        worlds=rows(ROOT/'configs/worlds.jsonl');self.assertEqual(len(worlds),512)
        self.assertEqual(len({core(w) for w in worlds}),512)
        old={tuple(w['core_content']) for w in rows(ROOT/'world_exposure_registry.jsonl')}
        self.assertFalse(old & {core(w) for w in worlds})
        self.assertEqual(sum(w['split']=='test_iid' for w in worlds),128)
        self.assertEqual(sum(w['split']=='train' for w in worlds),192)
    def test_tokens(self):
        # BART decoder start is itself EOS; source EOS is never removed by this function.
        self.assertEqual(effective_ids([2,0,5,2,1,1],{2}),([0,5,2],True))
        self.assertEqual(effective_ids([2,0,5],{2}),([0,5],False))
    def test_missing(self):self.assertIsNone(proportion(0,0));self.assertEqual(proportion(0,8),0)
    def test_joint(self):
        s=dict(target=True,preserved=True,parseable=True,grammar=True,ended=True)
        self.assertTrue(joint(s))
        for key in s:self.assertFalse(joint(dict(s,**{key:False})))
    def test_padding(self):self.assertEqual(masked_squared_norm([[1,2],[100,100]],[1,0]),5)
    def test_boundary_uncertainty(self):self.assertLess(wilson(8,8)[0],1);self.assertGreater(wilson(0,8)[1],0)
    def test_gpu_accounting(self):self.assertEqual(gpu_count('cpu=8,gres/gpu=1,gres/gpu:nvidia=1'),1)
    def test_atomic_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'a.json';dump(p,dict(status='COMPLETED',exit_code=0));before=p.read_bytes();dump(p,read(p));self.assertEqual(p.read_bytes(),before)
            self.assertEqual(list(Path(tmp).glob('.a*')),[])
    def test_worker_guard(self):
        import subprocess,sys,os
        env=dict(os.environ);env.pop('SLURM_JOB_ID',None);env.pop('SLURM_STEP_ID',None)
        p=subprocess.run([sys.executable,'-m','experiments.decoder_readout_invariance_editing_v1.run_stage','--manifest','missing','--task-index','0'],env=env,capture_output=True,text=True)
        self.assertNotEqual(p.returncode,0);self.assertIn('sbatch+srun',p.stderr)
