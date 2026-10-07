# Decoder readout invariance and latent editing v1

实际执行接口，从 /dataset1/zailong/workspace/encrypted_semantic_editing_pilot/.decoder-readout-worktree 运行：

```bash
/dataset1/zailong/workspace/encrypted_semantic_editing_pilot/.venv/bin/python -m experiments.decoder_readout_invariance_editing_v1.prepare --stage S0
/dataset1/zailong/workspace/encrypted_semantic_editing_pilot/.venv/bin/python -m experiments.decoder_readout_invariance_editing_v1.submit_stage --stage S0
/dataset1/zailong/workspace/encrypted_semantic_editing_pilot/.venv/bin/python -m experiments.decoder_readout_invariance_editing_v1.collect --stage S0
/dataset1/zailong/workspace/encrypted_semantic_editing_pilot/.venv/bin/python -m experiments.decoder_readout_invariance_editing_v1.publish --stage S0
```

CPU orchestration不执行模型；run_stage只接受已登记sbatch+srun。每run终态报告/压缩记录由CPU publisher串行提交，push并核验远端SHA。协议在 protocol.yaml，真实完成状态在 STATUS.md；未执行项不计0。完整大产物位于 ignored local/，索引含SHA与重建入口。
