# 当前执行状态

用户确认16例抽查通过，正则GPU验收通过。seed42六个候选已完成400updates与64world validation：锁定keep=0.1、mechanism=0.1；联合成功Plain1536/1536、Output-only1525/1536、Mechanism-guided1530/1536、Random-site1528/1536。仅为validation选型，不能称独立收益。正在发布本轮，随后seed43/44并行执行相同锁定方法。

S4独立test仍BLOCKED_TEST_INTEGRITY（5/128core提前暴露），正式test评测0；16例人工验收没有授权修改测试终点。所有产物位于/dataset1/zailong/，受控峰值最多2GPU。
