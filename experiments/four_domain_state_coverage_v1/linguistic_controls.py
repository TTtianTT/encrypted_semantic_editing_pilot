"""Dispatch within the same Slurm step to the selected study's frozen modules."""
import argparse,subprocess
from common import *

def main():
    p=argparse.ArgumentParser();p.add_argument('--index',type=int,required=True);args=p.parse_args();task=read(ROOT/'linguistic_tasks.json')[args.index]
    subprocess.run([str(PYTHON),str(ROOT/'linguistic_worker.py'),'--study',task['study'],'--model',task['model'],'--domain',task['domain']],check=True)

if __name__=='__main__':main()
