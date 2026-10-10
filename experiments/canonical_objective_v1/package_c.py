"""Deterministic gzip delivery of full predictions; raw hashes are retained."""
import gzip
from cutil import *

def main():
    out=[]
    for name in ('closure','dose','mixsingle','overshoot','chain','single','injection'):
        raw=ROOT/f'results/{name}.jsonl';dest=raw.with_suffix('.jsonl.gz')
        with raw.open('rb') as src,dest.open('wb') as f:
            with gzip.GzipFile(filename=raw.name,mode='wb',fileobj=f,mtime=0,compresslevel=6) as z:
                for chunk in iter(lambda:src.read(1048576),b''):z.write(chunk)
        # Confirm delivered bytes reconstruct the complete raw records.
        h=hashlib.sha256()
        with gzip.open(dest,'rb') as z:
            for chunk in iter(lambda:z.read(1048576),b''):h.update(chunk)
        digest=sha(raw);assert h.hexdigest()==digest
        out.append(dict(raw=str(raw.relative_to(ROOT)),raw_sha256=digest,raw_bytes=raw.stat().st_size,archive=str(dest.relative_to(ROOT)),archive_sha256=sha(dest),archive_bytes=dest.stat().st_size))
    dump('results/prediction_archives.json',out)

if __name__=='__main__':main()
