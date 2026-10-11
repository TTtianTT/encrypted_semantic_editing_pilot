from mutil import *
import py_compile
def main():
 verify()
 for path in ROOT.glob('*.py'):py_compile.compile(str(path),doraise=True)
 dump('results/preflight.json',dict(job_id=os.environ['SLURM_JOB_ID'],gpus=0,compiled_scripts=[p.name for p in ROOT.glob('*.py')],protocol_verified=True))
if __name__=='__main__':main()
