"""Post-result CPU narrative and descriptive cases; scientific estimates unchanged."""
from common_g15 import *

INTRO='''结论：F、O都修复自身两步，并改善真正留出的F2产物；seed44没有保住原子能力，三seed整体目标未达成。在线刷新O未显示优于固定补训F。

1. **能力保护：** IID旧yesterday all3全部160/160；F/O在seed42/43通过能力标准，seed44原子macro仅89.563%/87.359%，最差cell26/160、11/160。不能只报告today主任务成功。
2. **自身两步：** F/O在所有seed、IID/OOD均160/160；初始化P和自然控制N均0/160。O的两步路径已监督，不是新长度泛化；F的固定输入补训也恢复了自身运行。
3. **真正留出迁移：** IID的F接收U均160/160，O为157/160、160/160、160/160，P/N均0/160。seed42/43在能力保持条件下支持有限迁移；seed44不满足完整目标。OOD逐seedU结果与能力边界见主表。
4. **O是否优于F：** 自身full差均0pp；U的O−F为IID −0.625pp[−1.458,0.000]、OOD +1.042pp[−0.208,2.292]，没有额外优势证据，固定来源补训已足够恢复这次两步和留出迁移。

完整解释、负结果、自然接口边界和剩余问题见[INTERPRETATION.md](INTERPRETATION.md)。下表及区间保留锁定分析程序的原始统计；world CI只对应固定训练模型的世界抽样不确定性。
'''

def main():
    verify_lock()
    preserve=['core_results.csv','atomic_by_cell.csv','fixed_source_results.csv','old_source_results.csv','self_two_step_results.csv','paired_differences.csv','per_example.jsonl.gz']
    hashes={p:digest(ROOT/p) for p in preserve}
    report=(ROOT/'REPORT.md').read_text()
    marker='<!-- G15 post-result introduction -->'
    if marker not in report:
        head,rest=report.split('\n',1);report=head+'\n\n'+marker+'\n'+INTRO+'\n'+rest.lstrip()
    report='\n'.join('偏离/失败：两个GPU前CPU修正；seed43最后评估的内部时间保护触发后单卡补缺，不重训。详见[工程记录](engineering_deviations.json)和[前后哈希核验](resume_evaluation_audit.json)。所有seed/模型/评估已完成。' if line.startswith('偏离/失败：') else line for line in report.splitlines())+'\n'
    (ROOT/'REPORT.md').write_text(report)
    categories=list(csv.DictReader((ROOT/'case_categories.csv').open()))
    for r in categories:
        if r['category'] in ['old_maintenance_failure','old_H2_maintenance_failure']:
            r['category']='old_H2_maintenance_failure';r['scope']='H2 only; not H0/H1/all3'
        else:r['scope']='unchanged'
    csvwrite(ROOT/'case_categories.csv',categories)
    best={}
    with gzip.open(ROOT/'per_example.jsonl.gz','rt') as f:
        for line in f:
            r=json.loads(line);category=None
            if r['seed']==44 and r['split']=='iid' and r['method'] in ['F','O'] and r['kind']=='atomic' and r['status']=='reported_cancelled' and r['offset']==2 and r['perspective']=='third' and not r['joint']:category='atomic_'+r['method']
            if r['seed']==42 and r['split']=='iid' and r['method']=='O' and r['kind']=='fixed' and r['source']=='U' and r['matched'] and not r['joint']:category='heldout_O42'
            if r['seed']==44 and r['split']=='template_ood' and r['method']=='O' and r['kind']=='old' and r['matched'] and not r['joint']:category='maintenance_O44'
            if category:
                order=hashlib.sha256(('g15/interpretation/'+r['world_id']).encode()).hexdigest()
                # Tie keeps the source order in the complete committed archive.
                if category not in best or order<best[category][0]:best[category]=(order,r)
    rows=[dict(category=k,selection='Post-result descriptive only; minimum SHA256(g15/interpretation/world_id); tied sources keep archive order',**r) for k,(h,r) in sorted(best.items())]
    write(ROOT/'boundary_cases.jsonl.gz',rows)
    casefile=ROOT/'CASES.md';cases=casefile.read_text();case_marker='## Post-result boundary examples and category scope'
    cases=cases.split(case_marker)[0].rstrip()+'\n\n'+case_marker+'\n\nAutomatic maintenance-failure category is H2 only; its zero count does not describe H0/H1/all3. `case_categories.csv` now names that scope explicitly. Following examples are supplementary deterministic post-result descriptions, not the pre-inference12 cases, and do not change cohorts or estimates.\n\n'
    for r in rows:
        current=r.get('current',{}).get('output')
        if r['kind']=='atomic':current=render(r['world'],frame(r['world'],r['offset'],r['perspective']))
        cases+=f'### {r["category"]}: seed{r["seed"]}, {r["split"]}, {r["world_id"]}\n\nSource/current: {current}\n\nOutput: {r["output"]}\n\nGold: {r["gold"]}\n\nJoint={r["joint"]}; exact={r["exact"]}; error={r["error_type"]}; relative_date={r["predicted_relative_date"]}; delta_days={r["relative_date_delta_days"]}; first_failure={r.get("first_failure","NA fixed next step")}. Parsed: {json.dumps(r["parsed_facts"],ensure_ascii=False)}\n\n'
    casefile.write_text(cases.rstrip()+'\n')
    assert hashes=={p:digest(ROOT/p) for p in preserve}
    dump(ROOT/'post_result_reporting.json',dict(scientific_estimates_and_full_archive_unchanged=True,preserved_sha256=hashes,original_case_category_rule='old/H2 failure only',corrected_label='old_H2_maintenance_failure',category_counts_unchanged=True,supplementary_boundary_rows=len(rows),selection_descriptive_only=True,created_after_scientific_lock=True))
    print('G15 report annotated; statistics unchanged; boundary cases',len(rows))

if __name__=='__main__':main()
