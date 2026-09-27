"""Prepare human-only review of existing direct latent compositions; no judging."""
import csv, hashlib, json, random
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
P = ROOT / 'experiments/latent_consistency_v1'
OUT = P / 'human_review/direct_deduplicated'
OUT.mkdir(exist_ok=True)
groups = {}
inputs = []
for context in ['independent', 'seen_combo']:
    for lam in ['0', '0.1']:
        path = P / f'results/B_{context}_lambda{lam}_latent_once.jsonl'
        rows = [json.loads(line) for line in path.read_text().splitlines()]
        assert len(rows) == 100 and len({r['source_id'] for r in rows}) == 100
        inputs.append({'file': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
        for row in rows:
            key = (row['source_id'], row['output'])
            item = groups.setdefault(key, {'source': row['input'], 'output': row['output'], 'members': []})
            assert item['source'] == row['input']
            item['members'].append({'source_id': row['source_id'], 'method': row['method'], 'seed': row['seed'], 'path': row['path'], 'config_hash': row['config_hash']})
items = list(groups.values())
random.Random(42).shuffle(items)
fields = ['review_id', 'source', 'output', 'future_completed', 'passive_completed', 'agent_patient_preserved', 'other_events_preserved', 'numbers_units_preserved', 'negation_preserved', 'names_dates_preserved', 'readable', 'notes']
mapping = []
with (OUT / 'blind.csv').open('w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fields, lineterminator='\n')
    writer.writeheader()
    for i, item in enumerate(items, 1):
        rid = f'D{i:04d}'
        writer.writerow({'review_id': rid, 'source': item['source'], 'output': item['output']})
        mapping.append({'review_id': rid, 'members': item['members']})
assert len(mapping) == 335
assert sum(len(x['members']) for x in mapping) == 400
(OUT / 'PRIVATE_mapping.json').write_text(json.dumps(mapping, ensure_ascii=False, indent=2) + '\n')
(OUT / 'manifest.json').write_text(json.dumps({'source_count': 100, 'original_outputs': 400, 'unique_source_output_pairs': len(items), 'deduplication': 'exact source_id + output; no text normalization', 'shuffle_seed': 42, 'human_ratings_received': False, 'inputs': inputs}, indent=2) + '\n')
print('Prepared 335 unscored pairs; mapping covers all 400 outputs from 100 sources.')
