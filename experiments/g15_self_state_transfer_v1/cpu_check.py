"""Capture the actual CPU unit-test exit result; no GPU work."""
import subprocess, time
from common_g15 import *
def main():
    start=time.monotonic();result=subprocess.run([sys.executable,str(ROOT/'tests.py')],cwd=REPO,text=True,capture_output=True)
    log=result.stdout+result.stderr;(ROOT/'cpu_tests.log').write_text(log)
    dump(ROOT/'cpu_tests.json',dict(passed=result.returncode==0,exit_code=result.returncode,elapsed_seconds=time.monotonic()-start,log_sha256=digest(ROOT/'cpu_tests.log'),tests_source_sha256=digest(ROOT/'tests.py'),CPU_only=True))
    print(log,end='');raise SystemExit(result.returncode)
if __name__=='__main__':main()
