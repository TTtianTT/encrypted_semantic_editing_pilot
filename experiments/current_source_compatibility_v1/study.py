"""CPU-safe study paths; immutable baseline modules retain their own namespace."""
import sys,json,hashlib,datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parent
WORKTREE=ROOT.parent.parent
ORIGINAL=WORKTREE.parent
BASE=WORKTREE/'experiments/four_domain_state_coverage_v1'
sys.path.append(str(BASE))
from common import digest,dump,read,jsonl,rows
from semantics import render,gold,advance,states
from evaluator import score,parse
PYTHON=ORIGINAL/'.venv/bin/python'
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def checkpoint(seed):return BASE/f'checkpoints/formal/t5gemma_time_s{seed}/P.pt'
def worldmap():return {w['world_id']:w for w in rows(ROOT/'data/worlds.jsonl')}
def config():return read(ROOT/'config.json')
def verify_lock():
    lock=read(ROOT/'scientific_lock.json')
    for name,sha in lock['files'].items():assert digest(WORKTREE/name)==sha,name
    return digest(ROOT/'scientific_lock.json')
