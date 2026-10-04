"""Observed failure categories and raw-reading notes; CPU only, all seeds."""
import csv, collections
from study import *

def main():
    assert read(ROOT/'ANALYSIS_AUDIT.json')['all_seeds_complete']
    groups=[]
    for seed in (42,43,44):
        for method in ('N','F','R'):
            folder=ROOT/f'runs/formal/s{seed}/{method}_u200'
            for template,test in ((0,'iid'),(2,'ood')):
                rs=[r for r in rows(folder/'continuation_self.jsonl') if r['template']==template]
                correct_failed=[r for r in rs if r['first_success'] and not r['score']['success']]
                counts=collections.Counter()
                for r in correct_failed:
                    p,_=parse(r['prediction'],'time',template,False)
                    counts['known_wrong_relative']+=bool(p is not None and p.get('relative') is not None and p['relative']!=r['target_state'])
                    counts['unresolved_relative']+=bool(p is None or p.get('relative') is None)
                    counts['facts_not_certified_preserved']+=not r['score']['preserved']
                    counts['not_parseable']+=not r['score']['parseable']
                    counts['not_ended']+=not r['ended']
                groups.append(dict(seed=seed,condition=method,test=test,n=len(rs),first_correct=sum(r['first_success'] for r in rs),full2=sum(r['full2'] for r in rs),correct_prefix_failed_next=len(correct_failed),bad_prefix_endpoint_recovery=sum(not r['first_success'] and r['score']['success'] for r in rs),**{k:counts[k] for k in ('known_wrong_relative','unresolved_relative','facts_not_certified_preserved','not_parseable','not_ended')}))
    with (ROOT/'error_categories.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(groups[0]));w.writeheader();w.writerows(groups)
    keys=['seed','condition','test','first_correct','full2','correct_prefix_failed_next','bad_prefix_endpoint_recovery','known_wrong_relative','unresolved_relative','facts_not_certified_preserved']
    table='\n'.join(['|'+'|'.join(keys)+'|','|'+'|'.join(['---']*len(keys))+'|']+['|'+'|'.join(str(r[k]) for k in keys)+'|' for r in groups])
    text=['## 完整两步错误分类', '', table, '',
          '每行总数704；known_wrong_relative、unresolved_relative和事实未能确认保留只在第一步正确而第二步失败的样本中计算。'
          '这些类别可能重叠；事实未能确认保留包含输出缺失或评分无法识别，不直接等同于世界事实被实际改变。'
          '完整路径失败与错误前缀 endpoint 恢复分开，不能用恢复掩盖第一步错误。', '',
          '## 执行代理逐例阅读', '',
          '案例按 CASE_SELECTION 的固定 ID 规则选取，数量不代表频率；此阅读不是独立人工标注。']
    reading=read(ROOT/'AGENT_READING.json')
    for key,value in reading.items():
        if not key.startswith('formal_samples_'):continue
        for r in value:
            text.append('- '+str(r.get('condition',r.get('contrast','')))+' / '+r['category']+' / `'+r['id']+'`：'+r['assessment'])
    text+=['','## 分析边界','',
           '本轮核心任务只有一个外部时间参照；scope评分检查该受控目标，不代表复杂引语或多锚点归属能力。'
           '没有新增范围挑战或 probe，因此不据此断言内部锚点机制或唯一失败原因。'
           '模板 OOD 的自然单步和 gold-reencode 基本能力不足在结果中单列，不能全部解释为 latent 组合失败。']
    (ROOT/'ERROR_DETAIL.md').write_text('\n\n'.join(text)+'\n')
    print('Failure taxonomy written for all9 runs; raw-reading notes preserved')

if __name__=='__main__':
    main()
