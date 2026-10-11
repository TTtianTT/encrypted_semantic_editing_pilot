# 主张表补充：规范 CE 与写入几何

|主张|直接证据|边界|
|---|---|---|
|规范编码不是当前输出 CE 的最优点|同 world / 同目标 teacher forcing 下，RRR 初始化及微调状态的 CE 可低于 E(y)；绝对收益与配对 world bootstrap 区间见 canonical_ce_gap.json|这是有限受控目标上存在更低 CE 状态的证据；不主张找到了全局最优点|
|历史 CE 编辑几乎不沿规范方向写入|三 seed IID：cos(w,d)=-0.0119 至 -0.0052，||w||/||d||=3.31–3.40；结构 OOD=3.69–3.80；沿 d 的系数略负|历史编辑器与对齐转换；相对理想写入较大，不等于相对完整表示较大。Decoder shortcut 是解释，不是形式化攻击|
|CE 能奖励偏离规范的写法；组合破坏依赖优化路径|所有四优化器存在可测 CE 下降；AdamW1e-3 R5 掉到0%，小 lr/SGD 保留更多 R5|不能写成任意 CE 优化器必然破坏组合性；图中每点是实测检查点，连线不代表实测中间模型|

新图：optimizer_absolute_ce.svg（绝对 CE、规范基线、更新标签、置信区间）；optimizer_canonical_gap.svg（相对规范 CE 差值）。没有新增训练或模型预测。
