# Artifact audit

Base: 0b73738cf552e1ec29aa7a5db1eb1ee703804b66. Branch: experiment/causal-next-edit-stability-v1. Original dirty files and worktrees are retained (exact snapshot in run_manifest.json). Fetched origin; no newer causal/patching branch found. Newer current-source compatibility branch aea8310 is audited separately; it retrains receiver editors and is not this localized intervention.

Read source README, RESULTS, DATA_SPEC, backend, evaluator, train, checkpoints_index, config, job/submit scripts; source paths/hashes and all actual backbone/editor file checks are in run_manifest.json. Frozen facebook/bart-base FP32 and original google/t5gemma-2b-2b-ul2-it BF16, HF SDPA, eval, max_new_tokens160, deterministic greedy, original tokenizer/chat wrapper/caps192/256. No backbone/editor training. Historical P checkpoint is the full-core-dev NLL selected original atomic editor (600 updates, seeds42/43/44); 96 train worlds, 24 old dev, 32 old test. All training world content excluded; 200 new worlds use same slots/rendering and disjoint core content. Old test exposure during discovery is disclosed through original_split and never relabelled template OOD.

Natural N is E(render(world,state)); edited E is a deterministic recorded operation history over the original source-position memory and mask. R is exactly one E(Decode(edited)) and labelled reencode, never an encoder-internal history. All histories stay grouped by world across seeds. Time legal states−3..3, plus decrements relative day and minus increments it; illegal boundaries stop gold construction. Original independent parser defines success as parsed target+preservation+scope+grammar+normal EOS. Other domains retain source semantics and parser, but are outside the selected time condition.

Editor: z=h.float(); delta=b+u(v(z)); output=(z+delta*mask[...,None]).to(h.dtype). v.weight rank×d, u.weight d×rank, no activation, normalization, clipping or token mixing in inference; identity residual, scale1, bias at each valid token, padding identity. Training clipping is not inference clipping. Difference propagation is affine in FP32 but BF16 casts produce rounding, which must be measured rather than called exact. Read subspace row(v), write subspace col(u). Bias cancels analytically in differences, but not in absolute state/margin.

Existing environment Python3.12.3, torch2.11.0+cu128, transformers5.16.1; no upgrades. CUDA/GPU runtime inspected only inside Slurm. B300q/gpu:1, blank account/default normal QoS verified from historical sacct; script uses existing .venv and srun. New data/configs/small results in Git; large CPU state caches, logs and complete per-example results under ignored local/.

S0实际验收见results/S0_ACCEPTANCE.json：两模型各16world全部通过。观测Torch allocated显存峰值11,390,295,552 bytes（10.61GiB），逐任务记录与缺失allocation峰值的NA见GPU_memory_observations。8,684文件/15,612,036,908 bytes最终SHA256全部一致，见FINAL_HASH_VERIFICATION。

所有领域合法变换（原semantics.advance/states，仅time在本轮运行）：

| domain | states | plus | minus | stop |
| --- | --- | --- | --- | --- |
| time | -3..3 | s-1 | s+1 | 越界ValueError，无饱和 |
| space | 0..3 | (s+1)%4 | (s-1)%4 | 旋转循环 |
| person | 0..2 | (s+1)%3 | (s-1)%3 | speaker/listener循环 |
| emotion | 0..4 | s+1 | s-1 | 越界ValueError，无饱和 |

独立parser为语义判定规范化空格/大小写，未知表达不丢弃；joint success = ended AND grammar AND target AND preserved，其中scope=target AND preserved。当前文本配对及exact preservation使用未经strip的greedy原始文本。末轮再次核实训练ID/核心render与256候选零重叠，源码/权重/缓存哈希核验通过。实际GPU型号：NVIDIA B300 SXM6 AC。

独立测试与统计执行Python为c288ad1/hash4924e61a677e4902cfd649a92853a18e5080584d6ed7d66eb253220c02b156a4；交付实现和仅工程修改在run_manifest区分。哈希审计所用旧清单保存于results/hash_audit_inputs，保留历史输入。
