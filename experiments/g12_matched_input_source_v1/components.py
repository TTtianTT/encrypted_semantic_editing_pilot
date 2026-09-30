"""Derived component counts, not a scoring change or new evaluation."""
import collections
from common_g12 import *
def main():
 groups=collections.defaultdict(list)
 for kind,file,output in [('current','current_states','current'),('next','next_states','next'),('chain','long_chains','output'),('atomic','atomic','output')]:
  for r in read(f'outputs/{file}.jsonl'):
   stage=r.get('step',r.get('offset',r.get('history')));groups[kind,r['method'],r['seed'],r['split'],stage].append(r[output])
 rows=[]
 for (kind,arm,s,split,stage),xs in groups.items():
  rows.append(dict(kind=kind,method=arm,seed=s,split=split,stage=stage,N=len(xs),joint=sum(x['score']['joint_ok'] for x in xs),date_ok=sum(x['score']['date_ok'] for x in xs),person_ok=sum(x['score']['perspective_ok'] for x in xs),nondate_facts_ok=sum(x['score']['nondate_facts_ok'] for x in xs),parse_unresolved=sum(x['score']['parse_unresolved'] for x in xs),normal_end=sum(x['normal_end'] for x in xs)))
 csvwrite('evaluation/component_counts.csv',rows)
 import csv
 hs=list(csv.DictReader((ROOT/'evaluation/history.csv').open()));groups={}
 for r in hs:groups.setdefault((r['method'],r['seed'],r['split'],r['cohort']),{})[r['history']]=r
 deltas=[]
 for (arm,s,split,cohort),rs in groups.items():
  n=int(rs['0']['N']);s0=float(rs['0']['next_rate']) if n else None;s2=float(rs['2']['next_rate']) if n else None
  deltas.append(dict(method=arm,seed=s,split=split,cohort=cohort,N=n,H0=s0,H1=float(rs['1']['next_rate']) if n else None,H2=s2,Delta2=s0-s2 if n else None,low_coverage=n<40))
 csvwrite('evaluation/history_deltas.csv',deltas);print('G12 date/person/fact/end component counts and history deltas written')
if __name__=='__main__':main()
