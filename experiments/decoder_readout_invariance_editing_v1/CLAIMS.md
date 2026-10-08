# Claim边界

| Claim | 状态 | 支持/反证 |
| --- | --- | --- |
| 有结构大幅memory改变可保持当前native文本 | 探索支持 | BART288pair，T5Gemma32pair；无独立test |
| 同文本意味着分布或内部状态等价 | 不支持 | BART最大JS0.0124072；T5Gemma非零JS |
| 大幅不敏感形成全局nullspace/凸盆地 | 反证 | alpha0.5失配、0.75重入 |
| decoder不读memory | 不支持 | L5替换损坏日期/内容 |
| K/V自身成对补偿即可解释 | 不支持 | L5 BB仍0/64 |
| 局部query/memory配合 | 探索支持 | 在线KV_B0/32、Q_B与QKV_B32/32；非唯一电路 |
| L5是非目标内容专属电路 | 不支持 | 正常颜色V替换也伤害目标49/64 |
| 机制正则胜过输出/随机正则 | NA未运行 | 三方法缺checkpoint，主检验族未执行 |
| Plain改善这批历史源单操作 | validation支持 | 每seedhistory0/768→768/768，冻结历史参考不是update-matched新对照 |
| 长期编辑已稳定 | 反证 | 三/五步均0/256 |
| T5Gemma没有一般同文本pair | 反证 | E→E32/32探索world严格资格 |
| 固定128world仍是完全独立确认 | 失效 | 5个派生core提前编码；0正式test评测不等于0暴露 |
