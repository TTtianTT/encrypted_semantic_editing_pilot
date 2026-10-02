"""Restore exact raw prediction shards from delivered gzip JSONL on CPU."""
import gzip
from collections import defaultdict
from common import *

def main():
    restored=0
    for archive in read(ROOT/'prediction_archives.json'):
        members=defaultdict(list)
        with gzip.open(ROOT/archive['archive'],'rt') as f:
            for line in f:
                r=json.loads(line);members[r['artifact']].append(r['row'])
        for meta in archive['members']:
            p=ROOT/meta['path']
            if p.exists():assert digest(p)==meta['sha256'];continue
            jsonl(p,members[meta['path']]);assert digest(p)==meta['sha256'];restored+=1
    print('Restored and verified',restored,'exact prediction shards')

if __name__=='__main__':main()
