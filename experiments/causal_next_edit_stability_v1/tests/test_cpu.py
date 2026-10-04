import multiprocessing
import unittest
import time
from . import __doc__
from ..common import split
from ..resource_guard import allocation_rows,summarize,eligible,locked

def hold_lock(queue):
    with locked():
        queue.put(time.monotonic());time.sleep(.1)

class CPUChecks(unittest.TestCase):
    def test_allocation_not_steps(self):
        raw='12|10_0|COMPLETED|0:0|3600|gres/gpu=1|2026-10-04T10:00:00|2026-10-04T11:00:00|60\n12.batch|10_0.batch|COMPLETED|0:0|3600|gres/gpu=1|||\n13|10_1|FAILED|1:0|1800|gres/gpu=1|2026-10-04T10:30:00|2026-10-04T11:00:00|60'
        a=allocation_rows(raw);self.assertEqual(len(a),2);self.assertEqual(summarize(a),(1.5,2))
    def test_active_and_empty(self):
        for ledger,n in [(dict(submissions=[],gpu_hours=0),0),(dict(submissions=[dict(terminal=False)],gpu_hours=0),1),(dict(submissions=[],gpu_hours=39.5),1)]:
            with self.assertRaises((ValueError,RuntimeError)):eligible(ledger,n,1)
    def test_terminal_failure_allows_fixed_retry(self):
        eligible(dict(submissions=[dict(terminal=True)],gpu_hours=.2),1,.2)
    def test_split_group(self):
        for i in range(100):self.assertEqual(split(str(i)),split(str(i)))
    def test_shared_lock(self):
        q=multiprocessing.Queue();ps=[multiprocessing.Process(target=hold_lock,args=(q,)) for _ in range(2)]
        for p in ps:p.start()
        times=sorted(q.get() for _ in ps)
        for p in ps:p.join()
        self.assertGreaterEqual(times[1]-times[0],.09)
if __name__=='__main__':unittest.main()
