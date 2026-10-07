"""Conservative cross-branch core-content exposure audit, no model imports."""
import itertools
import json
from collections import defaultdict
from .common import *

def scan():
    refs=[line.split() for line in command('git','for-each-ref','--format=%(refname) %(objectname)','refs/remotes/origin').splitlines()]
    sources=defaultdict(list)
    for ref,head in refs:
        for line in command('git','ls-tree','-r',head).splitlines():
            meta,path=line.split('\t');blob=meta.split()[2]
            if path.endswith(('.json','.jsonl')) and ('world' in path or '/data/' in path or '/configs/' in path) and '/local/' not in path:
                sources[blob].append(dict(branch=ref,head=head,path=path))
    registry=defaultdict(list);inventory=[];errors=[]
    for blob,provenance in sorted(sources.items()):
        raw_bytes=subprocess.check_output(['git','cat-file','blob',blob],cwd=WT)
        raw=raw_bytes.decode()
        try:records=[json.loads(l) for l in raw.splitlines() if l.strip()] if provenance[0]['path'].endswith('.jsonl') else [json.loads(raw)]
        except (ValueError,TypeError) as e:errors.append(dict(blob=blob,error=str(e)));continue
        ws={}
        for r in records:
            for w in world_dicts(r):ws[(core(w),w.get('world_id'),w.get('split'))]=w
        if not ws:continue
        inventory.append(dict(git_blob=blob,sha256=hashlib.sha256(raw_bytes).hexdigest(),sources=provenance,unique_world_records=len(ws)))
        for (key,wid,split),w in ws.items():
            registry[key].append(dict(world_id=wid,declared_split=split,template=w.get('template','see source records'),mechanism_split=w.get('mechanism_split'),git_blob=blob,sources=provenance,exposure='reserved_or_exposed; conservative exclusion, not proof of neural evaluation'))
    # Uncommitted handoff reservations and local config files also remain excluded.
    localfiles=[]
    for wt in [PROJECT]+[p for p in PROJECT.iterdir() if p.is_dir() and p.name.endswith('worktree') and p!=WT]:
        for exp in (wt/'experiments').glob('*'):
            candidates=list(exp.glob('*world*.jsonl'))+list(exp.glob('configs/*world*.jsonl'))+list(exp.glob('data/*world*.jsonl'))
            for p in candidates:
                if p.stat().st_size>10_000_000:continue
                found=list(world_dicts(rows(p)))
                if not found:continue
                localfiles.append(dict(path=str(p),sha256=sha(p),records=len(found)))
                for w in found:
                    registry[core(w)].append(dict(world_id=w.get('world_id'),declared_split=w.get('split'),template=w.get('template','see source'),source_path=str(p),sha256=sha(p),exposure='local reserved_or_exposed'))
    out=[dict(core_content=list(k),core_hash=objsha(k),history_and_checkpoint_provenance='source branch + source records; checkpoint indexes audited separately',exposures=v) for k,v in sorted(registry.items())]
    jsonl(ROOT/'world_exposure_registry.jsonl',out)
    universe=list(itertools.product(['book','lamp','ticket','parcel','sensor','cup','box','key'],['blue','red','green','white','black'],range(1,10),['planned','completed','cancelled']))
    available=[k for k in universe if k not in registry]
    dump(ROOT/'manifests/exposure_inventory.json',dict(refs=refs,git_sources=inventory,local_sources=localfiles,parse_errors=errors,unique_excluded=len(registry),finite_core_universe=len(universe),available=len(available),required=512,available_cores=available))
    print(json.dumps(dict(excluded=len(registry),available=len(available),required=512,blobs=len(inventory),local_sources=len(localfiles),parse_errors=len(errors))))
    return available

if __name__=='__main__':scan()
