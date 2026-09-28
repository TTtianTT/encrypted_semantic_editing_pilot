import torch,json,collections
from engine import Engine,new_editors
from common import *

def main():
 eng=Engine();ws={w['record_id']:w for w in map(json.loads,(V1/'data/test_iid_worlds.jsonl').read_text().splitlines())};old=[r for r in map(json.loads,(V1/'outputs/composition.jsonl').read_text().splitlines()) if r['method']=='LowRank16' and r['test_stratum']=='test_iid' and r['path'].split('/')[0] in ['time_twice','time_return']]
 out=[]
 for seed in [42,43,44]:
  eds=new_editors();cp=V1/f'checkpoints/LowRank16/s{seed}/best.pt';eds.load_state_dict(torch.load(cp,weights_only=True));eh=digest(cp)
  for path,op2 in [('time_twice','T_plus'),('time_return','T_minus')]:
   a1={r['gold_record_id']:r for r in old if r['seed']==seed and r['path']==path+'/latent_chain'};a2={r['gold_record_id']:r for r in old if r['seed']==seed and r['path']==path+'/decode_reencode'};keys=sorted(a1)
   for i in range(0,80,16):
    eng.check();ids=keys[i:i+16];sources=[a1[k]['source_text'] for k in ids];actual=[a2[k]['intermediate_output'] for k in ids];gold=[render(ws[k],a1[k]['allowed_context']['middle_frame']) for k in ids]
    h,mask,_=eng.encode(sources)
    with torch.no_grad():h1=eds['T_plus'](h,mask)
    h2,m2,_=eng.encode(actual);h3,m3,_=eng.encode(gold)
    norms={}
    for label,hidden,m in [('A1',h1,mask),('A2',h2,m2),('A3',h3,m3)]:
     with torch.no_grad():delta=eds[op2](hidden,m)-hidden;ratios=delta.norm(dim=-1)/hidden.norm(dim=-1).clamp_min(1e-12)
     norms[label]=[ratios[j][m[j].bool()].tolist() for j in range(len(ids))]
    missing=[j for j in range(len(ids)) if actual[j]!=gold[j]];fresh={}
    if missing:
     rr,tt,ll=eng.infer([gold[j] for j in missing],eds,[op2]);fresh={j:rr[n][-1] for n,j in enumerate(missing)}
    for j,k in enumerate(ids):
     w=ws[k];c=a1[k]['allowed_context'];sourceids=eng.tok(sources[j])['input_ids'];midids=eng.tok(gold[j])['input_ids'];inside=offset_at(w,c['middle_frame'])>=-2
     for label,original in [('A1',a1[k]),('A2',a2[k]),('A3',a2[k])]:
      if label=='A3' and j in fresh:o=fresh[j]['output'];ended=fresh[j]['ended'];provenance='new_gold_mid_generation'
      else:o=original['output'];ended=original.get('final_ended',not original['truncated']);provenance='v1_saved_output' if label!='A3' else 'reuse_A2_exact_input_identity'
      out.append(dict(record_id=k,seed=seed,path=path,route=label,source_text=sources[j],actual_middle=actual[j],gold_middle=gold[j],target_text=original['target_text'],frames=c,source_offset=offset_at(w,c['source_frame']),middle_offset=offset_at(w,c['middle_frame']),support='inside53' if inside else 'outside27',first_score=score(actual[j],c['middle_frame'],w,a2[k]['intermediate_ended']),middle_exact=actual[j]==gold[j],original_input_token_ids=sourceids,gold_middle_token_ids=midids,source_tokens=len(sourceids),middle_tokens=len(midids),length_changed=len(sourceids)!=len(midids),position_correspondence_claim=False,attention_mask_length=int((mask if label=='A1' else m2 if label=='A2' else m3)[j].sum()),padded_mask_length=96,output=o,output_tokens=len(eng.tok(o)['input_ids']),score=score(o,c['target_frame'],w,ended),second_update_over_input_per_valid_token=norms[label][j],editor_hash=eh,model_hash=eng.model_hash,provenance=provenance))
   print('A',seed,path,flush=True)
 write('diagnostic_a/outputs.jsonl',out)
 groups=collections.defaultdict(list)
 for r in out:
  for sup in ['all80',r['support']]:
   for length in ['all','changed' if r['length_changed'] else 'unchanged']:groups[(r['seed'],r['path'],r['route'],sup,length)].append(r)
 csvwrite('diagnostic_a/summary.csv',[dict(seed=s,path=p,route=a,support=sup,length=le,N=len(rs),joint_ok=sum(r['score']['joint_ok'] for r in rs)/len(rs),parse_unresolved=sum(r['score']['parse_unresolved'] for r in rs)/len(rs),first_joint=sum(r['first_score']['joint_ok'] for r in rs)/len(rs),middle_exact=sum(r['middle_exact'] for r in rs)/len(rs)) for (s,p,a,sup,le),rs in groups.items()])
 dump('diagnostic_a/complete.json',{'rows':len(out),'A3_new_generation_rows':sum(r['provenance']=='new_gold_mid_generation' for r in out),'A1_A2_reused':True,'no_unaligned_hidden_distance':True})
if __name__=='__main__':main()
