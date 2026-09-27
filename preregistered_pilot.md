# 预登记：StylePTB TFU 低秩时态编辑预实验
登记时间：2026-09-27；登记于开发生成和测试生成之前。

GYAFC 官方入口要求申请，已检查本地 data/datasets 未找到；不联系第三方、不下载非官方镜像。采用官方 StylePTB（CC BY 4.0）TFU / To Future 配对任务。本轮问题改为：冻结共享编码解码器中，逐 token 输入相关低秩 affine 是否比全局 shift 更可靠地转换为将来时并保留指定内容。不能推广为正式程度结论。

## 数据与封存
使用官方 single_transform_checkout.py 的有序划分语义：前 floor(N/20) 开发，其后至 floor(N/10) 测试，其余训练。先按 BART token 数源/目标均不超过 96（含特殊 token）过滤，绝不截断。保留官方 split，最多 5000/500/1000，seed=42 抽样。多参考按规范化源句合并。跨 split 精确/字符 ngram cosine >= .92 近重复剔除低优先级样本（test > dev > train），同 split 精确源分组；近重复只检测不同源且长度比 >= .8。长度/去重统计、hash 写入 manifest。原始 TFU N 约7271，官方 dev/test 各约363，按实际报告，不能扩充测试。
测试文件仅数据准备审计读取；模型选择仅开发集。训练 seed=42，配置冻结后 43/44。三个 seed 同一划分。

## 表示与重构门槛 R
facebook/bart-base revision aadd2ab0ae0c8268c7c9693540e9904811f36177，MIT。encoder last_hidden_state，固定 [96,768]，可见 attention mask（披露长度），逐 token 编辑。G 只获得该 memory 和相同 mask；无原文旁路、属性提示或标签。greedy，num_beams=1，do_sample=false，max_new_tokens=100，统一 EOS；输出无 EOS 计截断失败。
先测试开发 identity；内容自动检查 >=90%、无效 <=5% 才通过 R，另报原始字符串逐字率和 token 指标。失败时允许唯一一次受控修复：仅训练源/目标自重构，AdamW lr=3e-5，batch=16，最多 2 epoch / 1200 steps，开发重构 loss 每200步选择最优；其后永久冻结同一 E/G。仍失败则编码解码瓶颈结束，不称低秩被证伪。

## 主比较
identity；可训练 shift b；lowrank_affine z + U(V^T z)+b，r=4,16,64；nonlinear_bottleneck 同选定 rank、GELU。b/U 初始化0，V小正态，实际梯度审计。float32 参数、可用 GPU bf16 autocast；E/G eval 且冻结，E 可 no_grad，G 训练编辑器时必须有梯度。
共同 AdamW lr=1e-3，weight_decay=0，batch16，最多1000更新，每200步开发目标 token loss（全开发集）保存最好；连续3次未改善1e-4可停止。各方法同损失/样本顺序/上限；rank 按4→16→64选开发目标 loss 最低，平手选小rank。nonlinear 用选定宽度；不另搜学习率。预算不足时首先省rank64，再16，但保留全部必要方法；如不足三个seed明确探索性，不自动B/C。确认43/44不重选rank和超参。

## 自动评估（不能冒充事实真值）
独立 spaCy en_core_web_sm 3.8.0 词性/依存规则：输出存在 will/shall 辅助词依存连接 VERB/AUX，作为 future_auto；报告该规则在未生成开发源/目标上的阳性率，不把它叫人工准确率，不要求源必定是负例。属性检测不读方法名，不依赖生成模型自评。
内容 strict_lemma_auto：去除标点/空格和将来时助动词 will/shall 后，其余词的有序 lemma 序列完全相同；同时数量、日期/时间、专名实体、否定 token 序列需保持。有序序列对无实体句仍生效；它保守地检查词汇/顺序，不能保证所有事件关系与否定辖域正确，也可能拒绝合法改写。实体比较小写并去标点；数字/单位保留由序列共同保证。分别报告各组件，未使用 NLI，未测人工流畅性。开发 gold/source 内容检查覆盖低于90%时，门槛A的自动结论标不足，不自动推进B/C，但继续全部主模型运行/导出。
有效性：非空、有EOS、至少一个英文字母、无同一3gram重复4次；不宣称语法流畅性经验证。Joint_auto = future_auto AND strict_content_auto AND valid_auto，所有预选测试源都在分母；失败不排除。逐字率原字符串比较，另报 tokenizer token 编辑距离重构相似度、chrF。主比较 lowrank_affine-shift，2000次源句 paired bootstrap，先句内平均seed再重采样；报告各seed、均值、分子/分母、95%百分位CI、seed波动。匿名审查100源，各方法随机排序，映射分开，尚未人工核验。额外固定20条数字/实体/否定 synthetic_diagnostic，只诊断，不进入主门槛。

## 决策、预算
A：三seed平均Joint_auto增益>=5pp，至少2/3方向一致，内容下降<=2pp，无泄漏或训练不公平，非仅合成，评估覆盖合格，剩余预算足够。CI跨0仅探索信号。
最多12累计GPU小时（模型准备/训练/生成/评估全计）；最多同时2GPU，默认1，通过sbatch+srun，Slurm计时为保守上界。预留C先于扩大B，CPU HE <=4墙钟小时、<=4线程。A不通过不自动扩数据/换模型/重搜。A通过才登记有限B/C子协议并执行，C最低16-32样本真实CKKS，不以噪声替代。客户端本地 E→T→G 成本直接计时；直接改写参考仅预算允许用已有本地模型，否则标未测。三个研究层次（编辑、密文正确性、部署）独立判定。

## 阶段 A 后追加登记：有限机制验证（2026-09-27）
**协议偏差，必须在报告披露**：上述“gold内容接受率低于90%不自动推进”是执行者添加、并非用户原始A门槛。观察到接受率84.02%后不改自动检查和已完成测试统计；遵从用户优先指令，原始门槛A全部满足时仍执行有限B/C。此扩展不得描述为完全符合初始额外门槛的预登记研究，也不能用来补强事实真值；内容检查的保守偏差需盲审解决。`gate_A.json` 保留额外门槛前后决定字段。

C优先：固定测试 source_id 排序前16条，使用seed42 rank64 checkpoint，不挑成功案例。TenSEAL/SEAL CKKS，N8192、模数[60,40,40,60]、scale2^40，SEAL tc128检查，因子化两次plaintext矩阵乘法。公开mask（长度泄漏），只计算有效token并恢复padding；客户端/服务器不同进程，仅公共context/评估密钥和ciphertext传给服务器，私钥仅客户端内存。服务器不读测试文本、latent明文或解密残差。共享机器同UID不能提供OS级隔离，仅协议消息边界验证。固定16样本，不扩至100；CPU最多3.5小时以保留4小时上限。三路径为float32原编辑器、float64有限精度控制（输入/参数round至2^-40，每次乘法后同样舍入）、真实CKKS。生成仍同一G和主配置。

客户端直接改写补充参考：已有本地Qwen2.5-7B-Instruct，固定测试source_id排序前100条，单一英文指令“Rewrite the sentence in future tense. Preserve names, quantities, dates, negation and event participants. Output only the rewritten sentence.” greedy，max_new_tokens=100。不选prompt、不调整阈值、不作为上界或阶段A门槛依据，独立报告与相同100源上的主方法。

B规模上限：先核查官方组合数据真实操作和source分组。仅挑有合法明确目标的两步组合，最多1000训练源/100开发/100测试。留出组合不用于训练/选参，seed42机制性探索；若无法合法构造独立训练组合监督，则不冒称带组合约束实验已完成，并记录具体数据阻塞。先完成C最小验证。

B在数据准备后、B训练/测试生成之前固定：使用官方 Tense+Voice codes `10`=future、`30`=present、`01`=active→passive；`31` present+passive是可用的训练组合，`11` future+passive从所有训练/开发选择中排除。所有source/target变体构成连通分量分组，跨官方split删低优先级分量，再按字符近重复>=.92删分量。最多1000训练组、100开发组、100独立测试组。每操作每组至多一对。三个scheme均重新初始化（不加载A编辑器），rank64、seed42、600次更新、batch8、AdamW1e-3、无B超参选择，固定最终checkpoint。composition_trained_lowrank使用0.5单步CE+0.5已见组合CE，因此额外组合监督和算力明确记录；不是完全无组合监督。未施加未经验证的交换律或可逆约束。
B内容评估允许语态重排/增加被动助词：非AUX lemma多重集（排除被动by）相同，加root事件/agent/patient词头、实体/数字/日期/否定多重集相同；future+passive依存规则，两项同时通过及content/valid定义B的Joint_auto。该规则仍非真值，报告gold覆盖及失败样本。路径为passive→future，latent连续编辑解码一次 vs 单步解码再编码。另在同一测试源上评估单步passive内容漂移。
