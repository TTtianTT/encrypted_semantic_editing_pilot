# Decoder readout invariance and latent editing v1

实际执行接口，从 /dataset1/zailong/workspace/encrypted_semantic_editing_pilot/.decoder-readout-worktree 运行：

```bash
/dataset1/zailong/workspace/encrypted_semantic_editing_pilot/.venv/bin/python -m experiments.decoder_readout_invariance_editing_v1.prepare --stage S0
/dataset1/zailong/workspace/encrypted_semantic_editing_pilot/.venv/bin/python -m experiments.decoder_readout_invariance_editing_v1.submit_stage --stage S0
/dataset1/zailong/workspace/encrypted_semantic_editing_pilot/.venv/bin/python -m experiments.decoder_readout_invariance_editing_v1.collect --stage S0
/dataset1/zailong/workspace/encrypted_semantic_editing_pilot/.venv/bin/python -m experiments.decoder_readout_invariance_editing_v1.publish --stage S0
```

CPU orchestration不执行模型；run_stage只接受已登记sbatch+srun。每run终态报告/压缩记录由CPU publisher串行提交，push并核验远端SHA。协议在 protocol.yaml，真实完成状态在 STATUS.md；未执行项不计0。完整大产物位于 ignored local/，索引含SHA与重建入口。

本轮实际结果与阻塞见 [FINAL_REPORT](FINAL_REPORT.md)。用户16例掩码验收通过后，BART四种rank16方法三个seed均完成400updates、全量单操作validation与自己的latent1/2/3/5步轨迹。单操作Mechanism-guided4579/4608，Output-only4580/4608，Random-site4579/4608，Plain4608/4608；没有发现机制增量。两步差异随seed/方向改变，三步与五步全部0。S0两模型通过；机制仅支持探索性局部query/memory配合；T5Gemma32探索world一般严格pair存在，但独立确认不可估计。S4因编码及实际输出core暴露保持BLOCKED_TEST_INTEGRITY，原123提案撤回，正式test评测0，没有完成整个计划。最新暴露union与范围见configs/FINAL_EXPOSURE_LOCK.json（审计结束后生成）。

CPU重算：`python -m experiments.decoder_readout_invariance_editing_v1.main_results --summarize`、`python -m experiments.decoder_readout_invariance_editing_v1.trajectory_results`、`python -m experiments.decoder_readout_invariance_editing_v1.trajectory_norm_results`、`python -m experiments.decoder_readout_invariance_editing_v1.cpu_audit`。绘图：`PYTHONPATH=experiments/decoder_readout_invariance_editing_v1/local/analysis_deps python experiments/decoder_readout_invariance_editing_v1/figures/rebuild.py`；依赖只用于绘图、不升级原环境。重新prepare S4仍受独立test完整性门禁，不会自动解封或补样本。所有缓存/日志/临时目录和外部发布账本位于/dataset1/zailong/；受控GPU作业均已终态，账户其他项目作业单列，不取消。
