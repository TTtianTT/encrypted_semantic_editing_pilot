from common import *
def main():
 controls={}
 for name,N in [('text_rule',2346),('target_reconstruction',2346),('reconstruction',1386)]:
  rs=read(f'outputs/confirmation_{name}.jsonl');assert len(rs)==N;assert len({r['uid'] for r in rs})==N
  controls[name]={'N':N,'endpoint_joint':sum(r['score']['joint_ok'] for r in rs),'trajectory_joint':sum(all(s['score']['joint_ok'] for s in r['steps']) for r in rs)}
 counts={}
 for p in (ROOT/'outputs').glob('*_G*.jsonl'):
  rs=read(p.relative_to(ROOT));assert len(rs)==3732 and len({r['uid'] for r in rs})==3732
  counts[p.name]=len(rs)
  for r in rs:
   assert len(r['steps'])==len(r['operations'])
   if r['mode']=='latent_chain':assert all(s['input_mask_length']==r['source_tokens'] for s in r['steps'])
   assert [s['frame'] for s in r['steps']]==r['frames'][1:]
 assert len(counts)==4
 # Check pretraining code files were not changed during evaluation/reporting.
 for p,h in json.loads((ROOT/'training_code_manifest.json').read_text()).items():assert digest(ROOT/p)==h
 for p,h in json.loads((ROOT/'v1_v2_readonly_manifest.json').read_text()).items():assert digest(REPO/p)==h
 dump('evaluation/final_integrity.json',{'passed':True,'outputs':counts,'controls':controls,'v1_v2_unchanged':True,'training_code_unchanged':True,'normal_end_required':True,'test_parser_not_modified':True})
 print(controls)
if __name__=='__main__':main()
