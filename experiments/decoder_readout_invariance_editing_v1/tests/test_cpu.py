import json
import tempfile
import unittest
from pathlib import Path
from ..common import ROOT,TASK_TMP,rows,core,dump,read,atomic
from ..metrics import effective_ids,proportion,joint,masked_squared_norm,wilson
from ..resources import gpu_count

class CPUChecks(unittest.TestCase):
    def test_world_grouping(self):
        worlds=rows(ROOT/'configs/worlds.jsonl');self.assertEqual(len(worlds),512)
        self.assertEqual(len({core(w) for w in worlds}),512)
        history=ROOT/'configs/historical_exposure_registry.jsonl'
        old={tuple(w['core_content']) for w in rows(history if history.exists() else ROOT/'world_exposure_registry.jsonl')}
        self.assertFalse(old & {core(w) for w in worlds})
        self.assertEqual(sum(w['split']=='test_iid' for w in worlds),128)
        self.assertEqual(sum(w['split']=='train' for w in worlds),192)
    def test_tokens(self):
        # BART decoder start is itself EOS; source EOS is never removed by this function.
        self.assertEqual(effective_ids([2,0,5,2,1,1],{2}),([0,5,2],True))
        self.assertEqual(effective_ids([2,0,5],{2}),([0,5],False))
    def test_counterfactual_reserved_core_guard(self):
        from ..provenance import control_core_allowed
        collisions=read(ROOT/'results/COUNTERFACTUAL_EXPOSURE_AUDIT.json')['collisions']
        for row in collisions:
            key=row['donor_core'];candidate=dict(object=key[0],color=key[1],quantity=key[2],status=key[3])
            self.assertFalse(control_core_allowed(candidate,row['recipient_split']))
    def test_missing(self):self.assertIsNone(proportion(0,0));self.assertEqual(proportion(0,8),0)
    def test_joint(self):
        s=dict(target=True,preserved=True,parseable=True,grammar=True,ended=True)
        self.assertTrue(joint(s))
        for key in s:self.assertFalse(joint(dict(s,**{key:False})))
    def test_padding(self):self.assertEqual(masked_squared_norm([[1,2],[100,100]],[1,0]),5)
    def test_boundary_uncertainty(self):self.assertLess(wilson(8,8)[0],1);self.assertGreater(wilson(0,8)[1],0)
    def test_gpu_accounting(self):self.assertEqual(gpu_count('cpu=8,gres/gpu=1,gres/gpu:nvidia=1'),1)
    def test_atomic_idempotent(self):
        with tempfile.TemporaryDirectory(dir=TASK_TMP) as tmp:
            p=Path(tmp)/'a.json';dump(p,dict(status='COMPLETED',exit_code=0));before=p.read_bytes();dump(p,read(p));self.assertEqual(p.read_bytes(),before)
            self.assertEqual(list(Path(tmp).glob('.a*')),[])
    def test_worker_guard(self):
        import subprocess,sys,os
        env=dict(os.environ);env.pop('SLURM_JOB_ID',None);env.pop('SLURM_STEP_ID',None)
        p=subprocess.run([sys.executable,'-m','experiments.decoder_readout_invariance_editing_v1.run_stage','--manifest','missing','--task-index','0'],env=env,capture_output=True,text=True)
        self.assertNotEqual(p.returncode,0);self.assertIn('sbatch+srun',p.stderr)
    def test_KV_interaction_identity(self):
        import numpy as np
        rng=np.random.default_rng(7);a=rng.normal(size=(3,5));b=rng.normal(size=(3,5));v=rng.normal(size=(5,4));w=rng.normal(size=(5,4));out=rng.normal(size=(4,6))
        exact=(b@w-a@v)@out
        decomposed=((b-a)@v+a@(w-v)+(b-a)@(w-v))@out
        np.testing.assert_allclose(exact,decomposed,atol=1e-12)
    def test_world_cluster_source_balance(self):
        from ..analyze import paired_bootstrap
        records=[]
        for world in ('a','b'):
            for seed in (42,43,44):
                for method in ('proposed','baseline'):
                    for source,count in [('natural',1),('history',9)]:
                        for _ in range(count):records.append(dict(world_id=world,seed=seed,method=method,source=source,joint=method=='proposed' and source=='natural'))
        r=paired_bootstrap(records,'proposed','baseline')
        self.assertEqual(r['n_worlds'],2);self.assertEqual(r['estimate'],.5);self.assertEqual(r['bootstrap_draws'],20000)
    def test_holm(self):
        from ..analyze import holm
        self.assertEqual(holm([.04,.01]),[.04,.02])
    def test_literal_next_fork_is_not_accuracy_xor(self):
        # Actual T5Gemma records include two failed next edits with different outputs.
        audit=read(ROOT/'results/BRIDGE_DEFINITION_AUDIT.json')
        rs=[r for r in audit['summary'] if r['model']=='t5gemma']
        self.assertEqual(sum(r['next_native_token_fork'] for r in rs),63)
        self.assertEqual(sum(r['legacy_accuracy_fork'] for r in rs),0)
    def test_prefix_only_missing_free_generation_is_NA(self):
        audit=read(ROOT/'results/S2_NUMERICAL_AUDIT.json')
        rs=[r for r in audit['summary'] if r['free_generation_status']=='NOT_RUN_DIAGNOSTIC_PREFIX_ONLY']
        self.assertTrue(rs)
        for row in rs:
            self.assertIsNone(row['free_generation_denominator'])
            self.assertIsNone(row['joint_numerator'])
    def test_main_unrun_comparisons_are_NA(self):
        audit=read(ROOT/'results/main_method_status.json')
        if not audit['confirmatory_family_executed']:
            for row in audit['comparisons']:
                self.assertIsNone(row['estimate']);self.assertIsNone(row['Holm_adjusted_p'])
        else:
            self.assertTrue(read(ROOT/'configs/S4_AMENDMENT_AUTHORIZATION.json')['approved'])
            self.assertEqual(audit['endpoint'],'AMENDED_UNEXPOSED123')
            for row in audit['comparisons']:self.assertIsNotNone(row['estimate'])
    def test_review_accepted_material_is_exact(self):
        from ..common import sha
        lock=read(ROOT/'configs/KEEP_MASK_REVIEW_LOCK.json')
        self.assertTrue(lock['reviewed_by_human']);self.assertEqual(lock['confirmation'],'16例抽查通过。')
        self.assertEqual(lock['review_material_sha256'],sha(ROOT/'reports/KEEP_MASK_REVIEW.md'))
        self.assertEqual(lock['mask_audit_sha256'],sha(ROOT/'configs/KEEP_MASK_AUDIT.jsonl'))
    def test_reused_memory_pool_has_no_test_world(self):
        allowed={w['world_id'] for w in rows(ROOT/'configs/worlds.jsonl') if w['split'] in ('train','validation')}
        for item in read(ROOT/'configs/S3_REUSE_LOCK.json')['entries']:
            self.assertEqual(set(item['source_worlds']),allowed)
            self.assertEqual(len(item['source_worlds']),256)
    def test_regularizer_GPU_acceptance(self):
        lock=read(ROOT/'configs/REGULARIZER_ACCEPTANCE_LOCK.json');self.assertTrue(lock['passed'])
        self.assertEqual(len(lock['checks']),3)
        for check in lock['checks']:
            self.assertTrue(check['teacher_detached']);self.assertTrue(check['hooks_cleaned'])
            self.assertTrue(all(v>0 for v in check['isolated_editor_gradient_norms'].values()))
    def test_amendment_preserves_original_scan_without_refill(self):
        path=ROOT/'configs/S4_PROTOCOL_AMENDMENT_PROPOSAL.json'
        if not path.exists():self.skipTest('No checkpoint-locked amendment proposal prepared')
        proposal=read(path);worlds={w['world_id'] for w in rows(ROOT/'configs/worlds.jsonl') if w['split']=='test_iid'}
        self.assertEqual(set(proposal['eligible_worlds'])|set(proposal['excluded_worlds']),worlds)
        self.assertFalse(set(proposal['eligible_worlds'])&set(proposal['excluded_worlds']))
        self.assertEqual(len(proposal['eligible_worlds']),123);self.assertEqual(len(proposal['excluded_worlds']),5)
        self.assertFalse(proposal['replacement_search']);self.assertFalse(proposal['original_endpoint_restored'])
    def test_no_test_unseal_without_explicit_amendment(self):
        if (ROOT/'configs/S4_AMENDMENT_AUTHORIZATION.json').exists():self.skipTest('Explicit authorization exists; tested by worker manifest guard')
        from ..prepare import prepare
        with self.assertRaisesRegex(RuntimeError,'BLOCKED_TEST_INTEGRITY'):prepare('S4')
