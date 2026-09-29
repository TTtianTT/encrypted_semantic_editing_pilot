# 既有证据与接口审计

2026-09-29。起始工作区无修改，无本批目录和相关Slurm作业；未发现适用AGENTS.md。独立分支以本地18bcf8c为起点，公共历史锚点v2=8bf6d42、v3=e1ec57b；本地包含未发布旧提交，后续远端只发布本批独立分支的新增目录，不将其他本地实验混入。

已阅读v1的PROTOCOL/REPORT/config/prepare/train/e0/semantics/evaluate_locked和manifest，v2/v3的prepare/engine/train/test/semantics/配置/采样日程及checkpoint元数据。旧逐例证据复算保存evaluation/old_evidence.json。v3新确认集G3 IID T_plus两视图均80/80、plus_plus轨迹80/80、plus3 11/80、人称→时间74/80（G1 79/80），OOD plus_plus 64/80。旧数据已影响方案，不作为本轮独立确认。v1/v2/v3全部资产哈希保存，结束核验不变。

G1覆盖源时间±3、人称仍±2并受记录日合法性约束。G2仅替换1600个T_plus出现为两步终点CE；G3同日程、同初始权重重新训练，两个阶段各0.5，每样本有效token均值的外权为G2终点token数。原子dev按全部目标token聚合NLL，600更新、每100检查、lr .001、AdamW无衰减、clip1、float32。新批只G1/G3，故不能识别“中间监督优于仅终点”这一因果比较。

复用语义schema与独立解析器，12模板家族8/4划分、状态/日期及否定规律。旧completed所有frame不得早于record_date，minus3的27/80不适用在输出前固定。模板奇偶与否定有关，OOD不是自然文本/新词泛化；标题及记录日明确呈现。未决不自动当已确认语义错误，自动评分+模型复核尚无真人标签。

接口适配：安装环境transformers 5.16.1、torch 2.11.0+cu128，T5/T5Gemma/T5Gemma2模块均可导入，无环境升级。检查安装源码：T5Gemma与T5Gemma2的encoder_outputs.last_hidden_state直接传decoder的encoder_hidden_states，cross-attention自身K/V投影发生其后；不在decoder内编辑。T5相同通过encoder_outputs路径；张量维度在运行时读取。T5Gemma2的视觉投影不是本纯文本实验的编辑位置。实际加载类、模块文件hash、模型config和特殊token由每模型manifest补充。

官方资料已核验：FLAN-T5是T5指令微调、无chat模板不等于不可用；T5Gemma2 270M-270M是预训练UL2 checkpoint；T5Gemma 2B-2B UL2 IT为指令模型，若官方tokenizer要求chat格式使用其真实模板。门控访问依赖现有权限，不自动接受许可。新模型float32/eager、包装A/B；BART复用旧sdpa和完全相同token上限。不同包装和tokenizer意味着比较对象是整套冻结接口，不能唯一归因架构或规模。

官方来源：[T5](https://huggingface.co/docs/transformers/model_doc/t5)、[T5Gemma](https://huggingface.co/docs/transformers/model_doc/t5gemma)、[T5Gemma2](https://huggingface.co/docs/transformers/model_doc/t5gemma2)、[FLAN base](https://huggingface.co/google/flan-t5-base)、[FLAN large](https://huggingface.co/google/flan-t5-large)、[T5Gemma2 pretrained](https://huggingface.co/google/t5gemma-2-270m-270m)、[T5Gemma IT](https://huggingface.co/google/t5gemma-2b-2b-ul2-it)。模型revision在CPU下载阶段固定。

本地没有L40S/A100分区，使用已获准B300q单GPU；不在登录节点做模型训练/生成。用户指定基础权重存于/dataset1/zailong/models/reference-frame-cross-backbone/，实验只保存路径与哈希。全部GPU加载/预检/失败/训练/评估计入14400秒，其中预检≤3600秒；下载不占GPU。
