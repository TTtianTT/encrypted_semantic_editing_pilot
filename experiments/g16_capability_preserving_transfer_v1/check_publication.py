"""CPU checks of the actual Git scope, small weights and delivery checksums."""
import re,subprocess
import torch
from common_g16 import *

def main():
    verify_lock();assert json.loads((ROOT/'delivery_audit.json').read_text())['passed']
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip()==CFG['baseline_commit']
    assert subprocess.check_output(['git','branch','--show-current'],cwd=REPO,text=True).strip()==CFG['branch']
    names=subprocess.check_output(['git','diff','--cached','--name-only'],cwd=REPO,text=True).splitlines()
    prefix=str(ROOT.relative_to(REPO))+'/'
    assert names and all(p.startswith(prefix) for p in names)
    assert not any('/local/' in p or '/outputs/' in p or '/learning/' in p or '/models/' in p or '/.venv/' in p for p in names)
    forbidden=re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|\b(?:hf_|ghp_|gho_|ghu_|ghs_|ghr_)[A-Za-z0-9]{20,}|Authorization: Bearer [A-Za-z0-9._~-]{20,}')
    assert all((REPO/p).stat().st_size<100*1024*1024 for p in names)
    for p in names:
        if not p.endswith(('.gz','.pt')):assert not forbidden.search((REPO/p).read_bytes()),p
    weights=[];mapping=json.loads((ROOT/'checkpoints_manifest.json').read_text())['models']
    for seed in CFG['seeds']:
        proof=json.loads((ROOT/f'seed_s{seed}_confirm_complete.json').read_text())
        for role in ['P','G','U']:
            z=mapping[str(seed)][role];state=torch.load(z['path'],map_location='cpu',weights_only=True)
            assert digest(z['path'])==z['sha256'] and statehash(state)==proof['frozen_before'][role]
        for method in ['N','F']:
            z=json.loads((ROOT/f'training/{method}_s{seed}.json').read_text());p=ROOT/z['final_path']
            state=torch.load(p,map_location='cpu',weights_only=True);assert statehash(state)==z['final_state_hash']
            assert all(t.dtype==torch.float32 for t in state.values()) and state['u.weight'].shape==(768,16) and state['v.weight'].shape==(16,768)
            weights.append(dict(seed=seed,version=method+'-final',sha256=digest(p),state_hash=statehash(state)))
        z=json.loads((ROOT/f'selection_s{seed}.json').read_text())
        if z['selected_step'] is not None:
            p=ROOT/z['checkpoint_path'];state=torch.load(p,map_location='cpu',weights_only=True);assert statehash(state)==z['checkpoint_state_hash']
            weights.append(dict(seed=seed,version='F-guard',actual_updates=z['selected_step'],sha256=digest(p),state_hash=statehash(state)))
    artifacts=json.loads((ROOT/'artifact_manifest.json').read_text())
    artifacts['complete_text_archives']=[dict(path=str(p.relative_to(ROOT)),sha256=digest(p),bytes=p.stat().st_size) for p in sorted(ROOT.glob('*jsonl.gz'))]
    dump(ROOT/'artifact_manifest.json',artifacts)
    excluded={str((ROOT/'publication_audit.json').relative_to(REPO)),str((ROOT/'artifact_manifest.json').relative_to(REPO))}
    inventory={p:dict(sha256=digest(REPO/p),bytes=(REPO/p).stat().st_size) for p in names if p not in excluded}
    assert not torch.cuda.is_initialized()
    dump(ROOT/'publication_audit.json',dict(passed=True,only_G16_paths_staged=True,no_credentials_detected=True,no_large_cache_or_base_or_environment_staged=True,largest_staged_file_bytes=max((REPO/p).stat().st_size for p in names),existing_P_G_U_roles_match_GPU_hashes=True,all_small_FP32_rank16_checkpoint_state_hashes_match=True,weights=weights,files=inventory,no_GPU_initialized=True,artifact_manifest_sha256=digest(ROOT/'artifact_manifest.json'),baseline_parent_commit=CFG['baseline_commit']))
    print('G16 publication scope, role/weight hashes and credentials scan passed',len(names),'files',flush=True)

if __name__=='__main__':main()
