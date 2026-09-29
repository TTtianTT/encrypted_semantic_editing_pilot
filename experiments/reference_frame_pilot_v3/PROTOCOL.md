# G3：逐步监督的最小验证（训练前冻结）
2026-09-29，Asia/Singapore。只新增G3 seed42，从v2 initial.pt训练600更新，batch16，四个LowRank16；BART/hash/tokenizer/float32/eval/冻结/AdamW .001/clip1/greedy/96输入/60生成上限均复用v2。v1/v2只读。不补seed、不搜索、不训练其他链或新模型。

研究问题：同一个T_plus在每次调用时能否正确移动参考日而保持事实？G2只监督终点不能证明每一步正确。既有v2测试已影响方案，称诊断集；新的160世界称确认集，IID/OOD各80，与全部v1/v2世界按完整事实键去重。生成语法与模板/状态分布保持v2。建议种子2026092903恰为v2 train种子，故训练前改为2026093003（OOD +1），记录去重与哈希。所有视图按世界划分，两步源±2、三步源±1；completed/minus3结构性不适用，模型输出前锁定分母。时间源覆盖±3，人称仍±2且受日期合法性约束。预选每层10世界匿名审查。复用hash一致的920视图校准，不重复GPU重构；新集保留规则/目标重构/同次数无编辑重构对照。

G1训练源和sample_schedule逐字复用，1600个替换出现固定。普通样本ell_j=CE1的有效token平均；链样本ell_j=.5 CE1+.5 CE2，w_j=G2终点有效token数；batch=sum(w_j ell_j)/sum(w_j)。同一H1连第一步CE及第二次编辑，H2不detach，源mask贯穿；只一次backward和step。BART解码器允许输入梯度。先用真实混合batch核验0/1与G2损失及活动算子梯度等价，再确认两条0.5路径有限非零、无BART梯度、mask/targets正确。非搜索。增加了监督token和计算，不称等FLOPs，也非唯一因果机制证明。

每100步按完整原子dev目标token加权NLL选best，与v2相同。另保存各检查点dev T_plus原子、plus_plus终点和逐例所有阶段交集，观察指标不选模。冻结checkpoint后对G1/G2/G3统一跑新确认集，复用G1/G2旧输出，仅补G3旧输出。

路径固定为六原子、plus_plus/minus_minus/plus_minus/minus_plus/plus_person/person_plus/person_return及plus3/minus3，每链latent和decode_reencode。纯链中间解码只用于诊断，计时单列。逐步按自己的frame评分，endpoint_joint与trajectory_joint分开，后者必须逐例交集。未决和未结束不成功，未决不自动当已确认语义错；已解析非日期错误单列字段与分母。T_plus按人称/offset/status分层。第一步错日期按同一frame下相对偏移比较，分类提前两步目标/原日期/其他/未决。

2000次按世界配对bootstrap，同层所有路径共享重采样索引；主差值同集合G3-G2，G1参照。只有seed42，不包含训练随机性。新IID的描述性继续门槛：T_plus原子≥95%，plus_plus全轨迹≥90%，两个时间×人称全轨迹各相对G1下降≤5pp；同时披露OOD、事实损坏、未决，不由单一门槛掩盖退化。三步没恢复不称通用组合，T_minus不变的失败不称遗忘。无真人标签，报告结构化自动检查+模型复核。

单GPU累计最多3600分配秒，使用sbatch B300q+srun，不在登录节点训练。v2整批570秒，G3与三个组新集预计小于900秒；训练作业上限900秒、评估上限1800秒，后续只在剩余预算内补缺。父/step取最大计费，等待另列。预算/信号提前保存可恢复状态，禁止自动扩时。只提交本目录，沿用已授权Git推送，不公开基础模型/凭据，latest优化器状态本地保留。
