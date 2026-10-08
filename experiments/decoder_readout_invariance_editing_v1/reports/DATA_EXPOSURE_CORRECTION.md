# Counterfactual control exposure correction

颜色 resampling 使不同 core_content 进入 encoder。遗漏了生成 donor 之前的 split 检查。5 个 IID test core（7 次recipient控制映射）和2个 reserved core提前暴露；完整列表见 results/COUNTERFACTUAL_EXPOSURE_AUDIT.json。历史报告的 independent_test_accessed=0 指正式test评测次数，未计算这些派生core，是审计缺口。正式评测次数仍为0；不能再称全部128core未暴露。

原world ID、分组和128扫描分母不改，不补搜。5个core今后只作replay，完整128独立主终点 BLOCKED_TEST_INTEGRITY；剩余123core的独立子集不能无声替换预注册终点。S0/S1/S2 train-validation证据与Plain训练可保留，但确认性claim暂停。所有科学失败及暴露保留。
