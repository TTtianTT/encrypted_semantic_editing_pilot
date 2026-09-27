# 先审核任务，不看模型输出

当前文件是待审核候选，不是冻结评估集。`task_review_candidates.csv` 中所有评分为空，目标来自原数据自动变换，未保证正确。不得以模型评分代替本轮要求的真人确认。解析器给出的施事/动词/受事只是辅助草稿。

真人逐源检查：
- 原句是否自然、意义清楚，是否有明确施事、及物事件和受事；占有义have、习语、非自然被动不能仅靠句法树判合格。
- future_target是否只改变允许的时间语法，没有与过去时间限定冲突。
- passive_target是否自然成被动、保留原时态和施受角色。
- combo_target是否为自然将来时被动，保留人物、事件、数量单位、否定及相关关系。

分别填写source_valid / future_valid / passive_valid / combo_valid / time_compatible / roles_unambiguous：1、0或U，不能留空；保留0与U以及理由。每行填真人代号human_reviewer及reviewed_at；记录修改目标的理由。可以修正目标句，不修改源句、ID、原始划分和行顺序。源句本身不成立时判0，不为凑足数量改写源句。无法形成自然被动时不要勉强造目标。`incomplete_target_candidates` 的空白目标须真人补写才有资格通过。

提交任务审核表时还须提供一个JSON声明（如实填写，不能预填为完成）：
```
{
  "reviewer_id": "真人代号",
  "reviewer_is_human": true,
  "tasks_reviewed_before_any_model_outputs": true,
  "previous_63_all_within_excluded_old_B100": true
}
```
最后一项只能在确认63个旧来源全在旧B100组内时填写true。否则提供63个source_id或源句，由实验端扩充排除清单并重新准备，不能假设已独立。

当前冻结脚本保持官方dev/test划分，需40/100个真人通过来源才可执行。审计已发现该规模无法从现有完整配对候选满足；在另行确认数据来源/划分方案前，这个审核包只供资源判断与任务排查，不会自动重新划分训练候选。
