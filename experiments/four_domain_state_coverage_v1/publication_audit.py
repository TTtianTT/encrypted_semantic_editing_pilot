"""Verify parameter exports and exact reconstruction of all archived JSONL shards."""
import gzip,hashlib,torch,argparse
from common import *

def main():
    assert not torch.cuda.is_initialized()
    parser=argparse.ArgumentParser();parser.add_argument('--study',choices=['four_domain_state_coverage_v1','space_relation_confirmation_v1'],default='four_domain_state_coverage_v1');args=parser.parse_args();base=ROOT.parent/args.study
    count=0;paths=[]
    for r in read(base/'checkpoints_index.json'):
        exported=base/r['published_editor'];assert digest(exported)==r['published_sha'];assert digest(Path(r['path']))==r['sha256'];paths.append(str(exported))
        a=torch.load(exported,map_location='cpu',weights_only=False);b=torch.load(r['path'],map_location='cpu',weights_only=False)
        assert a['step']==b['step'] and a['raw_checkpoint_sha']==r['sha256'];assert set(a['editor'])==set(b['editor'])
        assert all(torch.equal(a['editor'][k],b['editor'][k]) for k in a['editor']);count+=1
    assert len(paths)==len(set(paths)),'Phase/seed/role export namespace collision'
    members=lines=0
    for a in read(base/'prediction_archives.json'):
        assert digest(base/a['archive'])==a['sha256'];hashes={r['path']:hashlib.sha256() for r in a['members']};counts={r['path']:0 for r in a['members']}
        with gzip.open(base/a['archive'],'rt',encoding='utf-8') as f:
            for line in f:
                r=json.loads(line);raw=(json.dumps(r['row'],ensure_ascii=False)+'\n').encode();hashes[r['artifact']].update(raw);counts[r['artifact']]+=1;lines+=1
        for r in a['members']:assert hashes[r['path']].hexdigest()==r['sha256'] and counts[r['path']]==r['rows'],r['path'];members+=1
    dump(base/'PUBLICATION_AUDIT.json',dict(passed=True,editor_exports_exact=count,prediction_shards_roundtrip_exact=members,rows=lines,phase_namespaces_unique=True,no_cuda_initialized=not torch.cuda.is_initialized()))
    print(args.study,'publication verified:',count,'editors,',members,'shards,',lines,'rows')

if __name__=='__main__':main()
