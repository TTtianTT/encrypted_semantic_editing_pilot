# Decoder readout invariance and latent editing v1

实际执行接口，从 /dataset1/zailong/workspace/encrypted_semantic_editing_pilot/.decoder-readout-worktree 运行：

```bash
/dataset1/zailong/workspace/encrypted_semantic_editing_pilot/.venv/bin/python -m experiments.decoder_readout_invariance_editing_v1.prepare --stage S0
/dataset1/zailong/workspace/encrypted_semantic_editing_pilot/.venv/bin/python -m experiments.decoder_readout_invariance_editing_v1.submit_stage --stage S0
/dataset1/zailong/workspace/encrypted_semantic_editing_pilot/.venv/bin/python -m experiments.decoder_readout_invariance_editing_v1.collect --stage S0
/dataset1/zailong/workspace/encrypted_semantic_editing_pilot/.venv/bin/python -m experiments.decoder_readout_invariance_editing_v1.publish --stage S0
```

CPU orchestration不执行模型；run_stage只接受已登记sbatch+srun。每run终态报告/压缩记录由CPU publisher串行提交，push并核验远端SHA。协议在 protocol.yaml，真实完成状态在 STATUS.md；未执行项不计0。完整大产物位于 ignored local/，索引含SHA与重建入口。

本轮实际结果与阻塞见 [FINAL_REPORT](FINAL_REPORT.md)。S0两模型通过；BART机制为探索性局部query/memory配合；Plain三seed单操作validation1536/1536但三/五步0/256；T5Gemma32探索world一般严格pair存在。其他三训练方法NA，S4因5个test core派生暴露阻塞；没有完成完整计划。

CPU重算：`python -m experiments.decoder_readout_invariance_editing_v1.finalize`。绘图：`PYTHONPATH=experiments/decoder_readout_invariance_editing_v1/local/analysis_deps python experiments/decoder_readout_invariance_editing_v1/figures/rebuild.py`；依赖只用于绘图、不升级原环境。重新prepare S3_SELECT/S4会输出可审计阻塞状态，不能用于绕开review或test完整性门禁。
