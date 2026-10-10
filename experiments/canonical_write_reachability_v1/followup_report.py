"""Clearly labelled post-hoc aligned order checks and integrated interpretation."""
from collections import defaultdict
from shared import *

def main():
    verify();follow=read(ROOT/'alignment_followup_protocol.json')
    assert all(sha(ROOT/k)==v for k,v in follow['sources'].items())
    groups=defaultdict(list)
    for r in stream(ROOT/'results/alignment_followup.jsonl'):groups[r['model'],r['template'],r['sequence']].append(r)
    assert len(groups)==10*2*2
    summary=[]
    for (model,t,seq),rs in groups.items():
        assert len(rs)==80 and len({r['world_id'] for r in rs})==80
        for k in range(1,6):
            v=rate(r['full_trajectory'][k-1] for r in rs)
            eligible=[r for r in rs if k==1 or r['full_trajectory'][k-2]];c=rate(r['step_successes'][k-1] for r in eligible)
            summary.append(dict(model=model,template=t,sequence=seq,step=k,**v,conditional_n=c['n'],conditional_rate=c['rate'],conditional_ci95=c['ci95']))
    csvwrite('results/alignment_followup_summary.csv',summary)
    body='# 事后补充：对齐状态图上的操作顺序与解释\n\n'
    body+='初始协议已保留。看到对齐覆盖和首批 RRR 结果后，增加此补充实验；这是事后分析，不是预注册确认。补充协议与源码哈希在进一步 GPU 评测前锁定，未改变 RRR 参数或 ridge 选择，也未增加 neural training。\n\n'
    body+='## 必须先区分状态图覆盖\n\n'
    body+='模板编号 0／3 并不能保证所有时间转换 mask 对齐。四类相邻转换（−2↔−1、1↔2）改变 token 长度，在本规范 token 配对方案中未进入拟合。原 reordered 从 0 连做两个 plus，第二步正是 −1→−2；RRR 在该顺序的失败不能作为 rank 不足的证据。这不是神经网络无法生成更长输出的证明，而是理想目标 E(y) 的有效输入 mask 已不同。\n\n'
    body+='补充路径固定为：从 +1 开始 plus、plus、minus、minus、plus，状态依次 0、−1、0、+1、0；从 −1 开始 minus、minus、plus、plus、minus，状态依次 0、+1、0、−1、0。两者覆盖三个时间状态、重复同向操作及反向操作，全程处于对齐状态图内。\n\n'
    body+='[补充协议](alignment_followup_protocol.json)；[拟合覆盖](results/alignment_coverage.csv)。\n\n'
    body+='| 模型 | 模板 | 起始路径 | R1 | R2 | R3 | R4 | R5 | R5 Wilson 95% CI |\n| --- | --- | --- | --- | --- | --- | --- | --- | --- |\n'
    for (model,t,seq),rs in groups.items():
        rates=[rate(r['full_trajectory'][k] for r in rs) for k in range(5)];ci=rates[4]['ci95']
        body+='| '+' | '.join([model,str(t),seq,*[f'{100*r["rate"]:.2f}%' for r in rates],f'[{100*ci[0]:.2f}%, {100*ci[1]:.2f}%]'])+' |\n'
    body+='\n[逐样本输出与潜空间残差](results/alignment_followup.jsonl)；[条件续步率](results/alignment_followup_summary.csv)。\n\n'
    body+='## B：探针与错误内容的约束\n\n'
    body+='规范 IID 上 full 和正交补时间探针准确率均为 100%；S 探针为 seed42 55.36%、seed43 52.68%、seed44 48.93%。三个 seed 的当前正确编辑状态上，正交补探针均全部预测目标 0，而非源 +1。共享 full 探针的 S margin 贡献均为负、正交补均为正。这不支持“新值在 S、旧值留在其余部分”的具体解释；S 探针校准有限，不能反向声称它可靠编码旧值。模板 3 上 full probe 只有 28.75%，不能把这个探针的 OOD 标签用于时间载体结论。\n\n'
    body+='历史 CE 无修补主轨迹在第二步，三个 seed × 模板 0／3 的六格各 80/80 都落入不可解析／语法无效类别。当前证据首先表现为生成语法崩溃，不是可解析的“只改错时间”或“只损坏事实”；这也不意味着没有事实损坏，多标签记录保留了共同错误。\n\n'
    body+='## 成因判断的范围\n\n'
    rr=[r for r in summary if r['model']=='RRR_iid_only_r16' and r['step']==5]
    if all(r['rate']==1 for r in rr):
        body+='RRR-16 在两条补充路径与两个模板上全部 R1–R5 100%。结合初始往返路径，这证明在所测 mask 对齐状态图和历史留出 worlds 上，当前 rank-16 共享仿射类内确实存在可组合写法；单纯“rank-16 根本写不出有用规范状态”不能解释 CE 的失败。下一步优先研究规范目标或 RRR 初始化，而无需根据这组结果先提高 rank。\n\n'
    else:
        body+='补充路径并未全部由 RRR-16 恢复，需按表报告初始往返轨迹与跨三个状态的差异；不能仅依据 primary 的成功宣布一般可组合性。\n\n'
    body+='RRR 与 CE 的拟合数据覆盖、目标和优化方式同时不同。这项实验建立了能力类内的存在性证据；要把成因严格归于 CE 目标，需要后续在相同数据与预算下做目标对照。它不保证任意链长、任意操作或自然文本；模板 2 的单步地板效应仍独立。独立确认的 5 seed／新 worlds 也尚未执行。\n\n'
    (ROOT/'FOLLOWUP.md').write_text(body)
    mainreport=ROOT/'REPORT.md';text=mainreport.read_text();link='\n\n## 补充：排除 token 对齐覆盖混淆\n\n[事后对齐顺序实验与综合解读](FOLLOWUP.md)报告两条跨三个时间状态的五步路径、探针反证和成因判断边界。初始 reordered 的未覆盖转换不能用于秩能力结论。\n'
    if link not in text:mainreport.write_text(text+link)
    dump('results/alignment_followup_audit.json',dict(passed=True,training_updates=0,post_hoc=True,groups=len(groups),records=sum(map(len,groups.values())),all_worlds_disjoint_from_fit=all(r['world_id'] in read(ROOT/'protocol.json')['eval_worlds'] for rs in groups.values() for r in rs),followup_source_hashes_verified=True))
    print('Aligned follow-up verified and reported.')

if __name__=='__main__':main()
