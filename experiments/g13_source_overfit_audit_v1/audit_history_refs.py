"""Supplementary read-only overlap audit of manifests on other available Git refs."""
import importlib.util, subprocess
from common_g13 import *
def main():
    spec=importlib.util.spec_from_file_location('g13_prep',ROOT/'prepare.py'); prep=importlib.util.module_from_spec(spec); spec.loader.exec_module(prep)
    refs=subprocess.check_output(['git','for-each-ref','--format=%(refname)','refs/heads','refs/remotes/origin'],cwd=REPO,text=True).splitlines()
    known=json.loads((ROOT/'data/manifest.json').read_text())['old_files']; known_shas={x['sha256'] for x in known.values()}
    seen=set(); provenance=[]; facts=set(); texts=set(); errors=[]
    for ref in refs:
        if 'g13-source-overfit' in ref: continue
        tree=subprocess.check_output(['git','ls-tree','-r',ref],cwd=REPO,text=True)
        for line in tree.splitlines():
            entry,path=line.split('\t',1); obj=entry.split()[2]
            if not path.endswith('.jsonl') or not ('/data/' in path or 'world' in Path(path).name or 'manifest' in Path(path).name) or any(q in Path(path).parts for q in ['outputs','local','latents','latents_archive']): continue
            if obj in seen: continue
            seen.add(obj); raw=subprocess.check_output(['git','cat-file','blob',obj],cwd=REPO); sha=hashlib.sha256(raw).hexdigest()
            if sha in known_shas: continue
            provenance.append(dict(ref=ref,path=path,git_blob=obj,sha256=sha))
            for l in raw.decode().splitlines():
                if not l.strip(): continue
                try: r=json.loads(l)
                except Exception as e: errors.append(dict(path=path,error=str(e))); continue
                for w in prep.extract_worlds(r):
                    facts.add(key(w))
                    if 'template_family' in w:
                        for d in range(-4,5):
                            for p in ['first','third']:
                                if valid(w,[frame(w,d,p)]): texts.add(norm(render(w,frame(w,d,p))))
                texts.update(prep.text_fields(r))
    collisions=[]
    for w in read(ROOT/'data/worlds.jsonl'):
        ts={norm(render(w,frame(w,d,p))) for d in range(-4,5) for p in ['first','third'] if valid(w,[frame(w,d,p)])}
        if key(w) in facts or ts & texts: collisions.append(dict(record_id=w['record_id'],split=w['split'],fact_overlap=key(w) in facts,text_overlap=bool(ts & texts)))
    dump(ROOT/'historical_refs_overlap_audit.json',dict(timing='read-only supplementary audit after lock, while training; no data or configuration changes',refs=refs,additional_unique_manifest_blobs=provenance,additional_unique_facts=len(facts),additional_normalized_texts=len(texts),collisions=collisions,errors=errors,all_historical_data_claim=False,unavailable_manifests='remain unaudited'))
    print('supplementary manifest blobs',len(provenance),'facts',len(facts),'collisions',len(collisions),flush=True)
if __name__=='__main__': main()
