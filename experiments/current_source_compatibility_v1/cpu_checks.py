"""Independent arithmetic, split leakage, supervision equality and original artifact checks."""
import collections,csv,ast,subprocess
from study import *

def main():
    manifest=read(ROOT/'data/manifest.json')
    for path,sha in manifest['files'].items():assert digest(ROOT/path)==sha
    ws=worldmap();rs=rows(ROOT/'data/continuation.jsonl');test=rows(ROOT/'data/test_pairs.jsonl')
    assert len(rs)==1408 and len(test)==1408
    assert {r['current_state'] for r in rs}==set(range(-3,4))
    checks=0
    for r in rs+test:
      current=r['initial_state']+(-1 if r['a']=='plus' else 1);target=current+(-1 if r['b']=='plus' else 1)
      assert current==r['current_state'] and target==r['target_state'] and -3<=target<=3
      w=ws[r['world_id']]
      for text,g in ((r['current_text'],r['current_gold']),(r['target_text'],r['target_gold'])):
       assert score(text,g,w)['success'];assert not score(text,dict(g,relative=99),w)['success'];checks+=2
      assert r['target_gold']['event_date']==r['current_gold']['event_date']==w['event_date']
      assert r['target_gold']['status']==r['current_gold']['status']==w['status']
    assert all(ws[r['world_id']]['split']=='train' for r in rs) and all(ws[r['world_id']]['split']=='test' for r in test)
    signatures={};near_duplicate=0
    for w in ws.values():
      sig=tuple(sorted(render(w,s,t) for s in range(-3,4) for t in (0,1)))
      if sig in signatures:assert signatures[sig]==w['split'];near_duplicate+=1
      signatures[sig]=w['split']
    coverage=list(csv.DictReader((ROOT/'coverage.csv').open()))
    for seed in (42,43,44):
      values={m:{tuple(r[k] for k in ('role','initial_state','prefix','current_state','operation','target_state','template')):int(r['units']) for r in coverage if r['condition']==m and int(r['seed'])==seed} for m in ('N','F','R')}
      assert values['N']==values['F']==values['R']
      assert sum(v for k,v in values['N'].items() if k[0]=='replay')==800
      assert sum(v for k,v in values['N'].items() if k[0]=='continuation')==800
      assert {int(k[3]) for k,v in values['N'].items() if k[0]=='continuation'}==set(range(-3,4))
    for r in rows(ROOT/'data/long_paths.jsonl'):
      s=r['initial_state']
      for op,target in zip(r['operations'],r['states']):s+=-1 if op=='plus' else 1;assert s==target and -3<=s<=3
    for name in ('train_core','dev_core','test_core','test_expression'):assert digest(ROOT/f'data/{name}.jsonl')==digest(BASE/f'data/time/{name}.jsonl')
    for item in read(ROOT/'SOURCE_LINEAGE.json')['sources']:assert digest(Path(item['checkpoint']))==item['sha256']
    import torch
    for item in read(ROOT/'SOURCE_LINEAGE.json')['sources']:
      published=torch.load(item['checkpoint'],map_location='cpu',weights_only=True)['editor']
      raw=Path(item['old_checkpoint']['path']);assert digest(raw)==item['old_checkpoint']['sha256']
      original=torch.load(raw,map_location='cpu',weights_only=False)['editor']
      assert set(published)==set(original) and all(torch.equal(published[k],original[k]) for k in published)
      assert sum(v.numel() for v in published.values())==152064
    assert not torch.cuda.is_initialized(),'CPU audit unexpectedly initialized CUDA'
    import prepare,engine,evaluation
    for module in (prepare,engine,evaluation):assert Path(module.__file__).resolve().parent==ROOT,module.__file__
    assert not torch.cuda.is_initialized(),'Module import initialized CUDA'
    for p in ROOT.glob('*.py'):ast.parse(p.read_text())
    original_status=subprocess.check_output(['git','status','--porcelain','--untracked-files=all'],cwd=ORIGINAL,text=True)
    dump(ROOT/'CPU_AUDIT.json',dict(passed=True,arithmetic_and_parser_checks=checks,all_current_states_reachable=True,condition_supervision_equal=True,old_natural_tests_unchanged=True,cross_split_content_duplicates=0,within_split_near_duplicates=near_duplicate,original_git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ORIGINAL,text=True).strip(),original_git_status=original_status,at_utc=now()))
    print('CPU checks passed;',checks,'independent arithmetic/parser checks; all supervision matched')
if __name__=='__main__':main()
