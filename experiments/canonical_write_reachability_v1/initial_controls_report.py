"""Report the exact projection-failure context; preserve the historical comparison."""
from collections import defaultdict
from shared import *

def main():
    p=verify();spec=read(ROOT/'initial_projection_controls_protocol.json');assert all(sha(ROOT/k)==v for k,v in spec['sources'].items())
    groups=defaultdict(list);probes=defaultdict(list);error=0;count=0
    for r in stream(ROOT/'results/initial_projection_controls.jsonl'):
        assert r['world_id'] in p['eval_worlds'];count+=1
        if r['panel']=='control':
            groups[r['seed'],r['context'],r['condition']].append(r)
            if r['condition'] in ('random_full','random4','ridge_delta'):error=max(error,abs(r['norm']-r['matched_ridge_norm'])/r['matched_ridge_norm'])
        else:probes[r['seed'],r['context']].append(r)
    assert count==3*80*2*12 and error<1e-5
    summary=[]
    for (seed,context,condition),rs in groups.items():
        byworld=defaultdict(list)
        for r in rs:byworld[r['world_id']].append(r)
        assert len(byworld)==80
        out=dict(seed=seed,context=context,condition=condition,n_worlds=80,mean_norm=np.mean([r['norm'] for r in rs]))
        for metric in ('current_exact','current_success','next_success'):
            value=lambda r:r['current_exact'] if metric=='current_exact' else r['current' if metric=='current_success' else 'next']['score']['success']
            v=[np.mean([value(r) for r in rr]) for rr in byworld.values()];out[metric]=np.mean(v)
            out[metric+'_ci95']=bootstrap_mean(v) if condition.startswith('random') else previous.binomial_ci(int(sum(v)),80)
        summary.append(out)
    csvwrite('results/initial_projection_control_summary.csv',summary);ps=[]
    for (seed,context),rs in probes.items():
        assert len(rs)==80
        out=dict(seed=seed,context=context)
        for component in ('full','S','complement'):
            for role,target in [('target',-1),('source',0)]:
                r=rate(x[component+'_prediction']==target for x in rs);out[component+'_'+role+'_rate']=r['rate'];out[component+'_'+role+'_ci95']=r['ci95']
        for f in ('shared_S_contribution','shared_complement_contribution','shared_bias'):out[f]=np.mean([r[f] for r in rs])
        ps.append(out)
    csvwrite('results/initial_projection_probe_summary.csv',ps)
    body='# 事后补充：原始投影失败的 0→−1 状态\n\n'
    body+='历史 1→0 匹配对上的 ridge 位移与初始 0→−1 投影不是同一个状态转换。为直接检验原始失败，本表复用已经拟合的 ridge 和时间探针，没有新拟合、没有 neural training。设计和源码在本补充的推理前锁定；worlds 仍是相同历史分析留出集。\n\n'
    body+='canonical 状态采用 E(−1)，edited 状态采用 CE-plus(E(0))。ridge_delta 与随机位移均匹配后者实际 ridge 位移的逐 world Frobenius 范数；canonical 接受同一位移。own_ridge 另在各自状态上重新计算位移，显示原始操作本身涉及不同幅度，不能用它当幅度匹配对照。\n\n'
    body+='| seed | 状态 | 位移 | 平均范数 | 当前逐字保持 | 当前成功 | 下一步成功 | 当前保持 CI |\n| --- | --- | --- | --- | --- | --- | --- | --- |\n'
    for r in summary:
        ci=r['current_exact_ci95'];body+='| '+' | '.join([str(r['seed']),r['context'],r['condition'],f'{r["mean_norm"]:.4f}',*[f'{100*r[k]:.2f}%' for k in ('current_exact','current_success','next_success')],f'[{100*ci[0]:.2f}%, {100*ci[1]:.2f}%]'])+' |\n'
    body+='\n[幅度匹配对照及区间](results/initial_projection_control_summary.csv)；[逐样本输出](results/initial_projection_controls.jsonl)。下一步为 plus，目标 −2；它改变规范 token mask，因此这里只评价语义，不把目标潜空间不对齐当作误差。\n\n'
    body+='| seed | 状态 | full→目标 | S→目标 | S→源 | 正交补→目标 | 正交补→源 | 共享 S margin | 共享正交补 margin |\n| --- | --- | --- | --- | --- | --- | --- | --- | --- |\n'
    for r in ps:body+='| '+' | '.join([str(r['seed']),r['context'],*[f'{100*r[k]:.2f}%' for k in ('full_target_rate','S_target_rate','S_source_rate','complement_target_rate','complement_source_rate')],f'{r["shared_S_contribution"]:.4f}',f'{r["shared_complement_contribution"]:.4f}'])+' |\n'
    body+='\n[探针区间与贡献](results/initial_projection_probe_summary.csv)。规范 IID 上正交补探针 100% 准确，S 探针只有 49%–55%；因此分量标签仍需结合共享 margin 贡献和规范校准。\n\n'
    body+='不能把 1→0 和 0→−1 的不同结果平均成一个全局机制。随机位移损坏输出支持局部脆弱性，但特定方向比同范数随机方向更有害或能定向修复时，不能用“对任何扰动都一样脆弱”解释全部现象。\n\n'
    (ROOT/'INITIAL_CONTROLS.md').write_text(body)
    report=ROOT/'REPORT.md';text=report.read_text();link='\n\n[原始 0→−1 投影失败的幅度匹配对照与探针](INITIAL_CONTROLS.md)：与历史 1→0 对照分开报告。\n'
    if link not in text:report.write_text(text+link)
    dump('results/initial_projection_controls_audit.json',dict(passed=True,training_updates=0,post_hoc=True,records=count,maximum_relative_norm_error=error,all_source_hashes_verified=True))
    print('Initial-context controls audited and reported.')

if __name__=='__main__':main()
