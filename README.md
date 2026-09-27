# 低秩语义编辑 / 真实 CKKS 预实验

代码与实验报告：[GitHub 仓库](https://github.com/TTtianTT/encrypted_semantic_editing_pilot)。公开版本包含代码、固定数据划分、逐样本结果、匿名审查包、编辑器最佳权重和统计。HE 的可公开结果镜像在 `results/he/`；报告中 `he/trusted/` 路径指原服务器归档，明文隐状态数组和密钥材料不随仓库发布。基础模型、虚拟环境、下载论文/第三方源码及 optimizer latest checkpoint 也仅保留本地。`artifact_manifest.json` 是原始完整实验归档清单，部分列出的文件因此不在 Git 中；`PUBLICATION_MANIFEST.json` 列出此次发布文件。

数据来源、署名与许可见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。下载 BART 权重可运行 `python scripts/download_model.py`；首次运行前先创建 `models/bart-base` 目录。原服务器环境及恢复命令见下文，其他机器需建立对应依赖环境并设置可用 Slurm 分区。本地 Qwen 参考脚本的模型路径需按机器配置。

工作目录 `/dataset1/zailong/workspace/encrypted_semantic_editing_pilot`。结果、限制及 go/no-go 见 `FINAL_REPORT.md`。正式程度数据 GYAFC 未获得；实际任务是官方 StylePTB 的将来时编辑，不能称正式程度实验。

## 环境和资源

`.venv/bin/python` 是项目专用 Python3.12 环境；用 `.pth` 只读复用 `/dataset1/zailong/envs/peft-sft-lab/lib/python3.12/site-packages` 的 PyTorch/Transformers，独立安装 spaCy/评分/HE库，不修改已有环境。版本见 `environment.json`。运行设 OMP/OPENBLAS/MKL 4线程。BART-base pinned revision 与每文件hash在 `models/manifest.json`，StylePTB revision/hash/license在 `data/manifest.json`、`data/StylePTB_LICENSE`。没有访问付费API，没有上传/发布模型，也没有联系第三方。

所有GPU操作使用 `sbatch` 分配和 `srun` 启动。脚本不指定GPU编号或分区，分区由命令在查询 `sinfo` 后传入。实际先RTXq，node05因已完成进程无法被Slurm回收被DRAIN，后改B300q。默认一张，B与直接改写曾并行，各1张，总上限2。累计预算12GPU小时，HE CPU4墙钟小时；`budget.json` 用每作业父/子step最大耗时保守累计，不重复加step。已完成作业1611的取消是释放僵尸进程，不是未完成A。

## 实际运行入口

以下从本目录执行，原命令记录在 `commands.log`。数据/模型缓存已就绪，重跑无需联网。

```bash
export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4
.venv/bin/python scripts/prepare_data.py
sbatch --partition=<当前获准的空闲GPU分区> scripts/run.slurm
.venv/bin/python scripts/aggregate.py
.venv/bin/python scripts/audit_results.py

sbatch --partition=<GPU分区> scripts/gpu_task.slurm scripts/he_prepare.py
sbatch --partition=<CPU分区> --dependency=afterok:<prepare_job> scripts/cpu_he.slurm
sbatch --partition=<GPU分区> --dependency=afterok:<he_job> scripts/gpu_task.slurm scripts/he_decode.py

.venv/bin/python scripts/prepare_b.py
sbatch --partition=<GPU分区> scripts/gpu_task.slurm scripts/b_pilot.py
.venv/bin/python scripts/b_aggregate.py
sbatch --partition=<GPU分区> scripts/gpu_task.slurm scripts/direct_rewrite.py
.venv/bin/python scripts/budget.py
```

C/B均是A达到用户指定门槛后的有限扩展。初始预登记额外加入的gold内容覆盖门槛与用户推进要求存在冲突；按用户要求进行了扩展，偏差在 `preregistered_pilot.md` 追加节与最终报告明确披露，原文未覆盖。不要忽略该偏差或把自动分数当人工事实真值。

## 恢复与重现

A保存每200更新的 `checkpoints/<method>_r<rank>_s<seed>/latest.pt`（编辑器、Adam状态、数据步数）、`best.pt` 和完成JSON。数据顺序由固定seed重建；共享E/G为原始BART、未适配，只有训练部分用于编辑器拟合。相同命令会跳过完成方法及已有逐源输出；完整配置冻结在 `results/frozen_configuration.json`。checkpoint恢复不会重抽测试集。修复路径也有optimizer/RNG checkpoint，本轮未触发。B每100步保存，使用独立B目录。C逐样本保存，重启客户端会新建密钥，仅处理尚未完成样本；已有解密数值文件仍由可信端保存。不要在同目录改配置后混入旧JSONL；新科学探索应开新目录/确认集。

恢复前先运行 `scripts/budget.py`，根据剩余预算设更小 `sbatch --time=HH:MM:SS --export=ALL,PILOT_WALL_SECONDS=<余量减安全边界>`，不得将每次重启都当作新12小时额度。原始同环境实验可重现，数值完全一致不保证跨GPU/库版本成立。`scripts/budget.py` 中job列表是本轮实际ID，新提交需追加ID以正确累计。

A job1611；未启动1612取消；C准备1613、CPU1614、解码1618；直接改写1615失败（cuDNN SDPA执行计划）、1616仅禁用该后端后成功；B1617。状态与完整时间以 `logs/slurm_accounting.tsv` 为准，日志统一 `logs/slurm-<job>.out`。

## 文件与审计

- `preregistered_pilot.md`：预登记、后续有限B/C及协议偏差。
- `related_work.md` / `literature/`：指定论文与作者实现核查；不宣称新颖性。
- `scripts/pilot.py`：真实共享BART、梯度、训练、开发选择及固定测试生成；`scripts/evaluate.py`：固定独立语法/保守内容规则。
- `data/{train,dev,test}.jsonl`：5,000/363/364独立源，官方split；`data/b` 用所有变体连通分量分组并保留未见组合。
- `results/test_*.jsonl`：原输入、输出、参考、seed、配置hash、全部组件、失败及时间；`summary.csv`、`paired_statistics.json`：三seed主表与2000次源句paired bootstrap。
- `results/smoke.json`：恒等路径、因子方向、padding mask、梯度穿过冻结G、state_dict重载一致性。分母/分组检查在数据准备和聚合真实入口。
- `review/blind_review.csv`：100源、1000匿名输出（identity一次及3方法×3seed），单独 `method_mapping.csv`；**尚未人工核验**。
- `results/b`：有限单seed组合的实际样本、路径比较、额外漂移和bootstrap；不等于大规模组合泛化。
- `he/trusted`：仅可信客户端的latent、离线误差、明文输出及计时；不要当作服务器可读输入或公开包。目录权限700，但同UID实验不提供强隔离。`he/public` 仅公开模型参数、公钥/评估密钥context。私钥从未写盘或传给服务器。
- `scripts/he_server.py`：独立可执行，仅读取public目录，通过stdin/stdout接收/返回密文；`scripts/he_client.py`：生成密钥并驱动协议，`he_decode.py`：可信端使用同一个G解码。服务器不收到解密错误/接受拒绝反馈。

HE使用TenSEAL0.3.18/SEAL，N8192、[60,40,40,60]、scale2^40、TC128参数有效性检查。公开有效token数及mask，仅加密有效token，每token一密文，可信端恢复固定96位置。该长度泄漏比长度隐藏协议弱，所有三条数值路径使用相同mask。API将编码+加密、解密+解码合并计时，未伪造内部独立耗时。函数分解实际执行两次明密文矩阵乘法，非噪声模拟、非完整LLM私密推理；不声称模型参数保密、恶意安全或安全审计。

## 目标编码一致性与 Shift 收敛补充实验

协议见 [PROTOCOL.md](experiments/latent_consistency_v1/PROTOCOL.md)，分析见 [REPORT.md](experiments/latent_consistency_v1/REPORT.md)。保留原模型、固定划分与评分规则。B 在相同 600 步预算下做 λ=0/0.1 配对消融；A 的 Shift 恢复 Adam 状态继续到 5,000 步，属于额外预算的收敛诊断。测试集已使用过，本补充不作为独立确认集。

```bash
sbatch --partition=<实际获准分区> experiments/latent_consistency_v1/run.slurm
.venv/bin/python scripts/aggregate_consistency.py
.venv/bin/python scripts/report_consistency.py
```

原服务器可用同一命令续跑；`experiments/latent_consistency_v1/checkpoints/*/latest.pt` 保存优化器与进度，留在本地、不纳入 Git。完整训练会跳过，缺失或未完成的输出文件会重新生成。异机首次复现 Shift 延长训练前，须按原 A 入口生成三个 seed 的原始 `latest.pt`（仅最佳权重不足以恢复 Adam）。固定配置更改应使用新实验目录，不复用旧结果。日志位于 `experiments/latent_consistency_v1/logs/`；本次作业 1619，单 GPU、4 CPU。

直接组合人工审查包：[335对去重盲评表](experiments/latent_consistency_v1/human_review/direct_deduplicated/blind.csv)及[评分说明](experiments/latent_consistency_v1/human_review/direct_deduplicated/INSTRUCTIONS.md)。仅包含四组latent_once输出，覆盖原400条/100源；尚未人工评分。复现：`python3 scripts/prepare_deduplicated_review.py`。方法回填映射单独保存，不交给审查者。

新一轮[干净任务组合诊断](experiments/clean_composition_v1/README.md)目前仅完成未使用来源审计、待审候选和冻结/推理入口。真人任务审核与新来源方案尚未完成；没有新增训练、没有生成新评估集上的模型输出。不能把候选规则筛选当作可信数据集已建立。
