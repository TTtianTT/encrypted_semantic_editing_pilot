# 当前同文本状态的后续编辑分叉：因果干预结果

bart: 锁定pca_k4_a1.0，80个独立新world、三可用编辑器seed；C0=100.00%，R1=100.00%。局部与8-seed同维同范数随机均值的R1差=1.0，world-cluster95%CI=[1.0, 1.0]。随机对照当前保持可能较低，表B完整保留C0，不能仅用下一步恢复数字解释特异性。

本轮主效应仅来自 N→E donor；E→E 未取得配对，R 与 N 的状态数值相同，不能当作独立来源复现。共享4维方向逐有效memory token应用，平均patch范数13.4629，相对修补后有效表示范数48.32%；约占full donor差值均值范数的96.3%。因此这是低维但大幅度的donor-assisted修补，不能称微小扰动或一般健康状态恢复。随机条件C0均值18.65%，C1为0；保持当前状态的随机条件也未恢复下一步。

primary一次性修补完整R3=0.00%，R5=0.00%；Good的同序列真实上限见表C。

reordered一次性修补完整R3=0.00%，R5=0.00%；Good的同序列真实上限见表C。

t5gemma: BLOCKED / NOT ESTIMABLE。固定资格池没有可用于该协议的exact当前文本匹配配对；S0工具验收通过不等于有因果效应样本。当前输出的尾部空格/换行差异见历史witness和本轮qualification诊断，不进行strip放宽。S2–S4干预恢复率/区间为NA，不能写成0或作为科学反例。

本实验固定时间领域、原已准入 P 编辑器、三 seed42/43/44。冻结模型为 facebook/bart-base FP32 与原版 google/t5gemma-2b-2b-ul2-it BF16。所有数值来自已执行产物；未执行项为 NA/MISSING。来源、操作与有限候选池限制保留，局部 donor-assisted 干预不构成无 donor 部署算法或唯一完整 causal circuit。

协议与数据在独立 test 干预之前锁定。按 world 哈希划分、跨 seed 共同分组；96 个原训练 worlds 全排除，固定候选池256（旧 dev24、旧 test32、新200），不为凑数继续搜索。primary 为当前 state0 的 plus，每 world 一对，固定 E→E/N→E/R→E 优先级；本轮独立 test 只取新 worlds，少于40 world 时标探索性。模板0为 IID；机制 held-out 不称模板 OOD。旧测试只用于资格/发现，不能复称独立确认。

S0（见 results/S0_ACCEPTANCE.json）：bart passed=True, worlds=16, t5gemma passed=True, worlds=16。无干预当前/下一步 token 与原路径一致；no-op/self/alpha0 logits 精确相等、encoder forward0、padding不参与patch、hook退出移除、use_cache=False。Full donor仅是正对照；每个正式 pair 又核验 full/good 下一步及轨迹相等。

表 A 的完整分母和排除原因在 CSV/JSON（history组合计数与 world计数分列）。E→E 没有合格 donor 时不制造配对；N、R 标签分别保存，即便同文本 reencode 与 N 实际数值相同。两个预定义编辑历史之外的配对存在性未被穷尽。

以下表A按机制split汇总primary plus的world分母。旧dev/旧test/new身份及minus的完整表保留在 results/table_A_pairs.csv/json；qualification test的110个world含旧曝光数据，正式独立干预仅用其中80/84个合格新world。

| model | editor_seed | split | source | scanned_worlds | current_double_correct_worlds | exact_current_text_worlds | next_step_fork_worlds | same_shape_mask_worlds | final_pair_worlds | independent_new_test_qualified |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| bart | 42 | discovery | E→E | 93 | 93 | 93 | 0 | 0 | 0 | 0 |
| bart | 42 | discovery | N→E | 93 | 93 | 93 | 93 | 93 | 93 | 0 |
| bart | 42 | discovery | R→E | 93 | 93 | 93 | 93 | 93 | 93 | 0 |
| bart | 42 | test | E→E | 110 | 110 | 110 | 0 | 0 | 0 | 0 |
| bart | 42 | test | N→E | 110 | 110 | 110 | 110 | 110 | 110 | 84 |
| bart | 42 | test | R→E | 110 | 110 | 110 | 110 | 110 | 110 | 84 |
| bart | 42 | validation | E→E | 53 | 53 | 53 | 0 | 0 | 0 | 0 |
| bart | 42 | validation | N→E | 53 | 53 | 53 | 53 | 53 | 53 | 0 |
| bart | 42 | validation | R→E | 53 | 53 | 53 | 53 | 53 | 53 | 0 |
| bart | 43 | discovery | E→E | 93 | 93 | 93 | 0 | 0 | 0 | 0 |
| bart | 43 | discovery | N→E | 93 | 93 | 93 | 93 | 93 | 93 | 0 |
| bart | 43 | discovery | R→E | 93 | 93 | 93 | 93 | 93 | 93 | 0 |
| bart | 43 | test | E→E | 110 | 110 | 110 | 0 | 0 | 0 | 0 |
| bart | 43 | test | N→E | 110 | 110 | 110 | 110 | 110 | 110 | 84 |
| bart | 43 | test | R→E | 110 | 110 | 110 | 110 | 110 | 110 | 84 |
| bart | 43 | validation | E→E | 53 | 53 | 53 | 0 | 0 | 0 | 0 |
| bart | 43 | validation | N→E | 53 | 53 | 53 | 53 | 53 | 53 | 0 |
| bart | 43 | validation | R→E | 53 | 53 | 53 | 53 | 53 | 53 | 0 |
| bart | 44 | discovery | E→E | 93 | 93 | 93 | 0 | 0 | 0 | 0 |
| bart | 44 | discovery | N→E | 93 | 93 | 93 | 93 | 93 | 93 | 0 |
| bart | 44 | discovery | R→E | 93 | 93 | 93 | 93 | 93 | 93 | 0 |
| bart | 44 | test | E→E | 110 | 110 | 110 | 0 | 0 | 0 | 0 |
| bart | 44 | test | N→E | 110 | 110 | 110 | 110 | 110 | 110 | 84 |
| bart | 44 | test | R→E | 110 | 110 | 110 | 110 | 110 | 110 | 84 |
| bart | 44 | validation | E→E | 53 | 53 | 53 | 0 | 0 | 0 | 0 |
| bart | 44 | validation | N→E | 53 | 53 | 53 | 53 | 53 | 53 | 0 |
| bart | 44 | validation | R→E | 53 | 53 | 53 | 53 | 53 | 53 | 0 |
| t5gemma | 42 | discovery | E→E | 93 | 93 | 93 | 0 | 0 | 0 | 0 |
| t5gemma | 42 | discovery | N→E | 93 | 93 | 0 | 0 | 0 | 0 | 0 |
| t5gemma | 42 | discovery | R→E | 93 | 93 | 0 | 0 | 0 | 0 | 0 |
| t5gemma | 42 | test | E→E | 110 | 110 | 110 | 0 | 0 | 0 | 0 |
| t5gemma | 42 | test | N→E | 110 | 110 | 0 | 0 | 0 | 0 | 0 |
| t5gemma | 42 | test | R→E | 110 | 110 | 0 | 0 | 0 | 0 | 0 |
| t5gemma | 42 | validation | E→E | 53 | 53 | 53 | 0 | 0 | 0 | 0 |
| t5gemma | 42 | validation | N→E | 53 | 53 | 0 | 0 | 0 | 0 | 0 |
| t5gemma | 42 | validation | R→E | 53 | 53 | 0 | 0 | 0 | 0 | 0 |
| t5gemma | 43 | discovery | E→E | 93 | 93 | 93 | 0 | 0 | 0 | 0 |
| t5gemma | 43 | discovery | N→E | 93 | 93 | 0 | 0 | 0 | 0 | 0 |
| t5gemma | 43 | discovery | R→E | 93 | 93 | 0 | 0 | 0 | 0 | 0 |
| t5gemma | 43 | test | E→E | 110 | 110 | 110 | 0 | 0 | 0 | 0 |
| t5gemma | 43 | test | N→E | 110 | 110 | 0 | 0 | 0 | 0 | 0 |
| t5gemma | 43 | test | R→E | 110 | 110 | 0 | 0 | 0 | 0 | 0 |
| t5gemma | 43 | validation | E→E | 53 | 53 | 53 | 0 | 0 | 0 | 0 |
| t5gemma | 43 | validation | N→E | 53 | 53 | 0 | 0 | 0 | 0 | 0 |
| t5gemma | 43 | validation | R→E | 53 | 53 | 0 | 0 | 0 | 0 | 0 |
| t5gemma | 44 | discovery | E→E | 93 | 93 | 93 | 0 | 0 | 0 | 0 |
| t5gemma | 44 | discovery | N→E | 93 | 93 | 0 | 0 | 0 | 0 | 0 |
| t5gemma | 44 | discovery | R→E | 93 | 93 | 0 | 0 | 0 | 0 | 0 |
| t5gemma | 44 | test | E→E | 110 | 110 | 110 | 0 | 0 | 0 | 0 |
| t5gemma | 44 | test | N→E | 110 | 110 | 0 | 0 | 0 | 0 | 0 |
| t5gemma | 44 | test | R→E | 110 | 110 | 0 | 0 | 0 | 0 | 0 |
| t5gemma | 44 | validation | E→E | 53 | 53 | 53 | 0 | 0 | 0 | 0 |
| t5gemma | 44 | validation | N→E | 53 | 53 | 0 | 0 | 0 | 0 | 0 |
| t5gemma | 44 | validation | R→E | 53 | 53 | 0 | 0 | 0 | 0 | 0 |

表 B（seed 等权均值；8随机 seed先在同world/编辑器seed内平均，随机方向不算独立样本）。R1=C0且一步joint正确；保留当前exact、范数和随机比较。

| model | method | n_worlds | n_seed_worlds | C0 | exact_preservation | R1 | random_difference | random_difference_ci95 | patch_norm | relative_patch_norm |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| bart | bad | 80 | 240 | 1.0000 | 1.0000 | 0.0000 | NA | NA | 0.0000 | 0.0000 |
| bart | full | 80 | 240 | 1.0000 | 1.0000 | 1.0000 | NA | NA | 13.9818 | 0.5040 |
| bart | global_a0 | 80 | 240 | 1.0000 | 1.0000 | 0.0000 | NA | NA | 0.0000 | 0.0000 |
| bart | global_a0.25 | 80 | 240 | 0.9917 | 0.9917 | 0.0000 | NA | NA | 3.4954 | 0.1191 |
| bart | global_a0.5 | 80 | 240 | 1.0000 | 1.0000 | 0.0000 | NA | NA | 6.9909 | 0.2462 |
| bart | global_a1.0 | 80 | 240 | 1.0000 | 1.0000 | 1.0000 | NA | NA | 13.9818 | 0.5040 |
| bart | good | 80 | 240 | 1.0000 | 1.0000 | 1.0000 | NA | NA | 13.9818 | 0.5040 |
| bart | noop | 80 | 240 | 1.0000 | 1.0000 | 0.0000 | NA | NA | 0.0000 | 0.0000 |
| bart | pca_k4_a1.0 | 80 | 240 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | [1.0, 1.0] | 13.4629 | 0.4832 |
| bart | random_pca_k4_a1.0_8seed_mean | 80 | 240 | 0.1865 | 0.1865 | 0.0000 | NA | NA | 13.4629 | 0.4052 |
| bart | random_read_k1_a0.25_8seed_mean | 80 | 240 | 1.0000 | 1.0000 | 0.0000 | NA | NA | 0.4351 | 0.0142 |
| bart | read_k1_a0.25 | 80 | 240 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | [0.0, 0.0] | 0.4351 | 0.0142 |
| bart | reverse_pca_k4_a1.0 | 80 | 240 | 1.0000 | 1.0000 | 0.0000 | NA | NA | 13.4629 | 0.4403 |
| bart | reverse_read_k1_a0.25 | 80 | 240 | 1.0000 | 1.0000 | 1.0000 | NA | NA | 0.4351 | 0.0157 |
| bart | self | 80 | 240 | 1.0000 | 1.0000 | 0.0000 | NA | NA | 0.0000 | 0.0000 |

主比较统计：10,000次共同world-cluster percentile bootstrap，保持该world全部seed/方法关联；双侧符号翻转的对称/可交换假设单列，不是随机分配试验精确p值。两个模型的辅助p值按Holm校正；R3/R5、置信度/来源为次要探索性。

| model | method | n_worlds | n_seeds | estimate | ci95 | p_raw | p_holm |
| --- | --- | --- | --- | --- | --- | --- | --- |
| bart | pca_k4_a1.0 | 80 | 3 | 1.0000 | [1.0, 1.0] | 0.0001 | 0.0002 |
| t5gemma | NA | 0 | 0 | NA | NA | NA | NA |

表 C：只在t=0修补一次，之后只传递latent，用原T和未干预D。Gold由world状态机预先给定，两条合法5步序列分别为plus/minus/plus/minus/plus及plus/plus/minus/minus/plus；完整R3/R5不以最终endpoint替代。Good真实长链上限保留。

| model | sequence | method | n_worlds | R1 | R3 | R5 | step_endpoints | first_failure_distribution |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| bart | primary | bad | 80 | 0.0000 | 0.0000 | 0.0000 | [0.0, 0.0, 0.0, 0.0, 0.0] | {'1': 240.0} |
| bart | primary | full | 80 | 1.0000 | 0.0000 | 0.0000 | [1.0, 0.0, 0.0, 0.0, 0.0] | {'2': 240.0} |
| bart | primary | global_a0.5 | 80 | 0.0000 | 0.0000 | 0.0000 | [0.0, 0.0, 0.0, 0.0, 0.0] | {'1': 240.0} |
| bart | primary | good | 80 | 1.0000 | 0.0000 | 0.0000 | [1.0, 0.0, 0.0, 0.0, 0.0] | {'2': 240.0} |
| bart | primary | pca_k4_a1.0 | 80 | 1.0000 | 0.0000 | 0.0000 | [1.0, 0.0, 0.0, 0.0, 0.0] | {'2': 240.0} |
| bart | primary | random_pca_k4_a1.0_8seed_mean | 80 | 0.0000 | 0.0000 | 0.0000 | [0.0, 0.0, 0.0, 0.0, 0.0] | {'0': 195.25, '1': 44.75} |
| bart | reordered | bad | 80 | 0.0000 | 0.0000 | 0.0000 | [0.0, 0.0, 0.0, 0.0, 0.0] | {'1': 240.0} |
| bart | reordered | full | 80 | 1.0000 | 0.0000 | 0.0000 | [1.0, 0.0, 0.0, 0.0, 0.0] | {'2': 240.0} |
| bart | reordered | global_a0.5 | 80 | 0.0000 | 0.0000 | 0.0000 | [0.0, 0.0, 0.0, 0.0, 0.0] | {'1': 240.0} |
| bart | reordered | good | 80 | 1.0000 | 0.0000 | 0.0000 | [1.0, 0.0, 0.0, 0.0, 0.0] | {'2': 240.0} |
| bart | reordered | pca_k4_a1.0 | 80 | 1.0000 | 0.0000 | 0.0000 | [1.0, 0.0, 0.0, 0.0, 0.0] | {'2': 240.0} |
| bart | reordered | random_pca_k4_a1.0_8seed_mean | 80 | 0.0000 | 0.0000 | 0.0000 | [0.0, 0.0, 0.0, 0.0, 0.0] | {'0': 195.25, '1': 44.75} |

反向干预见表B reverse行及逐例current保持、一步损伤；它只能描述候选成分的相反行为，不把一般损伤视为特异性。其他操作保持若未单列执行为NA。

仿射传播为 row delta + delta VᵀUᵀ；实际forward保留bias、mask和dtype casts。FP32数值误差与BF16舍入误差如下，bias绝对量级不从差分抵消推断无作用。T5Gemma此表若存在仅为raw-text未匹配资格诊断，不是独立test或因果效果复现。读取/写入补空间用I−QQᵀ定义，可由投影比例补数得到；不构造巨大Ld矩阵。

| model | n | max_absolute_error | max_relative_error | mean_read_fraction | mean_bias_norm |
| --- | --- | --- | --- | --- | --- |
| bart | 240 | 0.0000 | 0.0000 | 0.0671 | 0.4045 |
| t5gemma | 16 | 0.2299 | 0.0046 | 0.0118 | 0.5497 |

表 D：固定相同gold前缀第一语义分叉token的连续margin。候选mediator来自对bad做上游修补的R路径。模块位置、粗筛、最多3模块、rank4共享discovery子空间、自patch验收及B/R/阻断/插入/off-path/reverse均在decoder文件。off-path按张量维数/位置匹配，实际扰动范数单列，不能据不等幅度控制宣称唯一特异路径。辅助结果仅支持readout效应和candidate路径证据，未执行自由生成decoder patch；不能称latent修复或唯一完整电路。未过validation gate则该项NA。

| model | module | n_worlds | upstream_gain | blocked_gain_removed | offpath_gain_removed | inserted_gain | R_mediator_shift_norm | offpath_shift_norm |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| bart | layer5.MLP | 32 | 11.5835 | 4.8075 | 0.8277 | 4.2680 | 5.7682 | 8.2541 |
| bart | layer5.cross_attention | 32 | 11.5835 | 10.0895 | 0.5563 | 8.3519 | 18.0899 | 15.2758 |
| bart | layer5.residual | 32 | 11.5835 | 11.5835 | 0.5563 | 11.5835 | 45.5460 | 5.7742 |

表 E：实际 seed/来源/NLL匹配子集（margin因多token候选不硬套阈值，NLL≤0.1 nat锁定）；缺来源为NA而非0恢复率。

| model | editor_seed | source | confidence_subset | n_worlds | C0 | R1 | R3 | R5 | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| bart | 42 | E→E | all | 0 | NA | NA | NA | NA | NA; no eligible primary-source records |
| bart | 42 | E→E | NLL_matched | 0 | NA | NA | NA | NA | NA; no eligible primary-source records |
| bart | 42 | N→E | all | 80 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | executed |
| bart | 42 | N→E | NLL_matched | 80 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | executed |
| bart | 42 | R→E | all | 0 | NA | NA | NA | NA | NA; no eligible primary-source records |
| bart | 42 | R→E | NLL_matched | 0 | NA | NA | NA | NA | NA; no eligible primary-source records |
| bart | 43 | E→E | all | 0 | NA | NA | NA | NA | NA; no eligible primary-source records |
| bart | 43 | E→E | NLL_matched | 0 | NA | NA | NA | NA | NA; no eligible primary-source records |
| bart | 43 | N→E | all | 80 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | executed |
| bart | 43 | N→E | NLL_matched | 80 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | executed |
| bart | 43 | R→E | all | 0 | NA | NA | NA | NA | NA; no eligible primary-source records |
| bart | 43 | R→E | NLL_matched | 0 | NA | NA | NA | NA | NA; no eligible primary-source records |
| bart | 44 | E→E | all | 0 | NA | NA | NA | NA | NA; no eligible primary-source records |
| bart | 44 | E→E | NLL_matched | 0 | NA | NA | NA | NA | NA; no eligible primary-source records |
| bart | 44 | N→E | all | 80 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | executed |
| bart | 44 | N→E | NLL_matched | 80 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | executed |
| bart | 44 | R→E | all | 0 | NA | NA | NA | NA | NA; no eligible primary-source records |
| bart | 44 | R→E | NLL_matched | 0 | NA | NA | NA | NA | NA; no eligible primary-source records |
| t5gemma | 42 | E→E | all | 0 | NA | NA | NA | NA | NA; no eligible primary-source records |
| t5gemma | 42 | E→E | NLL_matched | 0 | NA | NA | NA | NA | NA; no eligible primary-source records |
| t5gemma | 42 | N→E | all | 0 | NA | NA | NA | NA | NA; no eligible primary-source records |
| t5gemma | 42 | N→E | NLL_matched | 0 | NA | NA | NA | NA | NA; no eligible primary-source records |
| t5gemma | 42 | R→E | all | 0 | NA | NA | NA | NA | NA; no eligible primary-source records |
| t5gemma | 42 | R→E | NLL_matched | 0 | NA | NA | NA | NA | NA; no eligible primary-source records |
| t5gemma | 43 | E→E | all | 0 | NA | NA | NA | NA | NA; no eligible primary-source records |
| t5gemma | 43 | E→E | NLL_matched | 0 | NA | NA | NA | NA | NA; no eligible primary-source records |
| t5gemma | 43 | N→E | all | 0 | NA | NA | NA | NA | NA; no eligible primary-source records |
| t5gemma | 43 | N→E | NLL_matched | 0 | NA | NA | NA | NA | NA; no eligible primary-source records |
| t5gemma | 43 | R→E | all | 0 | NA | NA | NA | NA | NA; no eligible primary-source records |
| t5gemma | 43 | R→E | NLL_matched | 0 | NA | NA | NA | NA | NA; no eligible primary-source records |
| t5gemma | 44 | E→E | all | 0 | NA | NA | NA | NA | NA; no eligible primary-source records |
| t5gemma | 44 | E→E | NLL_matched | 0 | NA | NA | NA | NA | NA; no eligible primary-source records |
| t5gemma | 44 | N→E | all | 0 | NA | NA | NA | NA | NA; no eligible primary-source records |
| t5gemma | 44 | N→E | NLL_matched | 0 | NA | NA | NA | NA | NA; no eligible primary-source records |
| t5gemma | 44 | R→E | all | 0 | NA | NA | NA | NA | NA; no eligible primary-source records |
| t5gemma | 44 | R→E | NLL_matched | 0 | NA | NA | NA | NA | NA; no eligible primary-source records |

SAE：SKIPPED。Exact-text pairing unavailable for at least one model: the both-model discovery/validation prerequisite is unmet. No SAE escalation. 核心test前决策；不重新训练backbone或原编辑器。空间/其他领域未扩展。

实际Slurm资源（最终sacct刷新）：

| stage | array_id | terminal | GPU_hours | states |
| --- | --- | --- | --- | --- |
| smoke_bart | 2815 | True | 0.0186 | {'COMPLETED': 1} |
| scan_bart | 2816 | True | 0.3047 | {'COMPLETED': 3} |
| discovery_bart | 2820 | True | 0.0428 | {'COMPLETED': 1} |
| validation_bart | 2821 | True | 0.0661 | {'COMPLETED': 1} |
| smoke_t5gemma | 2822 | True | 0.0369 | {'COMPLETED': 1} |
| scan_t5gemma | 2823 | True | 1.5772 | {'COMPLETED': 3} |
| qualification_t5gemma | 2832 | True | 0.0597 | {'COMPLETED': 1} |
| decoder_bart | 2834 | True | 0.0281 | {'COMPLETED': 1} |
| fit_bart | 2835 | True | 0.0228 | {'COMPLETED': 2} |
| test_bart | 2837 | True | 3.6600 | {'TIMEOUT': 2, 'COMPLETED': 1} |
| test_bart | 2873 | True | 0.7389 | {'COMPLETED': 1} |
| aggregate_cpu | 2875 | True | 0.0000 | {'COMPLETED': 1} |
| verify_cpu | 2877 | True | 0.0000 | {'COMPLETED': 1} |

总allocation GPU-hours=6.555833，allocation起止事件重建峰值并发=2 GPU。未终态数组=[]。40GPUh/2GPU上限均按allocation核算；失败/smoke/retry计入，.batch和step不重复。

结论标签按实际表现：上游仅恢复一步为 operation-specific one-step compatibility repair；一次上游patch若提升所测完整长链为 observed multi-step recoverability improvement，仅限所测序列/分布；decoder单独patch为 readout repair。阴性/区间重叠不证明相等。少量成功、失败与reverse反例按固定world排序抽取于examples.jsonl，不能代替聚合。


## 十项验收回答与解释边界

1. BART每个seed固定扫描256个world，N→E与R→E的plus/minus均有256个合格world，E→E为0；primary每world仅取固定优先级的一对N→E。独立测试每seed仅取80个新world，三seed共用相同world簇，不计作240个独立world。T5Gemma每seed同样扫描256个world，严格规则下合格配对为0；其下一步修补指标为NA。原始分母和逐项排除计数见表A，不能将配对内恢复率称为候选池整体成功率提升。

2. 两模型16-world S0全部通过；无干预当前/下一步greedy IDs与原路径相等，no-op/self/alpha0 logits max/mean差0，encoder调用0，full donor复现donor一步，hook退出移除，padding不参与统计，诊断关闭KV cache。正式每world再复核资格与full-donor轨迹。未使用TransformerLens转换。

3. 锁定pca_k4_a1.0的独立C0=100.00%，当前exact=100.00%，R1=100.00%；相对8-seed同维同有效位置同Frobenius范数随机均值差=1.0000，95%CI=[1.0, 1.0]。同一对donor-minus-bad的共享4维方向逐memory token投影，不是4个token，也不是已命名语义特征。第二个锁定方法保留于表B及by-seed表，未按test效果更换方法。

4. 在Good上反向去除同一候选成分后，C0=100.00%，R1=0.00%。只有保持当前位置而损伤下一步的部分支持操作相关兼容性解释；token-span反向对照在discovery造成当前语义破坏，不能用作特异机制证据。随机控制的C0/C1均另报，不能隐去其一般损伤。

5. 真实编辑器是逐token仿射残差：T(h)=h+U(Vh)+b，有效位置mask后转回原dtype。差分用Delta+Delta VᵀUᵀ预测；FP32误差与BF16输出舍入误差分开列于operator表。Bias改变绝对状态，绝对读取/写入投影与bias对齐另存，不能由差分抵消宣称bias无用。关系诊断先于结果锁定定义；结果无变化时相关系数为NA，而不是零因果效应。

6. 路径诊断只在32个discovery world的固定gold共同前缀测第一语义分叉token margin。R的mediator来自修补Bad后的运行。最后一层cross-attention输出阻断/回填呈对应score变化；最后一层residual紧邻logits，完整替换的强作用本身不能识别独特语义路径。off-path维数和位置相同，但实际扰动范数不同，控制不足以证明唯一特异性。未执行decoder activation patch自由生成，因而这里报告teacher-forced读出效应/candidate causal mechanism，不宣称已证明输出恢复或完整causal circuit。

7. 所有长链只在t=0干预一次，后续不补donor、不重编码。以下完整R3/R5及Good上限与随机控制同时展示；各步endpoint、首次失败及错误分解另表，不能用末步偶然正确替代全链正确。

| sequence | method | R1 | R3 | R5 | step_endpoints |
| --- | --- | --- | --- | --- | --- |
| primary | bad | 0.0000 | 0.0000 | 0.0000 | [0.0, 0.0, 0.0, 0.0, 0.0] |
| primary | full | 1.0000 | 0.0000 | 0.0000 | [1.0, 0.0, 0.0, 0.0, 0.0] |
| primary | good | 1.0000 | 0.0000 | 0.0000 | [1.0, 0.0, 0.0, 0.0, 0.0] |
| primary | pca_k4_a1.0 | 1.0000 | 0.0000 | 0.0000 | [1.0, 0.0, 0.0, 0.0, 0.0] |
| primary | random_pca_k4_a1.0_8seed_mean | 0.0000 | 0.0000 | 0.0000 | [0.0, 0.0, 0.0, 0.0, 0.0] |
| reordered | bad | 0.0000 | 0.0000 | 0.0000 | [0.0, 0.0, 0.0, 0.0, 0.0] |
| reordered | full | 1.0000 | 0.0000 | 0.0000 | [1.0, 0.0, 0.0, 0.0, 0.0] |
| reordered | good | 1.0000 | 0.0000 | 0.0000 | [1.0, 0.0, 0.0, 0.0, 0.0] |
| reordered | pca_k4_a1.0 | 1.0000 | 0.0000 | 0.0000 | [1.0, 0.0, 0.0, 0.0, 0.0] |
| reordered | random_pca_k4_a1.0_8seed_mean | 0.0000 | 0.0000 | 0.0000 | [0.0, 0.0, 0.0, 0.0, 0.0] |

没有观察到完整R3/R5改善；结论仅为operation-specific one-step compatibility repair，不称长期稳定修复。

8. 三个可用编辑器seed均分开报告，等权seed均值不是训练随机性总体区间。N与一次R在全部256world×3seed的good/bad/mask逐元素相同；primary仅运行N，不将R视为独立机制复现。置信度NLL≤0.1 nat的保留数/弃样比例见confidence_audit，主test子集保留数见表E；多token完整候选margin阈值未被套用。T5Gemma工具等价性通过，但原始文本尾部空格/换行使N/R→E排除，不能作为科学反例。模板0为IID；没有模板OOD、跨领域或更丰富历史的确认。

9. SAE在test解封前已标SKIPPED：T5Gemma没有合格配对，双模型discovery/validation前置条件未满足；没有SAE训练或追加字典搜索。Backbone和原编辑器始终冻结。

10. 已执行S0/S1双模型三seed扫描，BART discovery/validation、discovery decoder路径、三seed锁定独立轨迹；T5Gemma无合格pair的S2–S4为NOT ESTIMABLE，SAE/额外领域为SKIPPED。Slurm拒绝增加运行中任务时限而允许pending子任务增加，真实返回码与子任务时限见ledger。若发生TIMEOUT，失败allocation与同配置缺失world恢复均累计GPU-hours；无需重做已完成world。总GPU-hours、峰值并发、全部终态以最终sacct刷新表为准；所有GPU通过唯一sbatch入口和srun。

主比较经验bootstrap在全一/全零样本上可能退化为零宽区间，这不表示总体无不确定性。仅3个固定编辑器seed、有限语法world及有特权good donor，不能推出通用语义feature、唯一circuit或无donor部署修复。

逐seed主方法表：

| editor_seed | method | n_worlds | C0 | C1 | R1 | exact_preservation |
| --- | --- | --- | --- | --- | --- | --- |
| 42 | good | 80 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| 42 | pca_k4_a1.0 | 80 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| 42 | random_pca_k4_a1.0_8seed_mean | 80 | 0.2172 | 0.0000 | 0.0000 | 0.2172 |
| 42 | reverse_pca_k4_a1.0 | 80 | 1.0000 | 0.0000 | 0.0000 | 1.0000 |
| 43 | good | 80 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| 43 | pca_k4_a1.0 | 80 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| 43 | random_pca_k4_a1.0_8seed_mean | 80 | 0.1000 | 0.0000 | 0.0000 | 0.1000 |
| 43 | reverse_pca_k4_a1.0 | 80 | 1.0000 | 0.0000 | 0.0000 | 1.0000 |
| 44 | good | 80 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| 44 | pca_k4_a1.0 | 80 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| 44 | random_pca_k4_a1.0_8seed_mean | 80 | 0.2422 | 0.0000 | 0.0000 | 0.2422 |
| 44 | reverse_pca_k4_a1.0 | 80 | 1.0000 | 0.0000 | 0.0000 | 1.0000 |

次要探索性长链差值的10,000次world-cluster CI：

| sequence | endpoint | n_worlds | estimate | ci95 |
| --- | --- | --- | --- | --- |
| primary | R3 | 80 | 0.0000 | [0.0, 0.0] |
| primary | R5 | 80 | 0.0000 | [0.0, 0.0] |
| reordered | R3 | 80 | 0.0000 | [0.0, 0.0] |
| reordered | R5 | 80 | 0.0000 | [0.0, 0.0] |



交付前仅补充文件原子发布、阶段命名防覆盖、资源刷新与CPU文件哈希核验；不重新训练、不运行新的干预、不据test重新选择。独立测试/统计的执行Python快照为 c288ad1，SHA256为4924e61a677e4902cfd649a92853a18e5080584d6ed7d66eb253220c02b156a4。完整checkpoint、来源缓存与结果的最终哈希核验见 results/FINAL_HASH_VERIFICATION.json，交付代码与历史执行哈希分别记录在run_manifest。

固定按world/seed/method排序的少量样本（完整文本、gold与预测在results/examples.jsonl，未按最高margin挑选）：

| example_type | world_id | editor_seed | method_name | C0 | R1 | R3 | R5 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| recovery | new_time_0000 | 42 | pca_k4_a1.0 | True | True | False | False |
| failure | new_time_0000 | 42 | pca_k4_a1.0 | True | True | False | False |
| reverse_damage | new_time_0000 | 42 | reverse_pca_k4_a1.0 | True | False | NA | NA |
| locked_secondary_no_recovery | new_time_0000 | 42 | read_k1_a0.25 | True | False | NA | NA |
| matched_random_current_damage | new_time_0000 | 42 | random_pca_k4_a1.0_61001 | False | False | False | False |
| donor_long_chain_failure | new_time_0000 | 42 | good | True | True | False | False |


最终核验：8,684文件/15,612,036,908 bytes SHA256全部一致，全部CPU/GPU作业已终止。观测Torch allocated显存峰值11,390,295,552 bytes（10.61GiB）；未捕获allocation峰值为NA。10项CPU检查通过，原工作区tracked内容/分支保留。实现快照3e5c3efaa466686f595d5076da092e440265661e，最终交付commit由Git日志及交付消息给出；未push。
