"""Independently reproduce scoped old P natural results; CPU only."""
import gzip,collections
from study import *
def main():
    audited=[]
    for seed in (42,43,44):
        source=BASE/f'runs/formal/t5gemma_time_s{seed}/predictions.jsonl.gz'
        expected={};rejected=collections.Counter();candidates=0
        with gzip.open(source,'rt') as f:
            for line in f:
                x=json.loads(line);r=x['row'];candidates+=1
                if not x['artifact'].endswith('/outputs/P/atomic_core.jsonl'):
                    rejected['other_artifact']+=1;continue
                if r['template'] not in (0,1):rejected['other_template']+=1;continue
                identifier=f"{r['world_id']}_t{r['template']}_s{r['state']}_{r['operation']}"
                assert identifier not in expected
                expected[identifier]=r
        new=rows(ROOT/f'runs/preflight/s{seed}/T0/old_natural.jsonl')
        assert len(expected)==len(new)==768
        strings=masks=0
        for r in new:
            old=expected[r['id']]
            assert r['score']==old['score'] and r['source']==old['source'] and r['target']==old['target'] and r['gold']==old['gold']
            strings+=r['prediction']==old['prediction'];masks+=r['mask_length']==old['mask_length']
        audited.append(dict(seed=seed,old_archive_sha256=digest(source),archive_candidates=candidates,selected_P_core_rows=768,rejected=dict(rejected),exact_all_score_fields=768,exact_source_target_gold=768,exact_strings_auxiliary=strings,exact_masks=masks))
    dump(ROOT/'OLD_RESULT_REPRODUCTION.json',dict(passed=True,rows=audited,at_utc=now()));print('Old P results verified:2304 rows,all semantic score fields and source/target/gold')
if __name__=='__main__':main()
