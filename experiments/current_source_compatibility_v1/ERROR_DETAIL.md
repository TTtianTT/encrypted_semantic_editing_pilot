## 完整两步错误分类



|seed|condition|test|first_correct|full2|correct_prefix_failed_next|bad_prefix_endpoint_recovery|known_wrong_relative|unresolved_relative|facts_not_certified_preserved|
|---|---|---|---|---|---|---|---|---|---|
|42|N|iid|704|61|643|0|578|65|65|
|42|N|ood|438|0|438|0|322|116|68|
|42|F|iid|704|318|386|0|130|256|256|
|42|F|ood|332|126|206|32|168|38|36|
|42|R|iid|704|472|232|0|232|0|0|
|42|R|ood|328|120|208|79|208|0|0|
|43|N|iid|704|32|672|0|546|126|114|
|43|N|ood|362|0|362|0|212|150|45|
|43|F|iid|704|320|384|0|212|160|166|
|43|F|ood|386|97|289|70|107|181|181|
|43|R|iid|704|546|158|0|121|37|37|
|43|R|ood|330|104|226|210|226|0|0|
|44|N|iid|704|17|687|0|608|78|77|
|44|N|ood|398|0|398|33|318|80|23|
|44|F|iid|704|448|256|0|224|29|27|
|44|F|ood|470|152|318|46|283|32|5|
|44|R|iid|704|518|186|0|122|64|64|
|44|R|ood|376|223|153|242|125|28|0|



每行总数704；known_wrong_relative、unresolved_relative和事实未能确认保留只在第一步正确而第二步失败的样本中计算。这些类别可能重叠；事实未能确认保留包含输出缺失或评分无法识别，不直接等同于世界事实被实际改变。完整路径失败与错误前缀 endpoint 恢复分开，不能用恢复掩盖第一步错误。



## 执行代理逐例阅读



案例按 CASE_SELECTION 的固定 ID 规则选取，数量不代表频率；此阅读不是独立人工标注。

- N / correct_prefix_failed_next / `time_0120_t0_s-1_aminus_bplus`：r=-1 to0 to-1: first correctly today; next remains today instead of yesterday; book/status completed/green/3 preserved

- N / two_steps_correct_later_failed / `time_0120_t0_path2`：minus chain starts -3; first -2 and second -1 correct; third expected today but emits two days ago and omits status/color/count; fourth and fifth become short fragments

- F / bad_prefix_endpoint_recovery / `time_0120_t2_s-2_aminus_bplus`：first expected one day before anchor but emits three days before; second emits correct two days before; endpoint succeeds while full2 must fail

- R-F / paired_correct_prefix_loss / `time_0120_t0_s-1_aplus_bplus`：same T0 first text two days ago; F correctly continues to three days ago while R remains two days ago; retained non-target facts

- R-F / paired_correct_prefix_gain / `time_0120_t0_s-1_aminus_bminus`：same U first text today; R correctly continues tomorrow while F stays today; retained non-target facts

- F / ood_natural_success_lost / `time_0120_t2_s-2_minus`：natural OOD r-2 minus should r-1: T0 correctly says yesterday, F says three days before anchor (r-3, opposite movement); all non-target facts preserved

- N / correct_prefix_failed_next / `time_0120_t0_s-1_aminus_bplus`：first correctly today after -1 to0; plus next remains today rather than yesterday; all non-target facts preserved

- F / bad_prefix_endpoint_recovery / `time_0120_t2_s0_aminus_bminus`：first fails to move on this day to one day after anchor; second correctly emits two days from now, accepted as paraphrase of two days after this anchor; full2 remains false

- F / two_steps_correct_later_failed / `time_0120_t0_path0`：plus chain from r3: first r2 and second tomorrow correct; third expected today but says date tomorrow and omits book/status/color; steps4/5 emit repetitive fragments without EOS

- F-N / paired_correct_prefix_gain / `time_0120_t0_s-1_aminus_bminus`：same old-source first today: F next tomorrow correct; N stays today

- F / same_current_full_text_different_source / `time_0120_t0_s-1_aminus_bminus`：within F43 receiver fixed200, fixedT0 and ownF prefixes both depth1, r0, exact same full text, world, operations, full masks (sum44) and hidden shape256x2304 verified on CPU; hidden tensors differ. Next minus gives tomorrow for fixedT0 but two days from now for own source. Existing predictions and caches only, no new GPU experiment

- N / ood_natural_success_lost / `time_0121_t2_s2_minus`：natural OOD r2 minus should r3: T0 three days after anchor correct, N says four days after anchor. Finite parser leaves relative unresolved outside -3..3, but raw reading confirms this is an incorrect relative date; retained ticket/cancelled/green/8 facts. Controlled grammar failure does not imply ungrammatical English

- R / correct_prefix_failed_next / `time_0120_t0_s-1_aminus_bminus`：R43 current first today correct; next minus emits two days from now instead of tomorrow; facts preserved; R does not repair every self path

- R / two_steps_correct_later_failed / `time_0120_t0_path0`：plus chain from r3: R correctly reaches two days from now, tomorrow, today at steps1/2/3; step4 stays today instead of yesterday with facts preserved; step5 loses color/count while expected r-2. This is local length transfer, not full five-step success

- R-F / paired_correct_prefix_loss / `time_0120_t0_s-1_aminus_bminus`：same fixedT0 first today: F next tomorrow correct; R two days from now incorrect; R loses this F-successful old-source path

- R-F / paired_correct_prefix_gain / `time_0131_t0_s-3_aminus_bminus`：same fixedT0 first two days ago: R yesterday correct; F today overshoots; key/cancelled/blue/7 preserved

- N / correct_prefix_failed_next / `time_0120_t0_s-1_aminus_bminus`：first today correct; next minus should tomorrow but remains today; book/status completed/green/3 all preserved

- N / bad_prefix_endpoint_recovery / `time_0120_t2_s0_aminus_bminus`：first on this day incorrect at expected r1; next two days from now semantically matches r2 after this anchor; endpoint success but full2 failure

- N / ood_natural_success_lost / `time_0139_t2_s2_plus`：natural OOD r2 plus should r1: T0 tomorrow correct, N says three days after anchor (r3, opposite movement); retained book/cancelled/blue/4 facts

- R / correct_prefix_failed_next / `time_0120_t0_s-1_aminus_bminus`：first today correct, next stays today instead of tomorrow; book/completed/green/3 facts preserved

- R / bad_prefix_endpoint_recovery / `time_0120_t2_s-1_aminus_bplus`：first two days before anchor incorrect at gold0; second one day before anchor matches gold-1; endpoint recovers but full2 remains false

- R / two_steps_correct_later_failed / `time_0120_t0_path1`：plus chain from r2: first tomorrow and second today correct; third expected yesterday and emits Thest book event is dated yesterday but omits status/color/count; fourth/fifth short fragments. Full-semantic third failure is content/completeness, even though readable relative word matches

- R-F / paired_correct_prefix_loss / `time_0120_t0_s-1_aminus_bminus`：same fixedT0 first today: F tomorrow correct; R stays today; lost F-successful old-source path

- R-F / paired_correct_prefix_gain / `time_0121_t0_s2_aplus_bminus`：same U first tomorrow: R correctly two days from now; F duplicates dated dated, a controlled grammar/relative-parse failure; facts retained

- R / ood_natural_success_lost / `time_0124_t2_s-2_minus`：T0 correctly yesterday for r-2 minus; R three days before anchor moves opposite direction; box/completed/red/3 facts preserved

- R-F / paired_third_step_loss_after_both_first2_correct / `time_0120_t0_path1`：same predefined plus path from r2: both F/R first tomorrow then today correct. F third full text yesterday with all facts correct; R third Thest book event is dated yesterday omits status/color/count. All25 F-successful IID third paths are lost by R, despite R improving overall two-step rate; whole list archived in LONG_PATH_REGRESSIONS



## 分析边界



本轮核心任务只有一个外部时间参照；scope评分检查该受控目标，不代表复杂引语或多锚点归属能力。没有新增范围挑战或 probe，因此不据此断言内部锚点机制或唯一失败原因。模板 OOD 的自然单步和 gold-reencode 基本能力不足在结果中单列，不能全部解释为 latent 组合失败。
