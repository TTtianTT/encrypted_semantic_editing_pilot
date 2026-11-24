"""Shared helpers for the paper scripts (CPU only; read locked results, never write into experiment directories)."""
import gzip
import hashlib
import json
import os
import sys
from pathlib import Path

PAPER = Path(__file__).resolve().parents[1]
REPO = PAPER.parent


def require_slurm():
    assert os.environ.get('SLURM_JOB_ID') and os.environ.get('SLURM_STEP_ID'), 'run via sbatch + srun (login node: git and file edits only)'


def read(p):
    p = REPO / p if not Path(p).is_absolute() else Path(p)
    if str(p).endswith('.gz'):
        with gzip.open(p, 'rt') as g: return json.load(g)
    return json.loads(p.read_text())


def sha(p):
    h = hashlib.sha256()
    with open(REPO / p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''): h.update(b)
    return h.hexdigest()


def get(obj, path):
    for k in str(path).split('/'):
        obj = obj[int(k)] if isinstance(obj, list) else obj[k]
    return obj


def macro_name(s):
    """LaTeX macro names: letters only."""
    assert s.isalpha(), s
    return s
