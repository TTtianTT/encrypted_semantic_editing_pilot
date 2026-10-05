import unittest
import tempfile
from unittest.mock import patch
from pathlib import Path
from experiments.state_handoff_diagnosis_v1.common import dump,jsonl,objsha,sha,cells
from experiments.state_handoff_diagnosis_v1.resource import eligible,allocation_rows,summarize
from experiments.state_handoff_diagnosis_v1.metrics import failure_partition,primary,ratio
from experiments.state_handoff_diagnosis_v1.publish import push_verify
from experiments.state_handoff_diagnosis_v1.collect import validate_shards

class Tests(unittest.TestCase):
    def test_cells(self):
        c=cells();self.assertEqual(len(c),22);self.assertTrue(all(-3<=r['state2']<=3 for r in c));self.assertEqual(len({(r['initial_state'],r['a']) for r in c}),12)
    def test_budget_and_single_phase(self):
        eligible(dict(submissions=[],gpu_hours=10),3,2,[])
        for l,n,h,q in [(dict(submissions=[],gpu_hours=10.01),3,2,[]),(dict(submissions=[],gpu_hours=0),0,1,[]),(dict(submissions=[dict(terminal=False)],gpu_hours=0),1,1,[]),(dict(submissions=[],gpu_hours=0),1,1,['other gpu'])]:
            with self.assertRaises((RuntimeError,ValueError)):eligible(l,n,h,q)
    def test_allocation_only(self):
        raw='1|9_0|COMPLETED|0:0|60|gres/gpu=1|2026-10-05T00:00:00|2026-10-05T00:01:00|1\n1.batch|9_0.batch|COMPLETED|0:0|60|gres/gpu=1|x|y|1\n2|9_1|TIMEOUT|0:0|60|gres/gpu=1|2026-10-05T00:00:30|2026-10-05T00:01:30|1'
        a=allocation_rows(raw);self.assertEqual(len(a),2);self.assertEqual(summarize(a),(120/3600,2))
    def test_no_endpoint_full(self):
        rs=[dict(kind='second',world_id='w',b='plus',condition=k,C0=False,C1=False,Cbridge=True,C2=True,Full=False) for k in ['PURE','ACTUAL_REENCODE','GOLD_CANONICAL']]
        self.assertEqual(primary(rs)['estimate'],0);self.assertEqual(failure_partition(rs)[0]['category'],'INITIAL_OR_FIRST_FAILURE')
    def test_partition(self):
        rs=[dict(kind='second',world_id='w',b='minus',condition=k,C0=True,C1=True,Cbridge=True,C2=k!='PURE',Full=k!='PURE') for k in ['PURE','ACTUAL_REENCODE','GOLD_CANONICAL']]
        self.assertEqual(primary(rs)['estimate'],1);self.assertEqual(failure_partition(rs)[0]['category'],'SOURCE_INTERFACE_COMPATIBLE')
    def test_zero_denominator(self):self.assertIsNone(ratio([],'Full')['rate'])
    def test_push_failure_not_verified(self):
        calls=[]
        def fail(args,cwd):calls.append(args);raise RuntimeError('network')
        with self.assertRaises(RuntimeError):push_verify('a',fail)
        self.assertEqual(len(calls),1)
    def test_remote_mismatch(self):
        def mismatch(args,cwd):return '' if args[1]=='push' else 'other refs/heads/test'
        with self.assertRaises(AssertionError):push_verify('a',mismatch)
    def test_partial_resume_small_shard(self):
        with tempfile.TemporaryDirectory() as d:
            task=dict(output=d,scientific_hash='fixed');p=Path(d)/'batch_0000.jsonl'
            records=[dict(kind='atomic',world_id='w',state=0,operation='plus',receiver='P')];jsonl(p,records);dump(p.with_suffix('.meta.json'),dict(scientific_hash='fixed',sha256=sha(p),rows=1,worlds=['w'],execution_commit='abc'))
            r,s,c=validate_shards(task);self.assertEqual(len(r),1);self.assertIsNone(c)
            task['scientific_hash']='changed'
            with self.assertRaises(AssertionError):validate_shards(task)
    def test_complete_no_shards_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            dump(Path(d)/'complete.json',dict(scientific_hash='f',expected_batches=1,expected_worlds=8))
            with self.assertRaises(AssertionError):validate_shards(dict(output=d,scientific_hash='f'))
    def test_failure_reports_and_pending_publication(self):
        from experiments.state_handoff_diagnosis_v1.collect import collect_run
        from experiments.state_handoff_diagnosis_v1.publish import publish_run
        from experiments.state_handoff_diagnosis_v1.common import read
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);output=root/'artifacts';output.mkdir()
            t=dict(run_id='cpu_fake_failure',output=str(output),round='R01',model='bart',seed=42,split='confirmation',scientific_hash='s',protocol_hash='p',world_hash='w',checkpoint_records=[],scope='test')
            a=[dict(gpus=1,elapsed_seconds=1,array_task_id='1_0',state='TIMEOUT')];l=dict(gpu_hours=1/3600,maximum_concurrent_gpus=1)
            with patch('experiments.state_handoff_diagnosis_v1.collect.ROOT',root):collect_run(t,a,l)
            self.assertEqual(read(root/'runs/cpu_fake_failure/conclusion.json')['scientific_status'],'BLOCKED')
            self.assertTrue((root/'runs/cpu_fake_failure/REPORT.md').exists())
            with patch('experiments.state_handoff_diagnosis_v1.publish.ROOT',root),patch('experiments.state_handoff_diagnosis_v1.publish.index_status'),patch('experiments.state_handoff_diagnosis_v1.publish.stage_small',return_value=['explicit_file']),patch('experiments.state_handoff_diagnosis_v1.publish.cmd',return_value='abc'),patch('experiments.state_handoff_diagnosis_v1.publish.push_verify',side_effect=RuntimeError('network')):
                with self.assertRaises(RuntimeError):publish_run(t['run_id'])
            receipt=read(root/'runs/cpu_fake_failure/receipt.json');self.assertEqual(receipt['state'],'LOCAL_COMMITTED_PUSH_PENDING');self.assertEqual(receipt['local_commit'],'abc')

if __name__=='__main__':unittest.main()
