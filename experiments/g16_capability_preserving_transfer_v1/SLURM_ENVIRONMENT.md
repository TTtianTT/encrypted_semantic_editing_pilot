# Slurm 环境与执行参数

提交前以 CPU 查询当前分区、资源、用户关联和活动作业，再复用 G15 已验证的环境。B300q 当时为 UP；未猜账号。用户关联查询没有返回条目，实际 allocation 记录中的 Account 为空、QOS 为 normal（照实保留）。没有取消无关作业。

下列快照是确认期间再次查询，不冒充提交前的原始输出。采集时间：2026-10-01 17:22:11 UTC。

```text
PARTITION|NODELIST|STATE|GRES|CPUS|MEMORY|TIMELIMIT
B300q|node01|idle|gpu:nvidia_b300_sxm6_ac:8(S:0-1)|256|1857537|infinite
B300q|node02|mix|gpu:nvidia_b300_sxm6_ac:8(S:0-1)|256|1857537|infinite
B300q|node03|mix|gpu:nvidia_b300_sxm6_ac:8(S:0-1)|256|1857537|infinite
```

每 allocation 恰好 1 GPU、4 CPU、64G，B300q，exclude=node01。三个 seed 显式映射 0/1/2→42/43/44，训练和确认各一个 array0–2%2，阶段不重叠。smoke15分钟、训练每seed41分钟、确认每seed22分钟；请求由完整开发/缓存/更新/确认接口 smoke 吞吐锁定，总3.40GPU小时。没有改写 CUDA_VISIBLE_DEVICES。

实际 account/QOS、raw/display JobID、起止与退出码在 allocation_details.psv/slurm_jobs.csv。GPU型号及PyTorch allocator峰值在 smoke_test.json/seed_s*_train_complete.json/seed_s*_confirm_complete.json；Slurm各step显存另存 slurm_step_usage.psv，仅用于显存核验，不重复计GPU小时。
