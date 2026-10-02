"""CPU final science/resource/scope audit; no GPU or modification of old assets."""
import re,subprocess
from common_g17 import *
def main():
    verify_lock();budget=json.loads((ROOT/'budget.json').read_text());assert budget['within_limits'] and budget['limit_gpu_hours']==2
    assert all(json.loads((ROOT/f'seed_s{s}_complete.json').read_text())['passed'] for s in CFG['seeds'])
    assert all(json.loads((ROOT/f'frozen_s{s}.json').read_text())['passed'] for s in CFG['seeds']);assert json.loads((ROOT/'analysis_audit.json').read_text())['all_records_CPU_rescored']==130560
    if (ROOT/'recovery_lock.json').exists():
        z=json.loads((ROOT/'recovery_lock.json').read_text());assert z['scientific_lock_sha256']==digest(ROOT/'scientific_lock.json')
        for p,h in z['preserved_output_sha256'].items():assert digest(ROOT/p)==h,p
        for p,h in z['preserved_cache_sha256'].items():assert json.loads((ROOT/p).read_text())['cache_sha256']==h;assert digest(json.loads((ROOT/p).read_text())['cache_path'])==h
    public=[p for p in ROOT.rglob('*') if p.is_file() and not any(n in p.relative_to(ROOT).parts for n in ['local','outputs','__pycache__']) and p.name!='submission.lock' and not p.name.endswith('.tmp')]
    assert not any(p.suffix in ['.pt','.safetensors','.pem','.key'] for p in public)
    assert max(p.stat().st_size for p in public)<50_000_000
    for p in public:
        if p.suffix not in ['.py','.md','.json','.csv','.sh','.sbatch','.log','.out','.err','.txt']:continue
        t=p.read_text(errors='replace')
        assert not re.search(r'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----|(?:ghp_|github_pat_)[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16}',t),p
    dump(ROOT/'publication_audit.json',dict(passed=True,base_commit=CFG['base_commit'],all3seeds_complete=True,zero_training=True,scientific_lock_unchanged_during_confirmation=True,recovered_existing_caches_and_outputs_unchanged=True,allocation_budget_and_concurrency_pass=True,public_files=len(public),largest_public_bytes=max(p.stat().st_size for p in public),no_weights_or_credentials=True,public_hashes={str(p.relative_to(ROOT)):digest(p) for p in public if p.name not in ['publication_audit.json','artifact_manifest.json']}))
    print('G17 publication checks passed',len(public),'files',budget)
if __name__=='__main__':main()
