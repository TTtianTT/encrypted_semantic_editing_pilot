"""Aggregate supplementary estimator validation and conditioned transfer panels."""
from aggregate import *

def main():
    predictions(rows(ROOT/'results/g4_same_editor_features.jsonl'),'g4_same_editor')
    groups=defaultdict(list)
    for r in rows(ROOT/'results/canonical_control.jsonl'):
        groups[r['seed'],r['template'],r['state'],r['method']].append(r)
    output=[]
    for key,rs in sorted(groups.items()):
        k=sum(r['success'] for r in rs);e=sum(r['exact_preservation'] for r in rs)
        output.append(dict(seed=key[0],template=key[1],state=key[2],method=key[3],N=len(rs),
            baseline_successes=sum(r['baseline']['score']['success'] for r in rs),successes=k,rate=k/len(rs),ci95=binomial_ci(k,len(rs)),
            exact_preservation=e/len(rs),exact_ci95=binomial_ci(e,len(rs)),mean_coordinate_mse=float(np.mean([r['coordinate_mse'] for r in rs]))))
    csvwrite('results/canonical_control_summary.csv',output)
    groups=defaultdict(list)
    for r in rows(ROOT/'results/cross_conditioned.jsonl'):
        groups[r['target_seed'],r['basis_seed'],r['template']].append(r)
    output=[]
    for key,rs in sorted(groups.items()):
        k=sum(r['joint'] for r in rs)
        output.append(dict(target_seed=key[0],basis_seed=key[1],template=key[2],N=len(rs),successes=k,rate=k/len(rs),
            ci95=binomial_ci(k,len(rs)),current_exact=sum(r['current_exact'] for r in rs)/len(rs),mean_norm=float(np.mean([r['patch_norm'] for r in rs]))))
    csvwrite('results/cross_conditioned_summary.csv',output)
    groups=defaultdict(list)
    for r in rows(ROOT/'results/decoder_cumulative.jsonl'):
        groups[r['seed'],r['direction'],r['layer_count'],r['condition']].append(r)
    output=[]
    for key,rs in sorted(groups.items()):
        k=sum(r['next_success'] for r in rs)
        output.append(dict(seed=key[0],direction=key[1],layer_count=key[2],condition=key[3],N=len(rs),successes=k,rate=k/len(rs),
            ci95=binomial_ci(k,len(rs)),mean_KL=float(np.mean([r['teacher_forced_vs_donor']['KL'] for r in rs])),post_hoc=True))
    csvwrite('results/decoder_cumulative_summary.csv',output)
    dump('results/supplement_complete.json',dict(training_updates=0,code_sha256=sha(__file__)))
    print('Supplementary summaries completed.')

if __name__=='__main__':main()
