"""G17 CPU helpers; exact read-only semantics/scorer imported from G16."""
import sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'g16_capability_preserving_transfer_v1'))
from common_g16 import *
G16=HERE.parent/'g16_capability_preserving_transfer_v1'
ROOT=HERE;REPO=ROOT.parents[1]
CFG=json.loads((ROOT/'configs/main.json').read_text());LEAF_SEEDS={}
def sub_seed(name):
    x=int.from_bytes(hashlib.sha256(f'{CFG["data_seed"]}/g17/{name}'.encode()).digest()[:8],'big');LEAF_SEEDS[name]=x;return x
def current_gate(producer,natural):
    failures=[n+'_'+k for n,o in [('producer',producer),('natural',natural)] for k in ['exact','normal_end','joint'] if not o[k]]
    return dict(matched=not failures,failures=failures)
def intersection(cohorts,names):return set.intersection(*(set(cohorts[n]) for n in names))
def paired_counts(f,n):
    assert len(f)==len(n)
    return dict(both=sum(a and b for a,b in zip(f,n)),only_F=sum(a and not b for a,b in zip(f,n)),only_N=sum(not a and b for a,b in zip(f,n)),neither=sum(not a and not b for a,b in zip(f,n)))
def wilson(k,n):
    if n==0:return [None,None]
    assert 0<=k<=n;z=1.959963984540054;p=k/n;den=1+z*z/n;mid=(p+z*z/(2*n))/den;half=z*((p*(1-p)/n+z*z/(4*n*n))**.5)/den
    return [max(0,mid-half),min(1,mid+half)]
def proportion(k,n):
    lo,hi=wilson(k,n);return dict(k=k,n=n,rate=k/n if n else None,wilson_low=lo,wilson_high=hi,exploratory=n<40,empty=n==0)
def verify_lock():
    z=json.loads((ROOT/'scientific_lock.json').read_text())
    for p,h in z['files'].items():assert digest(REPO/p)==h,p
    return z
