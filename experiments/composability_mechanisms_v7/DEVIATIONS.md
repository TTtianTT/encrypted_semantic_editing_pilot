# DEVIATIONS（composability_mechanisms_v7，计划 v8 的 C 线）

全部条目均在锁定前，除非另行注明。

1. **2026-11-25，计划变更：新增探索性单元 E1、E2（负责人阶段 2 指令第 5 节）**。原文已附在 `PLAN.md` 末尾。两者都是探索性单元，不参与 Q24–Q26 的判定。

2. **2026-11-25，模板 0 的数据沿用 v6/v7 的 confirm 集（负责人阶段 2 指令第 1.4 节）**。
   - G 单元（T5Gemma 9B-9B）与规模阶梯（B-B、L-L）的 weekday、month 模板 0，沿用 v6 confirm6 = v7 confirm7 的 160 个 world；train/dev 沿用 v1 的原划分。
   - 原因：模板 0 的组合空间（1080 种文本）已用尽（v7 DEVIATIONS #4）。
   - 文本沿用，但对这些模型是首次评测：v1–v7 从未用 9B-9B、B-B、L-L 编码或解码过任何文本。

3. **2026-11-24/25，自然文本的来源只用 WikiText-103 的 train 部分（B.1；锁定前）**。
   - 集群上已有的是 v1 下载的 train parquet（2 个文件，SHA256 记录在 `local/natural_candidates_summary.json`）。
   - 按文章 60/15/25 划分的对象是 train 部分的 29,444 篇文章，没有用 valid/test。
   - 候选句（步骤 1–6、8）：train 池 43,930，dev 池 11,230，confirm8 池 18,829。重建闸门（步骤 7）在锁定前的 GPU 作业中进行。

4. **2026-11-24，模型下载（C1；在 v7 运行期间，不占 GPU）**。
   - 下载的模型：
     - `google/t5gemma-9b-9b-ul2-it`（revision b894e16b…，40.7 GB）；
     - `google/t5gemma-b-b-ul2-it`（72899bc3…）；
     - `google/t5gemma-l-l-ul2-it`（ddd0c8a6…）；
     - `google/gemma-2-2b-it`（299a8560…）。
   - 三个 T5Gemma 尺寸都有 UL2-IT 版本，没有用 prefixLM 的替代。
   - 每个文件的 SHA256 记录在 `local/model_manifest_v8.json`；该清单会复制到 `data/` 中入库。
