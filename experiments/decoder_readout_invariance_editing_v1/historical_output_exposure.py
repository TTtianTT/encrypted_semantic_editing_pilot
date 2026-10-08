"""CPU scan of actual historical JSON/JSONL prediction artifacts across refs."""
import gzip
import io
from .common import *
from .predicted_exposure import strings,text_cores


def records(raw,path):
    if path.endswith('.gz'):raw=gzip.decompress(raw);path=path[:-3]
    if path.endswith('.jsonl'):
        for line in raw.decode().splitlines():
            if line.strip():yield json.loads(line)
    else:yield json.loads(raw)


def audit():
    worlds=rows(ROOT/'configs/worlds.jsonl');lookup={core(w):w for w in worlds}
    inventory=read(ROOT/'manifests/exposure_inventory.json');blobs={}
    for ref,head in inventory['refs']:
        for line in command('git','ls-tree','-r',head).splitlines():
            meta,path=line.split('\t');blob=meta.split()[2]
            if path.startswith('experiments/') and path.endswith(('.json','.jsonl','.jsonl.gz')) and not path.startswith('experiments/decoder_readout_invariance_editing_v1/'):
                blobs.setdefault(blob,[]).append(dict(branch=ref,head=head,path=path))
    hits=[];scanned=[];errors=[];seen_hash=set();text_count=0
    def consume(raw,path,source):
        nonlocal text_count
        digest=hashlib.sha256(raw).hexdigest()
        if digest in seen_hash:return
        seen_hash.add(digest);count=0
        try:
            for index,value in enumerate(records(raw,path)):
                for field,s in strings(value):
                    text_count+=1;count+=1
                    for key in text_cores(s):
                        if key not in lookup:continue
                        w=lookup[key]
                        hits.append(dict(world_id=w['world_id'],split=w['split'],core_content=list(key),field='/'.join((str(index),)+field),text=s,source=source,source_sha256=digest))
        except (ValueError,UnicodeError,OSError) as exc:errors.append(dict(source=source,error=repr(exc)))
        scanned.append(dict(source=source,sha256=digest,bytes=len(raw),text_fields=count))
        if len(scanned)%25==0:print(dict(files_scanned=len(scanned),bytes_scanned=sum(r['bytes'] for r in scanned),text_fields_scanned=text_count,matched_records=len(hits)),flush=True)
    for blob,source in sorted(blobs.items()):
        raw=subprocess.check_output(['git','cat-file','blob',blob],cwd=WT)
        consume(raw,source[0]['path'],dict(git_blob=blob,refs=source))
    for wt in [PROJECT]+[p for p in PROJECT.iterdir() if p.is_dir() and p.name.endswith('worktree') and p!=WT]:
        root=wt/'experiments'
        if not root.exists():continue
        for path in sorted(root.rglob('*')):
            if path.is_file() and str(path).endswith(('.json','.jsonl','.jsonl.gz')):
                consume(path.read_bytes(),str(path),dict(local_path=str(path)))
    result=dict(historical_refs=inventory['refs'],unique_files_scanned=len(scanned),text_fields_scanned=text_count,
        known_new_pool_core_hits={split:sorted({r['world_id'] for r in hits if r['split']==split}) for split in ('train','validation','test_iid','reserved_iid')},
        hits=hits,input_files=scanned,parse_errors=errors,neural_model_loaded=False,model_test_evaluations=0,
        rule='all string fields in accessible historical experimental JSON/JSONL/JSONL.gz; natural/symbolic complete core clauses, including invalid grammar conservatively')
    dump(ROOT/'results/HISTORICAL_OUTPUT_EXPOSURE_AUDIT.json',result)
    print({k:v for k,v in result.items() if k not in ('hits','input_files','historical_refs')})
    return result


if __name__=='__main__':audit()
