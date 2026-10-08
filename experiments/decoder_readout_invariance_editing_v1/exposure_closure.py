"""CPU-only closeout of audited core exposures; never authorizes a test."""
from datetime import datetime,timezone
import gzip
from .common import *

def run():
    names=('COUNTERFACTUAL_EXPOSURE_AUDIT.json','PREDICTED_CORE_EXPOSURE_AUDIT.json','HISTORICAL_OUTPUT_EXPOSURE_AUDIT.json')
    evidence={name:read(ROOT/'results'/name) for name in names}
    current=evidence[names[1]];historical=evidence[names[2]]
    encoder={r['donor_world_id'] for r in evidence[names[0]]['collisions'] if r['donor_split']=='test_iid'}
    generated=set(current['generated_text_test_cores']);old=set(historical['known_new_pool_core_hits']['test_iid'])
    excluded=encoder|generated|old
    worlds={w['world_id'] for w in rows(ROOT/'configs/worlds.jsonl') if w['split']=='test_iid'}
    assert excluded<=worlds and len(worlds)==128
    summary=dict(status='BLOCKED_TEST_INTEGRITY',original_scan_denominator=128,encoder_exposed_worlds=sorted(encoder),current_output_exposed_worlds=sorted(generated),historical_output_exposed_worlds=sorted(old),all_known_exposed_worlds=sorted(excluded),known_exposed_count=len(excluded),not_known_exposed_count=128-len(excluded),not_known_exposed_worlds=sorted(worlds-excluded),not_known_exposed_is_not_authorized_endpoint=True,parse_errors=historical['parse_errors'],original_endpoint_restored=False,replacement_search=False,test_model_evaluations=0,new_endpoint_authorized=False,original_worlds_sha256=sha(ROOT/'configs/worlds.jsonl'),split_lock_sha256=sha(ROOT/'configs/SPLIT_LOCK.json'),evidence_sha256={name:sha(ROOT/'results'/name) for name in names},historical_output_scan_scope=historical['rule'],historical_refs=len(historical['historical_refs']),historical_files=historical['unique_files_scanned'],historical_string_fields=historical['text_fields_scanned'],historical_prior_pool_exposures=historical['known_new_pool_core_hits'])
    dump(ROOT/'configs/FINAL_EXPOSURE_LOCK.json',summary)
    version=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ');folder=ROOT/'reports'/f'S4_EXPOSURE_CLOSURE_{version}_bart_s42';folder.mkdir()
    copied=[]
    for name in names:
        data=(ROOT/'results'/name).read_bytes()
        target=folder/(name+'.gz');atomic(target,gzip.compress(data,mtime=0))
        copied.append(dict(path=str(target),sha256=sha(target),uncompressed_sha256=summary['evidence_sha256'][name]))
    dump(folder/'NUMERICAL_AUDIT.json',summary)
    dump(folder/'RUN_STATUS.json',dict(stage='S4_EXPOSURE_CLOSURE',model='bart',seed=42,status='BLOCKED_TEST_INTEGRITY',completed_samples=0,remaining_samples=128,GPU_hours=0,neural_model_loaded=False))
    dump(folder/'ARTIFACTS.json',copied)
    text(folder/'REPORT.md',f"""# Independent-test exposure audit closeout

BLOCKED_TEST_INTEGRITY. Original fixed scan denominator remains 128; formal test model evaluations are 0. Known exposed cores: {len(excluded)}/128; remaining not known exposed: {128-len(excluded)}/128. These remaining IDs are an audit classification, not an authorized amended endpoint, and no replacement search was performed.

Encoder control exposure: {len(encoder)} cores. Actual current-run output exposure: {len(generated)} cores. Actual accessible historical output exposure: {len(old)} cores. Counts overlap; only the union is the exclusion denominator. All IDs, exact matching text, source field, branch/blob or file provenance and SHA are retained in the compressed evidence.

Historical audit: {historical['unique_files_scanned']} distinct SHA-deduplicated JSON/JSONL/JSONL.gz files across {len(historical['historical_refs'])} frozen refs and accessible original/worktree result directories; {historical['text_fields_scanned']} string fields; {len(historical['parse_errors'])} parse errors. Scope is complete natural/symbolic core clauses, conservatively including malformed grammar. This audit cannot assert exposure absence in inaccessible artifacts or unrecorded sessions. Prior train/validation core matches are also recorded and are not silently called new independent worlds.

The former 123-world proposal is withdrawn after additional output exposures. The 16-example approval covered I_keep masks only. No checkpoint, method selection, split, training input, method label, failure score or original endpoint was changed in response to these audit findings. S4 and independent mechanism confirmation remain NA; validation evidence cannot replace them. All trained checkpoints remain frozen.
""")
    text(folder/'INTERPRETATION.md','Historical output texts can expose core worlds without explicitly reusing their world IDs. Metadata-only historical auditing was insufficient. Preserve the original fixed denominator and report the failure rather than silently relabeling a reduced pool as the original independent endpoint.\n')
    text(ROOT/'reports/S4_AMENDMENT_PROPOSAL.md',f'# Previous proposal withdrawn\n\nThe original 123-world proposal is not executable. Complete conservative audits now identify {len(excluded)}/128 known exposed core worlds and {128-len(excluded)} not known exposed. This classification does not authorize a revised scientific endpoint; original S4 stays BLOCKED_TEST_INTEGRITY, formal evaluations 0. See configs/FINAL_EXPOSURE_LOCK.json and {folder.name}/REPORT.md for full provenance and limitations. No refill, no silent test selection.\n')
    print(dict(report=str(folder),known_exposed=len(excluded),not_known_exposed=128-len(excluded),test='BLOCKED_TEST_INTEGRITY'))

if __name__=='__main__':run()
