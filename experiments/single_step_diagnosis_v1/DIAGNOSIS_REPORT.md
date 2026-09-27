# 单步将来时编辑故障定位

**主要发现：多数已确认编辑错误仅在编辑后的路径出现，但至少一个分数报价错误也出现在不编辑的编码—解码路径。** 这将问题定位到不同计算路径，不能证明全是编辑器的问题，也不能证明BART架构不适合。

本轮在旧测试集上回溯诊断；没有训练、换模型、扫参数、组合约束或新增HE。所有语义与任务有效性评分为Codex模型复核，已接触方法及部分历史案例，**不是人工真值或独立盲评**。真人评分均空白。

## 材料与样本核实

工作起点commit `9bfafdb2bfb8b7888bb0891249d9d3b863be0c32`。从当前`data/test.jsonl`核实364条、规范化去重后364个来源，重复0；按source_id排序，Python random.Random(20260928)抽100，抽样不读取模型输出或旧成功标签。sample_manifest.json保存来源列表、样本/数据hash与算法，samples.jsonl保存x/y；所有100个来源均保留。

在新输出生成前，仅根据x/y逐项完成并冻结任务模型判断：valid75、invalid15、uncertain10，见task_validity.csv及task_review_frozen.json。无效涉及漏改并列谓词、模态堆叠、条件句机械加will及过去时间冲突；不确定主要是时间锚点、would模态及省略语境。对此分类也需真人校准。没有把输出失败换成新来源。165条新候选和clean_composition_v1冻结流程未使用或改动。

现有共同seed为42/43/44，按规则固定最小seed42。检查点SHA256与完整元数据见config.json/checkpoint_metadata.json：

| 方法 | 实际文件 | 训练预算上限 | 所选开发best步数 |
|---|---|---:|---:|
| shift | `experiments/latent_consistency_v1/checkpoints/shift_s42/best.pt` | 5000 | 4800 |
| lowrank | `checkpoints/lowrank_affine_r64_s42/best.pt` | 1000 | 600 |

**两者训练预算不等**，不能把本次差异解释为纯架构优势或性能上限。低秩rank64沿用原开发选择，本轮不重选。Shift曾续训到5000步，仍未证明充分收敛。两种编辑输出本轮重新生成，事后与相同源、相同检查点的旧结果核对均100/100文本一致，见prior_output_audit.json。

共享BART revision `aadd2ab0ae0c8268c7c9693540e9904811f36177`，本轮逐文件验证原模型manifest的SHA256；tokenizer同一目录及revision，文件hash见config.json。运行PyTorch 2.11.0+cu128、Transformers 5.16.1、tokenizers 0.23.2，CUDA 12.8，NVIDIA B300 SXM6 AC。E/G参数冻结、eval、float32。

四路径统一输入上限96、各自真实mask、greedy/beam1、不采样、max_new_tokens100、forced_eos=None；BART BOS/EOS/PAD/decoder-start为0/2/1/2。目标y仅进入目标还原及评分，编辑路径只输入x。无teacher forcing预测。前3来源及其3目标完成直接generate与encoder_outputs封装逐token一致、identity无编辑一致、mask和EOS检查。400输出均成功生成、无截断；完整配置、计时及长度在outputs.jsonl。

## 语义模型复核结果

三个维度独立评价：适用时态、意义保留、语法可读，均明确pass才联合pass。原句还原不要求将来时。目标还原对照在invalid/uncertain组不能称“正确目标”。分词空格、可辨认引语缺标点和分数转义按预登记口径处理，不因措辞不同自动失败；实际数字变化、谓词/角色错改仍失败。

| 路径 | 全100源明确通过 | 明确失败 | 联合不确定 | 固定有效75源明确通过 | 有效源不确定 |
|---|---:|---:|---:|---:|---:|
| 原句还原 D(E(x)) | 97/100 | 1 | 2 | 74/75 (98.67%) | 0 |
| 参考目标还原 D(E(y)) | 82/100 | 15 | 3 | 74/75 (98.67%) | 0 |
| Shift 编辑 | 69/100 | 19 | 12 | 64/75 (85.33%) | 0 |
| 低秩编辑 | 71/100 | 20 | 9 | 70/75 (93.33%) | 0 |

全部100源的目标还原失败15次不能理解为15次编码—解码新增错误：其中14次来自预先判无效的目标自身问题。实际新引入的重构语义错误在本次模型复核中只有S088（两个还原路径都改变分数）；S033目标还原反而补上参考缺失的be。源还原两个不确定来自原句省略语境，不能归因于编码器新增信息丢失。

| 任务有效性分层 | n | 原句还原 P/F/U | 目标还原 P/F/U | Shift P/F/U | 低秩 P/F/U |
|---|---:|---|---|---|---|
| fixed_valid | 75 | 74/1/0 | 74/1/0 | 64/11/0 | 70/5/0 |
| invalid | 15 | 14/0/1 | 0/14/1 | 5/8/2 | 1/14/0 |
| task_uncertain | 10 | 9/0/1 | 8/0/2 | 0/0/10 | 0/1/9 |

固定75有效源：低秩−Shift为 **+8.00个百分点，2000次来源paired bootstrap 95%区间[2.67, 14.67]**，统计seed20260928。两编辑器在有效源的联合不确定数为0，因此联合U的不同处理不改变此区间；但其中个别组件仍有U且另有明确fail，不能说每个维度都确定。区间只覆盖固定模型、固定本次评分下的样本不确定性，不覆盖检查点、任务有效性划分、评分者或模型偏差。

不确定敏感性（低秩−Shift；全体/任务U不是主有效源比较）：

| 分母 | 保守U不通过 | 两臂U通过 | 最不利于低秩 | 最有利于低秩 |
|---|---:|---:|---:|---:|
| all_sampled | +2.00pp [-4.00,8.00] | -1.00pp [-8.00,6.00] | -10.00pp [-19.00,-1.00] | +11.00pp [3.00,19.00] |
| fixed_valid | +8.00pp [2.67,14.67] | +8.00pp [2.67,14.67] | +8.00pp [2.67,14.67] | +8.00pp [2.67,14.67] |
| valid_plus_task_uncertain | +7.06pp [2.35,12.94] | +5.88pp [0.00,11.76] | -4.71pp [-14.12,4.71] | +17.65pp [9.41,25.88] |

全100源保守通过率范围：源还原97%–99%、目标还原82%–85%、Shift69%–81%、低秩71%–80%（右端仅将联合U作为成功的敏感性上界）。全体比较方向对不确定处理敏感，不能从有效子集的正差值宣称所有输入均占优。

## 故障集中位置

固定有效源中，两种还原均联合通过的子集为 **74/75**（占全部抽样74/100）。Shift通过64/74、失败10；低秩通过70/74、失败4，均无联合U。这个按还原结果选出的子集仅用于诊断，不能替代75有效源或100全部来源。

| 分母 | 同时通过 | 仅Shift通过 | 仅低秩通过 | 均未确认通过 | 两者明确失败 |
|---|---:|---:|---:|---:|---:|
| all_sampled (100) | 65 | 4 | 6 | 25 | 13 |
| fixed_valid (75) | 64 | 0 | 6 | 5 | 5 |
| valid_both_reconstructions_pass (74) | 64 | 0 | 6 | 4 | 4 |

完整pass/fail/uncertain 3×3交叉表见paired_outcomes.json；“均未确认”不等于双方都明确失败。有效源中Shift的11个失败有10个伴随双还原通过，低秩5个失败中有4个如此；两者余下的同一个来源S088也出现重构错误。其余有效错误集中于助动词/屈折、报告语漏改或破坏、事件及时间关系变化。本次未标出独立的明确否定翻转，不能据小样本推断这类错误不存在。分类可重叠，见failure_localization.json。

## 可核查案例

### S088

重构也失败：终价43又7/8被改为43又7/7。源还原还重复to43；编辑输出既改数字又留下过去tumbled。此例说明无编辑路径也有具体问题，不证明BART架构整体不适合。

- 原句：`goodyear tire & rubber tumbled 2 7\/8 to 43 7\/8`
- 参考：`goodyear tire & rubber will tumble 2 7\/8 to 43 7\/8`
- 原句还原 D(E(x))：`goodyear tire & rubber tumbled 2 7\/8 to 43 7\/7 to 43`
- 参考目标还原 D(E(y))：`goodyear tire & rubber will tumble 2 7\/8 to 43 7\/7`
- Shift 编辑：`goodyear tire & rubber tumbled 2 7\/8 to 43 7\/7`
- 低秩编辑：`goodyear tire & rubber tumbled 2 7\/8 to 43 7\/7`

### S072

双还原通过，编辑后事件被改：低秩把distributes变为distill（分销→蒸馏），语法和将来时可以成立，事件却不相同；Shift生成distory及重复will。

- 原句：`suntory distributes brown-forman bourbons in japan`
- 参考：`suntory will distribute brown-forman bourbons in japan`
- 原句还原 D(E(x))：`suntory distributes brown-forman bourbons in japan`
- 参考目标还原 D(E(y))：`suntory will distribute brown-forman bourbons in japan`
- Shift 编辑：`suntory will distory will will will be brown-forman bourbons in japan`
- 低秩编辑：`suntory will distill brown-forman bourbons in japan`

### S061

双还原通过，Shift删除报告事件并将Harold Simmons从引语说话者改为兴趣对象。低秩保留报告形式但在名字前插will，不能因大部分词保留就判成功。

- 原句：`i 'm not interested said dallas investor harold simmons`
- 参考：`i will not be interested will say dallas investor harold simmons`
- 原句还原 D(E(x))：`i 'm not interested said dallas investor harold simmons`
- 参考目标还原 D(E(y))：`i will not be interested will say dallas investor harold simmons`
- Shift 编辑：`i will not be interested in dallas investor harold simmons`
- 低秩编辑：`i will not be interested will say dallas investor will harold simmons`

### S010

双还原通过，Shift给出will apparently will not like，重复助动词导致语法失败；低秩保持正确未来否定。

- 原句：`investors apparently did n't like the news from rainbow technologies either`
- 参考：`investors apparently will not like the news from rainbow technologies either`
- 原句还原 D(E(x))：`investors apparently did n't like the news from rainbow technologies either`
- 参考目标还原 D(E(y))：`investors apparently will not like the news from rainbow technologies either`
- Shift 编辑：`investors will apparently will not like the news from rainbow technologies either`
- 低秩编辑：`investors apparently will not like the news from rainbow technologies either`

### S035

任务预先判invalid：参考遗漏formed的未来转换，目标还原复制这个错误。Shift反而给出will get… and will form；低秩复制错误参考。此例不计入主有效源比较，也说明参考一致不等于正确。

- 原句：`mr. vinson the professor got the law bug and formed litigation sciences`
- 参考：`mr. vinson the professor will get the law bug and formed litigation sciences`
- 原句还原 D(E(x))：`mr. vinson the professor got the law bug and formed litigation sciences`
- 参考目标还原 D(E(y))：`mr. vinson the professor will get the law bug and formed litigation sciences`
- Shift 编辑：`mr. vinson the professor will get the law bug and will form litigation sciences`
- 低秩编辑：`mr. vinson the professor will get the law bug and formed litigation sciences`

## 解释边界与下一步

正确目标还原成功只说明该目标自身编码能够被当前解码器处理；不是数学上界，也不证明编辑器可达到该表示。双还原通过而编辑失败把故障定位到编辑后的路径，但可能是算子改变的表示与解码器交互，不可断言全是编辑器或全是解码器。没有跨backbone对照、新多seed训练或新HE；历史16/16密文执行一致与本轮语义正确无关。

**下一项只建议固定检查点的输入规范化配对诊断**：对本轮分数转义与引语/报告语来源，由真人确认仅补标点、去数据转义而不改变含义的版本，与原样输入重跑同四路径。它直接检验分数及报告语错误有多少受输入格式影响；不以旧失败源的改善冒充独立泛化，不先换BART或追加一致性训练。本轮到此结束，不自动运行该实验。

## 用量、复算与材料

Slurm作业1621已COMPLETED，单GPU分配46秒（0.01278 GPU小时），脚本计时9.323秒；二者口径不同，预算按完整作业计。峰值allocated显存0.626 GiB、reserved 0.670 GiB。4 CPU线程。没有仍在运行的作业，累计GPU用量0.35806小时。

```bash
# 保留现有抽样及评分，不重新运行prepare覆盖记录
sbatch --partition=<当前获准GPU分区> experiments/single_step_diagnosis_v1/run.slurm
python3 scripts/export_single_step_review.py
OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 .venv/bin/python scripts/score_single_step_diagnosis.py
python3 scripts/report_single_step_diagnosis.py
```

prepare_single_step_diagnosis.py负责从当前文件新建固定抽样，已存在manifest时拒绝覆盖。模型语义判断本身不是可用代码重新“证明”的真值；score脚本只把已记录的逐条模型判断展开并统计，改变评分须另建版本。outputs.jsonl共400条，review_blind.csv为400条空白评分材料，method_map.json单独保存；model_review.csv包含实际模型复核、时间和输出hash，所有human字段为空。task_validity.csv保留100条任务判断及理由。

精确源还原98/100、精确目标还原97/100仅作辅助。S001删除分数反斜杠并不改变数值，因此语义通过；S088则改变真实分数。旧auto及各维度统计见auxiliary_exact_and_old_auto.json/summary.csv，不能据旧auto95/100目标还原联合值掩盖坏参考。
