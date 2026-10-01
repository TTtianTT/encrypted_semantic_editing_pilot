import subprocess
from common_g16 import *
if __name__=='__main__':
    r=subprocess.run([sys.executable,str(ROOT/'tests.py')],cwd=REPO,capture_output=True,text=True)
    (ROOT/'cpu_tests.log').write_text(r.stdout+r.stderr)
    dump(ROOT/'cpu_tests.json',dict(passed=r.returncode==0,exit_code=r.returncode,CPU_only=True,CUDA_not_initialized=True,tests_sha256=digest(ROOT/'tests.py')))
    print(r.stdout+r.stderr);assert r.returncode==0
