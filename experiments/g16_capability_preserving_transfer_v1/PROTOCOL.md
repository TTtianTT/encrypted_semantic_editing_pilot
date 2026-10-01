# G16运行前协议：能力约束固定来源修复与留出迁移复验

基准155cd8793d2f83d21c0f567e45073d845753ad6f，独立experiment/g16-capability-preserving-transfer-v1。仅N/F各seed42/43/44，共6条固定200-step训练；F-final与F-guard同轨迹，N仅final200。初始化P为G13 F3 final200，G为Original T0，U为G13 F2 final200，不从G15修复模型继续。精确manifest路径/SHA，BART-base revision/tokenizer/renderer/scorer/环境只读继承G15。rank16 b+UV，AdamW lr0.001/wd0/clip1，FP32/TF32 false、96padding、greedy beam1 max_new60 forcedEOS null，四块各8实例、有效target-token平均CE等权0.25。无O、搜索/新优化/探针/架构/新语义域/三步以上自身自由链。

先CPU读取G15所有N/F/O的100/150/200 train/dev逐cell/NLL/保护/固定D/旧维护和1–100/101–150/151–200每步loss/token/schedule/状态日志。若确定标签/状态流/任务有效性错误则停止新科学运行。没有梯度冲突观测就记录未测量。小诊断不能作为step150完整确认成功，不重测旧step150 U、不替换G15主结果。审计不用于调G16参数/阈值。

G16新数据主seed20261001，以g16 namespace SHA256叶子子流隔离split/status/round/shuffle/replay/bootstrap；真正调用及预定analysis叶子写入leaf_seeds.json。每status train512/dev128/IID160/template_OOD160，总2880，train1536/dev384；确认每split480世界中只有160plan用于来源/自身链，其余仅自然原子。模板0–7 vs8–11、极性支持与词汇/合法范围继承。全部事实FIELDS（模板不属于事实身份）和所有合法日期/人称渲染去重，复用G15已有来源清单并补G15全部世界；共享变体不跨split，不输出驱动补样，不能声称可访问清单之外全历史无泄漏。T_plus推进view_date一天，事件/record_date及非日期事实保持，gold用frame/render/advance而非字符串替换。

A=T(E(tomorrow))->today；B完整40合法cell均衡循环，无失败cell加权；C原G昨日H0/H1/H2->two days ago，均衡轮换；D仅N=E(today)、F=frozen P(E(tomorrow))->yesterday。每组6400实例，每步NF同世界/目标/token/顺序/旧来源，唯一差别D memory。E/D/P/G冻结，decoder训练forward保持memory梯度，A保留梯度，P缓存no_grad且完整FP32 token memory/mask/IDs不变；没有重编码、当前T刷新、gold reset或来源标签输入。每次A真实自由输出及D真实缓存当前输出均记录，不丢错误T第一步。NF独立全新optimizer和参数存储，RNG/optimizer/step/schedule保存恢复，重试不重复计数。

训练前每seed固定P-today和旧G-yesterday门槛，G15当前全文/exact/联合/EOS/历史前缀、H0-H2 mask控制规则不变。P训练集合<128入口失败，旧集合单列，投影schedule在任何T更新前固定并NF共用。U不用于train/dev集合。

候选固定25/50/75/100/125/150/175/200，step0仅基线。dev全部128plan及各status128世界，40-cell全部自由评估；N监测自己的自然D，不选择另一版，不看P/U未监督接收。F监测固定P D，不将它冒充更新自身第二步。train固定hash32plan与每status16atomic，只在0/50/100/150/200诊断、不参与选择。监测前后恢复Python/CPU/CUDA RNG；单测与GPU smoke比较插入监测后的下一输入/optimizer更新。

F候选必须同时：dev40-cell macro>=98%、每cell>=90%、旧all3>=90%、自身第一步A>=90%、固定P下一步D>=90%；旧C和P当前匹配各n>=64。使用原始整数与精确比例，缺值拒绝、不舍入；当前门槛不依赖next。选择最早合格t，立即只写一次selection_sSEED.json（t/SHA/每项计数），继续训练至200。没有候选则selected_step null，guard选择失败，不fallback。阈值是经验工作标准，基于G15设计，不是独立盲设计/非劣效性证明。U、G-today续步、确认输出、更新后自身第二步绝不进入开发选择。

全部3seed的6条训练完成、6个final SHA和3个选择汇总锁定后才开始任何新确认/加载U，训练与确认分开array且不重叠，不在GPU上等待其他seed。Q=P/N-final/F-final/存在时F-guard；guard=final同SHA复用推断。只评估这些版本，不将所有候选在U上遍历。U是G15已经公布过的同一补训留出生产者的新世界复验，不是研究全程从未考察的家族。

确认固定来源E(today)、P/G/U分别从相同E(tomorrow)编辑一次。完整当前全文正确/exact、EOS/事实及P/G/U相同mask形成共同C，自然重构纳入既有gate，自然mask单列、不替换、不因mask不同丢编辑来源；先锁C再调用Q，不看Q第一步/next。未匹配全保留，不补样；raw160、conditional n、gate-and-next均报；n<40探索性、0为NA。U为主要迁移，P为F已监督输入，G-today仅历史恢复边界。

Q自己的Q(Q(E(tomorrow)))只有两次编辑，raw160，first/endpoint/full/exact/首次失败各报，不插P/U/自然/gold reset。自运行第二步未参与G16开发选择，但任务概念并非新长度/新任务。旧H2构造及固定续步仅维护，非新自身三步链。重编码仅单列控制E(实际自由输出)，包括错误当前输出；相同正确全文时核对token/mask/memory一致，重复不当独立证据。

IID逐seed能力macro>=98%、每cell>=90%、旧all3>=90%、own full2>=90%，U对P/N配对改善为正；额外U>=90%为本轮高成功工作目标。只有3seed逐一达成且配对方向/区间支持才称三seed同时达成，缺guard/覆盖不足/cell失败不以均值掩盖。OOD相同指标逐seed公开，非IID标签的替代。主要比较F-final−N-final（等200步来源对照）、guard−final（同轨迹检查点选择）、guard−N/P（两个因素）；所有完整F训练算力计入，不宣称节省训练时间。

每seed原始计数先于3seed mean/sample SD；2000次split内共享世界paired bootstrap跨Q/来源/seed同步抽样；原子按status分层整个世界抽样，16/40+16/40+8/40保证40cell等权。空cohort NA，空draw计数省略，不改变分母。Wilson各二项比例含0/1，退化bootstrap不等于总体无不确定性；world CI不包含完整训练或选择随机性，不作480独立训练。12个事前hash世界，每seed/split2个，展示同世界所有版本；实际失败按明示hash首例事后描述，空类明示；自然/日期/非日期事实/解析未决分别保留，不用单个overshoot解释全部失败。

所有GPU含smoke/cache/model-forward/诊断/确认均sbatch+srun，检查allocation和step变量。每作业1GPU、全轮峰值2，只有一个active阶段array0–2%2，显式index→42/43/44；不覆盖CUDA_VISIBLE_DEVICES，不取消无关作业。提交前CPU核验B300q资源，实际默认account/QOS在allocation记录；不升级环境。顺序CPUaudit/data/lock/tests→单卡smoke完成通过→train array→CPU选择锁→confirm array→CPU聚合/Git。按[官方数组文档](https://slurm.schedmd.com/job_array.html)、[sbatch](https://slurm.schedmd.com/sbatch.html)、[srun](https://slurm.schedmd.com/srun.html)实现，仅借操作语法。

硬预算实际与累计申请均<=14400 GPU秒，包括失败/重试。smoke申请900秒，测cache16/cache128、完整5760-record dev、更新、848-record train-only final-interface吞吐；此structural控制的U/G槽明示为P占位，不加载U，不是科学U推断，不访问新确认。资源申请按完整规模线性组件、锁定1.6安全因子及startup/IO估计，预留600GPU秒工程补评估；若申请+预留超预算则不启动任意缩小组/不扩预算。安全时间检查、原子输出与optimizer/RNG恢复；仅确定工程故障可重试，结果不好不得重跑。allocation级sacct排除batch/extern/steps，raw/displayID、型号/时段/退出/显存allocator峰值和并发计入资源表。失败完整峰值不可得时标明，不编造。

科学锁含本轮代码/配置/数据/schedule/关键审计、依赖及checkpoint SHA，训练选择新记录只按预定规则追加；操作/工程偏离独立记录，不能回写科学方案。只stage本轮目录，小final/guard编辑器上传，候选/optimizer/大型FP32/cache/base/env留本地，实际路径/SHA清楚。普通commit/push独立分支，核验本地/远端SHA；完整实验与科学目标达成分开，负结果照实交付，不自动扩展。
