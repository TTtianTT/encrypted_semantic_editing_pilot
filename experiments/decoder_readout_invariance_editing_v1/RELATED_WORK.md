# 方法来源与实际采用情况

访问日期：2026-10-08（Asia/Singapore）。所有外部工具均为思路参考，无代码导入/安装。实际复用的是本仓库 four-domain HF/PyTorch backend、rank16 affine editor、独立 parser；branch `0b73738cf552e1ec29aa7a5db1eb1ee703804b66` 的精确文件 SHA 见 INPUTS.json / historical_file_audit.json。运行包版本锁定在 INPUTS.json（torch / transformers）；许可证遵循原仓库和依赖的既有政策，没有把论文引用当作代码授权。

| 来源 | 本轮采用 | 限制、版本与代码许可证 |
| --- | --- | --- |
| [ALTI+, EMNLP2022, arXiv v2](https://arxiv.org/abs/2205.11631v2)，[官方代码](https://github.com/mt-upc/transformer-contributions-nmt) | 区分 source memory / decoder prefix，关注value、residual与normalization | 没有复现 ALTI+ rollout；注意力权重不等于贡献。未复用代码，版本N/A；官方仓库 Apache2.0 |
| [Inseq, ACL2023](https://aclanthology.org/2023.acl-demo.40/)，[quickstart](https://www.inseq.org/en/latest/examples/quickstart.html)，[官方代码](https://github.com/inseq-team/inseq) | 逐生成token概率、对比指标思路 | 文档当前显示0.7.1，但未安装/复用，实际版本N/A；Apache2.0。模型名支持列表不能替代edited-memory接口验收 |
| [BLIP causal tracing, 2023](https://arxiv.org/abs/2308.14179) | 外部表示条件解码的替换/恢复干预 | 视觉语言模型的方法移植思路，非BART/T5Gemma现成backend；未复用代码，许可证未核验/N/A |
| [Value Zeroing, EACL2023](https://aclanthology.org/2023.eacl-main.245/) | 实际value干预与block响应 | 原论文聚焦encoder；cross-attention应用为本轮扩展，zeroing的OOD性质保留；未复用代码，版本/许可证N/A |
| [Anthropic circuit tracing](https://www.anthropic.com/research/open-source-circuit-tracing)，[circuit-tracer](https://github.com/decoderesearch/circuit-tracer) | 假设、路径干预、未解释误差边界 | 依赖预训练transcoder和适配模型，本轮不训练transcoder/SAE，不声称完整circuit。未复用代码，版本N/A；MIT |
| [Activation patching best practices, ICLR2024](https://arxiv.org/abs/2309.16042) | 多指标、干预对照与独立验证 | 共同正确两端不使用接近零分母recovery；未复用代码，版本/许可证N/A |
| [Slurm arrays](https://slurm.schedmd.com/job_array.html)，[sbatch](https://slurm.schedmd.com/sbatch.html)，[srun](https://slurm.schedmd.com/srun.html) | allocation、step和array区分 | `%2`只约束单array；外部全局锁+登记+squeue/sacct作跨stage门禁；官方文档参考，无代码复用 |

未安装Inseq或circuit-tracer；没有改变已有环境。论文不保证本仓库hook正确，S0实际验收结果决定后续是否可执行。
