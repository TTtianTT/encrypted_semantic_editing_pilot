# S3 regularizer acceptance — BART seed42

COMPLETED；Slurm3041_0；allocation GPU-hours 0.023333，累计2.415833，峰值2。只使用8个固定train world、自然/历史来源各4；用户16例人工抽查已确认并记录SHA，独立test评测0、原test完整性阻塞保留。

三方法各120update overfit：Output-only、Mechanism-guided、Random-site均8/8联合成功。三组从相同identity初始化；先独立两次CE warmup的gradient probe随后重置，不影响overfit或正式训练初始化。

独立KL编辑器梯度norm0.0858277082；真实L5机制项0.1119370908、随机L0项0.0145638026；CE梯度0.7908864617。全部有限且非零；teacher logits/readout无梯度、student readout保留梯度；探针每例5个保护token，排除pad和日期；机制hook退出后清理。backbone/history前后SHA相同且无参数梯度。完整逐步loss与24个预测压缩提交，数值从完整预测重算。

Output-only总loss0.453118958→0.001026490；Mechanism-guided→0.001668136；Random-site→0.001300838。仅train验收，不是方法效果确认，也不能由三者8/8推断机制增量价值。正式S3候选网格、validation选择与三个seed仍需执行；Plain完成checkpoint/原始H-mask缓存将按SHA复用，避免重复编码/训练。
