"""Failure recovery for artifact publication and immutable stage namespaces."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from experiments.causal_next_edit_stability_v1.common import atomic_write,atomic_torch_save

class StorageChecks(unittest.TestCase):
    def test_failed_publication_keeps_previous_artifact(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'state.pt';p.write_bytes(b'previous complete artifact')
            def fail(f):
                f.write(b'incomplete replacement')
                raise RuntimeError('simulated disk-write failure')
            with self.assertRaises(RuntimeError):atomic_write(p,fail)
            self.assertEqual(p.read_bytes(),b'previous complete artifact')
            self.assertEqual(list(Path(directory).iterdir()),[p])
    def test_cpu_tensor_publication(self):
        import torch
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'basis.pt';x=torch.arange(12).reshape(3,4)
            atomic_torch_save(p,dict(q=x))
            saved=torch.load(p,map_location='cpu',weights_only=True)
            self.assertTrue(torch.equal(x,saved['q']))
            self.assertEqual(list(Path(directory).iterdir()),[p])
    def test_existing_stage_is_not_overwritten(self):
        from experiments.causal_next_edit_stability_v1 import audit
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'configs').mkdir();p=root/'configs/old.json';p.write_text('immutable historical config')
            with patch.object(audit,'ROOT',root):
                with self.assertRaises(FileExistsError):audit.make_stage('old',[],'01:00:00')
            self.assertEqual(p.read_text(),'immutable historical config')
if __name__=='__main__':unittest.main()
