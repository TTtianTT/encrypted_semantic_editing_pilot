"""Post-hoc diagnostic only; never changes scores, denominators or training."""
import json,csv,collections
from datetime import date
from prepare import ROOT,dump
from semantics import parse
train=[json.loads(l) for l in (ROOT/'data/train_pairs.jsonl').read_text().splitlines()]
support=collections.defaultdict(set)
for r in train:
 p,e=parse(r['source_text'],r['allowed_context']['source_frame']);assert e is None
 offset=(date.fromisoformat(p['event_date'])-date.fromisoformat(r['allowed_context']['source_frame']['view_date'])).days
 support[r['operation_ids'][0]].add(offset)
worlds={w['record_id']:w for w in map(json.loads,(ROOT/'data/test_worlds.jsonl').read_text().splitlines())};groups=collections.defaultdict(list)
for line in (ROOT/'outputs/composition.jsonl').read_text().splitlines():
 r=json.loads(line)
 if not r['path'].startswith(('time_twice/','time_return/')):continue
 offset=(date.fromisoformat(worlds[r['gold_record_id']]['event_date'])-date.fromisoformat(r['allowed_context']['middle_frame']['view_date'])).days
 label='within_temporal_source_support' if offset in support[r['operation_ids'][1]] else 'outside_temporal_source_support'
 groups[(r['method'],r['seed'],r['test_stratum'],r['path'],label)].append(r)
rows=[dict(method=m,seed=s,stratum=st,path=p,source_support=label,N=len(rs),joint_ok=sum(r['score']['joint_ok'] for r in rs)/len(rs),parse_unresolved=sum(r['score']['parse_unresolved'] for r in rs)/len(rs)) for (m,s,st,p,label),rs in groups.items()]
with (ROOT/'evaluation/temporal_support_diagnostic.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
dump('evaluation/temporal_source_support.json',{'training_source_offsets':{k:sorted(v) for k,v in support.items()},'interpretation':'post-hoc support stratification, not replacement main denominator; offset=-3 is unseen as atomic temporal source; no claim of causal isolation'})
