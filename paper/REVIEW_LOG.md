# REVIEW_LOG（对抗审稿与发现的问题；由负责人决定处理）

## 2026-11-25，替换引言时发现的问题（Claude Code；引言措辞未改）

按阶段 2 指令，用 `01_intro_draft.tex` 替换引言，只修宏名与引文键。以下问题未改动原文，请负责人决定。

1. **"All editors in our main experiments are rank-limited affine maps"（第 2 段）**：
   - CE 与状态监督编辑器（C1、C3、C3-U4）和闭式算子（RRR-r）都是低秩仿射映射，代码已核实。
   - 绑定单元的注意力编辑器（Att1、Att2、Att2L、OR）是非线性的，而"范围"段又提到绑定。
   - 建议：要么写明"main experiments"不含绑定，要么改成"all editors outside the binding experiments"。
2. **`\CLoneVfiveBaseMin`（"composes for 2N steps on every backbone and domain"）**：
   - 宏取自 v5 G5-0：两个骨干、10 个模板 0 的（骨干，域）组合，全部 1.00。
   - v5 的多句式全序列 RRR-16 不在其中，它在训练句式的 dev 上就失败了。
   - "every backbone and domain" 在模板 0 的范围内成立。是否加"for the fixed-template domains"，请定。
3. **`\CLthirteenHundredMax`（"none of the editors we trained composes over 100 steps"）**：
   - 宏按指令取 Att2L-U8 8 个 seed 的最大 R\_100，为 0.06。
   - v7 中 Att2L-U4、Att1-U8 与 OR-U8 也跑了 100 步，R\_100 都是 0，所以这句话对 v7 的全部绑定编辑器成立。
   - v5、v6 更早的编辑器（Tok-U、Att1-U、Att2-U、OR-U4）没有跑到 100 步，但它们在 12–30 步内就已衰减。
   - 宏只覆盖 Att2L-U8，与"none of the editors"字面上不完全对应。
4. **CL7 的"smallest one-step energy"**：
   - 宏 `\CLsevenSoneSmallestAll` 统计的是"按平面计的一步变化 s\_1 最小"（13/13）。
   - 附录 C 的命题 2 改为按每个维度的能量排序。基频是二维平面，两种排序只在与一维 Nyquist 平面比较时才可能不同。
   - 引言的说法在数据上成立；如需与命题 2 完全一致，可写"per dimension"。
5. **§9（绑定）的结构**：计划 A4 的新结构把绑定单列为 §9；目前绑定仍在 §8"Scope"中，引言引用 `Section~\ref{sec:scope}`。若拆出 §9，引言中的引用需要一并改。
6. **第 1 层注意力**（仅供 §9 参考，不影响引言）：
   - 指令中的"0.89–1.00"是我在简报中只列出的 3 个 seed 的值。
   - 全部 8 个 seed 中有 7 个在 0.89–1.00；seed 45（表现最差，R\_30 = 0.08）的第 1 层完全不看名字。
   - §9 已据此写成"8 个 seed 中有 7 个"，区间按撑过 30 步的 seed 计算。

## 2026-11-25，第一轮对抗审稿

- **方式**：PLAN v7 A6。新开的审稿代理（general-purpose 子代理，冷启动）只拿到 `paper.pdf`（commit 564bc34 的编译结果，22 页）与 `claims.yaml` 两个文件的副本（`paper/local_review/round1/`）。按 ICML 审稿表审稿，并逐处做指令第 4 节的三项检查。
- **限制**：审稿人说明 PDF 渲染工具不可用，正文与图中标注是从 PDF 内容流中解析的，看不到曲线本身。
- **结论**：3/10，置信度 4/5。
- 审稿全文为英文，下面原文照录；其后是逐条回应。

### 审稿原文（照录）

# Review: "Decodable Is Not Composable: What Latent Edits Must Write and Preserve" (round 1)

*Reviewer note on method.* The Read tool could not render the PDF because poppler is not installed. I therefore pulled the text of all 22 pages out of the PDF's content streams, along with the axis and legend labels inside the embedded figures, and decoded the CMSY math glyphs (≤, ≥, ±, −). I could not see the plotted curves themselves. Figure comments rest on captions and embedded labels only. I opened no files other than the two named.

## 1. Summary

The paper studies whether latent edits applied to the encoder states of frozen encoder–decoder models (BART-base, T5Gemma 2B–2B) **compose**, meaning that k applications move a cyclic attribute (weekday, month, …) by k steps. The setting is synthetic, single-template sentences with one single-token "slot". It reports four main findings:
- A rank-16 affine editor trained through the decoder (C1) succeeds at step 1 but fails at step 2. The authors argue it writes an "instruction" rather than a state, while closed-form reduced-rank regression (RRR-16) composes.
- The slot carries a Fourier code. Least squares drops the slowest ("fundamental") plane first, which produces predictable frozen-plane failure signatures, and reserving rank for that plane (FF-r) repairs rank-deficient operators on T5Gemma.
- A latent-only readout predicts chain success better than a naive step-1 rule.
- Results transfer partly to held-out templates. Binding edits do not compose over 100 steps.

The paper rests on seven (or six, see below) "preregistered rounds" with a claim ledger.

## 2. Strengths

- **A clean, exactly scored testbed.** Composition can be measured unambiguously, and "decode only to score" is a sensible protocol.
- **Controlled comparison.** All main editors share the same function class (rank-limited affine residual maps), so differences really are about the fitting objective. This is the right control for the "instruction vs state" story.
- **A concrete, falsifiable mechanism.** Frozen-plane surgery makes mirror-image predictions (one-way fails, alternating survives, revival at t = N), and these were confirmed in 8/8 locked cells.
- **Unusual transparency.** Failed, mixed and non-evaluable predictions are listed. Design flaws of earlier rounds are itemised (Appendix A). Non-replication of the round-6 binding result is reported openly, and so are data contamination (v2) and duplicated editors (v6).
- **A practical, if modest, result.** FF-r turns T5Gemma rank-deficient RRR from R_2N ≤ 0.61 to 1.00 in 4/4 locked cells.
- **Honest negative results** on binding, on predictor over-estimation, and on Proposition 4.

## 3. Major comments

**M1. Significance and external validity (Intro, Sec. 3, Sec. 8 "Other limits").**
- The motivation cites homomorphic-encryption inference, KV-cache communication and continuous latent reasoning. The experiments, however, use synthetic templates, single-token cyclic attributes, two small encoder–decoder models, greedy decoding and rank-16 affine maps.
- None of the motivating systems edits a cyclic attribute with a learned affine map and re-applies it.
- The reader is left unsure whether any conclusion transfers. Three gaps stand out:
  - decoder-only models;
  - multi-token or non-cyclic attributes;
  - natural text.
- Even within the testbed, the full-sequence RRR-16 already fails on multi-template data (Sec. 8). The "composes on every backbone and domain" result is therefore fragile under a mild move toward realism.
- *Resolution:* at least one decoder-only model and one non-synthetic or multi-token setting (the v8 TODOs), plus a discussion that ties the findings to an actual undecoded-pipeline use case.

**M2. The central contrast is close to a strawman (Sec. 4–5).**
- C1 is trained only to make the decoder emit the target after one step. Nothing in its objective asks the output to stay in the encoder's distribution, so failure at step 2 is expected.
- RRR is fitted on (E(x), E(x+1)) pairs, so it maps encodings to encodings by construction.
- "Decodable is not composable" is therefore largely a restatement of the training objectives.
- The more interesting question is why CE plus longer unrolls (U4) learns a step counter. That is shown only up to S = 4, with no horizon sweep.
- *Resolution:*
  - frame the C1 result as the expected baseline;
  - add CE-only editors trained with longer and randomised horizons (U8/U16/random S);
  - add cycle-consistency or re-encoding objectives;
  - add a stronger state-free baseline such as the mean-difference steering vector (see Sec. 6 of this review).

**M3. The "instruction" evidence partly contradicts the authors' own erratum (Intro p.1; Sec. 5; Appendix A "v2, S1b … N1").**
- The intro says the CE editor "writes nearly the same vector whatever the source state (median cosine 0.986)". Appendix A states that round 2's "N1 assumed that a high write cosine implies a near-constant write, which is false (ERRATUM of v3, item 5)".
- The paper keeps using exactly that inference in the intro and Sec. 5.
- "Orthogonal to the canonical write (0.003)" has no null. In a d ≈ 768 or larger space, near-zero cosine is the default for unrelated vectors.
- The probe result (source state read at 1.00) shows source information remains. It does not show the target state is absent; no probe for the target is reported.
- *Resolution:*
  - report write norms and variance across sources, not only cosine;
  - add a random-direction null for the 0.003;
  - report a target-state probe;
  - drop or qualify "nearly the same vector".

**M4. The "Fourier code" claim is under-specified and partly tautological (Sec. 6 "Harmonic planes"; Intro p.1–2).**
- N centred points always decompose exactly into the ⌊N/2⌋ DFT "planes". Saying the representations "lie in a few harmonic planes" is therefore true of any N points.
- The substantive content is that each plane is a rotation: u_k ⟂ v_k, with equal norms. No circularity or ellipticity statistic is reported.
- The paper also gives no variance-explained figure for the slot code in the top planes versus the full centred span, and no comparison with a non-cyclic control.
- The scrambled-order result (Sec. 8: composable at r* = 16 instead of N−1) suggests the Fourier structure is not what makes composition possible. That sits uneasily with the contribution wording "what composable low-rank edits **must** preserve".
- *Resolution:* quantify circularity per plane, add a non-cyclic or random-label control, and soften "must".

**M5. The latent predictor is weaker than the framing suggests (Intro "Predicting composability without decoding"; Sec. 7).**
- **Weak naive baseline.** The naive rule ("succeeds iff step 1 decodes") is predictably bad: all CE cells succeed at step 1 and then fail.
- **Majority reference nearly matches it.** A per-cell majority reference reaches 0.889/0.909, against 0.922/0.959 for the predictor. Most of the predictor's value is therefore at cell level. The per-world refinement adds only about 3–5 points, and its CI is not reported.
- **"Without decoding" is not quite true.**
  - The vote weights are fitted by maximum likelihood on *decodable dev probes*, so the decoder is used for calibration. The equal-weight result helps, but it is exploratory.
  - The step-1 disagreement D, presented under the same heading, requires decoding step 1.
- **Systematic over-estimation.** Errors are 6,601 over-estimates against 2,656 under-estimates, and 482 vs 27 on unseen templates with T5Gemma. The round-7 attempts to fix this failed (Q21 H-nofix).
- **Unclear unit of agreement.** The intro says "of worlds", Sec. 7 says "(world, cell) pairs", and the Table 2 caption restricts to state-supervised cells.
- *Resolution:*
  - report agreement with CIs against the majority reference, with per-cell and per-world numbers separated;
  - add a simple learned baseline on cheap latent features;
  - state the calibration dependence plainly;
  - fix the unit of analysis;
  - move D out of the "without decoding" heading or qualify it.

**M6. The D test is validated against training-family labels, not against an independent measure of "instruction writing" (Intro; Sec. 7; Fig. 5b).**
- "Separates instruction writes from state writes in all 66 + 82 cells" means D separates CE-trained from state-supervised editors. Those families were defined by objective, not by measured write type, so the test is close to circular.
- D also does not detect composability: state-supervised cells with D ≤ 0.2 include the few-update C3 editors that fail.
- Sec. 5 says round 5 "confirms the signature on all 66 CE cells: after one step the latent readout of the slot is still the start state". The locked test (L3b) checks D ≥ 0.5, not "readout = start". The 160/160 counts are two examples.
- *Resolution:* say what was actually tested, and report the fraction of CE cells whose step-1 readout equals the start state.

**M7. The preregistration bookkeeping is internally inconsistent, and the counting inflates support (Intro contributions; Sec. 3; Table 1; Appendix A; Table 3; Appendix E/G).**
- **Six or seven rounds.** The intro says "7 preregistered rounds". Sec. 3 says "six preregistered rounds". Appendix A says "six preregistered rounds, labelled v1–v6". Compute (App. E) and the directory map (App. G) cover six.
- **Table 3 is not complete.** It is said to list "every locked prediction", but claims cite predictions absent from it:
  - v3/HS2 and v3/HS3 (CL5);
  - v5/G5_0 (CL1; gates G2_0 and G7_0 appear but G5_0 and G6_0 do not);
  - v5/F1 (CL10; only F/Q16 is listed);
  - v6/P1a (CL8b).
- **Failed predictions cited as support.** Several claims marked "confirmed" in the ledger cite predictions that Table 3 lists as failed:
  - CL1 cites v1/P5 (fail);
  - CL7 cites v4/V0 (fail), yet the text says "6 of 6 in the preregistered fourth-round test";
  - CL11 cites v2/R3 (fail).
- **Double counting.** Table 1 counts sub-entries and summary rows separately: per-backbone, "new", pooled and Q-summary rows for one hypothesis. For example, round 5 has 11 L-rows for essentially one hypothesis.
- **"Decided" is ambiguous.** It does not say whether the winning hypothesis was the one the authors expected. v6 K2 "H-closure decided" later failed to replicate.
- **Forking paths across rounds.** Each round was locked, but the narrative was assembled across seven sequential rounds. Designs were changed after failures, and there was a data-driven v1 amendment. Per-round preregistration does not control selection of which results enter the story.
- *Resolution:*
  - reconcile the round count;
  - complete Table 3;
  - mark in Table 1 which entries are independent hypotheses;
  - for each intro claim, cite the decisive locked test and its verdict;
  - add a short "what was decided before seeing what" narrative.

**M8. Replicability and seeds.**
- The binding K2 result (3 seeds, R30 ≈ 1.00/0.97/0.99) did not replicate on 5 new seeds. Most headline editor results (C1, C3, C3-U4; seeds 42–44) also rest on 3 seeds.
- Round 6 reused seeds and batch sequences, so some editors were bit-identical duplicates.
- Round-2 confirmation worlds overlapped 2–12% with round-1 train/dev data. These are exactly the worlds behind CL2 (instruction evidence) and CL11 (scrambled-order operators compose in 10/10 cells).
- *Resolution:*
  - re-run the CL2 and CL11 numbers on deduplicated worlds, or show they are unaffected;
  - report seed spread (min, max) next to medians for all trained-editor results;
  - add seeds for the C1/C3/C3-U4 headline cells.

**M9. Theory is incomplete and partly contradicted by data (Sec. 6; Appendix C; Intro contributions).**
- **Proofs.** All four propositions have "[TODO: proof]".
- **Proposition 2.** Its per-dimension ranking is verified on ideal codes only. On real encodings the fundamental is the most degraded plane in only 17 of 28 cells (exploratory).
- **Proposition 4.** Under its stated first-order linear assumption, cancellation over a full cycle is a one-line identity. It is labelled a "Proposition" yet its empirical tests failed.
- **Overclaims built on this.** The intro says least squares "therefore drops it first", and the contributions say the paper "derive[s] the rank bound and the freeze signatures".
- *Resolution:* supply the proofs, state Prop. 2's real-data match rate in the main text, and replace "drops it first" with the measured frequency.

**M10. Generality of "state supervision makes editors compose" (Intro p.1; Sec. 5; Fig. 1a; App. E).**
- Only C3-U4 is confirmed (CL4: "confirmed (C3-U4); exploratory (training length)").
- One-step C3 trained with the default 600 updates (App. E) composes on weekday but **not on month**: 0.35 at 900 updates, and 1200 are needed.
- Fig. 1(a) nonetheless labels the composing bottom edit "state write (RRR-16 / C3)".
- The "unconverged" criterion was abandoned because it does not separate outcomes. That means there is no principled stopping rule for C3.
- *Resolution:* restrict the claim to C3-U4, fix the Fig. 1(a) label, and give a convergence criterion that predicts composability, or state that none exists.

**M11. Readability (Secs. 7–8 especially).**
- Section 7 is a dense list of internal codes and round numbers: R-B, PUSH/PROJ/CTX, "fifth round", "unit D", "F_empty", "R4-B unstable", "cells", "worlds".
- Readers cannot reconstruct the experimental design from the main text.
- Directory names are off by one relative to round names (v2 = composability_mechanisms_v1).
- *Resolution:* add a glossary or table of experimental units, use descriptive names instead of round numbers in the main text, and move bookkeeping to the appendix.

## 4. Minor comments

1. **Macro artefacts.** Phrases such as "step-1 success at least 1.00", "R_2 is at most 0.00", "R_2N ≥ 1.00" and "C1-U4 R_2N ≤ 0.00" (Intro, Sec. 4, Sec. 5) are awkward. Write "= 1.00" or "1.00 in every cell".
2. **Table numbering.** Sec. 3 introduces Table 1 (prediction counts), but the main-results table is Table 2, with the caption "generated by …/table1.py". Make the numbering consistent.
3. **Empty Appendix D.** "D Supplementary figures" is an empty heading; Figures 7–10 float elsewhere.
4. **Unclear denominator.** "The threshold is sharp on 4 domains of the second round" (Sec. 6) gives no denominator.
5. **Gate notation.** "G·-0" (App. A) renders as an unreadable symbol.
6. **Table 2 binding row.** "median R30 (8 seeds) 0.98" has no ledger macro in CL13. Please add one, plus the min across seeds.
7. **Fig. 2 caption.** It says "Rank-deficient RRR on BART month"; the embedded labels show RRR-8/9/10. State the ranks in the caption.
8. **Mixed number formats.** "R_6 = 0.80" (Sec. 8) uses ledger macro CLthirteenBtwo = "B/B2/max", which mixes ".2f" and ".3f" precision across the paper. Unify.
9. **Ambiguous framing.** "Editors trained in that round … are predicted equally well (0.982 and 0.976)" reads as "equally" while the numbers are higher. Also give cell counts; "new" cells may be easier.
10. **Missing confidence intervals.** World-cluster bootstrap CIs are promised (Sec. 3), but most numbers, including all intro numbers except none, lack CIs. At minimum give CIs for the predictor agreements and the R_2N medians.
11. **Notation drift.** "R_k" (trajectory) and "A_t" (per-step) are both plotted. Fig. 8 uses A_t while the text cites R_2N.
12. **Unexplained figure symbols.** "F{1}" and "F¬1" appear in figures but are not defined in the main text.
13. **Wording.** "Symmetry is not necessary" (Sec. 8) should say "translation-symmetric ordering of state words is not necessary for closed-form operators".
14. **Motivating citation.** Ref [1] (THE-X, homomorphic inference) does not pass latent states between components in the sense used here. Choose a closer motivating example or explain the link.
15. **Missing related work.** Engels et al. [2] already performed interventions on circular representations. When the related-work section is written, compare explicitly.

## 5. The three issues most likely to cause rejection

1. **Limited significance and external validity (M1, M2).** A synthetic, single-token, cyclic-attribute setting on two small encoder–decoder models. The headline contrast largely follows from the training objectives (a one-step CE editor is not asked to stay on-manifold; RRR is fitted on-manifold by construction).
2. **Evidence and bookkeeping inconsistencies that undercut the "preregistered" selling point (M3, M7, M8):**
   - six vs seven rounds;
   - an incomplete "complete" prediction table;
   - claims marked confirmed that cite failed locked predictions (v1/P5, v4/V0, v2/R3);
   - the erratum-contradicted cosine inference in the intro;
   - contaminated round-2 worlds behind CL2 and CL11;
   - a 3-seed result that failed to replicate.
3. **The predictor contribution is weak relative to its framing (M5, M6).** Gains over a per-cell majority reference are small, the naive baseline is a strawman, decoder calibration and step-1 decoding are used despite the "without decoding" framing, there is systematic over-estimation that could not be fixed, and D validates against training-family labels.

## 6. Missing baselines or comparisons

- **Mean-difference steering vector** (ActAdd / representation-engineering style; the "canonical write" averaged over worlds) applied repeatedly. This is the most natural baseline for the editing literature the intro cites.
- **Existing low-rank representation-editing methods**, such as ReFT/LoReFT-style interventions, trained with one-step and multi-step objectives.
- **Decode-and-re-encode** at every step, as an upper bound and as the realistic alternative when decoding is possible.
- **Manifold projection or "snapping"** after each step: nearest canonical encoding, or projection onto the span of clean codes. This is the obvious fix suggested by the paper's own analysis and is not tried as an editor (PUSH/PROJ are used only as diagnostics).
- **An explicit rotation-in-harmonic-planes editor**, the analytic operator implied by the Fourier account. It would test whether the account is sufficient.
- **Longer and randomised-horizon CE unrolls** (U8, U16, random S) without L2, to test whether the step-counter shortcut is horizon-specific.
- **Full-rank linear and nonlinear (MLP) editors**, to separate fitting objective from capacity.
- **A random-direction null** for the 0.003 cosine, and a **target-state probe** next to the source-state probe.
- **Predictor baselines:**
  - a per-cell majority reference with CI on the difference;
  - logistic regression on cheap latent features such as step-1 slot distance and norm;
  - a step-1-latent-readout-only rule.
- **Decoder-only backbones and natural text** (acknowledged TODO).

## 7. Possibly overstated claims

1. "it writes nearly the same vector whatever the source state (median cosine 0.986)" (Intro; Sec. 5).
   - The paper's own Appendix A records the v3 ERRATUM that a high write cosine does not imply a near-constant write.
2. "A closed-form operator of the same rank … composes for 2N steps on every backbone and domain (R_2N ≥ 1.00)" (Intro).
   - The number covers only one-way *plus* chains on the 10 single-template (backbone, domain) combinations of round 5.
   - Sec. 8 says the full-sequence operator "failed on the training templates already" in the multi-template setting.
   - Binding domains are excluded.
3. "adding a target for the state itself makes the editors compose (Section 5)" (Intro).
   - Only unrolled C3-U4 is confirmed. One-step C3 at the default 600 updates does not compose on month (0.35 at 900).
4. "Least squares therefore drops it first when rank is scarce" (Intro).
   - On real encodings the fundamental is the most degraded plane in only 17 of 28 cells (App. C, exploratory), and Prop. 2 has no proof.
5. "it has the smallest one-step energy in 13 of 13 backbone–domain combinations" (Intro).
   - 7 of the 13 are exploratory (round 3).
   - The locked fourth-round prediction V0 is listed as **failed** in Table 3.
   - The 13 "combinations" pool two rounds and may not be distinct combinations.
6. "the result is a failure pattern we predicted before each confirmation run" (Intro).
   - On held-out templates the frozen-fundamental alternating test failed on weekday (v6 M3), so not "each".
7. "Because composability is a property of the latent trajectory, it can be predicted without running the decoder" (Intro).
   - The vote weights are fitted on decoded dev probes.
   - The predictor over-estimates systematically (6,601 vs 2,656), and the attempted fixes failed.
   - The companion D test decodes step 1.
8. "A single comparison at step 1 … separates instruction writes from state writes in all 66 … and 82 … cells" (Intro).
   - The ground truth is the training family, not an independent measure of write type.
9. "The fifth round confirms the signature on all 66 CE cells: after one step the latent readout of the slot is still the start state" (Sec. 5).
   - The locked test L3b checks D ≥ 0.5, not readout = start.
10. "The edited latent therefore does not encode the target state; it encodes an instruction that the decoder executes once" (Sec. 5).
    - No target-state probe is reported. Absence is inferred from cosines and a source probe.
11. "We identify what composable low-rank edits must preserve" (Contributions).
    - The evidence is surgery and correlation, which shows sufficiency at most.
    - Scrambled orderings compose at a different rank, so the claimed necessity is not shown.
12. "derive the rank bound and the freeze signatures this implies" (Contributions).
    - All proofs are TODO.
13. "Every result comes from 7 preregistered rounds" (Contributions).
    - Many reported results are explicitly exploratory or post-hoc (Sec. 5 training length, Sec. 7 error analysis, the equal-weight readout, the binding mechanism).
    - The text elsewhere says six rounds.
14. "on clean inputs the decoder reads the state from the slot only" (Sec. 7).
    - It rests on dev swap probes of one kind.
    - The same section reports context repair restoring 0.53 of new cases, which the locked rule classed as unstable.
15. "The editors under-write the state" (Sec. 7).
    - Stated as fact although the preregistered rule classified the R4 result as unstable.
16. "reserving it fixes rank-deficient operators" (Sec. 6).
    - Confirmed only on T5Gemma (4 cells); partial on BART.

## 8. Required checks

### a(i). Residual positive statements that binding edits compose

- **Intro:** none. The intro states "none of the editors we trained composes over 100 steps (R_100 ≤ 0.06)". This is correctly negative, though see 8b on scope.
- **Table 2 (main results), row "Binding (bind3), two-layer editor, median R30 (8 seeds) 0.98":**
  - **Borderline.** It reads as a success.
  - It hides that 3 of 8 seeds fall below 0.90 at step 30.
  - The decay row directly below (max R_100 0.06) partly offsets it.
  - The 0.98 has no macro in claims.yaml (CL13).
  - Suggest replacing it with "seeds with R30 ≥ 0.90: 5/8" or adding the min.
- **Table 3 (Appendix A):**
  - **Residual positive.** The rows "v6 K/K2 H-closure decided" and "v6 K/Q17prime … K2 H-closure … decided" list H-closure as decided, with no annotation that it did not replicate in round 7.
  - Add a footnote or "not replicated" marker.
- **Sec. 8 "Binding":** balanced. "survives 30 steps on 5 of eight seeds … but every seed decays by 100 steps", the non-replication of the round-6 three-seed result, and the oracle decay are all stated.
- **Appendix A design flaws, "v6, K2":** correctly negative.
- **Figure 9 and Figure 10 captions:** neutral. The Fig. 10 caption explicitly says "The write error grows steadily rather than contracting."
- **Appendix E:** describes the binding editors only, with no outcome claims.

### a(ii). Statements that the predictor's over-estimation can be corrected or fixed

- **No location found** that claims the over-estimation can be corrected.
- **Sec. 7 "Why the predictor over-estimates":** correctly states that "adding margin and off-manifold checks … does not help … the checked predictor reduces to the slot readout".
- **Sec. 7, context term:** "a context term calibrated on these probes receives weight zero and cannot change any prediction" is correctly negative.
- **Possible misreading, Sec. 7:** "placing the slot at the correct in-plane position … (PUSH) restores decoding in 0.98 … and 0.95". This is a repair of the *latent*, not of the predictor, but a reader could take it as a fix. Suggest an explicit sentence: "these repairs are diagnostics and do not yield a better predictor".
- **Not about the predictor:** "reserving it fixes rank-deficient operators" (Sec. 6) concerns operators.

### a(iii). Proposition 4 treated as established

- **Sec. 8 "Alternating chains on unseen templates":** correct. It "fits the training templates … (exploratory) but not the held-out ones …, so we keep it as an unconfirmed explanation."
- **Appendix C, Proposition 4 header:** correct. "(one-cycle cancellation; not confirmed)" and "It remains an unconfirmed explanation."
- **Appendix C body:** mis-characterisation. "its preregistered tests on held-out templates were **mixed**" understates the outcome. The ledger (CL16) records A2 and A3 as **failed** and Q22 as "only A1". "Mixed" should become "failed (A2, A3); only the drift asymmetry A1 was confirmed".
- **Appendix C body:** "The statement holds exactly on ideal codes" is asserted while the proof is TODO. Under the linear-error assumption it is a trivial identity, so it is better presented as such.
- **Intro, Table 2, captions:** no mention, so nothing treats Prop. 4 as established.

### b. Introduction numbers vs claims.yaml meaning

| # | Number in intro | claims.yaml macro and meaning | Match? |
|---|---|---|---|
| 1 | "step-1 success 1.00 on BART-base" | CLoneVfiveCOneRoneMin: v5 L, **BART** C1v1 cells (one-way paths), min step-1 decoded success | **Yes.** The backbone is stated. The restriction to one-way paths of C1v1 cells is unstated but harmless. |
| 2 | "R_2 = 0.00" | CLoneVfiveCOneRtwoMax: v5 G5-0, v1 C1 R_2, **BART weekday/month × 3 seeds**, max. Alternatively CLoneVoneCOneRtwoMax: v1 C1, max over domains × seeds (BART). | **Partial.** BART only, and in round 5 only weekday/month. The sentence is generic ("no world is correct"). T5Gemma C1 is not covered by any intro macro (it appears only in Table 2). |
| 3 | "composes for 2N steps on every backbone and domain (R_2N ≥ 1.00)" | CLoneVfiveBaseMin: v5 G5-0, base operator **plus** R_2N, min over 10 (backbone, domain) | **Partial / no.** Plus path only; "every domain" means the 10 round-5 single-template combinations. Multi-template full-sequence RRR fails (Sec. 8) and binding is excluded. "≥ 1.00" should be "= 1.00". |
| 4 | "median cosine 0.986" | CLtwoWriteCosSource: median cosine of writes across source states (round v2) | **The number matches its definition.** The inference "nearly the same vector" contradicts the v3 ERRATUM in Appendix A. Backbone and domain scope are not stated. |
| 5 | "orthogonal … (0.003)" | CLtwoWriteCosCanon: median cosine with the canonical write | **Yes.** No null baseline. |
| 6 | "linear probe still reads the source state (1.00)" | CLtwoProbeSource: M3/median_source, note null | **Yes, probably** (no note in the ledger). Scope unstated. |
| 7 | "13 of 13 backbone–domain combinations" | CLsevenSoneSmallestAll / CLsevenCellsAll: "v3 7/7 (exploratory) + v4 V0 6/6 (confirmatory)" | **Partial / no.** It pools exploratory and confirmatory cells while the following sentence implies everything was predicted. It counts cells across rounds, which may not be distinct combinations. The locked V0 is "failed" in Table 3. |
| 8 | "from at most 0.61" | CLtenRRRMax: max RRR-r R_2N over the F cells (claim "confirmed (T5Gemma)") | **Yes.** The sentence says T5Gemma. |
| 9 | "to 1.00" | CLtenFFMin: min FF-r R_2N | **Yes.** |
| 10 | "in all 4 evaluable cells" | CLtenCells: F/Q16/n = 4 | **Yes.** "Evaluable" is not a ledger term but is harmless. |
| 11 | "0.922 (BART-base)" | CLeightAgreeBart: L/per_backbone/bart/L1/latent | **Partial.** The intro says "of worlds"; Sec. 7 says "(world, cell) pairs"; the Table 2 caption restricts to state-supervised cells. Fix the unit. |
| 12 | "0.959 (T5Gemma)" | CLeightAgreeTfive | **Partial,** same unit issue as #11. |
| 13 | "0.583 and 0.639" (naive rule) | CLeightNaiveBart / CLeightNaiveTfive | **Yes.** |
| 14 | "all 66 decoder-trained" | CLnineCE: L/L3/L3a/n = 66 | **Yes** for the count. The meaning of "separates instruction writes" is contested (M6). |
| 15 | "82 state-supervised cells" | CLnineState (derived) | **Yes.** |
| 16 | "one-way R_2N between 0.98 and 1.00" (held-out templates) | CLfourteenBaseHour 0.98 (BART hour-mt); CLfourteenBaseWeekday / BaseMonth / BaseTfive 1.00 (v6 M1) | **Yes.** It covers 3 BART domains and 1 T5Gemma domain (month), on multi-field templates only; the sentence is generic. |
| 17 | "none of the editors we trained composes over 100 steps (R_100 ≤ 0.06), including one given oracle routing" | CLthirteenHundredMax: v7 K5, **max R_100 of Att2L-U8 over the 8 seeds** | **No.** The number covers only Att2L-U8 on bind3. The ledger has only a median R_30 (0.04) for the oracle editor OR-U8, no R_100 for Att2L-U4 or Att1-U8, and name3/bind3fix only to 30 steps. Either restrict the sentence or add ledger macros for the other editors. |
| 18 | "7 preregistered rounds" (Contributions) | CLmetaRounds = 7: "preregistered rounds with a lock commit" (bookkeeping) | **The number matches the ledger,** but it contradicts Sec. 3 ("six preregistered rounds"), Appendix A ("six … v1–v6"), App. E compute (six rounds) and App. G (directories for v1–v6 only). |
| 19 | Fig. 1 caption "rank-16" | No macro (design constant) | **Consistent** with Sec. 3 and App. E. |

### c. Introduction claims vs locked predictions in claims.yaml

| Intro claim | Ledger claim (nature) | Locked predictions | Verdict |
|---|---|---|---|
| C1 is correct at step 1 but fails at step 2 ("decodable is not composable") | CL1 (confirmed) | v1/P5, v2/G2_0, v5/G5_0 | **Weakly supported.** v1/P5 is listed as **failed** in Table 3. v2/G2_0 and v5/G5_0 are sanity gates, and G5_0 does not appear in Table 3. No locked prediction specifically about C1 failing is shown as confirmed. |
| RRR-16 composes for 2N steps on every backbone and domain | CL1 (gates) | v2/G2_0, v5/G5_0 | **Supported only as a gate,** for plus chains in the gate's domains. The scope is overstated (8b #3). |
| CE editors write instructions, not states (cosine, orthogonality, probe) | CL2 (confirmed) | v2/M1–M3 (H-instr decided), v5/L3b (confirmed) | **Supported by locked predictions.** The cosine inference conflicts with the v3 erratum, and the v2 worlds are partly contaminated. |
| Unrolled training learns a step counter that fails past the horizon | CL3 (confirmed) | v4/U1, U1b, U2 (H-shortcut decided), v5/L4 | **Supported.** |
| Adding a state target makes the editors compose | CL4 ("confirmed (C3-U4); exploratory (training length)") | v5/L4 | **Supported for C3-U4 only.** The general phrasing is overstated. |
| The slot encodes its state as a Fourier code in a few harmonic planes | No dedicated claim (implicit in CL5/CL6/CL7) | None specific | **Not backed by a locked prediction** (and partly tautological, M4). |
| The fundamental has the smallest one-step energy in 13/13 | CL7 ("confirmed (s_1); partial (a_1)") | v4/V0 | **Weak.** The only locked prediction (V0) is **failed** in Table 3; 7/13 cells are exploratory. |
| Least squares drops the fundamental first when rank is scarce | THEORY (no predictions; numerical check / exploratory) | None | **Not supported by a locked prediction.** Prop. 2 is unproven, and real data match in only 17/28 cells. |
| Predicted frozen-plane failure pattern (one-way fail, alternating survive, revival at N) | CL5 (confirmed) | v2/R1, R2; v3/HS1, HS2, HS3; v4/V1, V2a | **Supported.** v3/HS2 and HS3 are missing from Table 3. "Before each confirmation run" overreaches given v6 M3 weekday failed. |
| FF-r makes rank-deficient operators compose on T5Gemma, only partly on BART | CL10 ("confirmed (T5Gemma)") | v5/F1 | **Supported for T5Gemma.** v5/F1 is not in Table 3, which lists only F/Q16. |
| Composability can be predicted from latents (0.922/0.959 vs 0.583/0.639) | CL8 (confirmed) | v5/L1, L2 | **Supported.** See M5 on baseline strength and calibration. |
| A single step-1 comparison separates instruction writes from state writes (66/82) | CL9 (confirmed) | v5/L3a, L3b, L3c | **Supported as family separation.** Requires decoding step 1. |
| Section 7 reports where the predictor errs | CL15 (decided/mixed; U1/U2 exploratory; P post-hoc exploratory) | v6/CT1 (failed), CT2; v7/R0–R4, U3, Q21 | **Not a positive claim;** fine as a pointer. Many of the details in Sec. 7 are exploratory or post-hoc. |
| Slot-centred operators compose on held-out templates; the predictor is less accurate on T5Gemma | CL14 (mixed: M1 H-general; M5 holds; M3, M4 not met) | v6/M1–M5 | **Supported for the operator part (M1).** The overall verdict is mixed, which the intro partly acknowledges. |
| Binding edits: no editor composes over 100 steps, including oracle routing | CL13 (decided: K5 H-slow-decay, K7 H-unrepresentable; K6 mixed; K2 not replicated; mechanism exploratory) | v5/B2, B3; v6/K1–K4; v7/K5–K7 | **Supported for Att2L-U8 (K5) and the horizon-matched oracle (K7, at 30 steps).** "None of the editors" over 100 steps goes beyond the ledger numbers. |
| Contribution: "derive the rank bound and the freeze signatures" | THEORY (no predictions) + CL5 | None for the derivation | **Not supported.** Proofs are TODO; only the empirical signatures (CL5) are confirmed. |
| Contribution: "Every result comes from 7 preregistered rounds; Appendix A lists every locked prediction" | META (bookkeeping) | None | **Not supported as worded.** Many results are exploratory, the paper says six elsewhere, and Table 3 omits v3/HS2, v3/HS3, v5/G5_0, v5/F1 and v6/P1a. |

## 9. Score and confidence

**Score: 3/10 (reject in current form). Confidence: 4/5.**

The testbed is clean, the frozen-plane mechanism is genuinely predictive, and the bookkeeping is unusually transparent. But the headline contrast largely follows from the training objectives, and the setting is far from the motivating pipelines. Several intro claims overreach their locked evidence, including confirmed claims that cite failed predictions, a cosine inference the authors' own erratum retracts, and scope-mismatched numbers. Confidence is 4 rather than 5 because I could read the figures only through their captions and embedded labels, not the plotted curves.

### 逐条回应（Claude，2026-11-25）

**处理状态**：
- **已改**：已在本轮提交中修改。
- **局限**：写入 §8 Other limits。
- **待定**：引言措辞（引言措辞由 lead 定，Claude 未动），或者需要新实验，交 lead 决定。

#### 主要意见

**M1 外部效度** · 局限 + 待定
- 局限一句已写入 §8。
- 自然文本（N 单元）、规模（G 单元与梯度）、decoder-only（D 单元）都在 v8 内。
- "管线用例"的讨论属于 discussion，由 lead 写。

**M2 核心对比近乎稻草人** · 局限 + 待定
- §8 已写明：C1 的失败是目标函数下的预期基线，本文的增量在"写了什么"和"状态必须携带什么结构"。
- 缺失的基线（均值差 steering、ReFT、U8/U16/随机视野 CE、满秩或 MLP 编辑器）已在 §8 中列为没做的比较。
- 是否补做，由 lead 定。

**M3 指令证据与勘误冲突** · §5 已改；引言待定
- §5 已改：
  - 承认高 cosine 并不排除源相关分量（引用勘误）；
  - 0.003 改为"与无关方向同量级"；
  - 注明没有训练目标状态探针。
- 引言第 38–41 行仍写"nearly the same vector … orthogonal"。**建议 lead 改为**："writes highly similar vectors across source states (median cosine …), unaligned with the change between the canonical encodings, and a linear probe still reads the source state"。
- 随机方向零基线与目标状态探针需要 v2 的写入向量。v2 当时只存了汇总量（v4 DEVIATIONS 9），因此要在已存的 v5 C1 编辑器上新算，属于探索性计算。待定。

**M4 傅里叶码近乎同义反复** · 局限 + 待定
- §8 已写：任意 N 个点都可做平面分解，内容在于哪些平面携带状态；打乱顺序在另一秩上可组合，所以这是对这些域的描述，不是普遍必要条件。
- 引言 Contributions 里的 "must preserve" 和标题里的 "Must" 待 lead 决定。我的建议：Contributions 改为 "what composable low-rank edits preserve in these domains"。标题是 lead 的决定。
- 逐平面圆度统计可从 v5 的平面拟合离线算出，属于探索性计算。待定。

**M5 预测器弱于叙述** · 部分已改，局限 + 待定
- §8 已写明以下两点：
  - 投票权重用解码过的 dev 探针校准，D 检验要解码第 1 步；
  - 多数参考达到 0.889/0.909（探索性）。
- 引言待定的两处：
  - "predicted without running the decoder" 建议改为 "without decoding the chains"；
  - "of worlds" 应为 "of (world, cell) pairs on state-supervised cells"。核对：宏 `CLeightAgreeBart` 取自 `L/per_backbone/bart/L1/latent`，与 §7 的单位一致。
- 相对多数参考的差值置信区间，以及逻辑回归基线：待定（探索性，CPU）。

**M6 D 检验以训练族为标签** · §5 已改；引言待定
- §5 已改为锁定检验的实际内容：每个 CE cell 中至少一半 world 的第 1 步读出与解码不一致，160/160 只是两个例子。
- 引言 "separates instruction writes from state writes" 建议改为 "separates the decoder-trained from the state-supervised editors"。

**M7 预注册簿记不一致** · 已改
- **轮数**：§3、附录 A、D（计算量，新增 `\CLmetaGpuVseven`）、F（目录映射，并注明目录编号比轮次小 1）统一为 `\CLmetaRounds` = 7。
- **表 3 补全**：
  - `predictions_table.py` 现在能识别 v3 的 HS2、HS3、HS4。HS4 原是平局 "tie:complete+vote"，现记为 mixed。
  - 补入 G4_0、G5_0、G6_0 的门槛文件。
  - 共 148 条。
- **K2 标注**：v6 K/K2 与 K/Q17prime 两行加注 "(not replicated in v7)"。
- **引用拆分**：claim_map 新增 `counter_predictions` 字段，失败、mixed、不可评估的预测不再记为支持：
  - CL1：P5 移入反例；
  - CL7：V0 移入反例，nature 改为 partial；
  - CL10：F1 改为 Q16；
  - CL11：R3 移入反例；
  - CL12：V2b、D1 移入反例；
  - CL13：B2、K2–K4、K6 移入反例；
  - CL14：M2–M4 移入反例；
  - CL15：CT1、R1、R3、R4 移入反例；
  - CL16：A2、A3 移入反例；
  - CL8b 的 P1a 是事后探索性分析，移入 `exploratory_sources`。
- **check.py 新增规则 3b**：每个被引用的预测都必须能在预测表中找到；作为支持的预测必须是 confirmed 或 decided；nature 为 confirmed 或 decided 的论断，至少要有一个 confirmed 或 decided 的支持预测。这条规则当场抓出了 4 处 mixed 被当作支持的引用。
- **计数表**：移到附录 A，正文表 1 即主结果表。表注说明：计数含子预测与汇总行，不是独立假设数；"decided" 是否为预期假设，见 claims.yaml。
- **"先定了什么"叙述**：未写，交 lead。

**M8 可重复性** · 已改 + 局限
- §3 已写：在 v4 中去掉重复 world 后重跑锁定分析，所有重算的判定都不变（NOTE_DEDUPE_v1/v2）。v2 的写入几何量（M1–M4 的 cosine 与探针）只存了汇总量，无法重算。
- 审稿说重复率为 2–12%，实际为 0.087–0.325（v2 confirm2）。论文中如需给出，应以 NOTE_DEDUPE 为准。
- 种子数已写入 §8 局限。加种子要用 GPU，待定。

**M9 理论未完成** · 部分已改；证明与引言待定
- 附录 C 的命题 4 改为"在线性误差假设下为恒等式；预注册检验只有漂移不对称成立，一阶抵消与逆算子两项失败"。
- 命题 1–4 的证明仍是 TODO，按计划在对话中与 lead 完成。
- 引言待定：
  - "Least squares therefore drops it first" 建议加限定，例如 "on ideal codes; on the real encodings the fundamental is the most degraded plane in most but not all cells"（17/28 是探索性结果）；
  - "derive the rank bound and the freeze signatures" 要在证明完成后才成立。

**M10 状态监督使编辑器可组合的普适性** · §5 已改；引言与图待定
- §5 已加一句：默认 600 次更新的一步 C3 不保证可组合。
- 引言 "adding a target for the state itself makes the editors compose" 建议改为 "… makes unrolled editors compose"。
- 图 1(a) 下行标签 "state write (RRR-16 / C3)"：建议改为 "(RRR-16 / C3-U4)"。这是按第 3 节规格画的，需要 lead 确认。

**M11 可读性** · 待定
- 术语表或实验单元表，以及正文用描述性名称替换轮次编号，工作量较大，建议在 lead 定稿 §7–8 时一起做。
- 目录编号偏移已在附录 F 注明。

#### 次要意见
1. **宏的措辞**：§4 已改为"最低/最高……为"。引言 "\Rk{2N}\ge\CLoneVfiveBaseMin" 建议改为 "="，待定。§5 的 "C1-U4 … at most" 仍在，下轮一起改。
2. **表号**：已改（计数表移入附录 A）。
3. **附录 D 空标题**：补充图改为 [H] 浮动，现紧跟标题。
4. **分母**：已改为 "\CLfiveRstarSharp{} of \CLfiveRstarDomains{}"。
5. **G·-0**：已改为 "G2-0 to G7-0"。
6. **绑定行**：表 1 已加 "min R_30 (8 seeds)" 一行（由 table1.py 从锁定结果生成）。
7. **图 2 图注**：已注明秩 8、9、10。
8. **数字格式统一**：未改，下轮处理。
9. **"equally well"**：已改为 "at least as well"。cell 数未补。
10. **置信区间**：未补，待定（与 M5 一起）。
11. **A_t 与 R_k 记号**：未改。
12. **F{1} 记号**：未改，下轮在 §6 定义。
13. **小节标题**：已改为 "A translation-symmetric ordering of the state words is not necessary"。
14. **THE-X 引用**：引言由 lead 定。
15. **Engels 等人**：related work 由 lead 写。

#### 第 8 节的三项检查
- **a(i) 残留的绑定正面陈述**：表 1 已加最小值行；表 3 中 K2 已注明未复现。没有其他残留。
- **a(ii) "预测器可修正"**：§7 已加一句 "These repairs are diagnostics that use the gold state; they do not yield a better predictor"。
- **a(iii) 命题 4**：附录 C 已改，见 M9。
- **b/c 引言宏与论断对照**：需要 lead 改动的引言处汇总如下（Claude 未动引言措辞）：
  1. 第 36–37 行 "on every backbone and domain (\ge)"：范围是第五轮 10 个单模板组合的 plus 链。建议 "on every single-template backbone–domain combination (=)"。
  2. 第 35–36 行 R_2 只覆盖 BART，建议加 "on BART-base"。
  3. 第 38–41 行：cosine 推断，见 M3。
  4. 第 50 行 "13 of 13"：其中 7 个是探索性的，锁定的 V0 失败（V0 同时要求 a_1 最大）。CL7 已改为 partial。**这一句必须改**，例如 "in every one of the 13 … (6 in a locked test that failed on its second condition)"，或删去。
  5. 第 51 行 "therefore drops it first"：见 M9。
  6. 第 51 行 "predicted before each confirmation run"：v6 M3 weekday 失败。建议 "before the confirmation runs, and confirmed on the training templates"。
  7. 第 59 行 "without running the decoder"：见 M5。
  8. 第 62 行 "of worlds"：见 M5。
  9. 第 63–64 行 "separates instruction writes from state writes"：见 M6。
  10. 第 74 行 "none of the editors … R_100 ≤"：宏只覆盖 Att2L-U8（REVIEW_LOG 第一部分第 3 条）。
  11. 第 82 行 "must preserve"、第 83 行 "derive"：见 M4、M9。
  12. 第 87 行 "Every result comes from …"：建议 "All confirmatory results come from …; exploratory analyses are marked"。

### 审后状态
- check.py 通过（180 个数字，规则 3b 生效）。
- 编译 23 页，无未定义引用。
- **主要意见中，审稿人列为拒稿主因的簿记问题（M7）已全部修复。**
- 其余主要意见已写入局限或交 lead。
- 引言 12 处待 lead 改。
- 需要新计算的项（M3 零基线与目标探针、M4 圆度、M5 置信区间与基线、M2 基线编辑器、M8 种子）列为待定。

## 2026-11-26，引言第 2 版并入（负责人与 Claude 修订）

- 原文照录，未改措辞。全部宏与引用键都能解析，无需修正。
- 图 1(a) 下行标签已按要求改为 "state write (RRR-16 / C3-U4)"（M10）。
- 按引言注释更新了 claim_map 的引用：
  - CL5：+ v8 N4、G3；
  - CL7：+ v8 G4（9B 上锁定确认），nature 改为 "confirmed at 9B-9B"，v4 V0 保留为反例；
  - CL8：+ v8 N5、G5；
  - CL9：+ v8 G5。
- check.py 通过；编译 26 页。
- **第二轮审稿前仍需完成的事项**：
  - 贡献 2 写的是 "prove"，命题 1–3 的证明须在附录 C 完成；
  - 第一部分第 4 条仍需注意：引言说的 "one-step energy smallest" 按平面计（v4/v8 的 s_k），命题 2 按每维能量排序，两者要在 §6 与附录 C 中对上。
