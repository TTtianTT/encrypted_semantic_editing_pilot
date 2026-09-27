# 有限查新记录（2026-09-27，约20分钟）

检索范围只覆盖指定原始论文、方法章节和作者代码入口，不以“没检索到”推断新颖性。没有复现下面完整系统的结果；实际复用是 StylePTB 数据/官方划分逻辑、公开 BART 权重及标准库。下载源码仅用于核查，未复制进训练实现。

| 工作 / 可访问版本 | 已有能力及核查内容 | 本轮复用 / 仍待验证差异 |
|---|---|---|
| [Extracting Latent Steering Vectors](https://arxiv.org/html/2205.05124v1)，ACL Findings 2022 v1 | 方法§2逐句优化注入冻结GPT-2的向量来恢复给定句；风格控制用均值方向。测试参考逐句优化不适用于本协议。 | 借鉴固定方向对照，不复用逐测试目标优化。作者[代码入口](https://github.com/nishantsubramani/steering_vectors) revision `ef2c4916ae6e2711ed5282e2f1ee06b71f6670ec` 实查仅 README “Code coming soon”。本轮待验证共享BART memory中输入相关线性算子相对shift。 |
| [LatentOps](https://aclanthology.org/2023.emnlp-main.1030.pdf)，EMNLP 2023 | §3训练VAE连接编码器/预训练decoder，冻结后训练属性分类器，把能量相加并通过ODE移动z，支持组合及顺序编辑。核查 `eval_sampler.py`、`lace_tst_my.py`，有latent分类器和数值采样。 | [代码](https://github.com/guangyliu/LatentOps) `096cfe78e077ceff9f507f52292619f1460c2f3f`；现README说明原SharePoint checkpoint失效。未复用模型或代码。输入相关编辑/组合并非新概念；待验证固定浅层低秩affine而非多步非线性ODE的质量与HE成本。 |
| [EPAAE](https://aclanthology.org/2022.naacl-main.34.pdf)，NAACL 2022 | §3连续embedding扰动结合离散删词，组织自编码隐空间；§6均值差方向和强度缩放。核查作者 `noise.py` 的扰动/删词。 | [代码](https://github.com/sharan21/EPAAE) `47ccca31d27ed91ecaa1186345d1eaa2554d97cd`。不把训练得到的表示叫安全加密，不复用其训练模型；本轮避免不同编辑方法分别训练隐空间。 |
| [GYAFC](https://aclanthology.org/N18-1012/)，NAACL 2018 | 平行informal/formal文本和正式程度改写评估。 | [官方仓库](https://github.com/raosudha89/GYAFC-corpus)要求邮件申请；本地data/datasets未找到已授权副本。本轮未使用、未联系作者；不能称本轮正式程度实验。 |
| [StylePTB](https://aclanthology.org/2021.naacl-main.171/)，NAACL 2021 | 细粒度操作及部分组合，仓库明确列出TFU/TPA/TPR、语态和其他编辑；并非所有组合皆有数据。 | [官方仓库](https://github.com/lvyiwei1/StylePTB) `0c24befeb80098307d7bdff6c5adaf04529fa36f`；LICENSE为CC BY4.0。实际复用 `fulldata.h16` TFU及 `single_transform_checkout.py` 顺序划分；保留原split、分组去重。其转换目标包含自动构造，真实语料上的规则转换不等于人工语义真值。 |
| [MERGE](https://arxiv.org/html/2305.15769v3)，AAAI 2024版本 | §4以embedding resending和合并/近似模块优化私密自回归推理，依赖重新训练和MPC。核查 `benchmark/encryp_decoder.py` 的CrypTen、加密模块和时延记录。 | [代码](https://github.com/liangzid/MERGE) `87d0f7217efb6c608e9e722d04d05c1a539caf98`。未运行/复用；本轮客户端承担E/G，仅潜在远端小编辑器，成本边界不同，不与完整私密LM作总成本优越性比较。 |
| [CKKS](https://eprint.iacr.org/2016/421)，原始ePrint入口 | 近似复数/实数算术，重缩放管理精度/模数，支持打包；不是文本语义算法。入口、PDF及提取文本可访问；核查重缩放/精度边界，未完成独立密码安全审计。 | 若A通过才使用成熟实现验证Enc/Eval/Dec。当前阶段不把float算术、噪声或神经表示称为加密；安全参数需库文档单独核实。 |

与本计划最相邻的是LatentOps与固定steering方向：共同的“encode–latent edit–decode”并非新颖主张。本轮只检验更受限的低秩affine在统一重构模型、相同监督下的增益；未发现完全同配置不构成原创性证据。
